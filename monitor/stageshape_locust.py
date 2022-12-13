import logging
from locust import HttpUser, task, tag, LoadTestShape, constant_throughput, events
import urllib3
import json
import random
import numpy as np
import math
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO)


class OpenWhiskUser(HttpUser):
	wsk_auth = '23bc46b1-71f6-4ed5-8c54-816aa4f8c502:123zO3xZCLrMN6v2BKK1dXYFpXlPkccOFqm12CdAsMgRU4VrNZ9lyGVCGuMDGIwP'
	auth = tuple(wsk_auth.split(':'))
	url_noweb = '/api/v1/namespaces/guest/actions/'
	url_web = '/api/v1/web/guest/default/'
	beta = 1.0
	data_cache = {}
	bench_num = 20
	# wait_time = constant_throughput(1)

	def wait_time(self):
		return np.random.exponential(scale=self.beta)

	@task(1)
	@tag('base64')
	def base64(self):
		params = {}
		params['blocking'] = 'false'
		params['result'] = 'true'

		num = random.randint(0, self.bench_num)
		url = self.url_noweb + 'base-' + str(num).zfill(2)

		r = self.client.post(url, params=params, auth=self.auth, verify=False, name='/base64')

		if r.status_code > 300:
			logging.warning('base64 resp.status: %d, text: %s' % (r.status_code, r.text))

	@task(1)
	@tag('primes')
	def primes(self):
		params = {}
		params['blocking'] = 'false'
		params['result'] = 'true'

		num = random.randint(0, self.bench_num)
		url = self.url_noweb + 'prim-' + str(num).zfill(2)

		r = self.client.post(url, params=params, auth=self.auth, verify=False, name='/primes')

		if r.status_code > 300:
			logging.warning('primes resp.status: %d, text: %s' % (r.status_code, r.text))

	@task(1)
	@tag('img_resize')
	def img_resize(self):
		params = {}
		params['blocking'] = 'false'
		params['result'] = 'true'

		num = random.randint(0, self.bench_num)
		url = self.url_web + 'imgr-' + str(num).zfill(2)

		r = self.client.post(url, params=params, auth=self.auth, verify=False, name='/imgresize')

		if r.status_code > 300:
			logging.warning('imgresize resp.status: %d, text: %s' % (r.status_code, r.text))

	@task(1)
	@tag('markdown')
	def markdown(self):
		params = {}
		params['blocking'] = 'false'
		params['result'] = 'true'

		num = random.randint(0, self.bench_num)
		url = self.url_noweb + 'mark-' + str(num).zfill(2)

		r = self.client.post(url, params=params, auth=self.auth, verify=False, name='/markdown')

		if r.status_code > 300:
			logging.warning('markdown resp.status: %d, text: %s' % (r.status_code, r.text))

	@task(1)
	@tag('img_processing')
	def img_processing(self):
		params = {}
		params['blocking'] = 'false'
		params['result'] = 'true'

		num = random.randint(0, self.bench_num)
		url = self.url_web + 'imgp-' + str(num).zfill(2)

		r = self.client.post(url, params=params, auth=self.auth, verify=False, name='/imgprocess')

		if r.status_code > 300:
			logging.warning('imgprocessing resp.status: %d, text: %s' % (r.status_code, r.text))


class StageShape(LoadTestShape):
	SECONDS_PER_MINUTE = 60
	timelimit = 60 * SECONDS_PER_MINUTE

	start_user = 15
	step_time = 15 * SECONDS_PER_MINUTE
	step_user = 5

	def tick(self):
		run_time = self.get_run_time()

		if run_time > self.timelimit:
			return None

		cur_step = math.floor(run_time / self.step_time)
		cur_user = self.start_user + self.step_user * cur_step

		return (cur_user, cur_user)