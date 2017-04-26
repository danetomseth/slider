#include <AccelStepper.h>
#include <MultiStepper.h>
#include <Axis.h>


// Serial Variables
unsigned long serialdata;

int inbyte;


int total_steps;



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




// Stepper Variables
float ACCEL = 1000
float MIN_SPEED = 0.01
float MAX_SPEED = 6000


long current_speed[] = {0.0, 0.0, 0.0} // [x, y, z]




// Joystick Controls & INPUTS
#define analog_neutral 512
#define analog_zero 30
#define stop_button 40
#define shutter 43
#define analogX 10
#define analogY 9
#define analogZ 8
#define enable_pin 8

int joystick_pins[] = {analogX, analogY, analogZ};
static int analogRate = 1000;



// X-axis
AccelStepper stepperX(AccelStepper::DRIVER, 2, 5);
#define x_limit 9
Axis x_Axis(x_limit, 1.0, 8);

// Y-axis
AccelStepper stepperY(AccelStepper::DRIVER, 3, 6);
#define y_limit 10 
Axis y_Axis(y_limit, 1.0, 8);


// Z-axis
AccelStepper stepperZ(AccelStepper::DRIVER, 4, 7);
#define z_limit 11
Axis z_Axis(z_limit, 1.0, 8);


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
		case 1: { /* Simple Live Control */
			Serial.println("LIVE CONTROL");
			liveControl();
			break;
		}

		case 2: { /* Single Axis Control */
			Serial.println("SINGLE AXIS");
			break;
		}

		case 3: {
			Serial.println("PICTURE");
			takePicture();
			break;
		}

		case 4: { /* Timelapse Program */
			Serial.println("TIMELAPSE");
			while(!EXIT) {
				getSerial();
				switch(serialdata) {

					case 1: { /* Set Timelapse End */
						Serial.println("SET END");
						liveControl();
						resetTimelapse();
						break;
					}
					case 2: { /* Set Timelapse Start */
						Serial.println("SET START");
						setTimelapseStart();
						getSerial();
						total_frames = serialdata;
						getSerial();
						shutter_time = serialdata;

						programTimelapse(total_frames);
						break;
					}
					case 3: { /* Run Timelapse*/
						Serial.println("RUN TIMELAPSE");
						runTimelapse();
						EXIT = true;
						break;
					}
					case 4: {
						EXIT = true;
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

		

		case 5: {
			while(!stop()) {
				Serial.println("STANDBY...");
				delay(100);
			}
			break;
		}

		case 6: { /* Set Timelapse End */
			Serial.println("SET END");
			liveControl();
			resetTimelapse();
			break;
		}
		case 7: { /* Set Timelapse Start */
			Serial.println("SET START");
			setTimelapseStart();
			getSerial();
			total_frames = serialdata;
			getSerial();
			shutter_time = serialdata;

			programTimelapse(total_frames);
			break;
		}
		case 8: { /* Run Timelapse*/
			Serial.println("RUN TIMELAPSE");
			runTimelapse();
			EXIT = true;
			break;
		}

		case 9: {

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

/* -------- TIMELAPSE ---------- */

void setTimelapseStart() {
	// Move motors first, make sure steps and direction are being counted
	liveControl();
	// set each axis steps $$
	x_Axis.setStepCount(stepperX.count)
	y_Axis.setStepCount(stepperY.count)
	z_Axis.setStepCount(stepperZ.count)

}

void programTimelapse(int frames) {
	int stepArray[] = {0, 0, 0};
	stepArray[0] = x_Axis.programTimelapse(frames);
	stepArray[1] = y_Axis.programTimelapse(frames);
	stepArray[2] = z_Axis.programTimelapse(frames);

	//$$ Send programmed steps, each on newline
	Serial.println(stepArray[0])
	Serial.println(stepArray[1])
	Serial.println(stepArray[2])

}


void runTimelapse() {
	int i;
	for(i = 0; i < total_frames; i++) {
		if(stop()) {
			Serial.println("EXIT");
			break;
		}
		else {
			timelapseStep();
			Serial.println(i);
		}
	}
}

void timelapseStep() {
	// $$ run each motor for however man steps in segment
	stepperX.move(stepArray[0]);
	stepperY.move(stepArray[1]);
	stepperZ.move(stepArray[2]);
	delay(stable_delay);
	takePicture();
	delay(shutter_time);

}



void resetTimelapse() {
	x_Axis.resetTimelapse();
	y_Axis.resetTimelapse();
	z_Axis.resetTimelapse();

	// $$ zero motors
}



void liveControl() {
	int analog_counter = analogRate;
  enableMotors()

  while(1) {
    if (analog_counter > 0) { //read analog when rate is zero
      analog_counter--;
    }

    else {
      analog_counter = 1000; // reset analog read count

      if(stop()) { // Exit program if stop button is pressed
        Serial.println("STOPPING");
        break;
      }
      // Give the stepper a chance to step if it needs to
      runMotors();

      // Read the joystick for each channel (from 0 to 1023)
      readJoystick();

      // Update the stepper to run at this new speed
      updateSpeeds();
      
    }
    runMotors()
  }
  disableMotors();
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

void readJoystick() {
	// Read the values from joystick and assign mapped speed to the current speed arrar
	int motor;
	for(motor = 0; motor < 3; motor++) {
		current_speed[motor] = mapSpeed(joystick_pins[motor]);
	}

}


long mapSpeed(int analogPin) {
		// Scale the pot's value from min to max speeds
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

bool stop() {
	return digitalRead(stop_button);
}


void takePicture() {
	digitalWrite(shutter, HIGH);
  delay(100);
  digitalWrite(shutter, LOW);
}



