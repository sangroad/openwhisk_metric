import logging
from locust import HttpUser, task, tag, LoadTestShape, constant_throughput, event
import urllib3
import json
import random
import numpy as np
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO)


class OpenWhiskUser(HttpUser):
	wsk_auth = "23bc46b1-71f6-4ed5-8c54-816aa4f8c502:123zO3xZCLrMN6v2BKK1dXYFpXlPkccOFqm12CdAsMgRU4VrNZ9lyGVCGuMDGIwP"
	auth = tuple(wsk_auth.split(":"))
	url_noweb = "/api/v1/namespaces/guest/actions/"
	url_web = "/api/v1/web/guest/default/"
	beta = 1.0
	data_cache = {}
	# bench_num = 25
	bench_num = 20
	# wait_time = constant_throughput(1)

	def wait_time(self):
		return np.random.exponential(scale=self.beta)

	def on_stop(self):
		params = {}
		params["blocking"] = "false"
		params["result"] = "true"
		url = self.url_noweb + "func----"

		r = self.client.post(url, params=params, auth=self.auth, verify=False, name="/last")

		if r.status_code > 300:
			logging.warning("func---- resp.status: %d, text: %s" % (r.status_code, r.text))


	@task(1)
	@tag("base64")
	def base64(self):
		params = {}
		params["blocking"] = "false"
		params["result"] = "true"

		num = random.randint(0, self.bench_num)
		url = self.url_noweb + "base-" + str(num).zfill(2)

		r = self.client.post(url, params=params, auth=self.auth, verify=False, name="/base64")

		if r.status_code > 300:
			logging.warning("base64 resp.status: %d, text: %s" % (r.status_code, r.text))

	@task(1)
	@tag("http")
	def http(self):
		params = {}
		params["blocking"] = "false"
		params["result"] = "true"

		num = random.randint(0, self.bench_num)
		url = self.url_noweb + "http-" + str(num).zfill(2)

		r = self.client.post(url, params=params, auth=self.auth, verify=False, name="/http")

		if r.status_code > 300:
			logging.warning("http-endpoint resp.status: %d, text: %s" % (r.status_code, r.text))

	@task(1)
	@tag("primes")
	def primes(self):
		params = {}
		params["blocking"] = "false"
		params["result"] = "true"

		num = random.randint(0, self.bench_num)
		url = self.url_noweb + "prim-" + str(num).zfill(2)

		r = self.client.post(url, params=params, auth=self.auth, verify=False, name="/primes")

		if r.status_code > 300:
			logging.warning("primes resp.status: %d, text: %s" % (r.status_code, r.text))

	@task(1)
	@tag("chameleon")
	def chameleon(self):
		params = {}
		params["blocking"] = "false"
		params["result"] = "true"

		num = random.randint(0, self.bench_num)
		url = self.url_noweb + "cham-" + str(num).zfill(2)

		r = self.client.post(url, params=params, auth=self.auth, verify=False, name="/chameleon")

		if r.status_code > 300:
			logging.warning("chameleon resp.status: %d, text: %s" % (r.status_code, r.text))

	@task(1)
	@tag("img_resize")
	def img_resize(self):
		params = {}
		params["blocking"] = "false"
		params["result"] = "true"

		num = random.randint(0, self.bench_num)
		url = self.url_web + "imgr-" + str(num).zfill(2)

		r = self.client.post(url, params=params, auth=self.auth, verify=False, name="/imgresize")

		if r.status_code > 300:
			logging.warning("imgresize resp.status: %d, text: %s" % (r.status_code, r.text))

	@task(1)
	@tag("markdown")
	def markdown(self):
		params = {}
		params["blocking"] = "false"
		params["result"] = "true"

		num = random.randint(0, self.bench_num)
		url = self.url_noweb + "mark-" + str(num).zfill(2)

		r = self.client.post(url, params=params, auth=self.auth, verify=False, name="/markdown")

		if r.status_code > 300:
			logging.warning("markdown resp.status: %d, text: %s" % (r.status_code, r.text))

	@task(0)
	@tag("mobilenet")
	def mobilenet(self):
		params = {}
		params["blocking"] = "false"
		params["result"] = "true"

		num = random.randint(0, self.bench_num)
		url = self.url_web + "mobi-" + str(num).zfill(2)

		r = self.client.post(url, params=params, auth=self.auth, verify=False, name="/mobilenet")

		if r.status_code > 300:
			logging.warning("mobilenet resp.status: %d, text: %s" % (r.status_code, r.text))

	@task(1)
	@tag("img_processing")
	def img_processing(self):
		params = {}
		params["blocking"] = "false"
		params["result"] = "true"

		num = random.randint(0, self.bench_num)
		url = self.url_web + "imgp-" + str(num).zfill(2)

		r = self.client.post(url, params=params, auth=self.auth, verify=False, name="/imgprocess")

		if r.status_code > 300:
			logging.warning("imgprocessing resp.status: %d, text: %s" % (r.status_code, r.text))

	@task(0)
	@tag("sentiment")
	def sentiment(self):
		params = {}
		params["blocking"] = "false"
		params["result"] = "true"

		num = random.randint(0, self.bench_num)
		url = self.url_noweb + "sent-" + str(num).zfill(2)

		r = self.client.post(url, params=params, auth=self.auth, verify=False, name="/sentiment")

		if r.status_code > 300:
			logging.warning("sentiment resp.status: %d, text: %s" % (r.status_code, r.text))