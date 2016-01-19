#!/usr/bin/env python
# *-* coding: utf-8 *-*
import os
import subprocess
import sys
import time

import psutil


def get_process_by_name(arg_name):
    process_list = []
    for p in psutil.process_iter():
        try:
            if p.name().lower() == arg_name.lower():
                process_list.append(p)
        except psutil.AccessDenied as e:
            print("权限不足")
            return None
        except psutil.NoSuchProcess as e:
            print("没有找到该进程")
            return None
    return process_list


def get_conn_info(arg_process):
    conn_info = {}
    conn_info['all'] = arg_process.connections()
    return conn_info


def print_help():
    print(u"用法 python get_process_memory_info.py -p ... [-t ...]")
    print(u"说明：")
    print(u"\t流量统计方式：运行 sniffer_packet.py 进行抓包及获取端口，然后运行 calc_stream.py 统计结果")
    print(u"\t运行过程中会生成 $process_name_network.log $process_name_port_list.log 以及 package.csv 文件")
    print(u"选项：")
    print(u"\t -h/--help 帮助")
    print(u"\t -p 进程名")
    # print(u"\t -t 检测时间间隔[可选参数]")
    # print(u"\t -l 日志文件路径[可选参数]")


def get_argvs():
    global argv_process_name
    global argv_time_interval
    global argv_log_path
    count = 1
    while count < len(sys.argv):
        if sys.argv[count] == "-h" or sys.argv[count] == "--help":
            print_help()
            sys.exit(0)
        if sys.argv[count] == "-p":
            count += 1
            if count < len(sys.argv):
                argv_process_name = sys.argv[count]
        # if sys.argv[count] == "-l":
        #     count += 1
        #     if count < len(sys.argv):
        #         argv_log_path = sys.argv[count]
        count += 1


def clean_before():
    global argv_process_name
    csv_file = "package.csv"
    port_log_file = argv_process_name[:-4] + "_network_port_list.log"
    log_file = argv_process_name[:-4] + "_network.log"
    if os.path.isfile(csv_file):
        os.remove("package.csv")
    if os.path.isfile(port_log_file):
        os.remove(argv_process_name[:-4] + "_network_port_list.log")
    if os.path.isfile(log_file):
        os.remove(argv_process_name[:-4] + "_network.log")


if __name__ == '__main__':
    argv_process_name = ""
    argv_time_interval = ""
    argv_log_path = ""

    get_argvs()

    if argv_process_name == "":
        print_help()
        sys.exit(0)

    if argv_time_interval == "":
        argv_time_interval = 1
        print("时间间隔为空，使用默认值1秒")

    if argv_log_path == "":
        argv_log_path = "./"
        print("日志路径为空，使用默认值当前路径")

    process_list = get_process_by_name(argv_process_name)
    print("同名进程数量：", len(process_list))

    total_flow = 0

    # 运行前清理旧文件
    clean_before()
    # 文件第一行用于记录起始时间戳，第二行起为端口号
    with open(os.path.join(argv_log_path, argv_process_name[:-4] + "_network_port_list.log"), "a") as f:
        f.write(str(time.time()))

    if len(process_list) > 0:
        # 开始调用tshark抓包
        # 参数 -i 的值需修改
        # $ tshark -D 查看可选值列表，选择项目序号填入 -i 参数
        file_name = "package.csv"
        command = u"tshark -i 4 -T fields -E header=y -E separator=, -E quote=d -e frame.time_epoch -e ip.src -e ip.dst -e frame.len -e tcp.len -e udp.length -e tcp.srcport -e tcp.dstport -e udp.srcport -e udp.dstport > " + file_name
        p = subprocess.Popen(command, shell=True)

        port_list = []
        while True:
            for process in process_list:
                conn_info = get_conn_info(process)
                for v in conn_info['all']:
                    if v.laddr[1] not in port_list:
                        port_list.append(v.laddr[1])
                        with open(os.path.join(argv_log_path, argv_process_name[:-4] + "_network_port_list.log"),
                                  "a") as f:
                            # print(str(v.laddr[1]) + "\n")
                            f.write(str(v.laddr[1]) + "\n")
                    if len(v.raddr) > 0:
                        if v.raddr[1] not in port_list:
                            port_list.append(v.raddr[1])
                            with open(os.path.join(argv_log_path, argv_process_name[:-4] + "_network_port_list.log"),
                                      "a") as f:
                                # print(str(v.raddr[1]) + "\n")
                                f.write(str(v.raddr[1]) + "\n")
            time.sleep(1)

    else:
        print("没有找到该进程: " + argv_process_name)
        sys.exit(0)