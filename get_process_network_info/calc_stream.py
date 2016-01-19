#!/usr/bin/env python
# *-* coding: utf-8 *-*
import csv
import socket
import sys
import time


def print_help():
    print(u"用法 python calc_stream.py -p")
    print(u"说明：")
    print(u"\t流量统计方式：运行 sniffer_packet.py 进行抓包及获取端口，然后运行 calc_stream.py 统计结果")
    print(u"\t运行过程中会生成 $process_name_network.log $process_name_port_list.log 以及 package.csv 文件")
    print(u"选项：")
    print(u"\t -h/--help 帮助")
    print(u"\t -p 进程名")


def get_argvs():
    global argv_process_name
    count = 1
    while count < len(sys.argv):
        if sys.argv[count] == "-h" or sys.argv[count] == "--help":
            print_help()
            sys.exit(0)
        if sys.argv[count] == "-p":
            count += 1
            if count < len(sys.argv):
                argv_process_name = sys.argv[count]
        count += 1


def str_to_float(arg_str):
    try:
        return float(arg_str)
    except:
        print("不合法")
        return 0


def calc_stream_bytes(arg_start_time, arg_end_time, arg_port_list, arg_file_name):
    global upstream
    global downstream
    global total_stream

    valid_package = []
    with open(arg_file_name) as csv_file:
        dict_reader = csv.DictReader(csv_file)
        # 过滤获得所有在限定时间内的包
        for v in dict_reader:
            if arg_start_time <= str_to_float(v['frame.time_epoch']) <= arg_end_time:
                valid_package.append(v)

    for package in valid_package:
        for port in arg_port_list:
            port_str = str(port)
            if port_str in {package['tcp.srcport'], package['tcp.dstport'], package['udp.srcport'],
                            package['udp.dstport']}:
                total_stream += str_to_float(package['frame.len'])
                for src in package['ip.src'].split(","):
                    if src in ip_list:
                        upstream += str_to_float(package['frame.len'])
                        break
                    else:
                        downstream += str_to_float(package['frame.len'])
                break


if __name__ == '__main__':
    argv_process_name = ""
    get_argvs()

    if argv_process_name == "":
        print_help()
        sys.exit(0)

    port_list = []
    start_unix_time = 0
    with open(argv_process_name[:-4] + "_network_port_list.log") as port_file:
        lines = port_file.readlines()
        for i in range(len(lines)):
            if i is 0:
                start_unix_time = float(lines[0])
                continue
            port_list.append(int(lines[i]))

    # 本地ip列表
    ip_list = socket.gethostbyname_ex(socket.gethostname())[2]
    ip_list.append("127.0.0.1")

    upstream = 0
    downstream = 0
    total_stream = 0

    print("port list:", port_list)

    calc_stream_bytes(start_unix_time, 9999999999, port_list, "package.csv")

    print("total", total_stream)
    print("upstream", upstream)
    print("downstream", downstream)

    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

    write_str = '[' + str(now_time) + ']|{"total":"' + str(
            total_stream) + '", "upstream": ' + str(upstream) + '", "downstream": ' + str(downstream) + '"}\n'
    with open(argv_process_name[:-4] + "_network.log", "a") as log_file:
        print(write_str)
        log_file.write(write_str)
