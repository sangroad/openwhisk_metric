import socket
import numpy as np
import threading
import subprocess
import time
from multiprocess import Process

HOST = "127.0.0.1"
PORT = 7778
MSG_SIZE = 2048
# client_socket = None

MON_PERIOD = 0.03	# second
NUM_CORES = 20

def read_cpu_ns():
	with open("/sys/fs/cgroup/cpu/docker/cpuacct.usage_percpu", "r") as f:
		lines = f.readline()
	utils = np.array(lines.split(" ")[:-1]).astype(int)
	return utils

def get_cpu_util_metrics(cur, prev):
	interval_util = cur - prev

	avg_util = round(np.average(interval_util))
	max_util = round(np.max(interval_util))
	min_util = round(np.min(interval_util))
	mid_util = round(np.median(interval_util))

	return avg_util, max_util, min_util, mid_util

def monitor_mem_util():
	with open("/proc/meminfo", "r") as f:
		lines = f.readlines()

	total_mem = 0
	avail_mem = 0
	using_mem = 0
	for line in lines:
		tmp = line.split(" ")
		key = tmp[0]
		if "MemTotal" in key:
			total_mem = int(tmp[-2])
		if "MemAvailable" in key:
			avail_mem = int(tmp[-2])
	using_mem = total_mem - avail_mem
	return using_mem

def monitor_ipc():
	start = time.time()
	path = "/var/tmp/wsklogs/invoker0/ipc"
	cmd = "perf stat -C 1-19 -einstructions -ecycles sleep " + str(MON_PERIOD) + "s 2>" + path
	# cmd = "perf stat -C 1-19 -einstructions -ecycles sleep " + str(MON_PERIOD) + "s"
	out = subprocess.run(["perf", "stat", "-C1-19", "-einstructions", "-ecycles", "sleep", str(MON_PERIOD)+"s"], stderr=subprocess.PIPE)
	res = out.stderr.decode().replace(" ", "")
	idx = res.find("#")
	# print("latency: ", time.time() - start)
	return res[idx+1: idx+5]

def monitor(sock):
	while True:
		start = time.time()
		prev_util = read_cpu_ns()
		ipc = monitor_ipc()
		cur_util = read_cpu_ns()
		cpu_met = get_cpu_util_metrics(cur_util, prev_util)

		mem_util = monitor_mem_util()

		res = ""
		for m in cpu_met:
			res += str(m) + "@"
		
		res = res + str(mem_util) + "@" + str(ipc)
		# print(res)
		ow_send_metrics(res, sock)

def con_socket():
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_socket.connect((HOST, PORT))
	return client_socket

def ow_get_metrics(sock):
	while True:
		data = sock.recv(MSG_SIZE)
		print("received: %s" % repr(data.decode()))

def ow_send_metrics(metric, sock):
	sock.send(metric.encode())


if __name__ == "__main__":

	sock = con_socket()

	procs = []
	ow_proc = Process(target=ow_get_metrics, args=(sock,))
	procs.append(ow_proc)
	ow_proc.start()

	mon_proc = Process(target=monitor, args=(sock,))
	procs.append(mon_proc)
	mon_proc.start()

	for i in procs:
		i.join() 