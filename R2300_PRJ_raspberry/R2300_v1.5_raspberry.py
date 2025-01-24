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
from gpiozero import Button,LED
import time

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
    global sock
    distance =[]
    flat_distance =[0 for _ in range(483)]# np.zeros(483)
    flat_distance1 =[0 for _ in range(483)]# np.zeros(483)
    flat_distance2 =[0 for _ in range(483)]# np.zeros(483)
    flat_distance3 =[0 for _ in range(483)]# np.zeros(483)
    amplitude =[0 for _ in range(483)]# np.zeros(483)
    amplitude1 =[0 for _ in range(483)]# np.zeros(483)
    amplitude2 =[0 for _ in range(483)]# np.zeros(483)
    amplitude3 =[0 for _ in range(483)]# np.zeros(483)
    flag = 0
    flag1 = 0
    flag2 = 0
    flag3 = 0
    data =np.zeros([483,8])
    q.append(data)

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
                angle =abs(i-242)*(1.7453/483)
                #计算垂直距离，即报文反馈的距离*cos(angle)
                flat_distance.append(((form_data.data[i]&0xfffff)/1000)*math.cos(angle))

        if (form_data.layer_index ==0) and form_data.packet_number ==2:#判断是否是第一层，layer_index分别为：0，1，2，3；同时判断是否为此层的第二个包
            for i in range(0, len(form_data.data)):
                amplitude.append((form_data.data[i]>>20)&0xfff)#切割距离和强度
                distance.append((form_data.data[i]&0xfffff)/1000)
                angle =abs(i+291-242)*(1.7453/483)
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
                angle =abs(i-242)*(1.7453/483)
                #print(angle)
                flat_distance1.append(((form_data.data[i]&0xfffff)/1000)*math.cos(angle))
            #print(len(form_data.data))

        if (form_data.layer_index ==1) and form_data.packet_number ==2:#判断是否是第二层，layer_index分别为：0，1，2，3；同时判断是否为此层的第二个包
            for i in range(0, len(form_data.data)):
                amplitude1.append((form_data.data[i]>>20)&0xfff)#切割距离和强度
                distance.append((form_data.data[i]&0xfffff)/1000)
                angle =abs(i+291-242)*(1.7453/483)
                #print(angle)
                flat_distance1.append(((form_data.data[i]&0xfffff)/1000)*math.cos(angle))
            flag1 =0 #改变flag的值，告诉画图线程现在可以开始更新图像了

        if (form_data.layer_index ==2) and form_data.packet_number ==1:#判断是否是第三层，layer_index分别为：0，1，2，3；同时判断是否为此层的第一个包
            flag3 =1 #改变flag的值，使画图线程不可以在接收数据和处理数据时更新图像
            distance=[]#新建空白的distance列表；在后续循环中重新执行这一句等于清空原来的数据；因为下面用的都是append方法，所以需要先清空
            amplitude3= []#同上
            flat_distance3 = []
            for i in range(0, len(form_data.data)):
                amplitude3.append((form_data.data[i]>>20)&0xfff)#高12bit为能量强度
                distance.append((form_data.data[i]&0xfffff)/1000)#低20bit为距离
                #将100°分成483个点，每个点的弧度
                angle =abs(i-242)*(1.7453/483)
                #print(angle)
                flat_distance3.append(((form_data.data[i]&0xfffff)/1000)*math.cos(angle))
            #print(len(form_data.data))

        if (form_data.layer_index ==2) and form_data.packet_number ==2:#判断是否是第三层，layer_index分别为：0，1，2，3；同时判断是否为此层的第二个包
            for i in range(0, len(form_data.data)):
                amplitude3.append((form_data.data[i]>>20)&0xfff)#切割距离和强度
                distance.append((form_data.data[i]&0xfffff)/1000)
                angle =abs(i+291-242)*(1.7453/483)
                #print(angle)
                flat_distance3.append(((form_data.data[i]&0xfffff)/1000)*math.cos(angle))
            flag3 =0 #改变flag的值，告诉画图线程现在可以开始更新图像了

        if (form_data.layer_index ==3) and form_data.packet_number ==1:#判断是否是第四层，layer_index分别为：0，1，2，3；同时判断是否为此层的第一个包
            flag2 =1 #改变flag的值，使画图线程不可以在接收数据和处理数据时更新图像
            distance=[]#新建空白的distance列表；在后续循环中重新执行这一句等于清空原来的数据；因为下面用的都是append方法，所以需要先清空
            amplitude2= []#同上
            flat_distance2 = []
            for i in range(0, len(form_data.data)):
                amplitude2.append((form_data.data[i]>>20)&0xfff)#高12bit为能量强度
                distance.append((form_data.data[i]&0xfffff)/1000)#低20bit为距离
                #将100°分成483个点，每个点的弧度
                angle =abs(i-242)*(1.7453/483)
                #print(angle)
                flat_distance2.append(((form_data.data[i]&0xfffff)/1000)*math.cos(angle))

        if (form_data.layer_index ==3) and form_data.packet_number ==2:#判断是否是第四层，layer_index分别为：0，1，2，3；同时判断是否为此层的第二个包
            for i in range(0, len(form_data.data)):
                amplitude2.append((form_data.data[i]>>20)&0xfff)#切割距离和强度
                distance.append((form_data.data[i]&0xfffff)/1000)
                angle =abs(i+291-242)*(1.7453/483)
                #print(angle)
                flat_distance2.append(((form_data.data[i]&0xfffff)/1000)*math.cos(angle))
            flag2 =0 #改变flag的值，告诉画图线程现在可以开始更新图像了
        if flag == 0 and flag1 == 0 and flag2 == 0 and flag3 == 0:
            data = [flat_distance,flat_distance1,flat_distance2,flat_distance3,
                    amplitude,amplitude1,amplitude2,amplitude3]
            display_label0.config(text= f"{data[0][242]:.2f}")
            display_label1.config(text= f"{data[1][242]:.2f}")
            display_label2.config(text= f"{data[2][242]:.2f}")
            display_label3.config(text= f"{data[3][242]:.2f}")
        q.append(data)

