#!/bin/bash
for j in {0..1000};
do
	for i in {0..30};
	do
		num=`printf "%.3d" $i`
		wsk -i action invoke func$num
	done
done
