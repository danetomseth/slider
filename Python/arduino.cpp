#define slide 2
#define pan 3
#define tilt 4



void setup() {
  Serial.begin(9600);
  pinMode(slide, OUTPUT);
  pinMode(pan, OUTPUT);
  pinMode(tilt, OUTPUT);
}
 
int integerValue=0; 
unsigned long serialdata;
int inbyte;
char serialChar= 0; 
 
                              // Max value is 65535
char incomingByte;



void loop()
{
  if (Serial.available() >0){          // Check receive buffer.
    serialChar = Serial.read();            // Save character received. 
    Serial.flush();                    // Clear receive buffer.
  
  switch (serialChar) {
    
    case 't':
    case 'T':                          // If received 'a' or 'A':
      // Serial.println("TILT");
      getSerial();
      moveMotor(tilt);
        break;

    case 'p':
    case 'P':                          // If received 'd' or 'D':
      // Serial.println("PAN");
      getSerial();
      moveMotor(pan); 
        break;
        
    case 's':
    case 'S':                          // If received  's' or 'S':
      // Serial.println("SLIDE");
      getSerial();
      moveMotor(slide);
        break;
        
        
    default:                           
      Serial.print("'");
      Serial.print((char)serialChar);
      Serial.println("' is not a command!");
    }
  }
  
}


long getSerial()
{
  serialdata = 0;
  while (inbyte != '/')
  {
    inbyte = Serial.read();  
    if (inbyte > 0 && inbyte != '/')
    { 
      serialdata = serialdata * 10 + inbyte - '0';
      // Serial.println(serialdata);
    }
  }
  inbyte = 0;
  return serialdata;
  
}


void slide_high(){
  digitalWrite(slide, HIGH);
}

void slide_low(){
  digitalWrite(slide, LOW);
}


void tilt_high(){
  digitalWrite(tilt, HIGH);
}

void tilt_low(){
  digitalWrite(tilt, LOW);
}


void pan_high(){
  digitalWrite(pan, HIGH);
}

void pan_low(){
  digitalWrite(pan, LOW);
}




void moveMotor(int motor){
  int count = 0;
  switch(motor){
    case slide:
      while(Serial.available() == 0) {
          slide_high();
          delay(serialdata);
          slide_low();
          delay(serialdata);
          count++;
        }
      break;
    case pan:
      while(Serial.available() == 0) {
          pan_high();
          delay(serialdata);
          pan_low();
          delay(serialdata);
          count++;
        }
      break;
    case tilt:
      while(Serial.available() == 0) {
          tilt_high();
          delay(serialdata);
          tilt_low();
          delay(serialdata);
          count++;
        }
      break;
    default:
      Serial.println("INVALID MOTOR");
      break;
      

  }
  
  Serial.println(count);
  
  
}

// void getMotor(){
//   switch(serialdata)
//   {
//   case 1:
//     {
//       //analog digital write
//       getSerial();
//       switch (serialdata)
//       {
//       case 1:
//         {
//           //analog write
//           getSerial();
//           pinNumber = serialdata;
//           getSerial();
//           analogRate = serialdata;
//           pinMode(pinNumber, OUTPUT);
//           analogWrite(pinNumber, analogRate);
//           pinNumber = 0;
//           break;
//         }
//       case 2:
//         {
//           //digital write
//           getSerial();
//           pinNumber = serialdata;
//           getSerial();
//           digitalState = serialdata;
//           pinMode(pinNumber, OUTPUT);
//           if (digitalState == 1)
//           {
//             digitalWrite(pinNumber, LOW);
//           }
//           if (digitalState == 2)
//           {
//             digitalWrite(pinNumber, HIGH);
//           }
//           pinNumber = 0;
//           break;
         
//         }
//      }
//      break; 
//     }
//     case 2:
//     {
//       getSerial();
//       switch (serialdata)
//       {
//       case 1:
//         {
//           //analog read
//           getSerial();
//           pinNumber = serialdata;
//           pinMode(pinNumber, INPUT);
//           sensorVal = analogRead(pinNumber);
//           Serial.println(sensorVal);
//           sensorVal = 0;
//           pinNumber = 0;
//           break;
//         } 
//       case 2:
//         {
//           //digital read
//           getSerial();
//           pinNumber = serialdata;
//           pinMode(pinNumber, INPUT);
//           sensorVal = digitalRead(pinNumber);
//           Serial.println(sensorVal);
//           sensorVal = 0;
//           pinNumber = 0;
//           break;
//         }
//       }
//       break;
//     }
//   }
// }
// void first_menu(int x) {
//   Serial.println("IN MENU");
//   digitalWrite(led,HIGH); //Trigger one step
//   Serial.println(x);
//    switch (x) {
//     case 1:
//       Serial.println("Pulse");
//       integerValue = 0;
//       pulse();
//       break;
//     case 2:
//       //do something when var equals 2
//       Serial.println("TWO");
//       break;
//     default: 
//       Serial.println("DEFAULT");
//       // if nothing else matches, do the default
//       // default is optional
//     break;
//   }
// }


// void pulse() {
//   Serial.println("ENTER RATE");
//   digitalWrite(led,LOW); //Trigger one step
//   while(1) {            // force into a loop until 'n' is received
//       incomingByte = Serial.read();
//       if (incomingByte == '\n') break;   // exit the while(1), we're done receiving
//       if (incomingByte == 'x') break;
//       if (incomingByte == -1) continue;  // if no characters are in the buffer read() returns -1
//       integerValue *= 10;  // shift left 1 decimal place
//       // convert ASCII to integer, add, and shift left 1 decimal place
//       integerValue = ((incomingByte - 48) + integerValue);
//     }

//     // float motor_speed = 1.0 / integerValue;
//     // Serial.println(motor_speed,6);
//     Serial.println(integerValue);
//   digitalWrite(led,HIGH); //Trigger one step
//   digitalWrite(ena,HIGH); //Trigger one step
//   while(Serial.available() == 0) {
//     digitalWrite(stp,HIGH); //Trigger one step
//     delayMicroseconds(integerValue);
//     digitalWrite(stp,LOW); //Pull step pin low so it can be triggered again
//     delayMicroseconds(integerValue);
//   }
//   digitalWrite(led,LOW); //Trigger one step
//   digitalWrite(ena,LOW); //Trigger one step
//   Serial.println("FINISHED");
  
// }