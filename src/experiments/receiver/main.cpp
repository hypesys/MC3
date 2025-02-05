/**
 * @file Standalone receiver
 * @details Run with `./build/receiver <mode (one of read, write, or copy)> <parallelism (0 for all cores)> <warmup iterations> <run iterations> <buffer size in bytes>` (e.g.: copy mode, all cores, 32 warmup iterations, 64 run iterations, and 1 GiB buffer: `./build/receiver copy 0 32 64 1073741824`)
 */

#include <chrono>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <omp.h>

#include "contention_generator.hpp"

int main(int argc, char **argv)
{
  // Print usage
  if (argc != 6)
  {
    std::cerr << "Usage: " << argv[0] << " <mode (one of read, write, or copy)> <parallelism (0 for all cores)> <warmup iterations> <run iterations> <buffer size in bytes>" << std::endl;
    return 1;
  }

  // Parse arguments
  covert_channel::contention_mode mode = covert_channel::contention_mode(argv[1]);
  std::size_t parallelism = strtoul(argv[2], nullptr, 0);
  std::size_t warmupIterations = strtoul(argv[3], nullptr, 0);
  std::size_t runIterations = strtoul(argv[4], nullptr, 0);
  std::size_t bufferSize = strtoul(argv[5], nullptr, 0);

  // Validate arguments
  if (runIterations == 0 || bufferSize == 0)
  {
    std::cerr << "Invalid arguments" << std::endl;
    return 1;
  }

  // Set the parallelism
  if (parallelism == 0)
  {
    parallelism = omp_get_max_threads();
  }

  // Initialize the contention generator
  covert_channel::contention_generator generator(parallelism, bufferSize);

  // Print the header
  std::cout << "type,bandwidth,time" << std::endl;

  // Warm up
  for (std::size_t iteration = 0; iteration < warmupIterations; iteration++)
  {
    // Get the time
    int64_t time = std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now().time_since_epoch()).count();

    // Run
    double bandwidth = generator.run(mode);

    // Print the result
    std::cout << "warmup," << bandwidth << "," << time << std::endl;
  }

  // Run
  double *bandwidths = new double[runIterations];

  for (std::size_t iteration = 0; iteration < runIterations; iteration++)
  {
    // Get the time
    int64_t time = std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now().time_since_epoch()).count();

    // Run
    double bandwidth = generator.run(mode);

    // Save the result
    bandwidths[iteration] = bandwidth;
    
    // Get the current time with microsecond precision
    auto endTime = std::chrono::system_clock::now();
    auto end_time_t = std::chrono::system_clock::to_time_t(endTime);
    std::tm *ltm = std::localtime(&end_time_t);

    // Extract microseconds
    auto end_us = std::chrono::duration_cast<std::chrono::microseconds>(endTime.time_since_epoch()) % 1000000;
    auto end_ms = end_us / 1000;         // Millisecond part
    auto end_micro = end_us % 1000;      // Remaining microseconds

    // Format hours, minutes, and seconds
    char time_buffer[9];
    std::strftime(time_buffer, sizeof(time_buffer), "%H:%M:%S", ltm);

    // Print the result in microsecond precision
    std::cout << time_buffer << ":" 
              << (end_ms.count() < 10 ? "00" : end_ms.count() < 100 ? "0" : "") << end_ms.count() << ":" 
              << (end_micro.count() < 10 ? "00" : end_micro.count() < 100 ? "0" : "") << end_micro.count()
              << "    &   " << bandwidth << std::endl;
  }

  // Compute statistics
  double mean = 0;
  double min = bandwidths[0];
  double max = bandwidths[0];
  double stddev = 0;

  for (std::size_t iteration = 0; iteration < runIterations; iteration++)
  {
    // Update the mean
    mean += bandwidths[iteration];

    // Update the minimum
    if (bandwidths[iteration] < min)
    {
      min = bandwidths[iteration];
    }

    // Update the maximum
    if (bandwidths[iteration] > max)
    {
      max = bandwidths[iteration];
    }
  }

  // Compute the mean
  mean /= static_cast<double>(runIterations);

  for (std::size_t iteration = 0; iteration < runIterations; iteration++)
  {
    // Update the standard deviation
    stddev += (bandwidths[iteration] - mean) * (bandwidths[iteration] - mean) / (static_cast<double>(runIterations) - 1);
  }

  // Compute the standard deviation
  stddev = std::sqrt(stddev);

  // Print statistics
  std::cerr << "Mean: " << mean << " GB/s" << std::endl;
  std::cerr << "Min: " << min << " GB/s" << std::endl;
  std::cerr << "Max: " << max << " GB/s" << std::endl;
  std::cerr << "Stddev: " << stddev << " GB/s" << std::endl;

  // Cleanup
  delete[] bandwidths;

  return 0;
}
