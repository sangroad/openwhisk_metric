import socket

HOST = "127.0.0.1"
PORT = 7778
MSG_SIZE = 100

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

while True:
	data = client_socket.recv(MSG_SIZE)
	print("received: %s" % repr(data.decode()))