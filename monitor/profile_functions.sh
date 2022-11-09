#!/bin/bash

ACTION_NAME=$1

# exclude cold start
wsk -i action invoke $1-00
sleep 20s

for i in {1..10};
do
	wsk -i action invoke $1-00
	sleep 5s
done
