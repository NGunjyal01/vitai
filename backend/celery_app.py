from celery import Celery
from dotenv import load_dotenv
import os

load_dotenv()

celery = Celery(
    'vitai',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379')
)
celery.conf.task_serializer = 'json'
celery.conf.result_serializer = 'json'
celery.conf.include = ['tasks']