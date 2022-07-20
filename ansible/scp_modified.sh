#!/bin/bash
#INVOKERS=("caslab@10.150.21.190" "caslab@10.150.21.191" "caslab@10.150.21.192" "caslab@10.150.21.193" "caslab@10.150.21.194" "caslab@10.150.21.195" "caslab@10.150.21.196")
INVOKERS=("caslab@10.150.21.190" "caslab@10.150.21.191" "caslab@10.150.21.192")

for INVOKER in "${INVOKERS[@]}"
	do
		scp ../core/invoker/src/main/scala/org/apache/openwhisk/core/containerpool/PICKMESocket.scala $INVOKER:~/workspace/openwhisk_pickme/core/invoker/src/main/scala/org/apache/openwhisk/core/containerpool
		scp ../core/invoker/src/main/scala/org/apache/openwhisk/core/containerpool/ContainerPool.scala $INVOKER:~/workspace/openwhisk_pickme/core/invoker/src/main/scala/org/apache/openwhisk/core/containerpool
		scp ../core/invoker/src/main/scala/org/apache/openwhisk/core/containerpool/ContainerProxy.scala $INVOKER:~/workspace/openwhisk_pickme/core/invoker/src/main/scala/org/apache/openwhisk/core/containerpool
		scp ../core/invoker/src/main/scala/org/apache/openwhisk/core/invoker/InvokerReactive.scala $INVOKER:~/workspace/openwhisk_pickme/core/invoker/src/main/scala/org/apache/openwhisk/core/invoker
		scp ../common/scala/src/main/scala/org/apache/openwhisk/core/containerpool/Container.scala $INVOKER:~/workspace/openwhisk_pickme/common/scala/src/main/scala/org/apache/openwhisk/core/containerpool
		scp ../core/invoker/src/main/scala/org/apache/openwhisk/core/containerpool/docker/DockerContainer.scala $INVOKER:~/workspace/openwhisk_pickme/core/invoker/src/main/scala/org/apache/openwhisk/core/containerpool/docker
		ssh $INVOKER "cd ~/workspace/openwhisk_pickme/ansible; ./build.sh" &
	done

./build.sh
