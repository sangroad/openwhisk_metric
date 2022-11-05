import subprocess
import argparse
import time
import os

def read_db_data(start, limit, output_dir):
	cmd = "python3 read_function_stats_metric.py" + \
		" --since " + str(start) + \
		" --limit " + str(limit) + \
		" --output-dir " + str(output_dir)

	subprocess.run(cmd, shell=True)
	
def run_monitor():
	cmd = 'ssh caslab@10.150.21.198 "cd workspace/openwhisk_metric/monitor; ./monitor"'
	subprocess.run(cmd, shell=True)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	# parser.add_argument("--users", type=int, required=True)
	# parser.add_argument("--run-time", type=str, default=default_runtime)
	# parser.add_argument("--ow-type", type=str, required=True)	# pickme, mws, jsq

	args = parser.parse_args()
	output_dir = './data'

	start_time = int(time.time() * 1000)
	print(f"start time: {start_time}")
	run_monitor()

	time.sleep(120)
	limit = 100000
	read_db_data(start_time, limit, output_dir)