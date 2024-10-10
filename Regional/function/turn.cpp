//左转turn_plus(2, -255, 0, 280, 360, 430, -64, 75, 250, 120, 64, 25.6, 8.8, 32);
//右转turn_plus(3, 0, -255, 280, 360, 430, 75, -64, 250, 120, 64, 25.6, 8.8, 32);
//掉头turn_plus(2, -255, -255, 280, 360, 430, 48, -48, 820, 120, 64, 25.6, 8.8, 32);
//循迹along(127,miss,28,0,48);
void turn_plus(
  int mode, // turn模式
  int vb_left, 
  int vb_right, //刹车左右速度
  int dtime1,
  int dtime2,
  int dtime3, //3种刹车相隔时间的刹车持续时间
  int vt_left, 
  int vt_right, //僵直转向左右速度
  int ttime, //僵直时间
  int pidtime, //pid灰度矫正时间
  int vp, //pid基准速度
  float KP, 
  float KI,
  float KD // pid参数
  ){

  if(mode == 1){
    ctrl(vb_left,vb_right);
    delay(dtime1);
    turn_time = millis();
    return ;
  }//直走不转弯

  else ctrl(vb_left,vb_right);//刹车

  switch((millis()-turn_time)/500){//拐弯相隔时间
    case 0:
      delay(dtime1);//时间1
      break;
    case 1:case 2:
      delay(dtime2);//时间2
      break;
    default:
      delay(dtime3);//时间3
      break;
  }

  ctrl(vt_left,vt_right);
  delay(ttime);//僵直转向

  int tmode = 1;float tmiss;
  for(;;){
    if(tmode == 0)break;
    else tmode = gray_decide(&tmiss);
  }// 等待僵直转向到黑线

  zero_turn();//pid格式化
  long gray0_time = millis();
  while(millis() - gray0_time < pidtime){
    tmode = gray_decide(&tmiss);
    if(tmode==0){
      Serial.println(gray0_time);
      if(tmiss > 1 || tmiss < -1)gray0_time = millis();//打断计时
      for(int i = 0; i < 4; i++){
        pid_turn.miss_his[i] = pid_turn.miss_his[i+1];
        pid_turn.time_his[i] = pid_turn.time_his[i+1];
      }
      pid_turn.miss_his[4] = tmiss;
      pid_turn.time_his[4] = millis(); //pid迭代

      pid_turn.miss_i += (pid_turn.miss_his[4]-pid_turn.miss_his[3]) * (pid_turn.time_his[4]-pid_turn.time_his[3]) / 1000;
      float tmiss_d = 1000 * (pid_turn.miss_his[4]-pid_turn.miss_his[0]) / (pid_turn.time_his[4]-pid_turn.time_his[0]);
      int tmiss_m = (int)(KP * tmiss + KI * pid_turn.miss_i + KD * tmiss_d);
      ctrl(vp - tmiss_m, vp + tmiss_m); //pid参数输出
      turn_time = millis();
    }else gray0_time = millis();  //打断计时
  }
}
