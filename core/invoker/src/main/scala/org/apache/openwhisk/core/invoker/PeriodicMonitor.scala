package org.apache.openwhisk.core.invoker

import akka.actor.{ Actor, ActorSystem, Props }
import org.apache.openwhisk.core.containerpool.{ PICKMEBackgroundMonitor, PICKMESocketServer }
import org.apache.openwhisk.core.containerpool.ContainerProxy
import org.apache.openwhisk.core.containerpool.ContainerPool
import org.apache.openwhisk.core.containerpool.PICKMEPeriodicData

case class Tick()

class PeriodicMonitor extends Actor {
	def receive: Receive = {
		case t: Tick =>
			PICKMEBackgroundMonitor.calQueueLen()
	}
}

class PeriodicSender extends Actor {
	val actorSystem = ActorSystem("PICKMESystem")
	val socket = actorSystem.actorOf(Props[PICKMESocketServer], "periodic")

	def receive: Receive = {
		case t: Tick =>
			val creating = ContainerProxy.creating.cur
			val initializing = ContainerProxy.initializing.cur
			val busypool = ContainerPool.busyPool.size
			val freepool = ContainerPool.freePool.size

			socket ! PICKMEPeriodicData(busypool, freepool, initializing, creating)
	}
}