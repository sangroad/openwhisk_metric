#!/bin/bash
for j in {0..100};
do
	for i in {0..100};
	do
		num=`printf "%.3d" $i`
		sleep 0.01
		../bin/wsk -i action invoke func$num
	done
done
