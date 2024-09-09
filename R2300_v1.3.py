import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import socket
import threading
from collections import deque
import queue
import math
import sys
import numpy as np

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

def cut(obj,sec):
    return[obj[i:i+sec] for i in range(0, len(obj),sec)]

# 数据传输函数
def data_transfer(raw_data):
    form_data = R2300_data()  #上面定义的类
    # form_data.magic = raw_data[:2].hex()   #将raw_data[0]和raw_data[1]赋值给form_data.magic。由于raw_data里面的数据都是字节，因此需要用.hex()方法将其转换成16进制显示，否则会自动按照ASCII表转义
    # form_data.packet_type = raw_data[2:4]
    # form_data.packet_size = int.from_bytes(raw_data[4:8],byteorder= 'little')  #将raw_data[4]~raw_data[7]共4个字节转换成10进制的int类型数据，赋值给form_data.packet_size
    # form_data.header_size = int.from_bytes(raw_data[8:10],byteorder= 'little')
    # form_data.scan_number = int.from_bytes(raw_data[10:12],byteorder= 'little')
    form_data.packet_number = int.from_bytes(raw_data[12:14],byteorder= 'little')
    form_data.layer_index = int.from_bytes(raw_data[14:16],byteorder= 'little')
    # form_data.layer_inclination = int.from_bytes(raw_data[16:20],byteorder= 'little')
    # form_data.timestamp_raw = raw_data[20:28].hex()
    # form_data.reserved1 = raw_data[28:36].hex()
    # form_data.status_flags = raw_data[36:40].hex()
    # form_data.scan_frequency = int.from_bytes(raw_data[40:44],byteorder= 'little')
    # form_data.num_points_scan = int.from_bytes(raw_data[44:46],byteorder= 'little')
    # form_data.num_points_packet = int.from_bytes(raw_data[46:48],byteorder= 'little')
    # form_data.first_index = int.from_bytes(raw_data[48:50],byteorder= 'little')
    # form_data.first_angle = int.from_bytes(raw_data[50:54],byteorder= 'little')
    # form_data.angular_increment = int.from_bytes(raw_data[54:58],byteorder= 'little')
    # form_data.reserved2 = raw_data[58:62].hex()
    # form_data.reserved3 = raw_data[62:66].hex()
    # form_data.reserved4 = raw_data[66:74].hex()
    # form_data.reserved5 = raw_data[74:82].hex()
    # form_data.header_padding = raw_data[82:84]#对齐32位的整数倍，前面的全部加起来差两个字节才是32bit的整数倍，所以这里padding是两个字节
    data_raw= raw_data[84:]#原始数据，里面的类型是int，且全部连在一起
    data_cut = cut(data_raw,4)#在下方定义了一个函数，用于切割数据，这里将原始数按照4个字节来切分，里面的类型是bytes
    for i in range(len(data_cut)):
        form_data.data.append(int.from_bytes(data_cut[i],byteorder= 'little'))#将切分出来的数据转成int类型，然后赋值给form_data.data，至此数据这一帧报文处理完成
    return form_data  #返回按照格式处理好的数据
# UDP 接收线程
def udp_receiver(q):
    flat_distance = np.zeros(483)
    flat_distance1 = np.zeros(483)
    flat_distance2 = np.zeros(483)
    flat_distance3 = np.zeros(483)
    amplitude = np.zeros(483)
    amplitude1 = np.zeros(483)
    amplitude2 = np.zeros(483)
    amplitude3 = np.zeros(483)
    flag = 0
    flag1 = 0
    flag2 = 0
    flag3 = 0
    data =np.zeros([483,8])
    q.append(data)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', 10000))
    print("UDP receiver started")
    while not stop_flag.is_set():
        
        raw_data, addr = sock.recvfrom(10000)
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

        if (form_data.layer_index ==1) and form_data.packet_number ==1:#判断是否是第二层，layer_index分别为：0，1，2，3；同时判断是否为此层的第一个包
            flag1 =1 #改变flag的值，使画图线程不可以在接收数据和处理数据时更新图像
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

        if (form_data.layer_index ==1) and form_data.packet_number ==2:#判断是否是第二层，layer_index分别为：0，1，2，3；同时判断是否为此层的第二个包
            for i in range(0, len(form_data.data)):
                amplitude1.append((form_data.data[i]>>20)&0xfff)#切割距离和强度
                distance.append((form_data.data[i]&0xfffff)/1000)
                angle =abs(i+291-220)*(1.7453/500)
                #print(angle)
                flat_distance1.append(((form_data.data[i]&0xfffff)/1000)*math.cos(angle))
            flag1 =0 #改变flag的值，告诉画图线程现在可以开始更新图像了

        if (form_data.layer_index ==2) and form_data.packet_number ==1:#判断是否是第三层，layer_index分别为：0，1，2，3；同时判断是否为此层的第一个包
            flag2 =1 #改变flag的值，使画图线程不可以在接收数据和处理数据时更新图像
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

        if (form_data.layer_index ==2) and form_data.packet_number ==2:#判断是否是第三层，layer_index分别为：0，1，2，3；同时判断是否为此层的第二个包
            for i in range(0, len(form_data.data)):
                amplitude2.append((form_data.data[i]>>20)&0xfff)#切割距离和强度
                distance.append((form_data.data[i]&0xfffff)/1000)
                angle =abs(i+291-220)*(1.7453/500)
                #print(angle)
                flat_distance2.append(((form_data.data[i]&0xfffff)/1000)*math.cos(angle))
            flag2 =0 #改变flag的值，告诉画图线程现在可以开始更新图像了

        if (form_data.layer_index ==3) and form_data.packet_number ==1:#判断是否是第四层，layer_index分别为：0，1，2，3；同时判断是否为此层的第一个包
            flag3 =1 #改变flag的值，使画图线程不可以在接收数据和处理数据时更新图像
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

        if (form_data.layer_index ==3) and form_data.packet_number ==2:#判断是否是第四层，layer_index分别为：0，1，2，3；同时判断是否为此层的第二个包
            for i in range(0, len(form_data.data)):
                amplitude3.append((form_data.data[i]>>20)&0xfff)#切割距离和强度
                distance.append((form_data.data[i]&0xfffff)/1000)
                angle =abs(i+291-220)*(1.7453/500)
                #print(angle)
                flat_distance3.append(((form_data.data[i]&0xfffff)/1000)*math.cos(angle))
            flag3 =0 #改变flag的值，告诉画图线程现在可以开始更新图像了
        if flag == 0 and flag1 == 0 and flag2 == 0 and flag3 == 0:
            data = [flat_distance,flat_distance1,flat_distance2,flat_distance3,
                    amplitude,amplitude1,amplitude2,amplitude3]
        # print(f"length of layer1:{len(data[0])}")
        # print(f"length of layer2:{len(data[1])}")
        # print(f"length of layer3:{len(data[2])}")
        # print(f"length of layer4:{len(data[3])}")
        #q.put(data)
        q.append(data)

