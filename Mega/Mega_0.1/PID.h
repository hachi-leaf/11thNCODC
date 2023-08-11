#ifndef PID_H
#define PID_H

#include "Arduino.h"

class Inc_pid{ //增量式pid
  public:
    float miss[30]; // 误差
    float miss_now=0, miss_last=0, miss_lalast=0;
    int box; //卷积后参数和卷积盒长度
    float miss_i=0,miss_d=0; // 微分与积分
    float KP,KI,KD; // PID参数
    int time;

    void Inc_pid::init(float kp, float ki, float kd, int box_len); // pid参数,卷积盒长度.计算时间间隔
    float Inc_pid::compute(float miss_new); //计算并输出 
};

#endif