#!/bin/bash
for j in {0..100};
do
	for i in {0..100};
	do
		rand=$(($RANDOM % 101))
		num=`printf "%.3d" $rand`
		sleep 0.01
		../bin/wsk -i action invoke func$num
	done
done
