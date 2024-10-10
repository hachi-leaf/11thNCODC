#include "Encoder.h"
#include "PID.h"
#include "wit.h"
#include "gray.h"
#include "ware.h"

#define EnA_L 3
#define EnB_L 5
#define EnA_R 2
#define EnB_R 6

#define MAIN_ while (1) {
#define _MAIN }

#define AND *10 +

#define LEFT 2
#define RIGHT 3
#define END 5
#define BACK 4
#define FIRE 6

#define NUM (( encoder_L.output()+encoder_R.output() ) >> 3)

Encoder_Two_num encoder_L, encoder_R;
Pos_PID along, rest_inside, rest_outside;

void turn_left();
void turn_right();
void order_read();
void left();
void right();
void back();

void setup() {
  along.init(42, 0, 1.88, 9, 144, 2);        //循迹pid初始化
  rest_inside.init(4, 14, 0.12, 5, 188, 8);  //转向内侧轮pid初始化
  rest_outside.init(45, 24, 1.2, 5, 255, 4);
  encoder_L.init(EnA_L, EnB_L);
  encoder_R.init(EnA_R, EnB_R);  //编码器初始化
  gray_set();                    //灰度初始化
  wit_set();                     //wit初始化

  Serial.begin(115200);

  attachInterrupt(digitalPinToInterrupt(EnA_L), num_com_l, CHANGE);  //中断服务 左
  attachInterrupt(digitalPinToInterrupt(EnA_R), num_com_r, CHANGE);  //中断服务 右
}

// unsigned char road[20] = { 1 AND LEFT,
//                            1 AND LEFT,
//                            1 AND RIGHT,
//                            1 AND RIGHT,
//                            1 AND LEFT,
//                            1 AND RIGHT,
//                            1 AND LEFT,
//                            1 AND LEFT,
//                            2 AND LEFT,
//                            1 AND BACK,
//                            1 AND RIGHT,
//                            6 AND RIGHT,
//                            2 AND LEFT,
//                            1 AND LEFT,
//                            2 AND RIGHT,
//                            1 AND END };  //出门左拐

// unsigned char road[20] = { 1 AND LEFT,
//                            1 AND LEFT,
//                            1 AND RIGHT,
//                            1 AND RIGHT,
//                            1 AND LEFT,
//                            1 AND RIGHT,
//                            1 AND LEFT,
//                            1 AND LEFT,
//                            2 AND LEFT,
//                            1 AND END};
//                           //  1 AND RIGHT,
//                           //  6 AND RIGHT,
//                           //  2 AND LEFT,
//                           //  1 AND LEFT,
//                           //  2 AND RIGHT,
//                           //  1 AND END };  //出门左拐

unsigned char gmode = 0;
unsigned char road[30] = { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                            0, 0, 0, 0, 0, 0, 0, 0, 0, 0};

unsigned char back_it = 0;

void loop() {
  unsigned char mode;
  float gray = 0;
  int al_pm;
  int run_num;
  unsigned char cap = 0;
  long time_begin;

  MAIN_
  order_read();
  // for(int i = 0; i < 30; i++){
  //   Serial.print(road[i]);
  // };Serial.println();
  if (gmode == 0) {  //待机模式
    ctrl(0, 0);
  }
  if(gmode == 2){
    delay(300);
    turn_left();
    encoder_L.set_num(0);
    encoder_R.set_num(0);
    gmode = 1;
  }
  if(gmode == 3){
    delay(300);
    turn_right();
    encoder_L.set_num(0);
    encoder_R.set_num(0);
    gmode = 1;
  }
  if(gmode == 4){
    ctrl(88,88);
    delay(350);
    ctrl(0,0);
    delay(100);
    back();
    encoder_L.set_num(0);
    encoder_R.set_num(0);
    gmode = 1;
  }
  if (gmode == 1) {  //正常行进模式
    mode = gray_get(&gray);
    if(NUM > 390 && back_it == 1){
      ctrl(0,0);
      back();
      for (int i = 0; i < 29; i++) {
        road[i] = road[i + 1];
      }
      back_it = 0;
    }

    if(road[0] % 10 == END){
      if(road[0] / 10 == 1 || NUM > (road[0] / 10 - 1)*390 ){
        Serial.write('e');
        time_begin = millis();
        while (millis() - time_begin < 450) {
          mode = gray_get(&gray);
          al_pm = (int)along.compute(gray);
          ctrl(0 + al_pm, 0 - al_pm);
        }
        ctrl(0, 0);
        delay(100);
        ctrl(-88, -84);
        delay(650);
        Serial.write('d');
        gmode = 0;
        encoder_L.num = 0;
        encoder_R.num = 0;
        continue;
      }
    }
    if(road[0]%10 == FIRE){
      Serial.write('e');
      mode = 0;
      while (mode == 0) {
        mode = gray_get(&gray);
        al_pm = (int)along.compute(gray);
        ctrl(144 + al_pm, 144 - al_pm);
      }
    }
    switch (mode) {
      case 0:  //检测到直线
        al_pm = (int)along.compute(gray);
        run_num = ((encoder_L.output() + encoder_R.output()) >> 3);
        if (road[0] / 10 != 1) {  //单复数格长判断
          // 前一段时间转先底速稳定
          while (run_num < 100) {
            run_num = ((encoder_L.output() + encoder_R.output()) >> 3);
            mode = gray_get(&gray);
            al_pm = (int)along.compute(gray);
            ctrl(120 + al_pm, 120 - al_pm);
          }
          // 前2/3段路程加速
          while (run_num < (road[0] / 10 - 1) * 390 * 2 / 3) {
            run_num = ((encoder_L.output() + encoder_R.output()) >> 3);
            mode = gray_get(&gray);
            al_pm = (int)along.compute(gray);
            ctrl(255 + al_pm, 255 - al_pm);
          }
          // 减速且忽略转弯节点
          while (run_num / 390 < road[0] / 10 - 1) {
            run_num = ((encoder_L.output() + encoder_R.output()) >> 3);
            mode = gray_get(&gray);
            al_pm = (int)along.compute(gray);
            ctrl(120 + al_pm, 120 - al_pm);
          }
        }
        ctrl(120 + al_pm, 120 - al_pm);  //普通循迹
        break;
      case 1:
        ctrl(0, 0);
        // delay(999999999);
        // break;
      case 2:
      case 3:                    //检测到转弯情况
        switch (road[0] % 10) {  //转弯方式
          case 4:
            if(NUM > 195 && back_it == 1){
              ctrl(0,0);
              back();
              for (int i = 0; i < 29; i++) {
                road[i] = road[i + 1];
              }
              back_it = 0;
            }
            break;
          case 2:
            turn_left();
            encoder_L.set_num(0);
            encoder_R.set_num(0);
            for (int i = 0; i < 29; i++) {
              road[i] = road[i + 1];
            }
            break;
          case 3:
            turn_right();
            encoder_L.set_num(0);
            encoder_R.set_num(0);
            for (int i = 0; i < 29; i++) {
              road[i] = road[i + 1];
            }
            break;
        }
        break;
    }
  }
  _MAIN
}

