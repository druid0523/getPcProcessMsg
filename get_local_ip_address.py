import socket

ip_list = socket.gethostbyname_ex(socket.gethostname())[2]

print(ip_list)

print(ipList in ['0.0.0.0', '2.0.1.1', '192.168.56.1', '2.0.0.1', '172.25.21.12'])
