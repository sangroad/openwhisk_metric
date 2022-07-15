#!/bin/bash
for i in {0..30};
do
	num=`printf "%.3d" $i`
	sleep 0.01
	wsk -i action invoke func$num &
done
