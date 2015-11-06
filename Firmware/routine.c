/* Includes ------------------------------------------------------------------*/
#include "routine.h"

__IO uint32_t TimingDelay = 0;

/**
  * @brief  Led lamp
  * @param  none
  * @retval None
  */
void Led_lamp(void)
{
  /* Toggle LD3 */
  STM_EVAL_LEDToggle(LED3);
  /* Insert 50 ms delay */
  Delay(5);
  /* Toggle LD5 */
  STM_EVAL_LEDToggle(LED5);
  /* Insert 50 ms delay */
  Delay(5);
  /* Toggle LD7 */
  STM_EVAL_LEDToggle(LED7);
  /* Insert 50 ms delay */
  Delay(5);
  /* Toggle LD9 */
  STM_EVAL_LEDToggle(LED9);
  /* Insert 50 ms delay */
  Delay(5);
  /* Toggle LD10 */
  STM_EVAL_LEDToggle(LED10);
  /* Insert 50 ms delay */
  Delay(5);
  /* Toggle LD8 */
  STM_EVAL_LEDToggle(LED8);
  /* Insert 50 ms delay */
  Delay(5); 
  /* Toggle LD6 */
  STM_EVAL_LEDToggle(LED6);
  /* Insert 50 ms delay */
  Delay(5);
  /* Toggle LD4 */
  STM_EVAL_LEDToggle(LED4);
  /* Insert 50 ms delay */
  Delay(5);
}





/**
  * @brief  Inserts a delay time.
  * @param  nTime: specifies the delay time length, in 10 ms.
  * @retval None
  */
void Delay(__IO uint32_t nTime)
{
  TimingDelay = nTime;

  while(TimingDelay != 0);
}

/**
  * @brief  Decrements the TimingDelay variable.
  * @param  None
  * @retval None
  */
void TimingDelay_Decrement(void)
{
  if (TimingDelay != 0x00)
  { 
    TimingDelay--;
  }
}

/**
  * @brief  LED on / off
  * @param  status
  * @retval None
  */
void Led_all (uint8_t status)
{
  if (status == 0x00)
  {
    /* LEDs Off */
    STM_EVAL_LEDOff(LED3);
    STM_EVAL_LEDOff(LED6);
    STM_EVAL_LEDOff(LED7);
    STM_EVAL_LEDOff(LED4);
    STM_EVAL_LEDOff(LED10);
    STM_EVAL_LEDOff(LED8);
    STM_EVAL_LEDOff(LED9);
    STM_EVAL_LEDOff(LED5);
  }
  else
  {
    /* LEDs On */
    STM_EVAL_LEDOn(LED3);
    STM_EVAL_LEDOn(LED6);
    STM_EVAL_LEDOn(LED7);
    STM_EVAL_LEDOn(LED4);
    STM_EVAL_LEDOn(LED10);
    STM_EVAL_LEDOn(LED8);
    STM_EVAL_LEDOn(LED9);
    STM_EVAL_LEDOn(LED5);
  }
}


/**
  * @brief  init hardaware e periferiche
  * @param  None
  * @retval None
  */
void init_hardware(void)
{
  /* Initialize LEDs and User Button available on STM32F3-Discovery board */
  STM_EVAL_LEDInit(LED3);
  STM_EVAL_LEDInit(LED4);
  STM_EVAL_LEDInit(LED5);
  STM_EVAL_LEDInit(LED6);
  STM_EVAL_LEDInit(LED7);
  STM_EVAL_LEDInit(LED8);
  STM_EVAL_LEDInit(LED9);
  STM_EVAL_LEDInit(LED10);
  
  STM_EVAL_PBInit(BUTTON_USER, BUTTON_MODE_EXTI); 

  /* Configure the USB */
  init_USB();
  
  // aspetta la configurazione USB 
  // interrupt SysTick deve essere già abilitato 
  TimingDelay = 10;
  while (! ( (bDeviceState == CONFIGURED)&&(TimingDelay == 0x00) ) ){;};
}



/*
* @brief  Conversione da Hex a Ascii
*         es: 0x78A2 -> ascii ('7' + '8' + 'A' + '2')      
* @param  data = buffer IN in hex
* @param  tmp = buffer OUT con hex in ascii      
* @param  length = numero di byte da trasformare
* @retval None 
*/
void PrintHex(uint8_t *data, uint8_t *tmp, uint8_t length) 
{
  //uint8_t length = 12*Nsens;      
  uint8_t first ;
  int j=0;
  
  for (uint8_t i=0; i<length; i++) 
  {
    first = (data[i] >> 4) | 48;        //  prende i primi 4 bit e somma 48('0')       
    if (first > 57)                     // se non è un numero
      tmp[j] = first + (uint8_t)7;      // A B C D E F
    else 
      tmp[j] = first ;                  // numero 0 <= x <= 9
    j++;
    
    first = (data[i] & 0x0F) | 48;      // altri 4 bit
    if (first > 57)                     
      tmp[j] = first + (uint8_t)7; 
    else 
      tmp[j] = first;
    j++;
  }
}
