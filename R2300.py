#!/usr/bin/env python3
# coding: utf-8
import datetime
import socket
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import time
import threading
import math
import tkinter as tk

distance=[483]
flat_distance=[483]
flat_distance1=[483]
flat_distance2=[483]
flat_distance3=[483]
amplitude=[483]
amplitude1=[483]
amplitude2=[483]
amplitude3=[483]
flag=0
scan_flag =0


#定义一个class作为接受数据的结构
class R2300_data:
    def __init__(self):   #初始化class的子元素
        self.magic = ''  
        self.packet_type = ''
        self.packet_size = ''
        self.header_size = ''
        self.scan_number = ''
        self.packet_number = ''
        self.layer_index = ''
        self.layer_inclination = ''
        self.timestamp_raw = ''
        self.reserved1 = ''
        self.status_flags = ''
        self.scan_frequency = ''
        self.num_points_scan = ''
        self.num_points_packet = ''
        self.first_index = ''
        self.first_angle = ''
        self.angular_increment = ''
        self.reserved2 = ''
        self.reserved3 = ''
        self.reserved4 = ''
        self.reserved5 = ''
        self.header_padding = ''
        self.data=[] #未定义长度的列表

#定义一个函数，用于将收到的报文数据转换成数据结构的格式
def data_transfer(raw_data):
    form_data = R2300_data()  #上面定义的类
    form_data.magic = raw_data[:2].hex()   #将raw_data[0]和raw_data[1]赋值给form_data.magic。由于raw_data里面的数据都是字节，因此需要用.hex()方法将其转换成16进制显示，否则会自动按照ASCII表转义
    form_data.packet_type = raw_data[2:4]
    form_data.packet_size = int.from_bytes(raw_data[4:8],byteorder= 'little')  #将raw_data[4]~raw_data[7]共4个字节转换成10进制的int类型数据，赋值给form_data.packet_size
    form_data.header_size = int.from_bytes(raw_data[8:10],byteorder= 'little')
    form_data.scan_number = int.from_bytes(raw_data[10:12],byteorder= 'little')
    form_data.packet_number = int.from_bytes(raw_data[12:14],byteorder= 'little')
    form_data.layer_index = int.from_bytes(raw_data[14:16],byteorder= 'little')
    form_data.layer_inclination = int.from_bytes(raw_data[16:20],byteorder= 'little')
    form_data.timestamp_raw = raw_data[20:28].hex()
    form_data.reserved1 = raw_data[28:36].hex()
    form_data.status_flags = raw_data[36:40].hex()
    form_data.scan_frequency = int.from_bytes(raw_data[40:44],byteorder= 'little')
    form_data.num_points_scan = int.from_bytes(raw_data[44:46],byteorder= 'little')
    form_data.num_points_packet = int.from_bytes(raw_data[46:48],byteorder= 'little')
    form_data.first_index = int.from_bytes(raw_data[48:50],byteorder= 'little')
    form_data.first_angle = int.from_bytes(raw_data[50:54],byteorder= 'little')
    form_data.angular_increment = int.from_bytes(raw_data[54:58],byteorder= 'little')
    form_data.reserved2 = raw_data[58:62].hex()
    form_data.reserved3 = raw_data[62:66].hex()
    form_data.reserved4 = raw_data[66:74].hex()
    form_data.reserved5 = raw_data[74:82].hex()
    form_data.header_padding = raw_data[82:84]#对齐32位的整数倍，前面的全部加起来差两个字节才是32bit的整数倍，所以这里padding是两个字节
    data_raw= raw_data[84:]#原始数据，里面的类型是int，且全部连在一起
    data_cut = cut(data_raw,4)#在下方定义了一个函数，用于切割数据，这里将原始数按照4个字节来切分，里面的类型是bytes
    for i in range(len(data_cut)):
        form_data.data.append(int.from_bytes(data_cut[i],byteorder= 'little'))#将切分出来的数据转成int类型，然后赋值给form_data.data，至此数据这一帧报文处理完成
    return form_data  #返回按照格式处理好的数据

#用于按照sec长度来切割数据的函数
def cut(obj,sec):
    return[obj[i:i+sec] for i in range(0, len(obj),sec)]

