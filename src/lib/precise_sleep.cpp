/**
 * @file Precise sleep implementation
 * @see https://blog.bearcats.nl/perfect-sleep-function/
 */

#include <cstdint>
#include <stdexcept>
#include <thread>

#include "precise_sleep.hpp"

std::chrono::nanoseconds precise_sleep::sleep_for(std::chrono::nanoseconds duration)
{
  // Validate parameters
  if (duration.count() < PRECISE_SLEEP_MINIMUM_SLEEP_DURATION)
  {
    throw std::invalid_argument("Duration is too short");
  }

  // Get the current time
  auto t0 = std::chrono::steady_clock::now();

  // Calculate the course sleep duration
  int64_t rawCourseSleepDuration = static_cast<int64_t>(
      (floor(static_cast<double>(duration.count()) / static_cast<double>(PRECISE_SLEEP_COURSE_SLEEP_PERIOD)) - 1) *
      PRECISE_SLEEP_COURSE_SLEEP_PERIOD);
  auto courseSleepDuration = std::chrono::nanoseconds(rawCourseSleepDuration);

  // Sleep for the course duration
  std::this_thread::sleep_for(courseSleepDuration);

  // Get the epsilon (time to get the current time)
  auto t1 = std::chrono::steady_clock::now();
  auto t2 = std::chrono::steady_clock::now();
  auto epsilon = t2 - t1;

  // Calculate the precise desired end time
  auto desiredEndTime = t0 + duration - epsilon;

  // Spin wait until the precise time is reached
  while (std::chrono::steady_clock::now() < desiredEndTime)
  {
    // Do nothing
  }

  // Get the current time
  auto t3 = std::chrono::steady_clock::now();

  // Calculate the error
  auto error = duration - (t3 - t0);

  return error;
}

std::chrono::nanoseconds precise_sleep::sleep_until(std::chrono::time_point<std::chrono::steady_clock> time)
{
  // Get the current time
  auto t0 = std::chrono::steady_clock::now();

  // Validate parameters
  if (time <= (t0 + std::chrono::nanoseconds(PRECISE_SLEEP_MINIMUM_SLEEP_DURATION)))
  {
    throw std::invalid_argument("Time is too soon");
  }

  // Calculate the course sleep duration
  int64_t rawCourseSleepDuration = static_cast<int64_t>(
      (floor(static_cast<double>((time - t0).count()) / static_cast<double>(PRECISE_SLEEP_COURSE_SLEEP_PERIOD)) - PRECISE_SLEEP_COURSE_SLEEP_OFFSET) *
      PRECISE_SLEEP_COURSE_SLEEP_PERIOD);
  auto courseSleepDuration = std::chrono::nanoseconds(rawCourseSleepDuration);

  // Sleep for the course duration
  std::this_thread::sleep_for(courseSleepDuration);

  // Get the epsilon (time to get the current time)
  auto t1 = std::chrono::steady_clock::now();
  auto t2 = std::chrono::steady_clock::now();
  auto epsilon = t2 - t1;

  // Calculate the precise desired end time
  auto desiredEndTime = time - epsilon;

  // Spin wait until the precise time is reached
  while (std::chrono::steady_clock::now() < desiredEndTime)
  {
    // Do nothing
  }

  // Get the current time
  auto t3 = std::chrono::steady_clock::now();

  // Calculate the error
  auto error = time - t3;

  return error;
}
