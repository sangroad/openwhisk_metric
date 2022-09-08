#!/bin/bash
for it in {0..1};
do
	for i in {0..50};
	do
		num=`printf "%.3d" $i`
		wsk -i action invoke func$num
		sleep 0.1
	done
	sleep 20
done
