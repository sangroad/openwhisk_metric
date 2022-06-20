// pickme
package org.apache.openwhisk.core.loadBalancer

import scala.collection.mutable.Map

class ScheduleBuffer {
	var actionBuffer = Map.empty[String, Int]
}

object ScheduleBuffer {
	val scheduleBuffer = new ScheduleBuffer()

	def pushAction(action: String, invoker: Int) = {
		scheduleBuffer.actionBuffer = scheduleBuffer.actionBuffer + (action -> invoker)
	}

	def getInvoker(action: String): Int = {
		while(true) {
			scheduleBuffer.actionBuffer.get(action) match {
				case Some(i: Int) =>
					scheduleBuffer.actionBuffer.remove(action)
					return i
				case None =>
			}
		}

		return 0
	}
}