#用于更新图像的线程函数
def update_plot2():
    global flat_distance
    global flat_distance1
    global flat_distance2
    global flat_distance3
    global amplitude
    global amplitude1
    global amplitude2
    global amplitude3
    global flag
    global scan_flag
    data = np.zeros(483)
    color = np.zeros(483)
    # 创建一个2x2的子图布局
    fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(10, 7))

    # 确保 `axs` 是一个二维数组
    if not isinstance(axs, np.ndarray):
        axs = np.array([[axs]])

    # 初始化每个子图，并设置子图标题
    scatter_plots = []
    titles = ['Layer 1', 'Layer 2', 'Layer 3', 'Layer 4']  # 子图标题
    for ax, title in zip(axs.flatten(), titles):
        scatter_plot = ax.scatter(np.arange(483), data, c=color, cmap='coolwarm',vmin=32,vmax=2000,s=5)
        scatter_plots.append(scatter_plot)
        ax.set_title(title)  # 设置子图标题
        ax.set_xlim(0, 483)  # 设置x轴范围
        ax.set_ylim(0, 10)  # 设置y轴范围
        fig.colorbar(scatter_plot, ax=ax)  # 添加颜色条
    
    #plt.show(block=False)  # 显示图像，但不阻塞

    while True:
        # 更新数据
        if scan_flag == 1:
            if flag == 0:
                data = flat_distance  # 示例更新
                data1 = flat_distance1  # 示例更新
                data2 = flat_distance2  # 示例更新
                data3 = flat_distance3  # 示例更新

                color = amplitude  # 示例更新
                color1 = amplitude1  # 示例更新
                color2 = amplitude2  # 示例更新
                color3 = amplitude3  # 示例更新

            # 更新每个子图上的图像
                for i, (scatter_plot, data, amplitude) in enumerate(zip(scatter_plots, 
                                                                        [data,data1,data2,data3],
                                                                        [color,color1,color2,color3])):
                    scatter_plot.set_offsets(np.column_stack((np.arange(483), data)))
                    scatter_plot.set_array(amplitude)
                
                plt.pause(0.05)  # 刷新图像
                time.sleep(0.05)  # 每秒更新一次

