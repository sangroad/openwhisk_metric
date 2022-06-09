// pickme
package org.apache.openwhisk.core.containerpool

import org.apache.openwhisk.core.entity.{ActivationId, EntityName}
import scala.collection.mutable.Map
import akka.actor.{ActorSystem, Props}

class PICKMEMetric (backgroundMetric: PICKMEBackgroundMetric) {
	var actionName: String = ""
	var status: String = ""
	var inputSize: Int = 0

	var duration: Long = 0
	var waitTime: String = ""
	var initTime: String = ""

	def getBackgroundMetric() = backgroundMetric
}

case class FuncInitialData (activationId: ActivationId, actionName: EntityName, containerType: String)
case class FuncInputSize (activationId: ActivationId, inputSize: Int)
case class FuncDuration (activationId: ActivationId, duration: Long, waitTime: Option[spray.json.JsValue], initTime: Option[spray.json.JsValue])
case class PICKMESocketData (activationId: ActivationId, metric: PICKMEMetric)
case class PICKMEPeriodicData (busyPoolSize: Int, freePoolSize: Int, initContainers: Long, creatingContainers: Long)

class PICKMEActivationMonitor {

}

object PICKMEActivationMonitor {
	var activations = Map.empty[ActivationId, PICKMEMetric]
	val actorSystem = ActorSystem("PICKMESystem")
	val socket = actorSystem.actorOf(Props[PICKMESocketServer], "PICKMESocketServer")

	def setActivationColdWarm(initData: FuncInitialData) {
		val metric = new PICKMEMetric(PICKMEBackgroundMonitor.getCurrentStatus())
		metric.status = initData.containerType
		metric.actionName = initData.actionName.toString()
		activations += (initData.activationId -> metric)
	}

	def setActivationInputSize(inputSize: FuncInputSize) {
		val metric = activations.get(inputSize.activationId)

		if (metric.isDefined) {
			val storedMetric = metric.get
			storedMetric.inputSize = inputSize.inputSize
			activations.update(inputSize.activationId, storedMetric)
		}
	}

	def setActivationDuration(duration: FuncDuration) {
		val metric = activations.get(duration.activationId)

		if (metric.isDefined) {
			val storedMetric = metric.get
			storedMetric.duration = duration.duration
			
			if (duration.initTime.isDefined) {
				storedMetric.initTime = duration.initTime.get.toString()
			}
			else {
				storedMetric.initTime = "X"
			}

			if (duration.waitTime.isDefined) {
				storedMetric.waitTime = duration.waitTime.get.toString()
			}
			else {
				storedMetric.waitTime = "X"
			}
			// PICKMEActivationMonitor.activations.update(duration.activationId, storedMetric)

			// send socket
			// socket ! PICKMESocketData(duration.activationId, storedMetric)
			activations -= duration.activationId
		}	
	}

	// def props() = Props(classOf[PICKMEActivationMonitor])
}