# 更新图形
def update_plots():
    global sock
    global led_red
    if not stop_flag.is_set():
        if data_queue:
            position_amplitude_data = data_queue[-1]
        for i in range(4):
            if captured_flag == True and (len(position_amplitude_data[i]) == len(capture_position_amplitude_data[i])):
                difference = np.array(position_amplitude_data[i])-np.array(capture_position_amplitude_data[i])
                count = np.sum(np.abs(difference)>float(differ_textbox.get()))
                if i ==0 :
                    if count > int(count_textbox.get()):
                        print(f"Alarm: layer {i},different counts {count}")
                        led_red.on()
                    else:
                        led_red.off()
                else:
                     if count > int(count_textbox.get()):
                        print(f"Alarm: layer {i},different counts {count}")
    root.after(50, update_plots)

# 启动按钮点击事件
def start_listener():
    global stop_flag
    global udp_thread
    if stop_flag.is_set():
        stop_flag.clear()
        global sock
        if sock:
            print("UDP receiver started")
        if not hasattr(start_listener, "udp_thread") or not start_listener.udp_thread.is_alive():
            udp_thread = threading.Thread(target=udp_receiver, args=(data_queue,))
            udp_thread.daemon = True
            udp_thread.start()
            update_plots()

# 停止按钮点击事件
def stop_listener():
    global stop_flag
    stop_flag.set()
    global sock
    if sock:
        print("UDP receiver stopped")

# 抓取按钮点击事件
def capture_data():
    global captured_flag
    if data_queue:
        global capture_position_amplitude_data
        capture_position_amplitude_data= data_queue[-1]
        fig, axs = plt.subplots(2, 2)
        ax = axs.flatten()
        captured_flag = True
        print("Captured")
        for i in range(4):
            ax[i].scatter(range(len(capture_position_amplitude_data[i])), capture_position_amplitude_data[i],
                          c="green",s=5)
            ax[i].set_title(f"Layer {i+1}")
            ax[i].set_xlim(0, 483)  # 设置x轴范围
            ax[i].set_ylim(0, 10)  # 设置y轴范围            
        plt.tight_layout()  # 自动调整子图间距
        fig.canvas.manager.window.title("Captured Data")
        fig.show()
        if (capture_position_amplitude_data[0][242]) >float(height_textbox.get()) and (capture_position_amplitude_data[1][242]) >float(height_textbox.get()) and (capture_position_amplitude_data[2][242]) >float(height_textbox.get()) and (capture_position_amplitude_data[3][242]) >float(height_textbox.get()):
            horizontal_display0.config(text= f"{math.sqrt((capture_position_amplitude_data[0][242])**2-float(height_textbox.get())**2):.2f}")
            horizontal_display1.config(text= f"{math.sqrt((capture_position_amplitude_data[1][242])**2-float(height_textbox.get())**2):.2f}")
            horizontal_display2.config(text= f"{math.sqrt((capture_position_amplitude_data[2][242])**2-float(height_textbox.get())**2):.2f}")
            horizontal_display3.config(text= f"{math.sqrt((capture_position_amplitude_data[3][242])**2-float(height_textbox.get())**2):.2f}")
            print(f"{capture_position_amplitude_data[0][242]},{float(height_textbox.get())}")

# 关闭窗口时的事件处理函数
def on_closing():
    stop_listener()
    sock.close()
    root.destroy()
    sys.exit()



#set button
button_capture = Button(26)
button_capture.when_pressed = capture_data
led_red = LED(6)
led_green = LED(5)
led_green.on()


# 初始化 Tkinter 界面
root = tk.Tk()
root.title("R2300 application")

# 设置全局样式
style = ttk.Style()
style.configure('TButton', font=('Helvetica', 18), padding=10)
style.configure('TLabel', font=('Helvetica', 18))
style.configure('TEntry', font=('Helvetica', 38), padding=10)

