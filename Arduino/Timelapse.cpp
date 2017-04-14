#include "Arduino.h"
#include "Timelapse.h"


Timelapse::Timelapse(int totalPictures, int totalTime)
{
  _totalPictures = totalPictures;
  _totalTime = totalTime;
}


void Timelapse::calculate_steps_cycle()
{
    _totalSteps = _totalTime / _totalPictures
}

void Timelapse::run_step()
{
  _totalSteps = _totalTime / _totalPictures
}