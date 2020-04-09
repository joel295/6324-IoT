float ntu;
float voltage;
float vclear = 4.50; //base voltage for clear water..


void setup() {
  Serial.begin(9600);
  Serial.println("CLEARDATA"); //clears up any data left from previous projects
  Serial.println("LABEL,NTU"); //always write LABEL, so excel knows the next things will be the names of the columns (instead of Acolumn you could write Time for instance)
  Serial.println("RESETTIMER"); //resets timer to 0

}
void loop() {
  voltage = 0;
  for(int i=0;i<800;i++)
  {
      int sensorValue = analogRead(A1);
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
  Serial.println ("Sensor Output (NTU):");https://forum.arduino.cc/index.php?topic=437398.0
  //Serial.println (voltage);
  Serial.println (ntu);
  Serial.println();
  delay(1000);
}

float round_to_dp(float in_value, int decimal_place)
{
  float mult = powf(10.0f,decimal_place);
  in_value = round(in_value*mult)/mult;
  return in_value;
}
