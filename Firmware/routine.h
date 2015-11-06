#ifndef ROUTINE_H_
#define ROUTINE_H_

#include "main.h"


void TimingDelay_Decrement(void);
void Delay(__IO uint32_t nTime);
void Led_lamp(void);
void Led_all (uint8_t status);
void init_hardware(void);
void PrintHex(uint8_t *data, uint8_t *tmp, uint8_t length);


#endif /* ROUTINE_H_ */