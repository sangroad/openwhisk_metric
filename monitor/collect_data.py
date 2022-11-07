import subprocess
import argparse
import time
import os

def read_db_data(start, limit, users):
	cmd = 'ssh caslab@10.150.21.198 "cd workspace/openwhisk_metric/monitor; '
	cmd += 'python3 read_function_stats_metric.py' + \
		f' --since {start} --limit {limit} --users {users}"'

	# print(cmd)

	subprocess.run(cmd, shell=True)
	
def run_monitor(users):
	# cmd = 'ssh caslab@10.150.21.198 "cd workspace/openwhisk_metric/monitor; ./monitor ' + str(users) + ' &"'
	subprocess.Popen(['ssh', 'caslab@10.150.21.198', f'cd workspace/openwhisk_metric/monitor; ./monitor {users} &'])
	# subprocess.run(cmd, shell=True)
	# print(cmd)

def run_locust(users, runtime):
	cmd = 'locust -f poisson_rps_locust.py -H https://10.150.21.197 --headless' + \
		f' --users {users} --run-time {runtime}'

	subprocess.run(cmd, shell=True)
	# print(cmd)

if __name__ == "__main__":
	default_runtime = '1m'

	parser = argparse.ArgumentParser()
	parser.add_argument("--users", type=int, required=True)
	parser.add_argument("--runtime", type=str, default=default_runtime, required=True)

	args = parser.parse_args()

	start_time = int(time.time() * 1000)
	print(f"start time: {start_time}")
	# run_monitor(args.users)
	# time.sleep(5)

	run_locust(args.users, args.runtime)

	# time.sleep(120)
	limit = 100000
	read_db_data(start_time, limit, args.users)