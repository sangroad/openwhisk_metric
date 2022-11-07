#!/bin/bash
for i in {0..20};
do
	wsk -i action invoke app$i
done
wsk -i action invoke func----
