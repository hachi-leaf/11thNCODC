#include <Wire.h>
#include "gw_grayscale_sensor.h"
#include <math.h>

//tb6612对应引脚
#define AIN1 4
#define AIN2 7
#define BIN1 12
#define BIN2 13
#define PWMA 10
#define PWMB 11
#define STBY 8

#define _MAIN while(1){
#define MAIN_ }

/*PID结构体
  存取5次miss*/
struct PID {
  float KP,KI,KD;
  float miss_i = 0.0;
  float miss_his[5] = { 0, 0, 0, 0, 0 };
  long time_his[5] = { millis() - 40,
    millis() - 30, 
    millis() - 20, 
    millis() - 10, 
    millis() };};
/*电机控制
  自动规范阈值并判断正反转*/
void ctrl(
  int left, 
  int right);
/*PID记录归零
  传入结构体指针*/
void pid_zero(
  struct PID *pid);
/*PID运算并输出
  传入误差和结构体指针*/
float pid_com(
  struct PID *pid,
  float miss);
/*获取灰度情况
  传入误差变量指针*/
int gray_decide(
  float *miss);
/*寻迹算法
  传入基准速度pwm，误差，和pid指针*/
void along(
  struct PID *pid, 
  int pwm_cri, 
  float miss);
/*转弯函数
  具有灰度矫正功能*/
void turn(
  int vb_left,
  int vb_right,  //刹车左右速度
  int ta,
  float tb,
  int tk, //循迹时间拟合刹车时
  int vt_left,
  int vt_right,  //僵直转向左右速度
  int ttime,     //僵直时间
  int pidtime,   //pid灰度矫正时间
  int vp,        //pid基准速度
  float KP,
  float KI,// pid参数
  float KD,
  int slow_time);

/*缓慢前进
  传入时间*/
void slow(
  int time);
/*读取命令
  */
void order_read(
  );


void setup(){
  delay(200);

  //开启串口
  Serial.begin(115200);

  //开启TB6612
  digitalWrite(STBY, HIGH);

  //IIC set
  Wire.begin();

  //灰度传感器定义
  Wire.beginTransmission(0x4C);
  Wire.write(0xB0);
  Wire.endTransmission();
}

//全局变量
int road[40] = {//路线
  0,0,0,0,0, 0,0,0,0,0,
  0,0,0,0,0, 0,0,0,0,0,
  0,0,0,0,0, 0,0,0,0,0,
  0,0,0,0,0, 0,0,0,0,0};
int oper = 0;//允许运行
int error = 0;//中断
long turn_time;//转弯时间

void loop(){
  //变量定义
  PID along_pid,slow_pid;//循迹pid以及参数初始化
  along_pid.KP = 28;along_pid.KI = 0;along_pid.KD = 54;//cri 144
  int mode=-1;//灰度情况
  float miss;//误差
  
  _MAIN //循环
    order_read();
    if(error){
      ctrl(0,0);
      continue;
    }
    if(oper){
      mode = gray_decide(&miss);
      switch(mode){
        case 0:
        case 5:
          along(&along_pid,144,miss);
          break;
        case 1:
        case 2:
        case 3:
        case 4:
          switch(road[0]){
            case 1:
              turn(1,0,0,0,0,0,0,0,0,0,0,0,0,800);
              break;
            case 2:
              turn(-255,32,0,0,200,-144,192,250,50,64,64,2,32,800);
              break;
            case 3:
              turn(32,-255,0,0,300,192,-144,250,50,64,64,2,32,800);
              break;
            case 4:
              turn(-255,32,0,0,200,-144,144,250,50,64,64,2,32,0);
              break;
            case 5:
              ctrl(64,64);
              delay(300);
              ctrl(0,0);
              while(1){
                delay(99999999);              }
              
          }
          break;
      }
    }
  MAIN_
}

/*
转弯参数
  turn(-255, 0, 200, 0.1, 400, -64, 75, 300, 75, 64, 25.6, 8.8, 32,800);
  turn(0, -255, 200, 0.1, 400, 75, -64, 300, 75, 64, 25.6, 8.8, 32,800);
循迹参数
  along(&along_pid,108,miss);
*/

