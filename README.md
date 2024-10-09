# 11THNCODC（第十一届全国大学生光电设计竞赛）
- 赛题：“迷宫寻宝"光电智能小车
- 获奖：国赛一等奖
## 硬件
- Arduino Uno
- RDK X3 module
- 二轮差速小车
- tb6612电机驱动
- MG513电机及霍尔编码器
- 感为灰度传感器
- usb camera
- 维特智能6轴陀螺仪
- LM2596降压模块
- 24V电池组
- 自设计PCB印刷电路
## 软件
### 区赛 -Regional-
#### Arduino代码 -Arduino_guangsai-
##### `LEV/LEV.ino`
Arduino所有程序
#### 函数库 -function-
##### `map_read.py`
函数`map_read(img)`识别藏宝图，通过和原地图比对，并且验证宝藏点个数与对称性，准确识别
##### `shortest_road.py`
函数：`shortest_road(loc_go,loc_end,prt=False)`
- `loc_go`：起点列表
- `loc_end`：终点列表
- `prt=False`：是否打印地图布尔值
- `return list`：返回列表，列表内容为起点到终点在node的拐弯情况，1为直行，2为左转，3为右转，4为掉头
##### `turn.cpp`
使用了灰度矫正的转弯算法函数：
```
void turn_plus(
  int mode,
  int vb_left, 
  int vb_right,
  int dtime1,
  int dtime2,
  int dtime3,
  int vt_left, 
  int vt_right,
  int ttime,
  int pidtime,
  int vp,
  float KP, 
  float KI,
  float KD
  );
```
- `mode`：turn模式
- `vb_left`：刹车左速度
- `vb_right`：刹车右速度
- `dtime1`：刹车持续时间1
- `dtime2`：刹车持续时间2
- `dtime3`：刹车持续时间3
- `vt_left`：僵直转向左速度
- `vt_right`：僵直转向右速度
- `ttime`：僵直时间
- `pidtime`：pid灰度矫正时间
- `vp`：pid基准速度
- `KP`：PID算法P参数
- `KI`：PID算法I参数
- `KD`：PID算法D参数
### 国赛 -National-
#### RDK X3上位机代码 -RDK_guangsai-
- `LEV.py`：主程序
- `board.py`：控制台封装
- `dominoes_new.yolov5.bin`：骨牌识别模型
- `map_read.py`：藏宝图识别
- `postprocess.py`：yolov5后处理
- `Road_plan_new.py`：路径规划
- `Reprimand.py`：容斥处理
#### Arduino下位机代码 -Uno_1.1-
- `Uno_1.1.ino`：主程序
- `Encoder.h`：编码器封装头文件
- `gray.h`：灰度传感器封装头文件
- `PID.h`：pid控制封装头文件
- `ware.h`：其他库函数封装

