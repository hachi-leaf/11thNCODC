光赛小车题 已拿国赛一等奖
硬件：Arduino Uno，RDK X3 module，差速小车，tb6612电机驱动，MG513电机及霍尔编码器，感为灰度传感器，usb camera，维特智能6轴陀螺仪，LM2596降压模块，24V电池组
软件：
guangsai_national
|
+--Uno_1.1 #下位机代码
|  |
|  +--Uno_1.1.ino #主程序
|  |
|  +--Encoder.h #编码器封装头文件
|  |
|  +--gray.h #灰度传感器封装头文件
|  |
|  +--PID.h #pid控制封装头文件
|  |
|  +--ware.h #其他库函数封装
|
|
+--RDK_guangsai
   |
   +--LEV.py #主程序
   |
   +--board.py #控制台封装
   |
   +--dominoes_new.yolov5.bin #骨牌识别模型
   |
   +--map_read.py #藏宝图识别
   |
   +--postprocess.py #yolov5后处理
   |
   +--Road_plan_new.py #路径规划
   |
   +--Reprimand.py #容斥处理






