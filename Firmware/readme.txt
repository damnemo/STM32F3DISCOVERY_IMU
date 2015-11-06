/*
  ******************** PROJECT by Damiano Lollini *******************
  * @name    IMU 
  * @author  Damiano Lollini
  * @version V1.0
  * @date    8-OTTOBRE-2015
  * @brief   Invio di dati IMU con STM32F3DISCO
  ******************************************************************************
 */
 
 @par Description:
 -----------------
 Invio dati compass e gyro, premere user-button per inviare o stoppare l'invio
 di dati
 
 
 @par Directory contents:
 ------------------------
 LIBRERIA:      STM32F3-Discovery_FW_V1.1.0
 
 
 @par Hardware and Software environment:
 ---------------------------------------
 Board    -     STM32F3-Discovery
 Software -     IDE Ewarm.
 
 
 I2C - COMPASS
 ---------
 I2C    I2C1
 SCL    PB.6
 SDA    PB.7
 PE.5
 PE.4
 
 
  SPI - GYRO
 ---------
 SPI     SPI1
 SCK     PA.5
 MOSI    PA.7
 MISO    PA.6
 PE3
 PE1
 PE0
 
 
 USB
 ---------
 D+     PA.12
 D-     PA.11 
 
 
  @par Note:
 -----------------
 
 setup sensori:
    FONDOSCALA
    gyro             = 500 dps
    magnetometro     = 8.1 Gauss
    accelerometro    = 2 G
 
    SENSITIVITY per un dato fondoscala
    sens_mag = 205      # ±8.1 gauss
    sens_acc = 16	# ±2 g , già in mg
    sens_gyro = 17.5	# ±500 mdps/digit
 
   # ACC = (1/SENSITIVITY)* (REG)/16 (12 bit rappresentation)   [mg]
   # MAG = (REG) / SENSITIVITY                                  [mgauss]
   # GYRO = (REG) / SENSITIVITY                                 [mdps]
 
 
 
 BOARD -> PC
 -----------------
  // stringa da inviare
  // in hex -> gyro(2x,2y,2z) + compass(2x,2y,2z,2x,2y,2z)
  pacchetto = # + gyro + acc + mag + \n = 38 byte

 ES:
  #002BFF7AFFC21C80F78037B0FFA0FFD6FFB3
  #019FFC3DFF9824D0F3A04150FFA1FFD6FFB3
  #0374F9B5FCA82190FA1041F0FFA2FFD4FFB3
  #F79CF25DFAD11F90FA504420FFA1FFCEFFB6
 
 
 