#ifndef WARE_H
#define WARE_H

#include<Arduino.h>

#define BIN1 7
#define BIN2 4
#define AIN1 13
#define AIN2 12
#define PWMA 11
#define PWMB 10
#define STBY 8

void ctrl(int left, int right); // 输出pwm

float angle_cor(float angle_);

#endif