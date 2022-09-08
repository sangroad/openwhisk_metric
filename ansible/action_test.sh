#!/bin/bash
for it in {0..5};
do
	for i in {0..50};
	do
		num=`printf "%.3d" $i`
		wsk -i action invoke func$num
	done
done
