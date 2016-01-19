import socket

ip_list = socket.gethostbyname_ex(socket.gethostname())[2]

print(ip_list)

