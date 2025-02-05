/**
 * @file Standalone transmitter
 * @details Run with `./build/transmitter <mode (one of read, write, or copy)> <parallelism (0 for all cores)> <warmup iterations> <buffer size in bytes> <message>` (e.g.: copy mode, all cores, 32 warmup iterations, 1 GiB buffer, and "Hello, world": `./build/transmitter copy 0 32 1073741824 "Hello, world"`)
 */

#include <chrono>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <omp.h>
#include <string>
#include <thread>
#include <vector>

#include "contention_generator.hpp"

int main(int argc, char **argv)
{
  // Print usage
  if (argc != 8)
  {
    std::cerr << "Usage: " << argv[0] << " <mode (one of read, write, or copy)> <parallelism (0 for all cores)> <warmup iterations> <buffer size in bytes> <message> <transfer_rate> <sleep time when high>" << std::endl;
    return 1;
  }

  // Parse arguments
  covert_channel::contention_mode mode = covert_channel::contention_mode(argv[1]);
  std::size_t parallelism = strtoul(argv[2], nullptr, 0);
  std::size_t warmupIterations = strtoul(argv[3], nullptr, 0);
  std::size_t bufferSize = strtoul(argv[4], nullptr, 0);
  std::string message = argv[5];
  double switch_time = strtod(argv[6], nullptr);  // Convert the string to a double

  // Check if sleep_switch_time is provided, otherwise use default value of 0.0; meaning runs for whole interval
  // double sleep_switch_time = (argc > 7) ? strtod(argv[7], nullptr) : 0.0;
  double sleep_time_when_high = strtod(argv[7], nullptr);

  // Validate arguments
  if (bufferSize == 0 || message.empty())
  {
    std::cerr << "Invalid arguments" << std::endl;
    return 1;
  }

  // Set the parallelism
  if (parallelism == 0)
  {
    parallelism = omp_get_max_threads();
  }

  
  std::vector<bool> encoded;
  encoded.reserve(message.size() * 8 * 2);

  // Encode the message differential manchester encoding (0 is transition, 1 is no transition)
  // bool last = false;

  // for (char c : message)
  // {
  //   for (int i = 7; i >= 0; i--)
  //   {
  //     // Logic high
  //     if ((c >> i) & 1)
  //     {
  //       // No transition
  //       encoded.push_back(!last);
  //       encoded.push_back(!last);

  //       // Invert the last state
  //       last = !last;
  //     }
  //     // Logic low
  //     else
  //     {
  //       // Transition
  //       encoded.push_back(!last);
  //       encoded.push_back(last);

  //       // Keep the last state
  //       last = last;
  //     }
  //   }
  // }

  // 1 for high, 0 for low.
  for (char c : message)
  {
    for (int i = 7; i >= 0; i--)
    {
      // Logic high
      if ((c >> i) & 1)
      {
        // No transition
        encoded.push_back(true);
      }
      // Logic low
      else
      {
        encoded.push_back(false);
      }
    }
  }


  // Initialize the contention generator
  covert_channel::contention_generator generator(parallelism, bufferSize);

  // Warm up
  double averageBandwidth = 0.0;

  for (std::size_t iteration = 0; iteration < warmupIterations; iteration++)
  {
    // Run
    averageBandwidth += generator.run(mode);
  }
  averageBandwidth /= static_cast<double>(warmupIterations);

  // Calculate the sleep duration (in nanoseconds) based on the average bandwidth
  int64_t sleepDuration = static_cast<int64_t>(1.0 / averageBandwidth * 1e9);

  // Transmit the message
  for (bool high : encoded)
  {
    auto t0 = std::chrono::steady_clock::now();
    auto run_duration = switch_time * (1-sleep_time_when_high);  // X - Y (run duration)
    // std::cout << "run_duration" << run_duration << std::endl;
    auto startTime = std::chrono::system_clock::now();


    
    

    // Transmit high
    if (high)
    {
      //generator.run(mode);
      auto start_time = std::chrono::steady_clock::now();
      do
      {
        generator.run(mode);
        // std::cout << "Transmitter runs" << std::endl;
        // Iterate this code until X millisecond is completed. Note that this takes more than X millisecond due to last iteration.
      } while (std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now() - start_time).count() < run_duration);
      // Sleep for Y time after running for (X - Y) time

      // auto endTime2 = std::chrono::system_clock::now();
      // auto end_time_t2 = std::chrono::system_clock::to_time_t(endTime2);
      // // Convert to local time and format
      // std::tm *ltm2 = std::localtime(&end_time_t2);
      // auto end_ms2 = std::chrono::duration_cast<std::chrono::milliseconds>(endTime2.time_since_epoch()-startTime.time_since_epoch()) % 1000;
      // auto now_ms2 = std::chrono::duration_cast<std::chrono::milliseconds>(endTime2.time_since_epoch()) % 1000;
      // char time_buffer2[10]; // 
      // std::strftime(time_buffer2, sizeof(time_buffer2), "%H:%M:%S", ltm2); //std::strftime(time_buffer, sizeof(time_buffer), "%H,%M,%S", ltm);

      // std::cout << "high , before sleep "<< time_buffer2 << ":" << (now_ms2.count() < 10 ? "00" : now_ms2.count() < 100 ? "0" : "") << now_ms2.count() << std::endl;
      std::this_thread::sleep_for(std::chrono::nanoseconds(int(switch_time*sleep_time_when_high)*1000000)); // This is still not precise. I should 


      // auto endTime3 = std::chrono::system_clock::now();
      // auto end_time_t3 = std::chrono::system_clock::to_time_t(endTime3);
      // // Convert to local time and format
      // std::tm *ltm3 = std::localtime(&end_time_t3);
      // auto end_ms3 = std::chrono::duration_cast<std::chrono::milliseconds>(endTime3.time_since_epoch()-startTime.time_since_epoch()) % 1000;
      // auto now_ms3 = std::chrono::duration_cast<std::chrono::milliseconds>(endTime3.time_since_epoch()) % 1000;
      // char time_buffer3[10]; // 
      // std::strftime(time_buffer3, sizeof(time_buffer3), "%H:%M:%S", ltm3); //std::strftime(time_buffer, sizeof(time_buffer), "%H,%M,%S", ltm);

      // std::cout << "high , after sleep "<< time_buffer3 << ":" << (now_ms3.count() < 10 ? "00" : now_ms3.count() < 100 ? "0" : "") << now_ms3.count() << std::endl;
    }
    // Transmit low
    else
    {
      // sleep until X millisecond is completed. This part is precise.
      std::this_thread::sleep_for(std::chrono::nanoseconds(int(switch_time*1000000)));
    }

    auto t1 = std::chrono::steady_clock::now();

    // Update the blank duration
    sleepDuration = std::chrono::duration_cast<std::chrono::nanoseconds>(t1 - t0).count();

    auto endTime = std::chrono::system_clock::now();
    auto end_time_t = std::chrono::system_clock::to_time_t(endTime);
    // Convert to local time and format
    std::tm *ltm = std::localtime(&end_time_t);
    // Get microseconds instead of milliseconds
    auto end_us = std::chrono::duration_cast<std::chrono::microseconds>(endTime.time_since_epoch() - startTime.time_since_epoch()) % 1000000;
    auto now_us = std::chrono::duration_cast<std::chrono::microseconds>(endTime.time_since_epoch()) % 1000000;
    // Separate milliseconds and microseconds
    auto end_ms = end_us / 1000;  // Get the milliseconds part
    auto end_micro = end_us % 1000;  // Get the remaining microseconds part
    auto now_ms = now_us / 1000;
    auto now_micro = now_us % 1000;
    
    char time_buffer[10]; // 
    std::strftime(time_buffer, sizeof(time_buffer), "%H:%M:%S", ltm); //std::strftime(time_buffer, sizeof(time_buffer), "%H,%M,%S", ltm);
    
    // Print out Low/High with current time (Hour/min/second/microsecond)
    std::cout << (high ? "High " : "Low ") << time_buffer << ":"
              << (now_ms.count() < 10 ? "00" : now_ms.count() < 100 ? "0" : "") << now_ms.count() << ":"
              << (now_micro.count() < 10 ? "00" : now_micro.count() < 100 ? "0" : "") << now_micro.count()
              << std::endl;

    //std::cout << "Current time: " << time_buffer << "," << (now_ms.count() < 10 ? "00" : now_ms.count() < 100 ? "0" : "") << now_ms.count() << " (" << (high ? "High" : "Low") << " for " << sleepDuration << " ns)" << std::endl;

  }

  return 0;
}
