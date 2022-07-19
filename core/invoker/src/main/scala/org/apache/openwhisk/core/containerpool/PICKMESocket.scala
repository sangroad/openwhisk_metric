// pickme
package org.apache.openwhisk.core.containerpool

import akka.actor.{ Actor, Props }
import akka.io.{ IO, Tcp }
import akka.util.ByteString
import java.net.InetSocketAddress
import scala.concurrent.Future
import scala.collection.mutable

class PICKMESocketServer(port: Int, handler: Array[Byte] => Future[Unit]) extends Actor {
  import Tcp._
  import context.system

  IO(Tcp) ! Bind(self, new InetSocketAddress("0.0.0.0", port))
  var prevMsg: String = ""
  val determineLength: Int = 120
  val prevActivationSet = mutable.Set.empty[String]
  val prevActivationQueue = mutable.Queue.empty[String]

  val bufSize: Int = 10

  def receive = {
    case b @ Bound(localAddress) =>
      context.parent ! b

    case CommandFailed(_: Bind) =>
      context.stop(self)

    case c @ Connected(remote, local) =>
      val connection = sender()
      connection ! Register(self)

      context.become {
        case data: ByteString =>
          /* send container status */
          connection ! Write(data)
        case data: PICKMEPeriodicData =>
          /* send openwhisk-side metrics to RDMA process */
          val strData = s"*${data.busyPoolSize}@${data.freePoolSize}@${data.initContainers}@${data.creatingContainers}"
          val sendData = ByteString(strData)

          connection ! Write(sendData)
        case data: PICKMESocketData =>
          /* for ML metric collection */
          val metric = data.metric
          val bgMetric = metric.getBackgroundMetric()
          val strData = s"*${data.activationId}@${metric.actionName}@${metric.status}@${metric.duration}@${metric.waitTime}@${metric.initTime}" +
            s"@${bgMetric.avgCpu}@${bgMetric.maxCpu}@${bgMetric.minCpu}@${bgMetric.midCpu}@${bgMetric.mem}@${bgMetric.ipc}" +
            s"@${bgMetric.busyPoolSize}@${bgMetric.freePoolSize}@${bgMetric.queueLen}@${bgMetric.initContainer}" +
            s"@${bgMetric.creatingContainer}@${metric.inputSize}"

          val sendData = ByteString(strData)
          connection ! Write(sendData)
        case Received(data) =>
          val PICKMEflag = "PICKME"
          val received = data.utf8String
          val ret = received.split('*').foreach { msg =>
            if (msg.length() != 0) {
              val msgPart = msg.substring(0, determineLength)
              if (!prevActivationSet(msgPart)) {
                val addFlag = msg + PICKMEflag
                println(s"[pickme] received data: ${addFlag}")
                prevActivationSet += msgPart
                prevActivationQueue += msgPart

                if (prevActivationQueue.size > bufSize) {
                  val key = prevActivationQueue.dequeue()
                  prevActivationSet -= key
                }
                handler(addFlag.getBytes())
              }
              if (prevMsg != msgPart) {
                prevMsg = msgPart
              }
            }
          }
          /*
          val avgCpu = splitted(0)
          val maxCpu = splitted(1)
          val minCpu = splitted(2)
          val midCpu = splitted(3)
          val mem = splitted(4)
          val ipc = splitted(5)

          PICKMEBackgroundMonitor.collector.avgCpu = avgCpu.toLong
          PICKMEBackgroundMonitor.collector.maxCpu = maxCpu.toLong
          PICKMEBackgroundMonitor.collector.minCpu = minCpu.toLong
          PICKMEBackgroundMonitor.collector.midCpu = midCpu.toLong
          PICKMEBackgroundMonitor.collector.IPC = ipc.toFloat
          PICKMEBackgroundMonitor.collector.memUtil = mem.toLong

          /**
            * Content)
            * Is there warm instance of function name? yes (1), no (0) + busy function number + memory consumption of function free+busy instance
            * + function hit count list + function memory limit + arrival rate of invoker
          */
          val sendData = PICKMEBackgroundMonitor.checkWarmInstance(splitted(0)).toString + "@" + PICKMEBackgroundMonitor.getBusyFunc.toString + "@" + 
          PICKMEBackgroundMonitor.getMemoryConsumption.toString + "@" + PICKMEBackgroundMonitor.getHitCountList.toString + "@" + splitted(1)

          connection ! Write(ByteString(sendData))
          */

        case _: ConnectionClosed =>
          connection ! Close
          context.unbecome()
          // context.stop(self)
      }
  }
}

object PICKMESocketServer {
  def props() = Props(classOf[PICKMESocketServer])
}