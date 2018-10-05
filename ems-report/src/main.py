import csv
import json
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


def get_category(file_name):
    if file_name.endswith('.png'):
        category = 'SENTINEL-1_INSAR_FULL_RES_WRAPPED_INTERFEROGRAM_AND_DEM_BROWSE (BETA)'
    elif file_name.endswith('.unw_geo.zip'):
        category = 'SENTINEL-1_INSAR_UNWRAPPED_INTERFEROGRAM_AND_COHERENCE_MAP (BETA)'
    elif file_name.endswith('.full_res.zip'):
        category = 'SENTINEL-1_INSAR_FULL_RES_WRAPPED_INTERFEROGRAM_AND_DEM (BETA)'
    else:
        category = 'SENTINEL-1_INSAR_ALL_INTERFEROMETRIC_PRODUCTS (BETA)'
    return category


def lambda_handler(event, context):
    config = setup()
    es = get_elasticsearch_connection(config['host'])
    results = es.search(
        index=config['index'],
        doc_type='log',
        _source_include=['request_time', 'ip_address', 'user_id', 'http_status', 'file_name', 'bytes_sent'],
        size=10,
        q='user_id:asjohnston',
    )
    records = [result['_source'] for result in results['hits']['hits']]
    with open('/tmp/ems.csv', 'w') as f:
        for r in records:
            r['category'] = get_category(r['file_name'])
            r['formatted_time'] = datetime.strftime(datetime.strptime(r['request_time'], '%Y-%m-%dT%H:%M:%S+00:00'), '%d/%b/%Y:%H:%M:%S')
            f.write('[{formatted_time}]|&|{category}|&|{ip_address}|&|{user_id}|&|{bytes_sent}|&|{http_status}\n'.format(**r))
    s3 = boto3.client('s3')
    s3.upload_file('/tmp/ems.csv', 'asjohnston-dev', 'ems.csv')
