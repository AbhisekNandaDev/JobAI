from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import asyncio
from kafka import KafkaConsumer
import json
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import Table, Column, String, MetaData
import os

metadata = MetaData()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL)


job_details = Table(
    'jobs', metadata,
    Column('jobname', String),
    Column('jobdesc', String),
    Column('jobbenifits', String),
    Column('jobqualification', String),
    Column('jobskills', String),
    Column('joblocation', String),
    Column('jobsalary', String),
    Column('jobrequirements', String),
    Column('jobexperience', String),
    Column('companyname', String),
    Column('joblink', String)
)

async def save_to_db(batch):

    async with engine.begin() as conn:
        
        await conn.execute(
            job_details.insert(),
            batch
        )
    print(f"Saved {len(batch)} records to the database")
        
async def consume_and_save(topic, kafka_server='localhost:9092', db_params=None, batch_size=10, interval=300):
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=kafka_server,
        value_deserializer=lambda v: json.loads(v.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=False,
        group_id='my_group'
    )
    batch = []
    for message in consumer:
        #print(f"Consumed message: {message.value}")
        batch.append(message.value)
        consumer.commit() 
        if len(batch) >= batch_size:
            await save_to_db(batch)
            
            batch = []


def push_kafka_data_to_db():
    asyncio.run(consume_and_save('job_details_topic'))

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 10, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

dag = DAG(
    'kafka_to_db_dag',
    default_args=default_args,
    description='A simple DAG to push Kafka topic data to DB',
    schedule_interval='*/3 * * * *',
)

kafka_to_db_push = PythonOperator(
    task_id='push_kafka_data_to_db',
    python_callable=push_kafka_data_to_db,
    dag=dag,
)

kafka_to_db_push