void order_read(){
  char data;
  int i;
  while (Serial.available()) {
    data = Serial.read();
    if (data == 'r') {
      i = 0;
      while (1) {
        if (Serial.available()) {
          data = Serial.read();
          if (data == 'e') {
            for (; i < 40; i++) {
              road[i] = 0;
            }
            oper = 1;
            error = 0;
            turn_time = millis();
            return ;
          } else {
            road[i++] = data - '0';
          }
          delay(5);
        }
      }
    }

    if(data == 't') {
      error = 1;
      continue;
    }
    if(data == 'g') {
      error = 0;
      continue;
    }
    if(data == 'Y') {
      Serial.write("f");//转弯前发送信号

      int mode = 2;
      
      PID turn_pid;
      turn_pid.KP=25.6;turn_pid.KI=8.8;turn_pid.KD=32;
      int tmode[2] = {0,0};
      float tmiss;
      int th;

      tmode[0] = gray_decide(&tmiss);
      tmode[1] = tmode[0];
      if(tmode[0] == 1)th == 1;
      else th ==0;

      ctrl(75, -75);
      delay(300);  //僵直转向

      for (;;) {
        tmode[0] = tmode[1];
        tmode[1] = gray_decide(&tmiss);
        if(tmode[0]!=1 && tmode[1]==1)th++;
        if(tmode[1]!=1 && th)break;
      }  // 等待僵直转向到黑线

      long gray0_time = millis();
      float tm;
      while (millis() - gray0_time < 75){
        tmode[1] = gray_decide(&tmiss);
        if (tmode[1] == 0) {
          if (tmiss > 1 || tmiss < -1) gray0_time = millis();  //打断计时
          tm = pid_com(&turn_pid,tmiss);
          ctrl(16 - tm, 16 + tm);  //pid参数输出
        }
        else{
          gray0_time = millis();
        }
      }

      turn_time = millis();
      error = 0;
    }
    if(data == 'Z') {
      Serial.write("f");//转弯前发送信号

      int mode = 3;
      
      PID turn_pid;
      turn_pid.KP=25.6;turn_pid.KI=8.8;turn_pid.KD=32;
      int tmode[2] = {0,0};
      float tmiss;
      int th;

      tmode[0] = gray_decide(&tmiss);
      tmode[1] = tmode[0];
      if(tmode[0] == 1)th == 1;
      else th ==0;

      ctrl(-75, 75);
      delay(300);  //僵直转向

      for (;;) {
        tmode[0] = tmode[1];
        tmode[1] = gray_decide(&tmiss);
        if(tmode[0]!=1 && tmode[1]==1)th++;
        if(tmode[1]!=1 && th)break;
      }  // 等待僵直转向到黑线

      long gray0_time = millis();
      float tm;
      while (millis() - gray0_time < 75){
        tmode[1] = gray_decide(&tmiss);
        if (tmode[1] == 0) {
          if (tmiss > 1 || tmiss < -1) gray0_time = millis();  //打断计时
          tm = pid_com(&turn_pid,tmiss);
          ctrl(16 - tm, 16 + tm);  //pid参数输出
        }
        else{
          gray0_time = millis();
        }
      }

      turn_time = millis();
      error = 0;
    }
    if(data=='b'){
      ctrl(108,108);
      delay(500);
    }

    delay(5);
  }
}

