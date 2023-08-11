#include"PID.h"

void Inc_pid::init(float kp, float ki, float kd, int box_len){ //pid参数和卷积盒长度
  KP = kp;
  KI = ki;
  KD = kd;
  box = box_len;

  for(int i = 0; i < 3*box; i++){
    miss[i] = 0;
  }
}

float Inc_pid::compute(float miss_new){ //计算并输出 
  for(int i = 0; i < 3*box-1; i++){
    miss[i] = miss[i+1];
  }
  miss[3*box-1] = miss_new; // 迭代误差记录

  int j=0;
  float sum1=0,sum2=0,sum3=0;
  for(; j<1*box; j++)sum3 += miss[j];
  for(; j<2*box; j++)sum2 += miss[j];
  for(; j<3*box; j++)sum1 += miss[j];
  miss_now = sum1/box;
  miss_last = sum2/box;
  miss_lalast = sum3/box; // 卷积操作

  //按照增量式pid公式计算
  float datap = miss_now - miss_last;
  float datai = miss_now;
  float datad = miss_now - 2*miss_last + miss_lalast;

  //Serial.println(datai);

  /*if(KP*datap + KI*datai + KD*datad < 128)*/return KP*datap + KI*datai + KD*datad;
  //else return 128;
}

