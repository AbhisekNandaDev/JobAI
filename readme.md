
# JobAI

JobAI is a comprehensive job scraping and recommendation system. It leverages LinkedIn to scrape job postings, processes the data using a Kafka pipeline, and stores it in a PostgreSQL database. It then uses a machine learning model to provide job recommendations to users based on their profiles. The entire workflow is orchestrated using Apache Airflow.

## Features

- **User Authentication**: Secure user registration and login functionality.
- **LinkedIn Job Scraping**: A Selenium-based crawler to scrape job details from LinkedIn.
- **Asynchronous Data Pipeline**: Uses Kafka to handle data streams from the scraper to the database.
- **Job Recommendation System**: A KMeans clustering model to recommend jobs to users based on their profiles and job descriptions.
- **Orchestration with Airflow**: Airflow DAGs to schedule and manage the crawling and model training tasks.
- **Containerized Application**: Docker-compose setup for easy deployment and management of all services.

## Tech Stack

- **Backend**: FastAPI
- **Database**: PostgreSQL
- **Caching**: Redis
- **Data Streaming**: Kafka, Zookeeper
- **Web Scraping**: Selenium
- **Workflow Management**: Apache Airflow
- **Machine Learning**: Scikit-learn, NLTK
- **Containerization**: Docker

## Project Structure

```
├── dags
│   ├── airflow_crawler_schudler.py   # Airflow DAG for scheduling the LinkedIn crawler
│   ├── ariflow_kafka_schuler.py      # Airflow DAG to consume data from Kafka and save to DB
│   └── airflow_model_training.py     # Airflow DAG for training the recommendation model
├── .gitignore                        # Specifies files to be ignored by Git
├── docker-compose.yml                # Docker compose file to run all services
├── jwt_auth.py                       # JWT authentication helper functions
├── kafka_push.py                     # Kafka producer and consumer functions
├── linkedin.py                       # LinkedIn scraper using Selenium
├── main.py                           # Main FastAPI application with API endpoints
├── model_schema.py                   # Pydantic models for request/response validation
├── models.py                         # SQLAlchemy models for database tables
```

## Setup and Installation

### Prerequisites

- Docker and Docker Compose
- A `.env` file with the necessary environment variables.

### Environment Variables

Create a `.env` file in the root of the project with the following variables:

```
DATABASE_URL=postgresql+asyncpg://airflow:airflow@postgres:5432/airflow
LINKEDIN_EMAIL=your_linkedin_email
LINKEDIN_PASSWORD=your_linkedin_password
GROQ_KEY=your_groq_api_key
SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
KAFKA_SERVER=localhost:9092
```

### Installation

Clone the repository:

```bash
git clone https://github.com/abhiseknandadev/JobAI.git
cd JobAI
```

Build and run the services using Docker Compose:

```bash
docker-compose up --build -d
```

## Running the Project

Once the Docker containers are up and running, the following services will be available:

- **FastAPI Backend**: http://localhost:8000
- **FastAPI Docs**: http://localhost:8000/docs
- **Airflow Webserver**: http://localhost:8080 (Default credentials: admin/admin)
- **PostgreSQL**: localhost:5432
- **Kafka**: localhost:9092
- **Redis**: localhost:6379

## Airflow DAGs

You can manage and monitor the crawling and model training jobs from the Airflow UI.

- **crawler_scheduler**: Runs the LinkedIn crawler every 5 hours.
- **kafka_to_db_dag**: Runs every 3 minutes to consume job data from the `job_details_topic` in Kafka and save it to the PostgreSQL database.
- **airflow_model_training**: Runs every 30 minutes to train the KMeans recommendation model with the latest data from the database.

## API Endpoints

- `POST /signup`: Register a new user.
- `POST /login`: Login a user and get a JWT token.
- `POST /reset-password`: Reset user password.
- `GET /jobs`: Get a list of all jobs from the database.
- `POST /userProfile`: Create a user profile with job preferences.
- `GET /recommendations/{user_id}`: Get job recommendations for a specific user.
