#include <PS4BT.h>
#include <usbhub.h>

// Satisfy the IDE, which needs to see the include statment in the ino too.
#ifdef dobogusinclude
#include <spi4teensy3.h>
#include <SPI.h>
#endif

USB Usb;
//USBHub Hub1(&Usb); // Some dongles have a hub inside
BTD Btd(&Usb); // You have to create the Bluetooth Dongle instance like so

/* You can create the instance of the PS4BT class in two ways */
// This will start an inquiry and then pair with the PS4 controller - you only have to do this once
// You will need to hold down the PS and Share button at the same time, the PS4 controller will then start to blink rapidly indicating that it is in pairing mode
PS4BT PS4(&Btd, PAIR);

// After that you can simply create the instance like so and then press the PS button on the device
//PS4BT PS4(&Btd);

bool printAngle, printTouch;
uint8_t oldL2Value, oldR2Value;



#include <Axis.h>
#include <AccelStepper.h>
//#include <MultiStepper.h>


// Serial Variables
unsigned long serialdata;

int inbyte;





// Control Flow
int stop_status = 0;
bool steppers_enabled = false;



// Timelapse Variables
bool TIMELAPSE_READY = false;
bool TIMELAPSE_RUNNING = false;
bool EXIT = false;
int total_frames;


//Camera Variables
int stable_delay = 1000;
int shutter_time = 500;
int interval_time = 2000;




// Stepper Variables
float ACCEL = 1000;
float MIN_SPEED = 0.01;
float MAX_SPEED = 6000;


long current_speed[] = {0.0, 0.0, 0.0}; // [x, y, z]
long stepArray[] = {0, 0, 0};
long total_steps[] = {0, 0, 0};



// PS4 Constants 
float ANALOG_NEUTRAL = 122.5;
float ANALOG_OFFSET = 10.0;

// Joystick Controls & INPUTS

#define stop_button 40
#define shutter 43
#define analogX 10
#define analogY 8
#define analogZ 9
#define enable_pin 8

static int analogRate = 1000;



// X-axis
AccelStepper stepperX(AccelStepper::DRIVER, 2, 5);
#define x_limit 9
Axis x_Axis(x_limit, 1.0, 8, 'x');

// Y-axis
AccelStepper stepperY(AccelStepper::DRIVER, 3, 6);
#define y_limit 10 
Axis y_Axis(y_limit, 1.0, 8, 'y');


// Z-axis
AccelStepper stepperZ(AccelStepper::DRIVER, 4, 7);
#define z_limit 11
Axis z_Axis(z_limit, 1.0, 8, 'z');


void setup()
{
  Serial.begin(115200);
  #if !defined(__MIPSEL__)
    while (!Serial); // Wait for serial port to connect - used on Leonardo, Teensy and other boards with built-in USB CDC serial connection
  #endif
    if (Usb.Init() == -1) {
      Serial.print(F("\r\nOSC did not start"));
      while (1); // Halt
    }
    Serial.print(F("\r\nPS4 Bluetooth Library Started"));
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
  stepperX.setMaxSpeed(6000);
  stepperX.setAcceleration(1000);
}

