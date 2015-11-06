#ifndef SENS_H_
#define SENS_H_

/* include sensori */
#include "stm32f3_discovery_lsm303dlhc.h"
#include "stm32f3_discovery_l3gd20.h"

void init_GyroConfig(void);
void init_CompassConfig(void);

void read_Compass2(uint8_t *pt_compass);
void read_GyroAngRate2(uint8_t* pt_gyro);


#endif