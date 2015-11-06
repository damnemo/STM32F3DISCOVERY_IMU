/* Includes ------------------------------------------------------------------*/
#include "sens.h"

/**
  * @brief  Configure the Mems to gyroscope application.
  * @param  None
  * @retval None
  */
void init_GyroConfig(void)
{
  L3GD20_InitTypeDef L3GD20_InitStructure;
  L3GD20_FilterConfigTypeDef L3GD20_FilterStructure;
  
  /* Configure Mems L3GD20 */
  L3GD20_InitStructure.Power_Mode = L3GD20_MODE_ACTIVE;
  L3GD20_InitStructure.Output_DataRate = L3GD20_OUTPUT_DATARATE_1;
  L3GD20_InitStructure.Axes_Enable = L3GD20_AXES_ENABLE;
  L3GD20_InitStructure.Band_Width = L3GD20_BANDWIDTH_4;
  L3GD20_InitStructure.BlockData_Update = L3GD20_BlockDataUpdate_Continous;
  L3GD20_InitStructure.Endianness = L3GD20_BLE_LSB;
  L3GD20_InitStructure.Full_Scale = L3GD20_FULLSCALE_500; 
  L3GD20_Init(&L3GD20_InitStructure);
   
  L3GD20_FilterStructure.HighPassFilter_Mode_Selection =L3GD20_HPM_NORMAL_MODE_RES;
  L3GD20_FilterStructure.HighPassFilter_CutOff_Frequency = L3GD20_HPFCF_0;
  L3GD20_FilterConfig(&L3GD20_FilterStructure) ;
  
  L3GD20_FilterCmd(L3GD20_HIGHPASSFILTER_ENABLE);
}



/**
  * @brief  Configure the Mems to compass application.
  * @param  None
  * @retval None
  */
void init_CompassConfig(void)
{
  LSM303DLHCMag_InitTypeDef LSM303DLHC_InitStructure;
  LSM303DLHCAcc_InitTypeDef LSM303DLHCAcc_InitStructure;
  LSM303DLHCAcc_FilterConfigTypeDef LSM303DLHCFilter_InitStructure;
  
  /* Configure MEMS magnetometer main parameters: temp, working mode, full Scale and Data rate */
  LSM303DLHC_InitStructure.Temperature_Sensor = LSM303DLHC_TEMPSENSOR_DISABLE;
  LSM303DLHC_InitStructure.MagOutput_DataRate =LSM303DLHC_ODR_30_HZ ;
  LSM303DLHC_InitStructure.MagFull_Scale = LSM303DLHC_FS_8_1_GA;
  LSM303DLHC_InitStructure.Working_Mode = LSM303DLHC_CONTINUOS_CONVERSION;
  LSM303DLHC_MagInit(&LSM303DLHC_InitStructure);
  
   /* Fill the accelerometer structure */
  LSM303DLHCAcc_InitStructure.Power_Mode = LSM303DLHC_NORMAL_MODE;
  LSM303DLHCAcc_InitStructure.AccOutput_DataRate = LSM303DLHC_ODR_50_HZ;
  LSM303DLHCAcc_InitStructure.Axes_Enable= LSM303DLHC_AXES_ENABLE;
  LSM303DLHCAcc_InitStructure.AccFull_Scale = LSM303DLHC_FULLSCALE_2G;
  LSM303DLHCAcc_InitStructure.BlockData_Update = LSM303DLHC_BlockUpdate_Continous;
  LSM303DLHCAcc_InitStructure.Endianness=LSM303DLHC_BLE_LSB;
  LSM303DLHCAcc_InitStructure.High_Resolution=LSM303DLHC_HR_ENABLE;
  /* Configure the accelerometer main parameters */
  LSM303DLHC_AccInit(&LSM303DLHCAcc_InitStructure);
  
  /* Fill the accelerometer LPF structure */
  LSM303DLHCFilter_InitStructure.HighPassFilter_Mode_Selection =LSM303DLHC_HPM_NORMAL_MODE;
  LSM303DLHCFilter_InitStructure.HighPassFilter_CutOff_Frequency = LSM303DLHC_HPFCF_16;
  LSM303DLHCFilter_InitStructure.HighPassFilter_AOI1 = LSM303DLHC_HPF_AOI1_DISABLE;
  LSM303DLHCFilter_InitStructure.HighPassFilter_AOI2 = LSM303DLHC_HPF_AOI2_DISABLE;

  /* Configure the accelerometer LPF main parameters */
  LSM303DLHC_AccFilterConfig(&LSM303DLHCFilter_InitStructure);
}



/*****************************************/

void read_Compass2(uint8_t *pt_compass)
{
  uint8_t compass_temp[12] ={0};                // da 0..5 acc, da 6..11 mag
  
  LSM303DLHC_Read(ACC_I2C_ADDRESS,LSM303DLHC_OUT_X_L_A,&compass_temp[0], 6);
  LSM303DLHC_Read(MAG_I2C_ADDRESS,LSM303DLHC_OUT_X_H_M,&compass_temp[6], 6);

  /* dati accelerometro */
  /* da LittleEndian -> BigEndian ,buff[]=0x28,0xA3 -> buff[]=0xA3,0X28*/
  for(uint8_t j=0; j<3; j++)
  {
    pt_compass[j*2]= compass_temp[2*j+1];
    pt_compass[j*2+1]= compass_temp[2*j];
  } 
  
  /* dati magnetometro */
  /* swap da x,z,y -> x,y,z */
  /* i dati del magnetometro sono già in BigEndian*/
  pt_compass[6]= compass_temp[6];
  pt_compass[7]= compass_temp[7];
  pt_compass[8]= compass_temp[10];
  pt_compass[9]= compass_temp[11];
  pt_compass[10]= compass_temp[8];
  pt_compass[11]= compass_temp[9];
}



void read_GyroAngRate2(uint8_t *pt_gyro)
{
  uint8_t gyro_temp[6] ={0};
  
  L3GD20_Read(gyro_temp,L3GD20_OUT_X_L_ADDR,6);
  
  /* LittleEndian buff[]=0x28,0xA3 -> buff[]=0xA3,0X28*/
  for(uint8_t j=0; j<3; j++)
  {
    pt_gyro[j*2]= gyro_temp[2*j+1];
    pt_gyro[j*2+1]= gyro_temp[2*j];
  } 
}