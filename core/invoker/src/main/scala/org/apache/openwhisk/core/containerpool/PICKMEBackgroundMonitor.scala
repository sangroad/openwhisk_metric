// pickme
package org.apache.openwhisk.core.containerpool

import scala.collection.mutable.Map
import scala.collection.mutable.ListBuffer

case class PICKMEBackgroundMetric (avgCpu: Long, maxCpu: Long, minCpu: Long, midCpu: Long, mem: Long, ipc: Float, queueLen: Long,
																	busyPoolSize: Int, freePoolSize: Int, initContainer: Long, creatingContainer: Long)

class PICKMEBackgroundMonitor {
	var funcBundle = Map.empty[String, (Int, Int, Int)]

	// for busy containers
	var busyFunc: Int = 0
	// for free containers
	var freeFunc: Int = 0
	var memoryConsumption: Int = 0

	// busypool size
	var busyPoolSize: Int = 0
	// freepool size
	var freePoolSize: Int = 0

	// for queue length
	var curQueueLen: Long = 0
	var prevQueueLen: Long = 0
	var queueLen: Long = 0

	// for cpu
	var avgCpu: Long = 0
	var maxCpu: Long = 0
	var minCpu: Long = 0
	var midCpu: Long = 0

	// for memory
	var memUtil: Long = 0

	// for IPC
	var IPC: Float = 0

	// init containers, creating containers
	var initContainerNum: Long = 0

	// creating containers
	var creatingContainerNum: Long = 0
}

object PICKMEBackgroundMonitor {
	val collector = new PICKMEBackgroundMonitor()
	var shrinkList = new ListBuffer[String]()

	def getCurrentStatus() = {
		PICKMEBackgroundMetric(collector.avgCpu, collector.maxCpu, collector.minCpu, collector.midCpu, collector.memUtil, collector.IPC,
		collector.queueLen, collector.busyPoolSize, collector.freePoolSize,
		collector.initContainerNum, collector.creatingContainerNum)
	}

	def setCreatingContainer(num: Long) = {
		collector.creatingContainerNum = num
	}

	def setInitContainer(num: Long) = {
		collector.initContainerNum = num
	}

	def setBusyPoolSize(size: Int) = {
		collector.busyPoolSize = size
	}

	def setFreePoolSize(size: Int) = {
		collector.freePoolSize = size
	}

	def addQueueLen(len: Long) = {
		collector.curQueueLen += len
	}

	def calQueueLen() = {
		collector.queueLen = collector.curQueueLen - collector.prevQueueLen
		collector.prevQueueLen = collector.curQueueLen
	}

	def addFunction(name: String, memory: Int) = {
		collector.funcBundle.get(name) match {
			case Some((i, k, n: Int)) =>
				collector.funcBundle.update(name, (i, k, n+1))
			case None =>
				collector.funcBundle = collector.funcBundle + (name -> (memory, 0, 1))
		}
		collector.memoryConsumption += memory
	}

	def warmHit(name: String) = {
		collector.funcBundle.get(name) match {
			case Some((i, k: Int, n)) =>
				collector.funcBundle.update(name, (i, k+1, n))
			case None =>
		}
	}

	def getHitCountList : List[Int] = {
		var hitCountList = List[Int]()
		collector.funcBundle.foreach {
			case (s,(i, j: Int, k)) =>
				hitCountList = hitCountList :+ j
		}
		hitCountList
	}

	def shrinkFunction(name: String) = {
		collector.funcBundle.get(name) match {
			case Some((i, k, n)) =>
				if (n - 1 == 0 ) {
					collector.funcBundle.remove(name)
				}
				else {
					collector.funcBundle.update(name, (i, k, n - 1))
				}
				collector.memoryConsumption -= i
			case None =>
		}
	}
	
	def shrinking(name: String) = {
		shrinkList += name
	}

	def checkWarmInstance(name: String): Int = {
		if (collector.funcBundle.contains(name)) {
			return 1
		}
		else return 0
	} 

	def updateBusyFunc(num: Int) = {
		collector.busyFunc = num
	}

	def updateFreeFunc(num: Int) = {
		collector.freeFunc = num
	}
	
	def getBusyFunc : Int = {
		collector.busyFunc
	}
	
	def getMemoryConsumption : Int = {
		collector.memoryConsumption
	}

	def printBundle = {
		println(collector.funcBundle)
	}
}