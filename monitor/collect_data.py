import subprocess
import argparse
import time
import os

def read_db_data(start, limit, users, runtime):
	cmd = 'ssh caslab@10.150.21.198 "cd workspace/openwhisk_metric/monitor; '
	cmd += 'python3 read_function_stats_metric.py' + \
		f' --since {start} --limit {limit} --users {users} --runtime {runtime}"'

	print(cmd)

	subprocess.run(cmd, shell=True)
	
def run_monitor(users, runtime):
	# cmd = 'ssh caslab@10.150.21.198 "cd workspace/openwhisk_metric/monitor; ./monitor ' + str(users) + ' &"'
	subprocess.Popen(['ssh', 'caslab@10.150.21.198', f'cd workspace/openwhisk_metric/monitor; ./monitor {users} {runtime} &'])
	# subprocess.run(cmd, shell=True)

def pkill_monitor():
	cmd = 'ssh caslab@10.150.21.198 "pkill monitor"'
	subprocess.run(cmd, shell=True)

def run_locust(users, runtime):
	cmd = 'locust -f poisson_rps_locust.py -H https://10.150.21.197 --headless' + \
		f' --users {users} --run-time {runtime}'

	print(cmd)
	subprocess.run(cmd, shell=True)

def redeploy_ow():
	cmd = './redeploy_ow.sh'
	subprocess.run(cmd, shell=True)

if __name__ == "__main__":
	'''
	default_runtime = '20m'
	parser = argparse.ArgumentParser()
	parser.add_argument("--users", type=int, required=True)
	parser.add_argument("--runtime", type=str, default=default_runtime, required=True)

	args = parser.parse_args()
	'''

	users = [10, 15, 20, 25, 30]
	runtimes = ['20m', '40m']

	for runtime in runtimes:
		for user in users:
			start_time = int(time.time() * 1000)
			print(f"start time: {start_time}, user: {user}, runtime: {runtime}")
			run_monitor(user, runtime)

			time.sleep(5)

			run_locust(user, runtime)

			time.sleep(20)
			pkill_monitor()

			time.sleep(60)
			limit = 100000
			print(f"start time: {start_time}, user: {user}, runtime: {runtime}")
			read_db_data(start_time, limit, user, runtime)

			redeploy_ow()
			time.sleep(10)