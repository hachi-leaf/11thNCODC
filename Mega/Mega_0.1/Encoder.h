#ifndef ENCODER_H
#define ECODER_H

#include "Arduino.h"

#define LA 0
#define LB 1
#define RA 5
#define RB 4  // 编码器中断引脚号

#define pLA 2
#define pLB 3
#define pRA 18
#define pRB 19  // 编码器普通引脚号


class Encoder{
  public:
    int Aint, Bint, Adig, Bdig; // 终端引脚
    long num = 0; // 计数值
    float val[10] = {0,0,0,0,0, 0,0,0,0,0}; //转速

    void Encoder::init(int A, int B, int pA, int pB); // 初始化引脚
    void Encoder::itrpt(char AB); //中断服务
    void Encoder::compute(int time); // 计算速度
    float Encoder::output(); // 输出速度
};

#endif