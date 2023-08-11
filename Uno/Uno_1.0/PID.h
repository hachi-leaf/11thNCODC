#ifndef PID_H
#define PID_H

#include "Arduino.h"

// 位置式PID
class Pos_PID {
public:
  float KP, KI, KD;  // pid参数
  float miss[30];    // 误差记录
  float time[30];    //时间记录
  float miss_i = 0, miss_d = 0;
  int num;  // 误差缓存数
  float max, imax;

  void init(float kp, float ki, float kd, int n, float m, float im) {  // 初始化
    KP = kp;
    KI = ki;
    KD = kd;
    num = n;
    max = m;
    imax = im;
    for (int i = 0; i < num; i++) {
      miss[i] = 0;
      time[i] = millis();
      delay(10);
    }
  }

  void zero() {  // 误差清零
    for (int i = 0; i < num; i++) {
      miss[i] == 0;
      time[i] + 10 * (i - num);
    }
    miss_i = 0;
    miss_d = 0;
  }

  float compute(float miss_new) {
    for (int i = 0; i < num - 1; i++) {
      miss[i] = miss[i + 1];
      time[i] = time[i + 1];  //迭代
    }
    miss[num - 1] = miss_new;
    time[num - 1] = millis();  // new data

    miss_i += miss_new * (time[num - 1] - time[num - 2]) / 1000;

    if (miss_i > fabs(imax)) miss_i = fabs(imax);
    else if (miss_i < -fabs(imax)) miss_i = -fabs(imax);

    miss_d = 1000.0 * (miss[num - 1] - miss[0]) / (time[num - 1] - time[0]);  //计算 i值 d值
    delay(2);

    float out = KP * miss_new + KI * miss_i + KD * miss_d;
    if (out > fabs(max)) return fabs(max);
    else if (out < -fabs(max)) return -fabs(max);
    return out;
  }
};

//增量式pid
class Inc_PID {
public:
  float miss[60];  // 误差
  float miss_now = 0, miss_last = 0, miss_lalast = 0;
  int box;                       //卷积后参数和卷积盒长度
  float miss_i = 0, miss_d = 0;  // 微分与积分
  float KP, KI, KD;              // PID参数
  int time;

  void init(float kp, float ki, float kd, int box_len) {  //pid参数和卷积盒长度
    KP = kp;
    KI = ki;
    KD = kd;
    box = box_len;

    for (int i = 0; i < 3 * box; i++) {
      miss[i] = 0;
    }
  }

  float compute(float miss_new) {  //计算并输出
    for (int i = 0; i < 3 * box - 1; i++) {
      miss[i] = miss[i + 1];
    }
    miss[3 * box - 1] = miss_new;  // 迭代误差记录

    int j = 0;
    float sum1 = 0, sum2 = 0, sum3 = 0;
    for (; j < 1 * box; j++) sum3 += miss[j];
    for (; j < 2 * box; j++) sum2 += miss[j];
    for (; j < 3 * box; j++) sum1 += miss[j];
    miss_now = sum1 / box;
    miss_last = sum2 / box;
    miss_lalast = sum3 / box;  // 卷积操作

    //按照增量式pid公式计算
    float datap = miss_now - miss_last;
    float datai = miss_now;
    float datad = miss_now - 2 * miss_last + miss_lalast;

    return KP * datap + KI * datai + KD * datad;
  }
};

#endif