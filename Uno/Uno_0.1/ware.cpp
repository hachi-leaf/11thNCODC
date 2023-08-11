#include"ware.h"

void ctrl(int left, int right){ // 输出pwm
  digitalWrite(STBY, HIGH);

  if(left > 0){
    digitalWrite(AIN1, HIGH);
    digitalWrite(AIN2, LOW);
  }
  else{
    digitalWrite(AIN1, LOW);
    digitalWrite(AIN2, HIGH);
  }

  if(right > 0){
    digitalWrite(BIN1, HIGH);
    digitalWrite(BIN2, LOW);
  }
  else{
    digitalWrite(BIN1, LOW);
    digitalWrite(BIN2, HIGH);
  }

  analogWrite(PWMA, min(abs(left), 255) );
  analogWrite(PWMB, min(abs(right), 255) );
}

void gray_set(){ // 灰度iic初始化
  delay(200);
    //IIC set
  Wire.begin();

  //灰度传感器定义
  Wire.beginTransmission(0x4C);
  Wire.write(0xB0);
  Wire.endTransmission();
}

int gray_get(float *miss){ // 灰度获取
  float gray = 0.0;
  int num = 0;
  int left = 0, right = 0;
  Wire.requestFrom(0x4C, 8, 1);

  for (int i = 0; i < 8; ++i) {
    if(Wire.read() <= 64){
      if(i == 0)left++;
      if(i == 7)right++;
      num++;
      gray += 1.0*i - 3.5;
    }
  }

  if(!num)return 1; // 全白
  if(num>=4){
    if(left)return 2; //左
    if(right)return 3; //右
  }
  *miss = gray / num;
  return 0;
}

void PID::init(float kp, float ki, float kd, int n, float m, float im){
  KP = kp;
  KI = ki;
  KD = kd;
  num = n;
  max = m;
  imax = im;
  for(int i = 0; i < num; i++){
    miss[i] = 0;
    time[i] = millis();
    delay(10);
  }
}

float PID::compute(float miss_new){
  for(int i = 0; i < num-1; i++){
    miss[i] = miss[i+1];
    time[i] = time[i+1]; //迭代
  }
  miss[num-1] = miss_new;
  time[num-1] = millis();  // new data

  miss_i += miss_new*(time[num-1] - time[num-2])/1000;

  if(miss_i > fabs(imax))miss_i = fabs(imax);
  else if(miss_i < -fabs(imax))miss_i = -fabs(imax);

  miss_d = 1000.0*(miss[num-1] - miss[0])/(time[num-1] - time[0]); //计算 i值 d值
  delay(2);

  float out = KP*miss_new + KI*miss_i + KD*miss_d;
  if(out > fabs(max))return fabs(max);
  else if(out < -fabs(max))return -fabs(max);
  return out;
}

void Encoder::init(int pA, int pB){ // 初始化
  Adig = pA;
  Bdig = pB;
}

void Encoder::itrpt(){
  if(digitalRead(Adig) != digitalRead(Bdig))num++;
  else num--;
}