# 创建队列
data_queue = deque(maxlen=1) 
stop_flag = threading.Event()
stop_flag.set()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', 10000))

# 全局标志
captured_flag = False

# 创建按钮
button_frame = ttk.Frame(root)
button_frame.grid(row=1, column=0,columnspan=3, padx=10, pady=10)

start_button = ttk.Button(button_frame, text="Start", command=start_listener)
start_button.grid(row=0, column=0, padx=10, pady=10)

stop_button = ttk.Button(button_frame, text="Stop", command=stop_listener)
stop_button.grid(row=0, column=1, padx=10, pady=10)

capture_button = ttk.Button(button_frame, text="Capture", command=capture_data)
capture_button.grid(row=0, column=2, padx=10, pady=10)

# 创建高度输入框和距离显示
distance_frame = ttk.Frame(root)
distance_frame.grid(row=2, column=0, padx=1, pady=10)

# 创建四个 Label 来显示距离
distance_label0 = ttk.Label(distance_frame, text="0层直线距离:")
distance_label0.grid(row=0, column=0, padx=10, pady=10)
display_label0 = ttk.Label(distance_frame, text="0", foreground="blue")
display_label0.grid(row=0, column=1, padx=10, pady=10)

distance_label1 = ttk.Label(distance_frame, text="1层直线距离:")
distance_label1.grid(row=1, column=0, padx=10, pady=10)
display_label1 = ttk.Label(distance_frame, text="0", foreground="blue")
display_label1.grid(row=1, column=1, padx=10, pady=10)

distance_label2 = ttk.Label(distance_frame, text="2层直线距离:")
distance_label2.grid(row=2, column=0, padx=10, pady=10)
display_label2 = ttk.Label(distance_frame, text="0", foreground="blue")
display_label2.grid(row=2, column=1, padx=10, pady=10)

distance_label3 = ttk.Label(distance_frame, text="3层直线距离:")
distance_label3.grid(row=3, column=0, padx=10, pady=10)
display_label3 = ttk.Label(distance_frame, text="0", foreground="blue")
display_label3.grid(row=3, column=1, padx=10, pady=10)


# 创建4个 label 来显示水平距离
horizontal_frame = ttk.Frame(root)
#horizontal_frame.pack(pady=10)
horizontal_frame.grid(row=2, column=1, padx=1, pady=10)

horizontal_label0 = ttk.Label(horizontal_frame, text="0层水平距离:")
horizontal_label0.grid(row=0, column=0, padx=10, pady=10)
horizontal_display0 = ttk.Label(horizontal_frame, text="0", foreground="blue")
horizontal_display0.grid(row=0, column=1, padx=10, pady=10)

horizontal_label1 = ttk.Label(horizontal_frame, text="1层水平距离:")
horizontal_label1.grid(row=1, column=0, padx=10, pady=10)
horizontal_display1 = ttk.Label(horizontal_frame, text="0", foreground="blue")
horizontal_display1.grid(row=1, column=1, padx=10, pady=10)

horizontal_label2 = ttk.Label(horizontal_frame, text="2层水平距离:")
horizontal_label2.grid(row=2, column=0, padx=10, pady=10)
horizontal_display2 = ttk.Label(horizontal_frame, text="0", foreground="blue")
horizontal_display2.grid(row=2, column=1, padx=10, pady=10)

horizontal_label3 = ttk.Label(horizontal_frame, text="3层水平距离:")
horizontal_label3.grid(row=3, column=0, padx=10, pady=10)
horizontal_display3 = ttk.Label(horizontal_frame, text="0", foreground="blue")
horizontal_display3.grid(row=3, column=1, padx=10, pady=10)

# 创建两个 text box 来输入阈值
valve_frame = ttk.Frame(root)
valve_frame.grid(row=2, column=2, padx=1, pady=10)

height_textbox = ttk.Entry(valve_frame, width=10, font=('Helvetica', 18))
height_textbox.insert(0, "1")
height_lable = ttk.Label(valve_frame, text="Height:")
height_lable.grid(row=0, column=0, padx=10, pady=10)
height_textbox.grid(row=0, column=1, padx=10, pady=10)

differ_textbox = ttk.Entry(valve_frame, width=10, font=('Helvetica', 18))
differ_textbox.insert(0, "0.2")
differ_lable = ttk.Label(valve_frame, text="Differ:")
differ_lable.grid(row=1, column=0, padx=10, pady=10)
differ_textbox.grid(row=1, column=1, padx=10, pady=10)

count_textbox = ttk.Entry(valve_frame, width=10, font=('Helvetica', 18))
count_textbox.insert(0, "10")
count_lable = ttk.Label(valve_frame, text="Count:")
count_lable.grid(row=2, column=0, padx=10, pady=10)
count_textbox.grid(row=2, column=1, padx=10, pady=10)

start_listener()

# 绑定关闭窗口事件
root.protocol("WM_DELETE_WINDOW", on_closing)

# 进入主循环
root.mainloop()