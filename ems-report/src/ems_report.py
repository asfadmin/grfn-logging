import json
from datetime import datetime, timedelta
from logging import getLogger
from os import getenv
from tempfile import NamedTemporaryFile

import boto3
from aws_requests_auth.aws_auth import AWSRequestsAuth
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch.helpers import scan


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


def get_category(file_name: str) -> str:
    product_name = file_name.split('.')[0]

    if product_name.endswith('v2_0_6'):
        if file_name.endswith('.png'):
            return 'SENTINEL-1_INTERFEROGRAMS_BROWSE'
        if file_name.endswith('.unw_geo.zip'):
            return 'SENTINEL-1_INSAR_UNWRAPPED_INTERFEROGRAM_AND_COHERENCE_MAP'
        return 'SENTINEL-1_INTERFEROGRAMS'

    if product_name.endswith('v3_0_1'):
        if file_name.endswith('.png'):
            return 'ARIA_S1_GUNW_BROWSE'
        return 'ARIA_S1_GUNW'

    raise ValueError(f'File {file_name} must be v2_0_6 or v3_0_1')


def get_records(report_date, config):
    es = get_elasticsearch_connection(config['host'])
    query = {
        'query': {
            'range': {
                'request_time': {
                    'gte': report_date.strftime('%Y-%m-%d'),
                    'lte': report_date.strftime('%Y-%m-%d'),
                }
            }
        }
    }
    results = scan(es, query=query, index=config['index'])
    records = [result['_source'] for result in results]
    return records


def upload_report(records, report_date, config):
    report_name = '{0}{1:%Y%m%d}_ASF_DistCustom_GRFNBETA.flt'.format(config['prefix'], report_date)
    log.info('Uploading report to s3://{0}/{1}'.format(config['bucket'], report_name))
    with NamedTemporaryFile('w') as f:
        for r in records:
            r['category'] = get_category(r['file_name'])
            r['parsed_time'] = datetime.strptime(r['request_time'], '%Y-%m-%dT%H:%M:%S+00:00')
            f.write('[{parsed_time:%d/%b/%Y:%H:%M:%S}]|&|{category}|&|{ip_address}|&|{user_id}|&|{bytes_sent}|&|'
                    '{http_status}\n'.format(**r))
        f.flush()
        s3.upload_file(f.name, config['bucket'], report_name)


def generate_ems_report(report_date, config):
    log.info('Generating GRFN EMS report for {:%Y-%m-%d}'.format(report_date))
    records = get_records(report_date, config['elasticsearch'])
    upload_report(records, report_date, config['output'])


def lambda_handler(event, context):
    config = setup()
    if 'report_date' in event:
        report_date = datetime.strptime(event['report_date'], '%Y-%m-%d')
    else:
        report_date = datetime.utcnow() - timedelta(1)
    generate_ems_report(report_date, config)