# 更新图形
def update_plots():
    #if not stop_flag.is_set() and not data_queue.empty():
    if not stop_flag.is_set():# and data_queue:
        position_amplitude_data = data_queue[-1]
        # print(f"length of position_data1:{len(position_data[0])}")
        # print(f"length of position_data2:{len(position_data[1])}")
        # print(f"length of position_data3:{len(position_data[2])}")
        # print(f"length of position_data4:{len(position_data[3])}")
        for i in range(4):
            ax[i].clear()
            #ax[i].lines=[]
            scatter_plot=ax[i].scatter(range(len(position_amplitude_data[i])), position_amplitude_data[i],
                          c= position_amplitude_data[i+4],cmap='coolwarm',vmin=32,vmax=2500,s=5)
            ax[i].set_title(f"Layer {i+1}")
            ax[i].set_xlim(0, 483)  # 设置x轴范围
            ax[i].set_ylim(0, 10)  # 设置y轴范围
        # 在所有子图上共享一个颜色条
        # cbar = fig.colorbar(scatter_plot, ax=ax)  # ax 是一个包含所有子图的列表
        # cbar.set_label('Amplitude')
        plt.tight_layout()  # 自动调整子图间距        
        canvas.draw()
        #canvas.draw_idle()  # 只重新绘制改动的部分
        # canvas.flush_events()  # 处理图形事件
        # root.update_idletasks()  # 更新图形任务
        root.after(10, update_plots)

# 启动按钮点击事件
def start_listener():
    global stop_flag
    stop_flag.clear()
    udp_thread = threading.Thread(target=udp_receiver, args=(data_queue,))
    udp_thread.daemon = True
    udp_thread.start()
    update_plots()

# 停止按钮点击事件
def stop_listener():
    global stop_flag
    stop_flag.set()

# 抓取按钮点击事件
def capture_data():
    #if not data_queue.empty():
    if data_queue:
        #position_data = data_queue.get()
        position_amplitude_data = data_queue[-1]
        fig, axs = plt.subplots(2, 2)
        ax = axs.flatten()
        for i in range(4):
            ax[i].scatter(range(len(position_amplitude_data[i])), position_amplitude_data[i],
                          c= position_amplitude_data[i+4],cmap='coolwarm',vmin=32,vmax=2500,s=5)
            ax[i].set_title(f"Layer {i+1}")
            ax[i].set_xlim(0, 483)  # 设置x轴范围
            ax[i].set_ylim(0, 10)  # 设置y轴范围            
        plt.tight_layout()  # 自动调整子图间距
        #plt.show()
        fig.show()

# 关闭窗口时的事件处理函数
def on_closing():
    stop_listener()
    root.destroy()
    sys.exit()


# 初始化 Tkinter 界面
root = tk.Tk()
root.title("UDP Listener")

# 创建队列
#data_queue = queue.Queue()
data_queue = deque(maxlen=1) 
stop_flag = threading.Event()

# 创建图形
fig, ax = plt.subplots(2, 2,figsize=(15, 8))
ax = ax.flatten()

# 创建画布
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# 创建按钮
button_frame = ttk.Frame(root)
button_frame.pack(side=tk.TOP, pady=10)

start_button = ttk.Button(button_frame, text="Start", command=start_listener)
start_button.pack(side=tk.LEFT, padx=5)

stop_button = ttk.Button(button_frame, text="Stop", command=stop_listener)
stop_button.pack(side=tk.LEFT, padx=5)

capture_button = ttk.Button(button_frame, text="Capture", command=capture_data)
capture_button.pack(side=tk.LEFT, padx=5)

# 绑定关闭窗口事件
root.protocol("WM_DELETE_WINDOW", on_closing)

# 进入主循环
root.mainloop()