void loop() {
  Usb.Task();
  if (PS4.connected()) {
  getSerial();
  switch(serialdata) {
    /* Motor Control */
    case 100: { // Live Control

    }

    case 101: { // Select Motor

    }

    case 102: { // Control X

    }

    case 103: { // Control Y

    }

    case 104: { // Control Z

    }

    /* Timelapse Control */
    case 201: { /* Simple Live Control */
      Serial.println("LIVE CONTROL");
      liveControl();
      break;
    }

    case 202: { /* Single Axis Control */
      Serial.println("SINGLE AXIS");
      break;
    }

    case 203: {
      Serial.println("PICTURE");
      takePicture();
      break;
    }

    case 204: { /* Timelapse Program */
      Serial.println("TIMELAPSE");
      while(!EXIT) {
        getSerial();
        switch(serialdata) {

          case 1: { /* Set Timelapse End */
            Serial.println("SET END");
            liveControl();
            zeroTimelapse();
            break;
          }
          case 2: { /* Set Timelapse Start */
            Serial.println("SET START");
            setTimelapseStart();
            // $$ Remove
            getSerial();
            total_frames = int(serialdata);
            delay(1000);
            getSerial();
            interval_time = int(serialdata);
            delay(1000);

            programTimelapse(total_frames);
            TIMELAPSE_READY = true;
            break;
          }
          case 3: {
            if(TIMELAPSE_READY) {
              pi_timelapseStep();
            }
            break;
          }
          case 4: { /* Run Timelapse*/
            Serial.println("RUN TIMELAPSE");
            runTimelapse();
            EXIT = true;
            break;
          }
          case 5: {
            EXIT = true;
            TIMELAPSE_READY = false;
          }
          default: {
            Serial.println("DEFAULT");
            break;
          }
        }
      }

      EXIT = false;
      break;
    }

    

    case 205: {
      if(TIMELAPSE_READY) {
        timelapseStep();
      }
      break;
    }

    case 206: {
      Serial.println("ASYNC MOVE");
      total_steps[0] = stepperX.currentPosition() * -1;
      total_steps[1] = stepperY.currentPosition() * -1;
      total_steps[2] = stepperZ.currentPosition() * -1;
      // moveAll(total_steps[0], total_steps[1], total_steps[2]);
      break;
    }
    case 207: {
      Serial.println("MOVE HOME");
      
      // moveAllTo(0,0,0);
      break;
    }
    case 208: {
      printStepCounts();

      break;
    }

    case 209: {
      zeroTimelapse();
      printStepCounts();

      break;
    }


    /* Camera Control */
    
    case 300: { // Trigger Camera

    }
    
    /* Panorama Control */

    case 400: {

    }

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

/* -------- TIMELAPSE ---------- */

void setTimelapseStart() {
  // Move motors first, make sure steps and direction are being counted
  liveControl();
  // set each axis steps $$
  total_steps[0] = stepperX.currentPosition();
  total_steps[1] = stepperY.currentPosition();
  total_steps[2] = stepperZ.currentPosition();

  x_Axis.setStepCount(total_steps[0]);
  y_Axis.setStepCount(total_steps[1]);
  z_Axis.setStepCount(total_steps[2]);

}

void programTimelapse(int frames) {
  stepArray[0] = x_Axis.programTimelapse(frames);
  stepArray[1] = y_Axis.programTimelapse(frames);
  stepArray[2] = z_Axis.programTimelapse(frames);

  //$$ Send programmed steps, each on newline
  Serial.println(stepArray[0]);
  Serial.println(stepArray[1]);
  Serial.println(stepArray[2]);

}


void runTimelapse() {
  int i;
  for(i = 0; i < total_frames; i++) {
    if(stop()) {
      break;
    }
    else {
      timelapseStep();
    }
  }
}


void zeroTimelapse() {
  x_Axis.zeroSteps();
  y_Axis.zeroSteps();
  z_Axis.zeroSteps();
  zeroPosition();
}
void timelapseStep() {
  // $$ run each motor for however man steps in segment
  enableMotors();
  stepperX.runToNewPosition(stepArray[0]);
  stepperY.runToNewPosition(stepArray[1]);
  stepperZ.runToNewPosition(stepArray[2]);
  disableMotors();
  zeroPosition();
  delay(stable_delay);
  takePicture();
  delay(interval_time);

}

void pi_timelapseStep() {
  enableMotors();
  stepperX.runToNewPosition(stepArray[0]);
  stepperY.runToNewPosition(stepArray[1]);
  stepperZ.runToNewPosition(stepArray[2]);
  disableMotors();
  zeroPosition();
  delay(stable_delay);
  takePicture();
}







void liveControl() {

  int analog_counter = analogRate;
  enableMotors();

  while(1) {
    Usb.Task();
    if (analog_counter > 0) { //read analog when rate is zero
      analog_counter--;
    }

    else {
      analog_counter = 1000; // reset analog read count

      if(PS4.getButtonClick(TRIANGLE)) { // Exit program if stop button is pressed
        break;
      }

      if(PS4.getButtonClick(R1)) {
        takePicture();
      }
      // Give the stepper a chance to step if it needs to
      runMotors();

      // Read the joystick for each channel (from 0 to 1023)
      readAll();

      // Update the stepper to run at this new speed
      updateSpeeds();
      
  }
  runMotors();
}
disableMotors();
}


void readAll() {
  readSpeed(x_Axis.name);
  readSpeed(y_Axis.name);
  readSpeed(z_Axis.name);
}


void runMotors() {
  stepperY.runSpeed();
  stepperZ.runSpeed();
  stepperX.runSpeed();
}


void updateSpeeds() {
  // Updates the speed of each motor based on the last analog read speed
  stepperX.setSpeed(current_speed[0]);
  stepperY.setSpeed(current_speed[1]);
  stepperZ.setSpeed(current_speed[2]);
}

void readSpeed(char read_axis) {
  // Read the values from joystick and assign mapped speed to the current speed arrar
  long read_speed;
  
  if(read_axis == 'x') {
    read_speed = PS4.getAnalogHat(LeftHatX);
    current_speed[0] = read_speed;
  }
  else if(read_axis == 'y') {
    read_speed = PS4.getAnalogHat(RightHatX);
    current_speed[1] = read_speed;
  }
  else if(read_axis == 'z') {
    read_speed = PS4.getAnalogHat(RightHatY);
    current_speed[2] = read_speed;
  }
  else {
    read_speed = 0;
  }


}


long mapSpeed(float read_val) {
    // Scale the pot's value from min to max speeds
    long set_speed;
    static char sign = 0;
    float read_diff = 0.0;
    if(read_val > (ANALOG_NEUTRAL - ANALOG_OFFSET) && read_val < (ANALOG_NEUTRAL + ANALOG_OFFSET)) {
      return 0.0;
    }
    else if(read_val < ANALOG_NEUTRAL) {
      sign = -1;
      read_diff = (ANALOG_NEUTRAL - ANALOG_OFFSET) - read_val;
      set_speed = sign * ((read_diff/512.0) * (MAX_SPEED - MIN_SPEED)) + MIN_SPEED;
    }
    else {
      sign = 1;
      read_diff = read_val - (ANALOG_NEUTRAL - ANALOG_OFFSET);
      set_speed = sign * ((read_diff/512.0) * (MAX_SPEED - MIN_SPEED)) + MIN_SPEED;
    }
    return set_speed; 
  }


void enableMotors() {
  digitalWrite(enable_pin, LOW);
  steppers_enabled = true;
}

void disableMotors() {
  digitalWrite(enable_pin, HIGH);
  steppers_enabled = false;
}

void togglePower() {
  digitalWrite(enable_pin, steppers_enabled); // Motors Enable when pulled to ground
  steppers_enabled = !steppers_enabled;
}




void takePicture() {
  digitalWrite(shutter, HIGH);
  delay(100);
  digitalWrite(shutter, LOW);
}


void printStepCounts() {
  Serial.println("STEP COUNTS");
  Serial.print("X: ");
  Serial.println(stepperX.currentPosition());
  Serial.print("Y: ");
  Serial.println(stepperY.currentPosition());
  Serial.print("Z: ");
  Serial.println(stepperZ.currentPosition());
}

void zeroPosition() {
  stepperX.setCurrentPosition(0);
  stepperY.setCurrentPosition(0);
  stepperZ.setCurrentPosition(0);
}


bool stop() {
  Usb.Task();
  if(PS4.getButtonClick(TRIANGLE)) {
    return true;
  }
  else {
    return false;
  }
}










