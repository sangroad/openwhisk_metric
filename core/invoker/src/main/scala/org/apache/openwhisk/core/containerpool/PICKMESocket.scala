// pickme
package org.apache.openwhisk.core.containerpool

import akka.actor.{ Actor, Props }
import akka.io.{ IO, Tcp }
import akka.util.ByteString
import java.net.InetSocketAddress

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
        case data: PICKMESocketData =>
          val metric = data.metric
          val bgMetric = metric.getBackgroundMetric()
          val strData = s"${data.activationId}@${metric.actionName}@${metric.status}@${metric.duration}@${bgMetric.cpu}@${bgMetric.mem}@${bgMetric.ipc}" +
            s"@${bgMetric.busyPoolSize}@${bgMetric.freePoolSize}@${bgMetric.queueLen}@${bgMetric.initContainer}@${bgMetric.creatingContainer}@${metric.inputSize}"

          val sendData = ByteString(strData)
          connection ! Write(sendData)
          // println(s"[pickme] socket data: ${strData}")
        case Received(data) =>
          val splitted = data.utf8String.split(" ")
          /**
            * Content)
            * Is there warm instance of function name? yes (1), no (0) + busy function number + memory consumption of function free+busy instance
            * + function hit count list + function memory limit + arrival rate of invoker
          */
          // val sendData = PICKMEBackgroundMonitor.checkWarmInstance(splitted(0)).toString + "@" + PICKMEBackgroundMonitor.getBusyFunc.toString + "@" + 
          // PICKMEBackgroundMonitor.getMemoryConsumption.toString + "@" + PICKMEBackgroundMonitor.getHitCountList.toString + "@" + splitted(1)

          // connection ! Write(ByteString(sendData))

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