# include "ware.h"

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

float angle_cor(float angle_){
  float angle = angle_;
  while(angle>180){
    angle -= 360;
  }
  while(angle<-180){
    angle += 360;
  }
  return angle;
}
