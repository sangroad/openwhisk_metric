#!/bin/bash

workerip=190
vmip=170

node_end=6
port_end=7

for nodes in {0..0}
do
	for ip in {0..2}
	do
		sudo ssh -p $((3355+$ip)) root@10.150.21.$(($workerip+$nodes)) 'cd /root/openwhisk_metric; ./gradlew :core:invoker:distDocker' &
	done
done

wait < <(jobs -p)
echo "Complete!"
