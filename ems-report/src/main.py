import csv
from os import getenv
from logging import getLogger
from datetime import datetime
import boto3
from elasticsearch import Elasticsearch, RequestsHttpConnection
from aws_requests_auth.aws_auth import AWSRequestsAuth


log = getLogger()
s3 = boto3.client('s3')


def setup():
    log.setLevel('INFO')
    config = json.loads(getenv('CONFIG'))
    return config


def get_elasticsearch_connection(host):
    auth = AWSRequestsAuth(aws_access_key=getenv('AWS_ACCESS_KEY_ID'),
                           aws_secret_access_key=getenv('AWS_SECRET_ACCESS_KEY'),
                           aws_token=getenv('AWS_SESSION_TOKEN'),
                           aws_host=host,
                           aws_region=getenv('AWS_REGION'),
                           aws_service='es')
    es = Elasticsearch(hosts=[{'host': host, 'port': 443}],
                       use_ssl=True,
                       verify_certs=True,
                       http_auth=auth,
                       connection_class=RequestsHttpConnection)
    return es


def update_elasticsearch(records, config):
    es = get_elasticsearch_connection(config['host'])
    if not es.indices.exists(config['index']):
        es.indices.create(config['index'], body=index_body)
    for record in records:
        es.index(index=config['index'], id=record['id'], doc_type='log', body=record['data'])


def generate_ems_report(config):
    start = datetime.datetime(2018, 10, 4, 0, 0, 0)
    end = datetime.datetime(2018, 10, 4, 23, 59, 0)
    records = get_records_by_date(start, end, config['host'])
    report_content = generate_report_content(records)
    upload_report_content(report_content, config['output_bucket'])


def lambda_handler(event, context):
    config = setup()
    #generate_ems_report(config)
