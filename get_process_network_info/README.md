# 使用说明

用途：抓包统计进程流量

依赖：  
- win 下安装 Wireshark，WinPcap（安装Wireshark会自动安装）
- linux 下没试过，谢谢 :)

使用方式：  
1. 修改 sniffer_packet.py 文件112行的 tshark 命令行字符串，修改 `-i` 参数的值（在命令行中执行 `tshark -D` 查看可选网卡）  
2. 运行 sniffer_packet.py 进行抓包及获取端口  
3. `Ctrl + c` 退出 sniffer_packet.py 脚本  
3. 运行 calc_stream.py 统计结果


注1：运行脚本时加 `-h` 参数查看使用帮助  
注2：运行过程中会生成  
- $process_name_network.log 进程流量日志
- $process_name_port_list.log 第一行为抓包开始时间，第二行开始为进程使用的端口列表
- package.csv tshark 抓包结果

注3：使用的 tshark 抓包命令  
`tshark -i 4 -T fields -E header=y -E separator=, -E quote=d -e frame.time_epoch -e ip.src -e ip.dst -e frame.len -e tcp.len -e udp.length -e tcp.srcport -e tcp.dstport -e udp.srcport -e udp.dstport`
