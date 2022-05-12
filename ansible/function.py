import time

def loop(count):
	for i in range(0, count):
		#for j in range(0, 42000):
		#for j in range(0, 48000):
		for j in range(0, 57000):
			pass


def main(args):
	# exec time in milliseond scale
	run_time = args.get('execTime')
	start = time.time()

	loop(run_time)

	end = time.time()
	execTime = (end - start) * 1000

	# print exec time in millisecond scale
	print(execTime)

	return { 'runTime' : execTime }

# for debug
if __name__ == '__main__':
	main({ 'execTime' : 100 })
	# main({ 'runTime' : 0 })
