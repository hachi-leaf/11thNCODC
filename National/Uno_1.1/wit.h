#ifndef WIT_H
#define WIT_H

#include <Arduino.h>
#include <Wire.h>
#include <REG.h>
#include <wit_c_sdk.h>

#define ACC_UPDATE		0x01
#define GYRO_UPDATE		0x02
#define ANGLE_UPDATE	0x04
#define MAG_UPDATE		0x08
#define READ_UPDATE		0x80
static char s_cDataUpdate = 0, s_cCmd = 0xff;

static int32_t IICreadBytes(uint8_t dev, uint8_t reg, uint8_t *data, uint32_t length);

static int32_t IICwriteBytes(uint8_t dev, uint8_t reg, uint8_t* data, uint32_t length);

static void CopeSensorData(uint32_t uiReg, uint32_t uiRegNum);
void CopeCmdData(unsigned char ucData);

void wit_set();

int angle_get(float *angle);


#endif