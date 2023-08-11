#include"ware.h"

PID along,rest;
Encoder encoder;

void setup(){
  along.init(24,0,0.009,5,255,999999999);
  rest.init(24, 16, 0.16, 5, 127,8);
  encoder.init(EnA_L,EnB_L);

  Serial.begin(115200);
  gray_set();

  attachInterrupt(digitalPinToInterrupt(EnA_L), num_com, CHANGE);
}



void loop(){
  /*
  float miss = 0;
  float mpwm;
  int mode = gray_get(&miss);
  if(mode!=1){
    mpwm = along.compute(miss);
    ctrl(127+mpwm,127-mpwm);
  }
  else if(mode==2){
    ctrl(0,200);
    delay(260);
  }
  else if(mode==3){
    ctrl(200,0);
    delay(260);
  }
  else ctrl(0,0);
  */
  int mpwm;
  while(1){
  mpwm = (int)rest.compute(encoder.num);
  ctrl(-mpwm,0);
  Serial.println(encoder.num/10);
  }
}

void num_com(){encoder.itrpt();}

