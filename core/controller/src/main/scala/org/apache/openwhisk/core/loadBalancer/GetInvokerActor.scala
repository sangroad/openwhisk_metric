// pickme
package org.apache.openwhisk.core.loadBalancer

import akka.actor.{ Actor, Props }
import java.io.RandomAccessFile
import java.nio.MappedByteBuffer
import java.nio.channels.FileChannel
import java.nio.CharBuffer

class GetInvokerActor extends Actor {
	val name = "logs/getInvoker"
	val mem_size = 209715200 //1024

	val memoryMappedFile = new RandomAccessFile(name, "rw")
	var channel: MappedByteBuffer = memoryMappedFile.getChannel.map(FileChannel.MapMode.READ_WRITE, 0, mem_size)
	var charBuf: CharBuffer = channel.asCharBuffer()

	var position = 0
	var msg_size = 46 // for 'funcXXX' like name
	// var msg_size = 50

	def receive = {
		case data: String =>
			var done = true
			while(done) {
				if(charBuf.get(position).toChar == '*') {
					var tmp: String = ""
					var n = 0
					while(tmp.length != msg_size) {
						while(charBuf.get(position + n + 1) == '\u0000') {}
						tmp = tmp + charBuf.get(position + n + 1)
						n = n + 1
					}

					// println(s"[pickme] ${tmp}")
					var parse_msg = tmp.split("@")
					// println("sghan: parse msg: " + parse_msg)
					ScheduleBuffer.pushAction(parse_msg(0).toString, parse_msg(3).toInt)
					position = position + msg_size + 1
					done = false
				}
			} 
	}
}

object GetInvokerActor {
	def props() = Props(classOf[GetInvokerActor])
}