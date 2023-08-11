#include"MsTimer2.h"
#include"Encoder.h"
#include"PID.h"

#define A1 9
#define A2 12
#define B1 7
#define B2 6  //电机控制

Encoder encoder_L,encoder_R; // 实例化编码器对象
Inc_pid inc_L,inc_R; // 实例化增量式pid对象

void pwm(int left,int right);

void setup(){
  Serial.begin(115200); //open Serial

  encoder_L.init(LA,LB,pLA,pLB);
  encoder_R.init(RA,RB,pRA,pRB); //初始化编码器管脚号

  inc_L.init(0,6,0,3);
  inc_R.init(0,0,0,1); // 增量式pid参数初始化

  attachInterrupt(LA, changela, CHANGE);
  attachInterrupt(LB, changelb, CHANGE);
  attachInterrupt(RA, changera, CHANGE);
  attachInterrupt(RB, changerb, CHANGE); // 开启中断

  MsTimer2::set(20, mstime); // 开启定时服务
  MsTimer2::start();
}

float exp_val_L = -4; // 期望速度
int pwm_L = 0;

void loop(){

  //获取速度并打印
  Serial.print(encoder_L.output());
  Serial.print(",");
  Serial.println(encoder_R.output());
}

// 中断服务，计数
void changela(){encoder_L.itrpt('A');}
void changelb(){encoder_L.itrpt('B');}
void changera(){encoder_R.itrpt('A');}
void changerb(){encoder_R.itrpt('B');}

float miss_L;

// 定时服务，计算速度，pid输出
void mstime(){
  encoder_L.compute(20);
  encoder_R.compute(20);
  miss_L = exp_val_L - encoder_L.output();
  pwm_L += (int)inc_L.compute(miss_L);
  //Serial.println((int)inc_L.compute(miss_L));
  pwm(pwm_L,0);
}

//pwm输出
void pwm(
  int left,
  int right
  ){
/*
  if(left>=0){
    if(left >= 255)left = 255;
    analogWrite(A1, 255 - left);
    analogWrite(A2, 255);
  }
  else{
    if(left < -255)left = -255;
    analogWrite(A1, 255);
    analogWrite(A2, 255 + left);
  }*/

  analogWrite(A1, left <= 0 ? (left < -255 ? -255 : -left) : 0);
  analogWrite(A2, left <= 0 ? 0 : (left > 255 ? 255 : left));

  analogWrite(B1, right <= 0 ? (right < -255 ? -255 : -right) : 0);
  analogWrite(B2, right <= 0 ? 0 : (right > 255 ? 255 : right));
}