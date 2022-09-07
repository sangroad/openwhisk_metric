#!/bin/bash
for i in {0..100};
do
	num=`printf "%.3d" $i`
	wsk -i action invoke func$num
done
