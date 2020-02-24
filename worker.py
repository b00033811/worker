'''worker should have all required dependencies for your job to work,
in this example we will simply use numpy to calculate a moving average
hence we need to include it in the requirments file'''
from redis import Redis
from rq import Queue, Worker
from os import environ
from job import predict
redis = Redis(host=environ['REDIS_HOST'],port=environ['REDIS_PORT'])
queue = Queue(connection=redis)
worker = Worker([queue], connection=redis)
worker.work()