void num_com_l() {
  encoder_L.itrpt();
}  // 中断服务

void num_com_r() {
  encoder_R.itrpt();
}  // 中断服务

void order_read() {
  char s0, s1, s2;
  int i;
  while (Serial.available() > 0) {
    s1 = Serial.read();
    if (s1 == 'r' || s1 == 'z' || s1 == 'y' || s1 == 'b') {
      i = 0;
      delay(2);
      while (1) {
        s0 = Serial.read();
        delay(2);
        s2 = Serial.read();
        if (s2 == 'e' ) {
          road[i] = (s0 - '0') AND END;
          if(s1 == 'r')gmode = 1;
          else if(s1 == 'z')gmode = 2;
          else if(s1 == 'y')gmode = 3;
          else if(s1 == 'b')gmode = 4;
          break;
        }else if (s2 == 'f' ) {
          road[i] = (s0 - '0') AND FIRE;
          if(s1 == 'r')gmode = 1;
          else if(s1 == 'z')gmode = 2;
          else if(s1 == 'y')gmode = 3;
          else if(s1 == 'b')gmode = 4;
          break;
        } else if (s2 == 'l') {
          road[i] = (s0 - '0') AND LEFT;
        } else if (s2 == 'r') {
          road[i] = (s0 - '0') AND RIGHT;
        } else if (s2 == 'b') {
          road[i] = (s0 - '0') AND BACK;
          back_it = 1;
        }


        i++;
        delay(2);
      }
    }
    else if(s1 == 'g'){
      ctrl(127,127);
      delay(500);
    }
    delay(2);
  }
}

void turn_left() {
  float _;
  rest_inside.zero();
  rest_outside.zero();
  encoder_L.set_num(0);
  float angle_now, angle_exp, a_rts = 0;
  int pwm_inside, pwm_outside;

  while (!a_rts) {
    a_rts = angle_get(&angle_exp);
  }
  angle_exp = angle_cor(angle_exp + 75);

  while (1) {
    pwm_inside = (int)rest_inside.compute(1.0 * encoder_L.output());

    a_rts = angle_get(&angle_now);
    if (fabs(angle_cor(angle_exp - angle_now)) <= 15) {
      while (gray_get(&_) == 1) {
        delay(1);
      }
      return;
    }
    if (a_rts) pwm_outside = (int)rest_outside.compute(angle_cor(angle_exp - angle_now));
    else pwm_outside = 0;


    ctrl(-pwm_inside, pwm_outside);  //内侧轮固定
  }
}

void turn_right() {
  float _;
  rest_inside.zero();
  rest_outside.zero();
  encoder_R.set_num(0);
  float angle_now, angle_exp, a_rts = 0;
  int pwm_inside, pwm_outside;

  while (!a_rts) {
    a_rts = angle_get(&angle_exp);
  }
  angle_exp = angle_cor(angle_exp - 75);

  while (1) {
    pwm_inside = (int)rest_inside.compute(1.0 * encoder_R.output());

    a_rts = angle_get(&angle_now);
    if (fabs(angle_cor(angle_exp - angle_now)) <= 15) {
      while (gray_get(&_) == 1) {
        delay(1);
      }
      return;
    }
    if (a_rts) pwm_outside = (int)rest_outside.compute(angle_cor(angle_exp - angle_now));
    else pwm_outside = 0;

    ctrl(-pwm_outside, -pwm_inside);  //内侧轮固定
  }
}

void back() {
  long time_begin = millis();
  int back_mode;
  float miss;
  back_it = 0;
  ctrl(120, 120);
  delay(100);
  encoder_R.set_num(390 * 7 /2);
  encoder_L.set_num(0);
  while (1) {
    ctrl(-rest_inside.compute(1.0 * encoder_L.output()), -rest_inside.compute(1.0 * encoder_R.output()));
    if (abs(encoder_L.output()) <= 39 && abs(encoder_R.output()) <= 39) {
      break;
    }
  }
  ctrl(127, 0);
  delay(300);
  encoder_R.set_num(0);
  while (1) {
    back_mode = gray_get(&miss);
    if (gray_get(&miss) == 0) {
      ctrl(0, 0);
      return;
    }
  }
}