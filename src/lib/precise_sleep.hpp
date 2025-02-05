/**
 * @file Precise sleep definition
 * @see https://blog.bearcats.nl/perfect-sleep-function/
 */

#pragma once

#include <chrono>
#include <cmath>
#include <cstddef>

/**
 * @brief Minimum sleep duration (in nanoseconds)
 *
 * @details This should be large enough to ensure that it's incredibly unlikely
 * that the precise sleep family of functions are called with a duration
 * shorter than the duration of calling the functions without them actually
 * sleeping (and just delaying things with the overhead of the functions, such
 * as the error calcuation). Currently this is empirically derived by running
 * the sleep benchmark with a duration of 0 and observing the error (which is
 * the total overhead of the function) and then using a normal distribution
 * to calculate a value that has a Z-score >= 4 (which is gives an equivalent
 * probability of no more than 1 in 30,000 that the function will be called
 * and sleep for longer than the duration of the function overhead itself).
 */
#define PRECISE_SLEEP_MINIMUM_SLEEP_DURATION 500

/**
 * @brief Course sleep period (in nanoseconds)
 *
 * @details This should be equal to the `sysctl_sched_latency` value in the
 * kernel
 */
#define PRECISE_SLEEP_COURSE_SLEEP_PERIOD 6 * 1000 * 1000

/**
 * @brief Course sleep offset (in periods)
 *
 * @details This is the number of course sleep periods to spin instead for. A
 * higher value will result in a more accurate sleep but will also increase the
 * overhead of the function.
 */
#define PRECISE_SLEEP_COURSE_SLEEP_OFFSET 1

/**
 * @brief Precise sleep namespace
 */
namespace precise_sleep
{
  /**
   * @brief Sleep for a precise duration
   * @param duration Duration to sleep for
   * @return Error
   */
  std::chrono::nanoseconds sleep_for(std::chrono::nanoseconds duration);

  /**
   * @brief Sleep until a precise time
   * @param time Time to sleep until
   * @return Error
   */
  std::chrono::nanoseconds sleep_until(std::chrono::time_point<std::chrono::steady_clock> time);
} // namespace precise_sleep
