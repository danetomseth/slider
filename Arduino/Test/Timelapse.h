#ifndef Timelapse_h
#define Timelapse_h

#include "Arduino.h"

class Timelapse
{
  public:
    Timelapse(int totalPictures, int totalTime);
    void calculate_steps_cycle();
    void run_step();
  private:
    int _pictures;
    int _totalSteps
    int _totalTime
};



#endif