#ifndef GRAY_H
#define GRAY_H

#include<Arduino.h>
#include "gw_grayscale_sensor.h"

void gray_set(){ // 灰度iic初始化
  delay(100);
    //IIC set
  Wire.begin();

  //灰度传感器定义
  Wire.beginTransmission(0x4C);
  Wire.write(0xB0);
  Wire.endTransmission();
}

// int gray_get(float &miss)
int gray_get(float *miss){ // 灰度获取
  float gray = 0.0;
  int num = 0;
  int left = 0, right = 0;
  Wire.requestFrom(0x4C, 8, 1);

  for (int i = 0; i < 8; ++i) {
    if(Wire.read() <= 48){
      if(i == 0 )left++;
      if(i == 7 )right++;
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


#endif