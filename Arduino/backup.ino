#include <AccelStepper.h>
#include <MultiStepper.h>


int enable_pin = 8;
unsigned long serialdata;
unsigned long SpeedX;
unsigned long SpeedY;
unsigned long SpeedZ;
int inbyte;
int servoPin;

int pinNumber;
int sensorVal;
int analogRate;
int digitalState;
int total_steps;

int stop_status = 0;

int analogX = 10;
int analogY = 9;
int analogZ = 8;

#define  MAX_SPEED 8000
#define  MIN_SPEED 0.1
#define analog_neutral 512
#define analog_zero 30
#define stop_button 40
#define shutter 43

#define x_limit 9
#define y_limit 10 
#define z_limit 11

AccelStepper stepperX(AccelStepper::DRIVER, 2, 5);
AccelStepper stepperY(AccelStepper::DRIVER, 3, 6);
AccelStepper stepperZ(AccelStepper::DRIVER, 4, 7);

void setup()
{
  Serial.begin(9600);
  pinMode(enable_pin, OUTPUT);
  pinMode(shutter, OUTPUT);
  pinMode(stop_button, INPUT);

  pinMode(x_limit, INPUT_PULLUP);
  pinMode(y_limit, INPUT_PULLUP);
  pinMode(z_limit, INPUT_PULLUP);

  digitalWrite(enable_pin, HIGH);
  digitalWrite(shutter, LOW);
  stepperY.setMaxSpeed(6000);
  stepperY.setAcceleration(1000);
  stepperZ.setMaxSpeed(6000);
  stepperZ.setAcceleration(1000);
  stepperX.setMaxSpeed(7000);
  stepperX.setAcceleration(200);
}

void loop()
{
  
  getSerial();
  switch(serialdata)
  {
  case 1:
    {
      
      while(!digitalRead(stop_button)) {
    SpeedX = analogRead(analogX);
    SpeedY = analogRead(analogY);
    SpeedZ = analogRead(analogZ);
    Serial.print(SpeedX);
    Serial.print(" : ");
    Serial.print(SpeedY);
    Serial.print(" : ");
    Serial.print(SpeedZ);
    Serial.print("\n");
    delay(100);
  
  }
    }
    case 2:
    {
      Serial.println("Limits");
      testLimits();

      break;
    }
    case 3:
    {
      Serial.println("Enabled");
      digitalWrite(enable_pin, LOW);
      delay(8000);
      digitalWrite(enable_pin, HIGH);
      Serial.println("Disabled");
      

      break;
    }
    case 4:
    {
      Serial.println("Shutter Test");
      digitalWrite(shutter, HIGH);
      delay(250);
      digitalWrite(shutter, LOW);
      Serial.println("DONE");

      break;
    }
    case 5:
    {
      Serial.println("ANALOG SPEED Z");
      analogSpeedZ();
      Serial.println("DONE");

      break;
    }
    case 6:
    {
      Serial.println("ANALOG SPEED Y");
      analogSpeedY();
      Serial.println("DONE");

      break;
    }
    case 7:
    {
      Serial.println("CHOOSE MOTOR");
      Serial.println("1: X");
      Serial.println("2: Y");
      Serial.println("3: Z");
      getSerial();
      switch(serialdata)
      {
        case 1:
          {
            Serial.println("MOVING X");
            moveAxis('x');
            Serial.println("DONE");
            break;
          }
        case 2:
          {
            Serial.println("MOVING Y");
            moveAxis('y');
            Serial.println("DONE");
            break;
          }
        case 3:
          {
            Serial.println("MOVING Z");
            moveAxis('z');
            Serial.println("DONE");
            break;
          }
      }
      break;
    }
    case 8:
    {
      Serial.println("Reading Button");
      while(1) {
        stop_status = digitalRead(stop_button);
        Serial.println(stop_status);
        delay(250);
      }
      
      Serial.println("DONE");

      break;
    }
    case 9:
    {
      Serial.println("FULL CONTROL");
      liveControl();      
      Serial.println("DONE");

      break;
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
    }
  }
  inbyte = 0;
  return serialdata;
}

void moveMotor(int steps_to_take) {
  digitalWrite(enable_pin, LOW);
  stepperY.runToNewPosition(steps_to_take);
  digitalWrite(enable_pin, HIGH);
}


void readJoystick() {
  int count = 0;
  while(count < 100) {
    SpeedX = analogRead(analogX);
    SpeedY = analogRead(analogY);
    SpeedZ = analogRead(analogZ);
    Serial.print(SpeedX);
    Serial.print(" : ");
    Serial.print(SpeedY);
    Serial.print(" : ");
    Serial.print(SpeedZ);
    Serial.print("\n");
    delay(100);
    count++;
  }
}


void readChannel(int channel) {
  int count = 0;
  int Speed = 0;
  while(count < 100) {
    Speed = analogRead(channel);
    Serial.println(Speed);
    delay(100);
    count++;
  }
}






