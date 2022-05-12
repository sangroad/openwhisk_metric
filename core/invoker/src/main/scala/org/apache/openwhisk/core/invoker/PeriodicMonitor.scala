package org.apache.openwhisk.core.invoker

import akka.actor.Actor
import org.apache.openwhisk.core.containerpool.PICKMEBackgroundMonitor

case class Tick()

class PeriodicMonitor extends Actor {
	def receive: Receive = {
		case t: Tick =>
			PICKMEBackgroundMonitor.calQueueLen()
			PICKMEBackgroundMonitor.readCpuUtil()
			PICKMEBackgroundMonitor.readMemUtil()
	}
}