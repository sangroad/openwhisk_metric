#!/bin/bash
for i in {0..30};
do
	num=`printf "%.3d" $i`
	../bin/wsk -i action invoke func$num
done