void analogSpeedZ() {
  static float current_speed = 0.0;         // Holds current motor speed in steps/second
  digitalWrite(enable_pin, LOW);
  static int analog_read_counter = 1000;    // Counts down to 0 to fire analog read
  while(1) {
    if (analog_read_counter > 0) {
      analog_read_counter--;
    }
    else {
      analog_read_counter = 5000;
      if(digitalRead(stop_button)) {
        Serial.println("STOPPING");
        break;
      }
      // Now read the pot (from 0 to 1023)
      // Give the stepper a chance to step if it needs to
      stepperZ.runSpeed();
      //  And scale the pot's value from min to max speeds
      current_speed = map_speedZ(analogRead(analogZ));
      // Update the stepper to run at this new speed
      stepperZ.setSpeed(current_speed);
    }
    stepperZ.runSpeed();
  }
  digitalWrite(enable_pin, HIGH);

}

long map_speedZ(int read_val) {
    static char sign = 0;
    float read_diff = 0.0;
    if(read_val > (analog_neutral - analog_zero) && read_val < (analog_neutral + analog_zero)) {
      return 0.0;
    }
    else if(read_val < analog_neutral) {
      sign = -1;
      read_diff = (analog_neutral - analog_zero) - read_val;
      SpeedZ = sign * ((read_diff/512.0) * (MAX_SPEED - MIN_SPEED)) + MIN_SPEED;
    }
    else {
      sign = 1;
      read_diff = read_val - (analog_neutral - analog_zero);
      SpeedZ = sign * ((read_diff/512.0) * (MAX_SPEED - MIN_SPEED)) + MIN_SPEED;
    }
   return SpeedZ; 

   
}


void analogSpeedY() {
  static float current_speed = 0.0;         // Holds current motor speed in steps/second
  digitalWrite(enable_pin, LOW);
  static int analog_read_counter = 1000;    // Counts down to 0 to fire analog read
  while(1) {
    if (analog_read_counter > 0) {
      analog_read_counter--;
    }
    else {
      analog_read_counter = 5000;
      if(digitalRead(stop_button)) {
        Serial.println("STOPPING");
        break;
      }
      // Now read the pot (from 0 to 1023)
      // analog_value = analogRead(analogY);
      // Give the stepper a chance to step if it needs to
      stepperY.runSpeed();
      //  And scale the pot's value from min to max speeds
      current_speed = map_speedY(analogRead(analogY));
      // Update the stepper to run at this new speed
      stepperY.setSpeed(current_speed);
    }
    stepperY.runSpeed();
  }
  digitalWrite(enable_pin, HIGH);

}




long map_speedY(int read_val) {
    static char sign = 0;
    float read_diff = 0.0;
    if(read_val > (analog_neutral - analog_zero) && read_val < (analog_neutral + analog_zero)) {
      return 0.0;
    }
    else if(read_val < analog_neutral) {
      sign = -1;
      read_diff = (analog_neutral - analog_zero) - read_val;
      SpeedY = sign * ((read_diff/512.0) * (MAX_SPEED - MIN_SPEED)) + MIN_SPEED;
    }
    else {
      sign = 1;
      read_diff = read_val - (analog_neutral - analog_zero);
      SpeedY = sign * ((read_diff/512.0) * (MAX_SPEED - MIN_SPEED)) + MIN_SPEED;
    }
   return SpeedY; 
}

long map_speedX(int read_val) {
    static char sign = 0;
    float read_diff = 0.0;
    if(read_val > (analog_neutral - analog_zero) && read_val < (analog_neutral + analog_zero)) {
      return 0.0;
    }
    else if(read_val < analog_neutral) {
      sign = -1;
      read_diff = (analog_neutral - analog_zero) - read_val;
      SpeedX = sign * ((read_diff/512.0) * (MAX_SPEED - MIN_SPEED)) + MIN_SPEED;
    }
    else {
      sign = 1;
      read_diff = read_val - (analog_neutral - analog_zero);
      SpeedX = sign * ((read_diff/512.0) * (MAX_SPEED - MIN_SPEED)) + MIN_SPEED;
    }
   return SpeedX; 

   
}


void analogPanTilt() {
  static float current_speedZ = 0.0;         // Holds current motor speed in steps/second
  static float current_speedY = 0.0;         // Holds current motor speed in steps/second
  digitalWrite(enable_pin, LOW);
  static int analog_read_counter = 1000;    // Counts down to 0 to fire analog read
  while(1) {
    if (analog_read_counter > 0) {
      analog_read_counter--;
    }
    else {
      analog_read_counter = 3000;
      if(digitalRead(stop_button)) {
        Serial.println("STOPPING");
        break;
      }
      // Now read the pot (from 0 to 1023)
      // Give the stepper a chance to step if it needs to
      stepperY.runSpeed();
      stepperZ.runSpeed();
      //  And scale the pot's value from min to max speeds
      current_speedY = map_speedY(analogRead(analogY));
      current_speedZ = map_speedZ(analogRead(analogZ));
      // Update the stepper to run at this new speed
      stepperY.setSpeed(current_speedY);
      stepperZ.setSpeed(current_speedZ);
    }
    stepperY.runSpeed();
    stepperZ.runSpeed();
  }
  digitalWrite(enable_pin, HIGH);

}


