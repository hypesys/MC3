/**
 * @file Timing consistency benchmark
 * @details Run with `./build/timing-consistency <mode (one of run-for, run-until, sleep-for, or sleep-until)> <iterations> <duration in nanoseconds> [contention mode (one of read, write, or copy)] [parallelism (0 for all cores)] [buffer size in bytes]` (e.g.: run-for mode, 32 iterations, 1 second each, copy contention mode, all cores, and 1 GiB buffer: `./build/timing-consistency run-for 32 1000000000 copy 0 1073741824`)
 * Note that contention mode, parallelism, and buffer size are required for run-for and run-until modes
 */

#define RUN_FOR_MODE "run-for"
#define RUN_UNTIL_MODE "run-until"
#define SLEEP_FOR_MODE "sleep-for"
#define SLEEP_UNTIL_MODE "sleep-until"

#include <cmath>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <omp.h>
#include <tuple>

#include "contention_generator.hpp"
#include "precise_sleep.hpp"

int main(int argc, char **argv)
{
  // Print usage
  if (argc != 4 && argc != 7)
  {
    std::cerr << "Usage: " << argv[0] << " <mode (one of " << RUN_FOR_MODE << ", " << RUN_UNTIL_MODE << ", " << SLEEP_FOR_MODE << ", " << SLEEP_UNTIL_MODE << " <iterations> <duration in nanoseconds> [contention mode (one of read, write, or copy)] [parallelism (0 for all cores)] [buffer size in bytes]" << std::endl;
    return 1;
  }

  // Parse arguments
  std::string mode = argv[1];
  std::size_t iterations = strtoul(argv[2], nullptr, 0);
  auto duration = std::chrono::nanoseconds(strtoul(argv[3], nullptr, 0));

  // Validate arguments
  if ((
          mode != RUN_FOR_MODE &&
          mode != RUN_UNTIL_MODE &&
          mode != SLEEP_FOR_MODE &&
          mode != SLEEP_UNTIL_MODE) ||
      iterations == 0 ||
      std::chrono::duration_cast<std::chrono::nanoseconds>(duration).count() == 0)
  {
    std::cerr << "Invalid arguments" << std::endl;
    return 1;
  }

  // Initialize the contention generator
  covert_channel::contention_generator *generator = nullptr;
  covert_channel::contention_mode *contentionMode = nullptr;

  if (mode == RUN_FOR_MODE || mode == RUN_UNTIL_MODE)
  {
    // Parse arguments
    contentionMode = new covert_channel::contention_mode(argv[4]);
    std::size_t parallelism = strtoul(argv[5], nullptr, 0);
    std::size_t bufferSize = strtoul(argv[6], nullptr, 0);

    // Validate arguments
    if (bufferSize == 0)
    {
      std::cerr << "Invalid arguments" << std::endl;
      return 1;
    }

    // Set the parallelism
    if (parallelism == 0)
    {
      parallelism = omp_get_max_threads();
    }

    // Create the contention generator
    generator = new covert_channel::contention_generator(parallelism, bufferSize);
  }

  // Print the header
  std::cout << "iteration,error" << std::endl;

  // Run
  double *errors = new double[iterations];

  for (std::size_t iteration = 0; iteration < iterations; iteration++)
  {
    // Do the work
    std::chrono::nanoseconds errorDuration = std::chrono::nanoseconds(0);
    if (mode == RUN_FOR_MODE || mode == RUN_UNTIL_MODE)
    {
      if (generator == nullptr || contentionMode == nullptr)
      {
        std::cerr << "Generator or contention mode not initialized" << std::endl;
        return 1;
      }

#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wmaybe-uninitialized"
      if (mode == RUN_FOR_MODE)
      {
        errorDuration = std::get<1>(generator->run_for(*contentionMode, duration));
      }
      // else
      // {
      //   errorDuration = std::get<1>(generator->run_until(*contentionMode, std::chrono::steady_clock::now() + duration));
      // }
#pragma GCC diagnostic pop
    }
    else if (mode == SLEEP_FOR_MODE)
    {
      errorDuration = precise_sleep::sleep_for(duration);
    }
    else
    {
      errorDuration = precise_sleep::sleep_until(std::chrono::steady_clock::now() + duration);
    }

    // Compute the error
    // int64_t error = std::abs(std::chrono::duration_cast<std::chrono::nanoseconds>(errorDuration).count());
    int64_t error = std::chrono::duration_cast<std::chrono::nanoseconds>(errorDuration).count();

    // Print the row
    std::cout << iteration << "," << error << std::endl;

    // Save the error
    errors[iteration] = static_cast<double>(error);
  }

  // Compute statistics
  double mean = 0;
  double min = errors[0];
  double max = errors[0];

  for (std::size_t iteration = 0; iteration < iterations; iteration++)
  {
    // Update the mean
    mean += errors[iteration];

    // Update the minimum
    if (errors[iteration] < min)
    {
      min = errors[iteration];
    }

    // Update the maximum
    if (errors[iteration] > max)
    {
      max = errors[iteration];
    }
  }

  // Compute the mean
  mean /= static_cast<double>(iterations);

  // Compute the standard deviation
  double stddev = 0;

  for (std::size_t iteration = 0; iteration < iterations; iteration++)
  {
    // Update the standard deviation
    stddev += (errors[iteration] - mean) * (errors[iteration] - mean) / (static_cast<double>(iterations) - 1);
  }

  // Compute the standard deviation
  stddev = std::sqrt(stddev);

  // Print statistics
  std::cerr << "Mean error: " << mean << " ns" << std::endl;
  std::cerr << "Min error: " << min << " ns" << std::endl;
  std::cerr << "Max error: " << max << " ns" << std::endl;
  std::cerr << "Stddev error: " << stddev << " ns" << std::endl;

  // Cleanup
  if (generator != nullptr)
  {
    delete generator;
  }

  if (contentionMode != nullptr)
  {
    delete contentionMode;
  }

  delete[] errors;

  return 0;
}