void turn(
  int vb_left,
  int vb_right,  //刹车左右速度
  int ta,
  float tb,
  int tk, //循迹时间拟合刹车时
  int vt_left,
  int vt_right,  //僵直转向左右速度
  int ttime,     //僵直时间
  int pidtime,   //pid灰度矫正时间
  int vp,        //pid基准速度
  float KP,
  float KI,// pid参数
  float KD,
  int slow_time){

    Serial.write("f");//转弯前发送信号

    int mode = road[0];

    for (int i = 0; i < 39; i++) {
      road[i] = road[i + 1];
    }
    road[39] = 0;  //road迭代

    if (mode == 1) {
      if(road[0] == 0){
        oper = 0;
        ctrl(0,0);

      }
      else{
        ctrl(108, 108);
        delay(75);
        return ;
      }
    }  //直走不转弯

    ctrl(vb_left, vb_right);//刹车
    int detime = (int)(ta + tb*(millis()-turn_time));
    if(detime < tk)delay(detime);
    else delay(tk);
    
    PID turn_pid;
    turn_pid.KP=KP;turn_pid.KI=KI;turn_pid.KD=KD;
    int tmode[2] = {0,0};
    float tmiss;
    int th;

    tmode[0] = gray_decide(&tmiss);
    tmode[1] = tmode[0];
    if(tmode[0] == 1)th == 1;
    else th ==0;

    ctrl(vt_left, vt_right);
    delay(ttime);  //僵直转向

    for (;;) {
      tmode[0] = tmode[1];
      tmode[1] = gray_decide(&tmiss);
      if(tmode[0]!=1 && tmode[1]==1)th++;
      if(tmode[1]!=1 && th)break;
    }  // 等待僵直转向到黑线

    long gray0_time = millis();
    float tm;
    while (millis() - gray0_time < pidtime){
      tmode[1] = gray_decide(&tmiss);
      if (tmode[1] == 0) {
        if (tmiss > 1 || tmiss < -1) gray0_time = millis();  //打断计时
        tm = pid_com(&turn_pid,tmiss);
        ctrl(vp - tm, vp + tm);  //pid参数输出
      }
      else{
        gray0_time = millis();
      }
    }
    if(road[0]==0 && mode != 4){
      oper = 0;
      error = 1;
      PID slow_pid;
      slow_pid.KP = 12;slow_pid.KI = 0;slow_pid.KD = 24;//cri 36
      gray0_time = millis();
      while(millis() - gray0_time < slow_time){
        tmode[1] = gray_decide(&tmiss);
        if(tmode[1]!=1)along(&slow_pid,36,tmiss);
        else continue;
      }
      ctrl(-52,-52);
      delay(slow_time);
      ctrl(0,0);
    }
    turn_time = millis();
}

void along(
  struct PID *pid, 
  int pwm_cri, 
  float miss){

    float m = pid_com(pid,miss);
    ctrl((int)(pwm_cri - m), (int)(pwm_cri + m));
}

int gray_decide(
  float *miss){

    uint8_t recv_value = 0;
    float flag = 0.0;
    int num = 0;
    int left = 0, right = 0;
    Wire.requestFrom(0x4C, 8, 1);

    for (int i = 0; i < 8; ++i) {
      recv_value = Wire.read();
      //Serial.print(" ");Serial.print(recv_value);
      if((int)recv_value <= 64){
        flag += 3.5 - i;
        num++;
        if (i == 0) left++;
        if (i == 7) right++;  //记录0,7号传感器情况
      }
    }

    if (!num) return 1;   //空白情况
    else if (num <= 3) {  //正常循迹情况
      *miss = 1.0 * flag / num;
      return 0;
    }
    else if (num > 3) {
      if (left && right) return 4;  //左右有黑线
      else if (left) return 2;      //左侧黑线
      else if (right) return 3;     //右侧黑线
      else return 5;                //其他情况
    }
}

float pid_com(
  struct PID *pid,
  float miss){
    for (int i = 0; i < 4; i++) {
      (*pid).miss_his[i] = (*pid).miss_his[i + 1];
      (*pid).time_his[i] = (*pid).time_his[i + 1];
    }
    (*pid).miss_his[4] = miss;
    (*pid).time_his[4] = millis();  //pid迭代

    (*pid).miss_i += ((*pid).miss_his[4] - (*pid).miss_his[3]) * ((*pid).time_his[4] -(*pid).time_his[3]) / 1000;
    float d = 1000 * ((*pid).miss_his[4] - (*pid).miss_his[0]) / ((*pid).time_his[4] - (*pid).time_his[0]);
    
    return (*pid).KP*miss + (*pid).KI*(*pid).miss_i + (*pid).KD*d;
}

void pid_zero(
  struct PID *pid){
    for (int i; i < 5; i++) {
      (*pid).miss_his[i] = 0;
      (*pid).time_his[4 - i] = millis() - i * 10;
    }
    (*pid).miss_i = 0;
}

void ctrl(
  int left, 
  int right){
    if (left > 255) left = 255;
    if (left < -255) left = -255;
    if (right > 255) right = 255;
    if (right < -255) right = -255;

    if (right >= 0) {
      digitalWrite(AIN1, HIGH);
      digitalWrite(AIN2, LOW);
    } 
    else {
      digitalWrite(AIN2, HIGH);
      digitalWrite(AIN1, LOW);
    }

    if (left >= 0) {
      digitalWrite(BIN1, HIGH);
      digitalWrite(BIN2, LOW);
    } 
    else {
      digitalWrite(BIN2, HIGH);
      digitalWrite(BIN1, LOW);
    }
    analogWrite(PWMB, abs(left));
    analogWrite(PWMA, abs(right));
}