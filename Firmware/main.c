/**
  ******************************************************************************
  * @file    main.c 
  * @author  MCD Application Team
  * @version V1.1.0
  * @date    20-September-2012
  * @brief   Main program body
  ******************************************************************************
  * @attention
  *
  * <h2><center>&copy; COPYRIGHT 2012 STMicroelectronics</center></h2>
  *
  * Licensed under MCD-ST Liberty SW License Agreement V2, (the "License");
  * You may not use this file except in compliance with the License.
  * You may obtain a copy of the License at:
  *
  *        http://www.st.com/software_license_agreement_liberty_v2
  *
  * Unless required by applicable law or agreed to in writing, software 
  * distributed under the License is distributed on an "AS IS" BASIS, 
  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  * See the License for the specific language governing permissions and
  * limitations under the License.
  *
  ******************************************************************************
  */


/* Includes ------------------------------------------------------------------*/
#include "main.h"

  
/* Private variables ---------------------------------------------------------*/
  RCC_ClocksTypeDef RCC_Clocks;
__IO uint32_t UserButtonPressed = 0;


// per i dati in hex
// gyro(2x,2y,2z) + compass(2x,2y,2z,2x,2y,2z)
// 6 gyro + 12 compass = 18 byte
uint8_t pack_dati[18];

// stringa da inviare
// 1 marker + pack_dati*2 + 1 marker = 38 byte
uint8_t pack_dati_ascii[38] = {[0]='#',[37]='\n'};



// usb var
extern __IO uint8_t Receive_Buffer[64];
extern __IO  uint32_t Receive_length ;
extern __IO  uint32_t length ;
uint8_t Send_Buffer[64];
__IO uint32_t packet_sent=1;
__IO uint32_t packet_receive=1;


/**
  * @brief  Main program.
  * @param  None 
  * @retval None
  */
int main(void)
{  
  /* SysTick end of count event each 10ms */
  RCC_GetClocksFreq(&RCC_Clocks);
  SysTick_Config(RCC_Clocks.HCLK_Frequency / 100);
  
  init_hardware();

  /* Reset UserButton_Pressed variable */
  UserButtonPressed = 0x00; 
   
  /* Demo Gyroscope */
  init_GyroConfig();
  
  /* Demo Compass */
  init_CompassConfig();
  
  
  /* Infinite loop */
  while (1)
  {   

    
    /* Waiting User Button is pressed */
    while (UserButtonPressed == 0x00)
    {
      Led_lamp();
    }


    
    /* Waiting User Button is pressed */
    while (UserButtonPressed == 0x01)
    {
      Delay(5);
      
      Led_all(0xFF);
      
      /* Read Gyro Angular data 6 byte */
      read_GyroAngRate2(&pack_dati[0]);
      /* Read Compass data 12 byte */
      read_Compass2(&pack_dati[6]);  
      
      /* converte i 18 byte dati in 36 byte ascii */
      /* pack_dati_ascii in totale è 38, compresi i 2 marker */
      PrintHex(&pack_dati[0],&pack_dati_ascii[1],18);
      
      /* se l'usb è riconosciuta dal pc esegue questa istruzione */
      if (bDeviceState == CONFIGURED)
      {
        CDC_Send_DATA2(&pack_dati_ascii[0], 38);
      }
    }
  }
  
  
}






#ifdef  USE_FULL_ASSERT

/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t* file, uint32_t line)
{ 
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */

  /* Infinite loop */
  while (1)
  {
  }
}
#endif

/**
  * @}
  */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
