#include "wit.h"

static int32_t IICreadBytes(uint8_t dev, uint8_t reg, uint8_t *data, uint32_t length) {
  int val;
  Wire.beginTransmission(dev);
  Wire.write(reg);
  Wire.endTransmission(false);  //endTransmission but keep the connection active

  val = Wire.requestFrom(dev, length);  //Ask for bytes, once done, bus is released by default

  if (val == 0) return 0;
  while (Wire.available() < length)  //Hang out until we get the # of bytes we expect
  {
    if (Wire.getWireTimeoutFlag()) {
      Wire.clearWireTimeoutFlag();
      return 0;
    }
  }

  for (int x = 0; x < length; x++) data[x] = Wire.read();

  return 1;
}


static int32_t IICwriteBytes(uint8_t dev, uint8_t reg, uint8_t *data, uint32_t length) {
  Wire.beginTransmission(dev);
  Wire.write(reg);
  Wire.write(data, length);
  if (Wire.getWireTimeoutFlag()) {
    Wire.clearWireTimeoutFlag();
    return 0;
  }
  Wire.endTransmission();  //Stop transmitting

  return 1;
}

static void CopeSensorData(uint32_t uiReg, uint32_t uiRegNum) {
  int i;
  for (i = 0; i < uiRegNum; i++) {
    switch (uiReg) {
      case AZ:
        s_cDataUpdate |= ACC_UPDATE;
        break;
      case GZ:
        s_cDataUpdate |= GYRO_UPDATE;
        break;
      case HZ:
        s_cDataUpdate |= MAG_UPDATE;
        break;
      case Yaw:
        s_cDataUpdate |= ANGLE_UPDATE;
        break;
      default:
        s_cDataUpdate |= READ_UPDATE;
        break;
    }
    uiReg++;
  }
}

void wit_set() {
  Wire.begin();
  Wire.setClock(400000);
  WitI2cFuncRegister(IICwriteBytes, IICreadBytes);
  WitRegisterCallBack(CopeSensorData);
  WitInit(WIT_PROTOCOL_I2C, 0x28);
}

int angle_get(float *angle) {
  *angle = NULL;
  int returnm = 0;
  WitReadReg(AX, 12);
      while (Serial.available()) 
    {
      CopeCmdData(Serial.read());
    }
  float fAcc[3], fGyro[3], fAngle[3];
  if (s_cDataUpdate) {
    for (int i = 0; i < 3; i++) {
      fAcc[i] = sReg[AX + i] / 32768.0f * 16.0f;
      fGyro[i] = sReg[GX + i] / 32768.0f * 2000.0f;
      fAngle[i] = sReg[Roll + i] / 32768.0f * 180.0f;
    }
    if (s_cDataUpdate & ACC_UPDATE) {
      // Serial.print("acc:");
      // Serial.print(fAcc[0], 3);
      // Serial.print(" ");
      // Serial.print(fAcc[1], 3);
      // Serial.print(" ");
      // Serial.print(fAcc[2], 3);
      // Serial.print("\r\n");
      s_cDataUpdate &= ~ACC_UPDATE;
    }
    if (s_cDataUpdate & GYRO_UPDATE) {
      // Serial.print("gyro:");
      // Serial.print(fGyro[0], 1);
      // Serial.print(" ");
      // Serial.print(fGyro[1], 1);
      // Serial.print(" ");
      // Serial.print(fGyro[2], 1);
      // Serial.print("\r\n");
      s_cDataUpdate &= ~GYRO_UPDATE;
    }
    if (s_cDataUpdate & ANGLE_UPDATE) {
      // Serial.print("angle:");
      // Serial.print(fAngle[0], 3);
      // Serial.print(" ");
      // Serial.print(fAngle[1], 3);
      // Serial.print(" ");
      // Serial.print(fAngle[2], 3);
      // Serial.print("\r\n");
      *angle = fAngle[2];
      returnm = 1;
      s_cDataUpdate &= ~ANGLE_UPDATE;
    }
    if (s_cDataUpdate & MAG_UPDATE) {
      // Serial.print("mag:");
      // Serial.print(sReg[HX]);
      // Serial.print(" ");
      // Serial.print(sReg[HY]);
      // Serial.print(" ");
      // Serial.print(sReg[HZ]);
      // Serial.print("\r\n");
      s_cDataUpdate &= ~MAG_UPDATE;
    }
    s_cDataUpdate = 0;
  }
  return returnm;
}

void CopeCmdData(unsigned char ucData)
{
	static unsigned char s_ucData[50], s_ucRxCnt = 0;
	
	s_ucData[s_ucRxCnt++] = ucData;
	if(s_ucRxCnt<3)return;										//Less than three data returned
	if(s_ucRxCnt >= 50) s_ucRxCnt = 0;
	if(s_ucRxCnt >= 3)
	{
		if((s_ucData[1] == '\r') && (s_ucData[2] == '\n'))
		{
			s_cCmd = s_ucData[0];
			memset(s_ucData,0,50);
			s_ucRxCnt = 0;
		}
		else 
		{
			s_ucData[0] = s_ucData[1];
			s_ucData[1] = s_ucData[2];
			s_ucRxCnt = 2;
			
		}
	}
}