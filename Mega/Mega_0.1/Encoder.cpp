#include "Encoder.h"

void Encoder::init(int A, int B, int pA, int pB){ // 初始化引脚
  Aint = A;
  Bint = B; //中断号
  Adig = pA;
  Bdig = pB; //引脚号
  pinMode(Adig, INPUT);
  pinMode(Bdig, INPUT); // mod set
}

void Encoder::itrpt(char AB){ //中断服务
  if(AB == 'A'){
    if(digitalRead(Adig) == digitalRead(Bdig))num++;
    else num--;
  }
  else if(AB == 'B'){
    if(digitalRead(Adig) != digitalRead(Bdig))num++;
    else num--;
  }
}

void Encoder::compute(int time){ // 计算速度
  for(int i = 0; i < 9; i++)val[i] = val[i+1]; //迭代
  val[9] = 1000.0*num/time/390/4;
  num = 0;
}

float Encoder::output(){ // 输出速度
  float sum = 0;
  for(int i = 0; i < 10; i++)sum += val[i];
  return sum/10; //卷积操作
}
