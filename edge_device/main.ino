
#include <OneWire.h>
#include <DallasTemperature.h>
#include <EEPROM.h>
#include <GravityTDS.h>

#define TdsSensorPin A1

const int SENSOR_PIN = 13; // Arduino pin connected to DS18B20 sensor's DQ pin
float tdsValue = 0;
OneWire oneWire(SENSOR_PIN);    
GravityTDS gravityTds;
DallasTemperature sensors(&oneWire);
float Celcius=0;
float ntu;
float voltage;
float vclear = 4.50; //base voltage for clear water..

void setup() {


  Serial.begin(9600);
  gravityTds.setPin(TdsSensorPin);
  gravityTds.setAref(5.0);  //reference voltage on ADC, default 5.0V on Arduino UNO
  gravityTds.setAdcRange(1024);  //1024 for 10bit ADC;4096 for 12bit ADC
  //initialization
  gravityTds.begin();
  sensors.begin();
  Serial.print("Temperature(C), ");
  Serial.print("Turbidity(ntu), ");
  Serial.println("TDS(ppm)");

  // put your setup code here, to run once:

}

void loop() {

  //Temperature

  sensors.requestTemperatures(); 
  Celcius=sensors.getTempCByIndex(0);

  Serial.print(Celcius);
  Serial.print(", ");


  // turbidity
  voltage = 0;
  for(int i=0;i<800;i++)
  {
      int sensorValue = analogRead(A2);
      voltage += sensorValue * (5.0 / 1024.0);
  }
  voltage = voltage/800;
  voltage = round_to_dp(voltage,1);
  if (voltage<1.0)
  {
    ntu = 3000; //max NTU value, umpure water.
  }
  else
  {
    ntu = -1120.4*square(voltage)+5742.3*voltage-3152.25;
  }
  Serial.print(ntu);
  Serial.print(", ");

  //tds

  gravityTds.setTemperature(Celcius);  // set the temperature and execute temperature compensation
  gravityTds.update();  //sample and calculate
  tdsValue = gravityTds.getTdsValue();  // then get the value
  Serial.println(tdsValue,0);
  
  delay(2000);
}


float round_to_dp(float in_value, int decimal_place)
{
  float mult = powf(10.0f,decimal_place);
  in_value = round(in_value*mult)/mult;
  return in_value;
}
