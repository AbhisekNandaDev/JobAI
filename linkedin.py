import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from groq import Groq
import json
import os
import re
import random
from kafka_push import send_to_kafka
GROQ_KEY=os.getenv("GROQ_KEY")
client = Groq(api_key=GROQ_KEY)

options = Options()

LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")



def login(driver, username, password):
    """Logs in to LinkedIn with the specified driver."""
    driver.get("https://www.linkedin.com/login")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.XPATH, '//button[@type="submit"]').click()
    time.sleep(10)  # Wait for login to complete

# distractions
distraction_links=["https://www.linkedin.com/mynetwork/grow/?skipRedirect=true","https://www.linkedin.com/groups/","https://www.linkedin.com/","https://www.linkedin.com/notifications/?filter=all"]

prompt = """
You are an expert AI assistant specialized in extracting structured information from text. Your task is to analyze the provided text and extract the required details according to the given JSON schema. Strictly adhere to the schema, ensuring all fields are accurately populated or assigned fallback values (null) if the required information is missing or incomplete.
JSON Schema:
{
    "jobname": "extract Name of the job if it exists, otherwise None.",
    "jobdesc": "extract Description of the job in 100 words if it exists, otherwise None.",
    "jobbenifits": "extract Benefits of the job if they exist,try to extract from text if not mentioned directly otherwise None.",
    "jobqualification": "extract Qualifications required for the job if they exist it not exist Roles And Responsibilities or Qualifications And Skills, otherwise None.",
    "jobskills": "extract Skills required for the job if they exist (e.g., Python, JavaScript,Sales) try to extract from text if not mentioned directly , otherwise None.",
    "joblocation": "extract Location of the job if it exists, otherwise None.",
    "jobsalary": "extract salary for the job in inr if it exists, otherwise None.",
    "jobrequirements": "extract Requirements for the job if it exists, otherwise None.",
    "jobexperience": "extract salary for the job if it exists, otherwise None.",
    "companyname": "extract Name of the company that posted the job if it exists, otherwise None."
}
Analyze the text and provide the output strictly in JSON format with no additional text or explanations.

Text:"""

def crawl_details(browser:webdriver,link):
    browser.get(link)
    time.sleep(3)
    job_name = browser.find_element(By.CSS_SELECTOR,"div.t-14.artdeco-card").text
    browser.implicitly_wait(10)
    see_more_button = browser.find_element(By.CSS_SELECTOR, "button[aria-label='Click to see more description']")
    see_more_button.click()
    print("Clicked the 'See more' button!")
    text = browser.find_element(By.CSS_SELECTOR,"div.jobs-description__content.jobs-description-content.jobs-description__content--condensed").find_element(By.CSS_SELECTOR,"div.mt4")
    text_data = text.text
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {
                "role": "user",
                "content": prompt+job_name+text_data
            }
        ],
        temperature=1,
        max_tokens=5030,
        top_p=1,
        stream=False,
        response_format={"type": "json_object"},
        stop=None,
    )
    final_data = json.loads(completion.choices[0].message.content)
    final_data["joblink"]=link
    
    return final_data




def run_crawler():
    drivers = [webdriver.Edge() for _ in range(2)]
    login(drivers[0], LINKEDIN_EMAIL, LINKEDIN_PASSWORD)
    login(drivers[1], LINKEDIN_EMAIL, LINKEDIN_PASSWORD)

    driver=drivers[0]
    page_crawler_driver=drivers[1]

    start=0
    all_links=[]
    for i in range(2):
        try:
            job_cards_links=[]
            url="https://www.linkedin.com/jobs/all/?currentJobId=4109961752&f_I=4&origin=JOB_SEARCH_PAGE_JOB_FILTER&sortBy=R&start="+str(start)
            driver.get(url)
            
            scrollable_element = driver.find_element(By.CSS_SELECTOR, "div.hIAMCqpFeYcVjeOPoulLoCCKJjLsx")
            last_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_element)       
            while True:
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_element)
                
                time.sleep(2)
                
                new_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_element)
                
                if new_height == last_height:
                    break
                last_height = new_height
                
            time.sleep(5)
            jobs = driver.find_element(By.CSS_SELECTOR,"ul.rjmNTMLkNvPwnJnFTCybgSFpgYGQ")
            job_cards=jobs.find_elements(By.CSS_SELECTOR,"li.ember-view.DijVmLPbnmOkBbOHcNzmOjUzYORNxkzwmY.occludable-update.p0.relative.scaffold-layout__list-item")
            for job in job_cards:
                try:
                    link = job.find_element(By.TAG_NAME,"a").get_attribute("href")
                    job_cards_links.append(link)
                except:
                    pass
            all_links=all_links+job_cards_links
            start=start+25
        except:
            pass
    
    data=[]
    count=0
    for link in all_links:
        if count == 5:
            dist_url= random.choice(distraction_links)
            page_crawler_driver.get(dist_url)
            count=0
            continue
        try:
            send_to_kafka(topic="job_details_topic",data=crawl_details(page_crawler_driver,link),kafka_server='localhost:9092')
            print("Sent data to Kafka!")
            count=count+1
        except:
            try:
                send_to_kafka(topic="job_details_topic",data=crawl_details(page_crawler_driver,link),kafka_server='localhost:9092')
                print("Sent data to Kafka!")
                count=count+1
            except Exception as e:
                print(f"Error: {e}")
                pass