#用于接受和处理数据线程函数
def update_data():
    global flat_distance
    global flat_distance1
    global flat_distance2
    global flat_distance3
    global amplitude
    global amplitude1
    global amplitude2
    global amplitude3
    global flag
    global scan_flag
    sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   #创建一个socket服务器对象，其中socket.AF_INET代表用的是IPv4，如果是socket.AF_INET6则是IPv6； socket.SOCK_DGRAM代表UDP；SOCK_STREAM是TCP
    sk.bind(('',10000))   #将本机IP和10000号端口设置为UDP的接口，R2300从这个端口接入
    print("Start UDP receive program")
    while True:
        if scan_flag == 1:
            raw_data, client_address=sk.recvfrom(10000)   #接受R2300传来的数据，缓存10000条消息
            form_data = data_transfer(raw_data)   #转换数据格式，使其更便于观察


            if (form_data.layer_index ==0) and form_data.packet_number ==1:#判断是否是第一层，layer_index分别为：0，1，2，3；同时判断是否为此层的第一个包
                flag =1 #改变flag的值，使画图线程不可以在处理数据时更新图像
                distance=[]#新建空白的distance列表；在后续循环中重新执行这一句等于清空原来的数据；因为下面用的都是append方法，所以需要先清空
                amplitude= []#同上
                flat_distance = []
                for i in range(0, len(form_data.data)):
                    amplitude.append((form_data.data[i]>>20)&0xfff)#高12bit为能量强度
                    distance.append((form_data.data[i]&0xfffff)/1000)#低20bit为距离
                    #将100°(弧度1.7453）分成483个点，计算当前点到中心点的弧度
                    angle =abs(i-220)*(1.7453/500)
                    #print(angle)
                    #计算垂直距离，即报文反馈的距离*cos(angle)
                    flat_distance.append(((form_data.data[i]&0xfffff)/1000)*math.cos(angle))
                #print(len(form_data.data))

            if (form_data.layer_index ==0) and form_data.packet_number ==2:#判断是否是第一层，layer_index分别为：0，1，2，3；同时判断是否为此层的第二个包
                for i in range(0, len(form_data.data)):
                    amplitude.append((form_data.data[i]>>20)&0xfff)#切割距离和强度
                    distance.append((form_data.data[i]&0xfffff)/1000)
                    angle =abs(i+291-220)*(1.7453/500)
                    #print(angle)
                    flat_distance.append(((form_data.data[i]&0xfffff)/1000)*math.cos(angle))
                flag =0 #改变flag的值，告诉画图线程现在可以开始更新图像了

            if (form_data.layer_index ==1) and form_data.packet_number ==1:#判断是否是第一层，layer_index分别为：0，1，2，3；同时判断是否为此层的第一个包
                flag =1 #改变flag的值，使画图线程不可以在接收数据和处理数据时更新图像
                distance=[]#新建空白的distance列表；在后续循环中重新执行这一句等于清空原来的数据；因为下面用的都是append方法，所以需要先清空
                amplitude1= []#同上
                flat_distance1 = []
                for i in range(0, len(form_data.data)):
                    amplitude1.append((form_data.data[i]>>20)&0xfff)#高12bit为能量强度
                    distance.append((form_data.data[i]&0xfffff)/1000)#低20bit为距离
                    #将100°分成483个点，每个点的弧度
                    angle =abs(i-220)*(1.7453/500)
                    #print(angle)
                    flat_distance1.append(((form_data.data[i]&0xfffff)/1000)*math.cos(angle))
                #print(len(form_data.data))

            if (form_data.layer_index ==1) and form_data.packet_number ==2:#判断是否是第一层，layer_index分别为：0，1，2，3；同时判断是否为此层的第二个包
                for i in range(0, len(form_data.data)):
                    amplitude1.append((form_data.data[i]>>20)&0xfff)#切割距离和强度
                    distance.append((form_data.data[i]&0xfffff)/1000)
                    angle =abs(i+291-220)*(1.7453/500)
                    #print(angle)
                    flat_distance1.append(((form_data.data[i]&0xfffff)/1000)*math.cos(angle))
                flag =0 #改变flag的值，告诉画图线程现在可以开始更新图像了

            if (form_data.layer_index ==2) and form_data.packet_number ==1:#判断是否是第一层，layer_index分别为：0，1，2，3；同时判断是否为此层的第一个包
                flag =1 #改变flag的值，使画图线程不可以在接收数据和处理数据时更新图像
                distance=[]#新建空白的distance列表；在后续循环中重新执行这一句等于清空原来的数据；因为下面用的都是append方法，所以需要先清空
                amplitude2= []#同上
                flat_distance2 = []
                for i in range(0, len(form_data.data)):
                    amplitude2.append((form_data.data[i]>>20)&0xfff)#高12bit为能量强度
                    distance.append((form_data.data[i]&0xfffff)/1000)#低20bit为距离
                    #将100°分成483个点，每个点的弧度
                    angle =abs(i-220)*(1.7453/500)
                    #print(angle)
                    flat_distance2.append(((form_data.data[i]&0xfffff)/1000)*math.cos(angle))
                #print(len(form_data.data))

            if (form_data.layer_index ==2) and form_data.packet_number ==2:#判断是否是第一层，layer_index分别为：0，1，2，3；同时判断是否为此层的第二个包
                for i in range(0, len(form_data.data)):
                    amplitude2.append((form_data.data[i]>>20)&0xfff)#切割距离和强度
                    distance.append((form_data.data[i]&0xfffff)/1000)
                    angle =abs(i+291-220)*(1.7453/500)
                    #print(angle)
                    flat_distance2.append(((form_data.data[i]&0xfffff)/1000)*math.cos(angle))
                flag =0 #改变flag的值，告诉画图线程现在可以开始更新图像了

            if (form_data.layer_index ==3) and form_data.packet_number ==1:#判断是否是第一层，layer_index分别为：0，1，2，3；同时判断是否为此层的第一个包
                flag =1 #改变flag的值，使画图线程不可以在接收数据和处理数据时更新图像
                distance=[]#新建空白的distance列表；在后续循环中重新执行这一句等于清空原来的数据；因为下面用的都是append方法，所以需要先清空
                amplitude3= []#同上
                flat_distance3 = []
                for i in range(0, len(form_data.data)):
                    amplitude3.append((form_data.data[i]>>20)&0xfff)#高12bit为能量强度
                    distance.append((form_data.data[i]&0xfffff)/1000)#低20bit为距离
                    #将100°分成483个点，每个点的弧度
                    angle =abs(i-220)*(1.7453/500)
                    #print(angle)
                    flat_distance3.append(((form_data.data[i]&0xfffff)/1000)*math.cos(angle))

            if (form_data.layer_index ==3) and form_data.packet_number ==2:#判断是否是第一层，layer_index分别为：0，1，2，3；同时判断是否为此层的第二个包
                for i in range(0, len(form_data.data)):
                    amplitude3.append((form_data.data[i]>>20)&0xfff)#切割距离和强度
                    distance.append((form_data.data[i]&0xfffff)/1000)
                    angle =abs(i+291-220)*(1.7453/500)
                    #print(angle)
                    flat_distance3.append(((form_data.data[i]&0xfffff)/1000)*math.cos(angle))
                flag =0 #改变flag的值，告诉画图线程现在可以开始更新图像了


def start_scan():
    global scan_flag
    scan_flag =1

def stop_scan():
    global scan_flag
    scan_flag =0

#主函数，用于启动两个线程以及生成图形界面
if __name__ =="__main__":

    thread1 = threading.Thread(target=update_data)
    thread1.daemon = True
    thread1.start()

    # 创建线程实例
    thread = threading.Thread(target=update_plot2)
    #设置守护线程，主线程退出，子线程也退出
    thread.daemon = True
    # 启动线程
    thread.start()



    #用tkinter创建一个窗口
    root = tk.Tk()
    root.title("R2300")
    root.geometry("100x100")
    #创建两个按钮
    button1 = tk.Button(root, text="Start", command=start_scan)
    button2 = tk.Button(root, text="Stop", command=stop_scan)
    button1.pack()
    button2.pack()
    root.mainloop()

    

    
