from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
import sqlalchemy
import joblib
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 10, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'airflow_model_training',
    default_args=default_args,
    description='A simple DAG to train a KMeans model',
    schedule_interval=timedelta(minutes=30),
)

def preprocess_text(text):
    # Lowercase
    text = text.lower()
    # Remove special characters
    text = re.sub(r'[^a-z\s]', '', text)
    # Tokenize and remove stopwords
    stop_words = set(stopwords.words('english'))
    words = [word for word in text.split() if word not in stop_words]
    # Lemmatize
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word) for word in words]
    return ' '.join(words)

def extract_data():
    metadata = MetaData()
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_async_engine(DATABASE_URL)
    query = "SELECT * FROM jobs"
    df = pd.read_sql(query, db_connection)
    df.to_csv('/tmp/data.csv', index=False)

def preprocess_data():
    df = pd.read_csv('/tmp/data.csv')
    df['processed_text'] = df['text_column'].apply(preprocess_text)
    df.to_csv('/tmp/processed_data.csv', index=False)

def train_model():
    df = pd.read_csv('/tmp/processed_data.csv')
    text_data = df['processed_text'].tolist()

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer()),
        ('scaler', StandardScaler(with_mean=False)),
        ('kmeans', KMeans(n_clusters=3, random_state=42))
    ])

    pipeline.fit(text_data)
    joblib.dump(pipeline, '/tmp/kmeans_model.pkl')

# Define the tasks
extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    dag=dag,
)

preprocess_task = PythonOperator(
    task_id='preprocess_data',
    python_callable=preprocess_data,
    dag=dag,
)

train_task = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    dag=dag,
)

# Set task dependencies
extract_task >> preprocess_task >> train_task
