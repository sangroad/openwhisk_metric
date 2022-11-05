// pickme
package org.apache.openwhisk.core.containerpool

import akka.actor.{ Actor, Props }
import akka.io.{ IO, Tcp }
import akka.util.ByteString
import java.net.InetSocketAddress
import org.apache.openwhisk.core.connector.ActivationMessage

class PICKMESocketServer extends Actor {
  import Tcp._
  import context.system

  IO(Tcp) ! Bind(self, new InetSocketAddress("0.0.0.0", 7778))

  def receive = {
    case b @ Bound(localAddress) =>
      context.parent ! b

    case CommandFailed(_: Bind) =>
      context.stop(self)

    case c @ Connected(remote, local) =>
      val connection = sender()
      connection ! Register(self)

      context.become {
        case data: ActivationMessage =>
          val strData = s"*${data.activationId},${data.action.name}"
          val sendData = ByteString(strData)
          connection ! Write(sendData)
        case data: PICKMESocketData =>
          val metric = data.metric
          val bgMetric = metric.getBackgroundMetric()
          val strData = s"*${data.activationId}@${metric.actionName}@${metric.status}@${metric.duration}@${metric.waitTime}@${metric.initTime}" +
            s"@${bgMetric.avgCpu}@${bgMetric.maxCpu}@${bgMetric.minCpu}@${bgMetric.midCpu}@${bgMetric.mem}@${bgMetric.ipc}" +
            s"@${bgMetric.busyPoolSize}@${bgMetric.freePoolSize}@${bgMetric.queueLen}@${bgMetric.initContainer}" +
            s"@${bgMetric.creatingContainer}@${metric.inputSize}"

          val sendData = ByteString(strData)
          connection ! Write(sendData)
          // println(s"[pickme] socket data: ${strData}")
        case Received(data) =>
          val splitted = data.utf8String.split("@")
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