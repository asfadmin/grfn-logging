import csv
import json
from os import getenv
from os.path import basename
from logging import getLogger
from gzip import GzipFile
from datetime import datetime
from io import StringIO
import re
import boto3
from elasticsearch import Elasticsearch, RequestsHttpConnection
from aws_requests_auth.aws_auth import AWSRequestsAuth


log = getLogger()
s3 = boto3.client('s3')

index_body = {
    'dataRecord': {
        'properties': {
            'request_time': {'type': 'date'},
            'file_name':    {'type': 'string'},
            'user_id':      {'type': 'string'},
            'ip_address':   {'type': 'ip'},
            'http_status':  {'type': 'long'},
            'bytes_sent':   {'type': 'long'},
        },
    },
    'settings': {
        'number_of_replicas': 0,
        'number_of_shards': 1,
    },
}


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


def get_user_id(request_query_string):
    userid_pattern = re.compile(r'userid=([a-zA-Z0-9\._]+)')
    result = userid_pattern.search(request_query_string)
    if result:
        return result.group(1)
    return ''


def to_number(s):
    if s == '-':
        return 0
    return int(s)


def get_cloudfront_records(bucket, key):
    obj = s3.get_object(Bucket=bucket, Key=key)
    content = GzipFile(None, 'rb', fileobj=obj['Body']).read().decode()
    records = csv.reader(StringIO(content), delimiter='\t')
    marshalled_records = [
        {
            'id': record[14],
            'data': {
                'request_time': datetime.strptime(record[0]+record[1]+'+0000', "%Y-%m-%d%H:%M:%S%z"),
                'ip_address': record[4],
                'file_name': basename(record[7]),
                'user_id': get_user_id(record[11]),
                'http_status': to_number(record[8]),
                'bytes_sent': to_number(record[3]),
            },
        }
        for record in records if not record[0].startswith('#') and record[5] == 'GET' and record[8] in ['200', '206']
    ]
    return marshalled_records


def get_s3_records(bucket, key, role_arn):
    obj = s3.get_object(Bucket=bucket, Key=key)
    content = obj['Body'].read().decode()
    records = csv.reader(StringIO(content), delimiter=' ', quotechar='"')
    marshalled_records = [
        {
            'id': record[6],
            'data': {
                'request_time': datetime.strptime(' '.join(record[2:4]), "[%d/%b/%Y:%H:%M:%S %z]"),
                'ip_address': record[4],
                'file_name': basename(record[8]),
                'user_id': record[5].split('/')[-1],
                'http_status': to_number(record[10]),
                'bytes_sent': to_number(record[12]),
            },
        }
        for record in records if record[7] == 'REST.GET.OBJECT' and record[10] in ['200', '206'] and record[5].startswith(role_arn)
    ]
    return marshalled_records


def get_log_records(bucket, key, role_arn):
    if key.endswith('.gz'):
        return get_cloudfront_records(bucket, key)
    return get_s3_records(bucket, key, role_arn)


def lambda_handler(event, context):
    config = setup()
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        log.info('Processing file s3://{0}/{1}'.format(bucket, key))
        records = get_log_records(bucket, key, config['role_arn'])
        update_elasticsearch(records, config['elasticsearch'])
