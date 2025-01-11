from kafka import KafkaProducer, KafkaConsumer
import json
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import Table, Column, String, MetaData
from sqlalchemy.orm import sessionmaker
import time
from threading import Thread
from sqlalchemy.future import select
import os

metadata = MetaData()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL)
KAFKA_SERVER = os.getenv("KAFKA_SERVER")
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

def send_to_kafka(topic, data, kafka_server=KAFKA_SERVER):
    producer = KafkaProducer(
        bootstrap_servers=kafka_server,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    producer.send(topic, data)
    producer.flush()

async def save_to_db(batch):

    async with engine.begin() as conn:
        
        await conn.execute(
            job_details.insert(),
            batch
        )
    print(f"Saved {len(batch)} records to the database")
        
async def consume_and_save(topic, kafka_server=KAFKA_SERVER, db_params=None, batch_size=10, interval=300):
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
        consumer.commit()  # Manually commit the offset after processing each message
        if len(batch) >= batch_size:
            await save_to_db(batch)
            
            batch = []