void liveControl() {
  static float current_speedZ = 0.0;         // Holds current motor speed in steps/second
  static float current_speedY = 0.0;         // Holds current motor speed in steps/second
  static float current_speedX = 0.0;         // Holds current motor speed in steps/second
  digitalWrite(enable_pin, LOW);
  static int analog_read_counter = 1000;    // Counts down to 0 to fire analog read
  while(1) {
    if (analog_read_counter > 0) {
      analog_read_counter--;
    }
    else {
      analog_read_counter = 2000;
      if(digitalRead(stop_button)) {
        Serial.println("STOPPING");
        break;
      }
      // Now read the pot (from 0 to 1023)
      // Give the stepper a chance to step if it needs to
      stepperY.runSpeed();
      stepperZ.runSpeed();
      stepperX.runSpeed();
      //  And scale the pot's value from min to max speeds
      current_speedY = map_speedY(analogRead(analogY));
      current_speedZ = map_speedZ(analogRead(analogZ));
      current_speedX = map_speedX(analogRead(analogX));
      // Update the stepper to run at this new speed
      stepperY.setSpeed(current_speedY);
      stepperZ.setSpeed(current_speedZ);
      stepperX.setSpeed(current_speedX);
    }
    stepperY.runSpeed();
    stepperZ.runSpeed();
    stepperX.runSpeed();
  }
  digitalWrite(enable_pin, HIGH);

}


void moveAxis(char axis) {
  int axis_analog_pin;
  float current_speed = 0.0;
  if(axis == 'x') {
    Serial.println("RUNNING X");
    axis_analog_pin = analogX;
  }
  else if(axis == 'y') {
    Serial.println("RUNNING Y");
    axis_analog_pin = analogY; 
  }
  else if(axis == 'z') {
    Serial.println("RUNNING Z");
    axis_analog_pin = analogZ; 
  }
  else {
    Serial.println("INVALID AXIS");
  }

  static int analog_read_counter = 1000;    // Counts down to 0 to fire analog read
  
  digitalWrite(enable_pin, LOW);
  while(1) {
    if (analog_read_counter > 0) {
      analog_read_counter--;
    }
    else {
      analog_read_counter = 2000;
      current_speed = map_speed(axis_analog_pin);
      if(digitalRead(stop_button)) {
        Serial.println("STOPPING");
        break;
      }
      if(axis == 'x') {
        stepperX.runSpeed();
        stepperX.setSpeed(current_speed);
      }
      else if(axis == 'y') {
        stepperY.runSpeed(); 
        stepperY.setSpeed(current_speed);
      }
      else if(axis == 'z') {
        stepperZ.runSpeed(); 
        stepperZ.setSpeed(current_speed);
      }
      else {
        Serial.println("INVALID AXIS");
        break;
      }
      
    }
    if(axis == 'x') {
        stepperX.runSpeed();
      }
      else if(axis == 'y') {
        stepperY.runSpeed(); 
      }
      else if(axis == 'z') {
        stepperZ.runSpeed(); 
      }
      else {
        Serial.println("INVALID AXIS");
        break;
      }
  }
  digitalWrite(enable_pin, HIGH);
}

long map_speed(int analogPin) {
    int read_val = analogRead(analogPin);
    long set_speed;
    static char sign = 0;
    float read_diff = 0.0;
    if(read_val > (analog_neutral - analog_zero) && read_val < (analog_neutral + analog_zero)) {
      return 0.0;
    }
    else if(read_val < analog_neutral) {
      sign = -1;
      read_diff = (analog_neutral - analog_zero) - read_val;
      set_speed = sign * ((read_diff/512.0) * (MAX_SPEED - MIN_SPEED)) + MIN_SPEED;
    }
    else {
      sign = 1;
      read_diff = read_val - (analog_neutral - analog_zero);
      set_speed = sign * ((read_diff/512.0) * (MAX_SPEED - MIN_SPEED)) + MIN_SPEED;
    }
   return set_speed; 
}


void testLimits() {
  int x_status = digitalRead(x_limit);
  int y_status = digitalRead(y_limit);
  int z_status = digitalRead(z_limit);

  while(1) {
    if(digitalRead(stop_button)) {
        Serial.println("STOPPING");
        break;
      }
    if(!digitalRead(x_limit)) {
      Serial.println("X");
    }
    if(!digitalRead(y_limit)) {
      Serial.println("Y");
    }
    if(!digitalRead(z_limit)) {
      Serial.println("Z");
    }
  }

}







