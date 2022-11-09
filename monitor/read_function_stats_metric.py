# Check https://github.com/apache/openwhisk/blob/master/docs/annotations.md
# for couchdb record annotations
# the unit of time metric should be milliseconds

# assume docker version >= 1.13
import os
import time
import numpy as np
import argparse
import logging
import subprocess
import csv
import json

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--limit', dest='limit', type=int, default=200000)
parser.add_argument('--since', dest='since', type=int, required=True)
parser.add_argument('--users', dest='users', type=str, required=True)
parser.add_argument('--runtime', dest='runtime', type=str, required=True)
parser.add_argument('--detail-lat', dest='detail_lat', action='store_true')

args = parser.parse_args()
since = int(args.since)
limit = args.limit

# CouchDB (from #OPENWHISK_DIR/ansible/db_local.ini)
'''
[db_creds]
db_provider=CouchDB
db_username=yz2297
db_password=openwhisk_couch
db_protocol=http
db_host=128.253.128.68
db_port=5984

[controller]
db_username=whisk_local_controller0
db_password=some_controller_passw0rd

[invoker]
db_username=whisk_local_invoker0
db_password=some_invoker_passw0r
'''
DB_PROVIDER = 'CouchDB'
DB_USERNAME = 'admin'
DB_PASSWORD = 'password'
DB_PROTOCOL = 'http'
DB_HOST = '10.150.21.197'
DB_PORT = '5984'

# -----------------------------------------------------------------------
# miscs
# -----------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)

# since should be millisecond scale
def get_activation_since(since, limit=100000):
	"""
	Returns the activation IDs (including the namespace)
	"""
	res = requests.post(url=DB_PROTOCOL + '://' + DB_HOST + ':' + DB_PORT + '/' + 'whisk_local_activations/_find',
		json={
			"selector": {
				"start": {
					"$gte": since
				}
			},
			"fields": ['activationId', 'annotations', 'duration', 'end', 'name', 'namespace', 'start', 'response'],
			"limit": limit
		}, auth=(DB_USERNAME, DB_PASSWORD))
	doc = json.loads(res.text)['docs']
	return doc


# read activation data from db
activations = get_activation_since(since=since, limit=limit)
metric_file = open(f'./data/only_metric_{args.users}_{args.runtime}.csv')
result_file = open(f'./data/data_{args.users}_{args.runtime}.csv', 'w')

metric_reader = csv.reader(metric_file)
result_writer = csv.writer(result_file, delimiter=',')

header = next(metric_reader)
header.extend(['duration', 'waitTime', 'initTime', 'creationTime'])
result_writer.writerow(header)

activation_result = {}

for record in activations:
	activation_id = record['activationId']
	duration = record['duration']
	waitTime = 0
	initTime = 0
	creationTime = 0

	for d in record['annotations']:
		if d['key'] == 'waitTime':
			waitTime = d['value']
		elif d['key'] == 'initTime':
			initTime = d['value']
		elif d['key'] == 'coldstartTime':
			creationTime = d['value']

	activation_result[activation_id] = [duration, waitTime, initTime, creationTime]

for line in metric_reader:
	activation_id = line[0]
	line.extend(activation_result[activation_id])
	result_writer.writerow(line)