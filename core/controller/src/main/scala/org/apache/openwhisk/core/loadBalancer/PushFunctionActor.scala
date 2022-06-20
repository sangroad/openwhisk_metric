// pickme
package org.apache.openwhisk.core.loadBalancer

import akka.actor.{ Actor, Props }
import java.io.RandomAccessFile
import java.nio.MappedByteBuffer
import java.nio.channels.FileChannel
import java.nio.CharBuffer

class PushFunctionActor extends Actor {
	val name = "logs/pushFunction"
	val size = 209715200
	val memoryMappedFile = new RandomAccessFile(name, "rw")
	val channel: MappedByteBuffer = memoryMappedFile.getChannel.map(FileChannel.MapMode.READ_WRITE, 0, size)
	var charBuf: CharBuffer = channel.asCharBuffer()

	def receive: Receive = {
		case data: String =>
			charBuf.put(data.toCharArray())
	}
}

object PushFunctionActor {
	def props() = Props(classOf[PushFunctionActor])
}