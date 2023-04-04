#!/bin/bash
for j in {0..500};
do
	for i in {0..1};
	do
		num=`printf "%.3d" $i`
		sleep 0.1
		../bin/wsk -i action invoke func$num
	done
done
