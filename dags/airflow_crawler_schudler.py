from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from linkedin_crawler import run_crawler
import linkedin

def run_crawler():
    linkedin.run_crawler()
    

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'crawler_scheduler',
    default_args=default_args,
    description='A simple DAG to run crawlers',
    schedule_interval='0 */5 * * *', 
)


run_crawler_task = PythonOperator(
    task_id='run_crawler',
    python_callable=run_crawler,
    dag=dag,
)

run_crawler_task