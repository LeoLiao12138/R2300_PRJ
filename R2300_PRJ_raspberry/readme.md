# 为树莓派专门写的版本
## 树莓派3B+
check_network_and_run.sh是尝试ping R2300的IP地址10.0.10.76，如果ping不同，则重试，如果ping通了，则执行python脚本http_handle_request_and_start.py和R2300_v1.5_raspberry.py。

其中http_handle_request_and_start.py是通过http发送request_handle和start指令，让R2300开始发送UDP数据到10.0.10.110的10000端口。

R2300_v1.5_raspberry.py是主程序，相比于电脑的v1.4版本，有以下改动：
1. 启动后自动运行，不需要点击start按钮。
2. 处理好了进程的一些数据冲突，比如deque开始时没有数值，会报错。
3. 增加了线程的启动和停止功能，但是后续不需要控制
4. 取消掉了4层图像显示的功能，只留三个按钮和数值更新显示。因为图像更新会占用太多资源，导致数值处理太慢。
5. 通过外部GPIO输入进行capture控制，输出led灯，当程序正常开始运行，就绿灯亮，当有东西进入第0层和capture的曲线不同的时，红灯亮。
6. 增加了differ和count输入框，用来输入允许与capture图像不同的阈值和不同的个数
7. 增加了高度输入框，用来输入R2300的安装高度，由勾股定理计算每层激光的中心点距离R2300的水平距离。
---

要使树莓派能够上电后自动运行程序，需要将check-network.service文件放到/etc/systemd/system目录下，然后将其他文件放到桌面的R2300文件夹中，并运行start_check_network_service.sh脚本，就能让树莓派上电后自动运行程序。

上电后，等待绿灯即GPIO.21亮起，说明程序启动成功，此时给capture引脚即GPIO.26一个低电平，即完成captrue，此时就正式开始监控，当第0层有物体进入时，就会红灯即GPIO.22亮起，离开时则又会熄灭。

需要通过pip3安装以下库：
- matplotlib
- numpy
- gpiozero
- （还有一些可能有遗漏，后续再补充）

需要设置网口的IP地址为10.0.10.110

另外，要关注一下新装的系统的/boot/config.txt文件，确保里面有以下内容,或者把这几句的注释去掉
- hdmi_force_hotplug=1
- hdmi_group=1
- hdmi_mode=16
作用是让树莓派开机后自动检测HDMI信号，并设置为1080p的分辨率。这样可以在不管有没有显示器都会强制以1080p的分辨率启动。这样可以避免在无显示器的情况下，HDMI信号不输出的问题，才不会让tkinter报错"tkinter.TclError: no display..."


目前树莓派3B+的版本已经测试通过，但是手里的树莓派网口有问题，能进不能出，所以用了一个无线路由器转发一下。后续重新买一个网口好的树莓派应该就可以直插了。

还有一个问题是，树莓派3B+的GPIO21和GPIO22的驱动电流比较小，所以需要买一个继电器扩展板来做以后24V的输出控制。