#ifndef WARE_H
#define WARE_H

#include "Arduino.h"
#include "Wire.h"
#include "gw_grayscale_sensor.h"

#define BIN1 7
#define BIN2 4
#define AIN1 13
#define AIN2 12
#define PWMA 11
#define PWMB 10
#define STBY 8

#define EnA_L 3
#define EnB_L 5
#define EnA_R 2
#define EnB_R 6

void ctrl(int left, int right); // pwm输出

void gray_set();

int gray_get(float *miss);



class PID{
  public:
    float KP,KI,KD; // pid参数
    float miss[20]; // 误差记录
    float time[20]; //时间记录
    float miss_i = 0, miss_d = 0; 
    int num; // 误差缓存数
    float max,imax;

    void PID::init(float kp, float ki, float kd, int n, float m, float im); // 初始化
    float PID::compute(float miss_new); // 计算
};

class Encoder{
  public:
    int Adig, Bdig; // 中断引脚
    long num = 0; // 计数值

    void Encoder::init(int pA, int pB); // 初始化引脚
    void Encoder::itrpt(); //中断服务
};

#endif