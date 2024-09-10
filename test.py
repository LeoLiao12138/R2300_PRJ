import tkinter as tk  
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  
from matplotlib.figure import Figure  
import numpy as np  
import matplotlib.pyplot as plt  
from matplotlib.colors import Normalize

update_flag = 0
x1 = np.linspace(-2*np.pi,2*np.pi,100)
y1 = np.zeros(100)
colors = np.zeros(100)

def update_plots():
    global updata_flag  
    global x1,y1,colors
    #用update_flag 来判断是否更新数据
    if update_flag == 1:
    # 生成4组新数据作为散点图的坐标和颜色
        for i in range(4):  
            x1 = np.linspace(-2*np.pi,2*np.pi,100)
            y1 = np.linspace(0,10,100)
            colors = np.random.randint(0,10,100)  
            
            # 清除现有的散点图  
            scatter_plots[i].clear()  
            
            # 在子图上绘制新的散点图，并设置颜色，点的大小  
            scatter = scatter_plots[i].scatter(x1, y1, c=colors, cmap='coolwarm', s=10)  
            
            # 设置子图的标题  
            scatter_plots[i].set_title(f'Subplot {i+1}')  
            # 设置子图的X轴和Y轴的范围
            scatter_plots[i].set_xlim(min(x1), max(x1))
            scatter_plots[i].set_ylim(0, 10)
    # 绘制图像
    fig.canvas.draw()  
    # 1s后重新调用本函数更新数据和重新画图
    root.after(10, update_plots)    
  
#start按钮点击后将update_flag置为1
def start_button_clicked():  
    global update_flag  
    update_flag = 1
#停止按钮点击后将update_flag置为0
def stop_button_clicked():  
    global update_flag  
    update_flag = 0
#抓图按钮点击后，将当前时刻的x1,y1,colors绘制成一幅静态图
def capture_button_clicked():  
    global x1,y1,colors
    for i in range(4): 
        # 清除散点
        scatter_plots2[i].clear()  
        
        # 在子图上绘制新的散点图，并设置颜色  
        scatter = scatter_plots2[i].scatter(x1, y1, c=colors, cmap='coolwarm', s=2)  
        
        # 设置子图的标题  
        scatter_plots2[i].set_title(f'Subplot {i+1}')  
        # 设置子图的X轴和Y轴的范围
        scatter_plots2[i].set_xlim(min(x1), max(x1))
        scatter_plots2[i].set_ylim(min(y1), max(y1))
    # 更新图像
    fig1.canvas.draw()

def draw_scatter_plots_in_tkinter():  
    global root
    # 创建一个新的Tkinter窗口  
    root = tk.Tk()  
    root.geometry("800x900")
    root.title("Dynamic Scatter Plots with Colors and Colorbars")  
  
    #创建两个按钮，用于启动和停止图像更新
    start_button = tk.Button(root, text="Start", command=start_button_clicked)
    stop_button = tk.Button(root, text="Stop", command=stop_button_clicked)
    start_button.pack(side=tk.TOP)
    stop_button.pack(side=tk.TOP)

    #创建一个按钮，用于捕获图像
    capture_button = tk.Button(root, text="Capture", command=capture_button_clicked)
    capture_button.pack(side=tk.TOP)

    # 创建两个matplotlib图形对象  
    global fig,fig1
    fig = Figure(figsize=(6, 4), dpi=100)  
    fig1 = Figure(figsize=(6, 4), dpi=100)  

    # 设置子图的间隔
    fig.subplots_adjust(hspace=0.5, wspace=0.2)
    fig1.subplots_adjust(hspace=0.5, wspace=0.2)

    # 每幅图创建4个子图，并保存在scatter_plots 和 scatter_plots2中
    global scatter_plots,scatter_plots2
    scatter_plots = [fig.add_subplot(2, 2, i+1) for i in range(4)] 
    scatter_plots2 = [fig1.add_subplot(2, 2, i+1) for i in range(4)]
  
    # 初始绘制散点图（这里可以省略，因为update_plots会负责绘制）  
  
    # 将matplotlib图形嵌入到Tkinter窗口中  
    canvas = FigureCanvasTkAgg(fig, master=root)  
    canvas.draw()  
    canvas1 = FigureCanvasTkAgg(fig1, master=root)  
    canvas1.draw()

    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.NONE, expand=1)  
    canvas1.get_tk_widget().pack(side=tk.TOP, fill=tk.NONE, expand=1)  


  
    # 为整个图像添加颜色条  
    norm = Normalize(vmin=0, vmax=10)#创建一个 Normalize 对象：用于指定颜色条的最大值和最小值
    mappable = plt.cm.ScalarMappable(cmap='coolwarm', norm=norm) #创建 ScalarMappable 对象：使用 Normalize 对象进行颜色映射。
    cbar_ax = fig.add_axes([0.92, 0.1, 0.03, 0.8])  #用于在当前的 Figure 对象中添加一个新的 Axes 子图。参数 [0.92, 0.1, 0.03, 0.8] 是一个列表，表示新 Axes 的位置和大小。
    fig.colorbar(mappable= mappable, cax=cbar_ax) #创建一个颜色条，并使用 mappable 对象进行颜色映射。

    # 调用一次update_plots函数，后续在update_plots函数中自己每隔1s调用一次自己
    update_plots()
  
    # 启动Tkinter事件循环  
    root.mainloop()  
  
# 调用函数，在Tkinter窗口中显示动态更新的matplotlib绘制的散点图  
draw_scatter_plots_in_tkinter()