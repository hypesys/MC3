/**
 * @file Contention generator implementation
 */

#include <cmath>
#include <iostream>
#include <locale>
#include <new>
#include <stdexcept>
#include <stdlib.h>
#include <unordered_map>

#include "contention_generator.hpp"
#include "precise_sleep.hpp"

covert_channel::contention_mode::contention_mode(std::string mode)
{
  static const std::unordered_map<std::string, covert_channel::contention_mode::Value> string_to_contention_mode = {
      {"READ", covert_channel::contention_mode::Value::READ},
      {"WRITE", covert_channel::contention_mode::Value::WRITE},
      {"COPY", covert_channel::contention_mode::Value::COPY}};

  // Convert the mode to upper case
  std::string upper = mode;
  for (std::string::size_type i = 0; i < upper.length(); ++i)
  {
    upper[i] = std::toupper(upper[i], std::locale());
  }

  // Find the mode
  auto it = string_to_contention_mode.find(upper);
  if (it == string_to_contention_mode.end())
  {
    throw std::invalid_argument("Invalid contention mode");
  }

  this->value = it->second;
}

const std::string covert_channel::contention_mode::to_string()
{
  static const std::unordered_map<covert_channel::contention_mode::Value, std::string> contention_mode_to_string = {
      {covert_channel::contention_mode::Value::READ, "READ"},
      {covert_channel::contention_mode::Value::WRITE, "WRITE"},
      {covert_channel::contention_mode::Value::COPY, "COPY"}};

  return contention_mode_to_string.at(this->value);
}

covert_channel::contention_generator::contention_generator(std::size_t _concurrency, std::size_t _bufferSize)
{
  // Validate parameters
  if (_concurrency == 0 || _bufferSize < alignment || _bufferSize % alignment != 0)
  {
    throw std::invalid_argument("Buffer size must be a positive integer multiple of the alignment");
  }

  // Update state
  this->concurrency = _concurrency;
  this->bufferSize = _bufferSize;

  // Allocate the buffers
  this->readBuffers.reserve(this->concurrency);
  this->writeBuffers.reserve(this->concurrency);

  for (std::size_t threadIndex = 0; threadIndex < this->concurrency; threadIndex++)
  {
    this->readBuffers.push_back(std::aligned_alloc(alignment, _bufferSize));
    if (this->readBuffers.back() == nullptr)
    {
      throw std::bad_alloc();
    }

    this->writeBuffers.push_back(std::aligned_alloc(alignment, _bufferSize));
    if (this->writeBuffers.back() == nullptr)
    {
      throw std::bad_alloc();
    }
  }
}

double covert_channel::contention_generator::run(covert_channel::contention_mode mode, std::size_t length)
{
  // Validate parameters
  if (length > this->bufferSize)
  {
    throw std::invalid_argument("Length must be less than or equal to the buffer size");
  }

  // Get the current time
  auto t0 = std::chrono::steady_clock::now();

  // Generate contention
  switch (mode)
  {
  case covert_channel::contention_mode::Value::READ:
  {
#ifdef __AVX2__
#pragma omp parallel for
    for (std::size_t threadIndex = 0; threadIndex < this->concurrency; threadIndex++)
    {
      __asm__ __volatile__(
          // Load the size of the buffers to rcx
          "lea (%[length]), %%rcx\n"
          // Load the address of the read buffer to source index (rsi)
          "lea (%[readBuffer]), %%rsi\n"

          // Skip the loop if less than 512 bytes
          "cmp $512, %%rcx\n"
          "jl 2f\n"

          // Loop
          "1:\n"
          "vmovntdqa (%%rsi), %%ymm0\n"
          "vmovntdqa 32(%%rsi), %%ymm0\n"
          "vmovntdqa 64(%%rsi), %%ymm0\n"
          "vmovntdqa 96(%%rsi), %%ymm0\n"
          "vmovntdqa 128(%%rsi), %%ymm0\n"
          "vmovntdqa 160(%%rsi), %%ymm0\n"
          "vmovntdqa 192(%%rsi), %%ymm0\n"
          "vmovntdqa 224(%%rsi), %%ymm0\n"
          "vmovntdqa 256(%%rsi), %%ymm0\n"
          "vmovntdqa 288(%%rsi), %%ymm0\n"
          "vmovntdqa 320(%%rsi), %%ymm0\n"
          "vmovntdqa 352(%%rsi), %%ymm0\n"
          "vmovntdqa 384(%%rsi), %%ymm0\n"
          "vmovntdqa 416(%%rsi), %%ymm0\n"
          "vmovntdqa 448(%%rsi), %%ymm0\n"
          "vmovntdqa 480(%%rsi), %%ymm0\n"

          // Loop iteration
          "add $512, %%rsi\n"
          "sub $512, %%rcx\n"
          "cmp $512, %%rcx\n"
          "jge 1b\n"

          // End of the loop
          "2:\n"

          // Fence
          "sfence\n"
          : : [length] "r"(length), [readBuffer] "r"(this->readBuffers[threadIndex])
          : "rcx", "rsi", "cc", "ymm0");
    }
#elif __ARM_NEON
#pragma omp parallel for
    for (std::size_t threadIndex = 0; threadIndex < this->concurrency; threadIndex++)
    {
      __asm__ __volatile__(
          // Load the size of the buffers to x8
          "mov x8, %[length]\n"
          // Load the address of the read buffer to x9
          "mov x9, %[readBuffer]\n"

          // Skip the loop if less than 256 bytes
          "cmp x8, #256\n"
          "blt end\n"

          // Loop
          "1:\n"
          "ldnp x0, x1, [x9]\n"
          "ldnp x0, x1, [x9, #16]\n"
          "ldnp x0, x1, [x9, #32]\n"
          "ldnp x0, x1, [x9, #48]\n"
          "ldnp x0, x1, [x9, #64]\n"
          "ldnp x0, x1, [x9, #80]\n"
          "ldnp x0, x1, [x9, #96]\n"
          "ldnp x0, x1, [x9, #112]\n"
          "ldnp x0, x1, [x9, #128]\n"
          "ldnp x0, x1, [x9, #144]\n"
          "ldnp x0, x1, [x9, #160]\n"
          "ldnp x0, x1, [x9, #176]\n"
          "ldnp x0, x1, [x9, #192]\n"
          "ldnp x0, x1, [x9, #208]\n"
          "ldnp x0, x1, [x9, #224]\n"
          "ldnp x0, x1, [x9, #240]\n"

          // Loop iteration
          "sub x8, x8, #256\n"
          "cbnz x8, 1b\n"

          // End of the loop
          "2:\n"

          // Fence
          "dsb sy\n"
          : : [length] "r"(length), [readBuffer] "r"(this->readBuffers[threadIndex])
          : "cc", "x0", "x1", "x8", "x9");
    }
#else
#error "Unsupported architecture";
#endif
  }
  break;

  case covert_channel::contention_mode::Value::WRITE:
  {
#ifdef __AVX2__
#pragma omp parallel for
    for (std::size_t threadIndex = 0; threadIndex < this->concurrency; threadIndex++)
    {
      __asm__ __volatile__(
          // Load the size of the buffers to rcx
          "lea (%[length]), %%rcx\n"
          // Load the address of the write buffer to destination index (rdi)
          "lea (%[writeBuffer]), %%rdi\n"

          // Skip the loop if less than 512 bytes
          "cmp $512, %%rcx\n"
          "jl 2f\n"

          // Zero out the ymm0 register (XOR it with itself)
          "vxorps %%ymm0, %%ymm0, %%ymm0\n"

          // Loop
          "1:\n"
          "vmovntdq %%ymm0, (%%rdi)\n"
          "vmovntdq %%ymm0, 32(%%rdi)\n"
          "vmovntdq %%ymm0, 64(%%rdi)\n"
          "vmovntdq %%ymm0, 96(%%rdi)\n"
          "vmovntdq %%ymm0, 128(%%rdi)\n"
          "vmovntdq %%ymm0, 160(%%rdi)\n"
          "vmovntdq %%ymm0, 192(%%rdi)\n"
          "vmovntdq %%ymm0, 224(%%rdi)\n"
          "vmovntdq %%ymm0, 256(%%rdi)\n"
          "vmovntdq %%ymm0, 288(%%rdi)\n"
          "vmovntdq %%ymm0, 320(%%rdi)\n"
          "vmovntdq %%ymm0, 352(%%rdi)\n"
          "vmovntdq %%ymm0, 384(%%rdi)\n"
          "vmovntdq %%ymm0, 416(%%rdi)\n"
          "vmovntdq %%ymm0, 448(%%rdi)\n"
          "vmovntdq %%ymm0, 480(%%rdi)\n"

          // Loop iteration
          "add $512, %%rdi\n"
          "sub $512, %%rcx\n"
          "cmp $512, %%rcx\n"
          "jge 1b\n"

          // End of the loop
          "2:\n"

          // Fence
          "sfence\n"
          : : [length] "r"(length), [writeBuffer] "r"(this->writeBuffers[threadIndex])
          : "rcx", "rdi", "memory", "cc",
            "ymm0");
    }
#elif __ARM_NEON
#pragma omp parallel for
    for (std::size_t threadIndex = 0; threadIndex < this->concurrency; threadIndex++)
    {
      __asm__ __volatile__(
          // Load the size of the buffers to x8
          "mov x8, %[length]\n"
          // Load the address of the write buffer to x10
          "mov x10, %[writeBuffer]\n"

          // Skip the loop if less than 256 bytes
          "cmp x8, #256\n"
          "blt end\n"

          // Loop
          "1:\n"
          "stnp x0, x1, [x10]\n"
          "stnp x0, x1, [x10, #16]\n"
          "stnp x0, x1, [x10, #32]\n"
          "stnp x0, x1, [x10, #48]\n"
          "stnp x0, x1, [x10, #64]\n"
          "stnp x0, x1, [x10, #80]\n"
          "stnp x0, x1, [x10, #96]\n"
          "stnp x0, x1, [x10, #112]\n"
          "stnp x0, x1, [x10, #128]\n"
          "stnp x0, x1, [x10, #144]\n"
          "stnp x0, x1, [x10, #160]\n"
          "stnp x0, x1, [x10, #176]\n"
          "stnp x0, x1, [x10, #192]\n"
          "stnp x0, x1, [x10, #208]\n"
          "stnp x0, x1, [x10, #224]\n"
          "stnp x0, x1, [x10, #240]\n"

          // Loop iteration
          "sub x8, x8, #256\n"
          "cbnz x8, 1b\n"

          // End of the loop
          "2:\n"

          // Fence
          "dsb sy\n"
          : : [length] "r"(length), [writeBuffer] "r"(this->writeBuffers[threadIndex])
          : "memory", "cc", "x0", "x1", "x8", "x10");
    }
#else
#error "Unsupported architecture";
#endif
  }
  break;

  case covert_channel::contention_mode::Value::COPY:
  {
    // // Used to verify the inline assembly works as expected
    // for (std::size_t threadIndex = 0; threadIndex < this->_concurrency; threadIndex++)
    // {
    //   for (std::size_t item = 0; item < length / sizeof(int64_t); item++)
    //   {
    //     static_cast<int64_t *>(this->readBuffers[threadIndex])[item] = static_cast<int64_t>(item);
    //   }
    // }

#ifdef __AVX2__
#pragma omp parallel for
    for (std::size_t threadIndex = 0; threadIndex < this->concurrency; threadIndex++)
    {
      __asm__ __volatile__(
          // Load the size of the buffers to rcx
          "lea (%[length]), %%rcx\n"
          // Load the address of the read buffer to source index (rsi)
          "lea (%[readBuffer]), %%rsi\n"
          // Load the address of the write buffer to destination index (rdi)
          "lea (%[writeBuffer]), %%rdi\n"

          // Skip the loop if less than 512 bytes
          "cmp $512, %%rcx\n"
          "jl 2f\n"

          // Loop
          "1:\n"
          "vmovntdqa (%%rsi), %%ymm0\n"
          "vmovntdqa 32(%%rsi), %%ymm1\n"
          "vmovntdqa 64(%%rsi), %%ymm2\n"
          "vmovntdqa 96(%%rsi), %%ymm3\n"
          "vmovntdqa 128(%%rsi), %%ymm4\n"
          "vmovntdqa 160(%%rsi), %%ymm5\n"
          "vmovntdqa 192(%%rsi), %%ymm6\n"
          "vmovntdqa 224(%%rsi), %%ymm7\n"
          "vmovntdqa 256(%%rsi), %%ymm8\n"
          "vmovntdqa 288(%%rsi), %%ymm9\n"
          "vmovntdqa 320(%%rsi), %%ymm10\n"
          "vmovntdqa 352(%%rsi), %%ymm11\n"
          "vmovntdqa 384(%%rsi), %%ymm12\n"
          "vmovntdqa 416(%%rsi), %%ymm13\n"
          "vmovntdqa 448(%%rsi), %%ymm14\n"
          "vmovntdqa 480(%%rsi), %%ymm15\n"
          "vmovntdq %%ymm0, (%%rdi)\n"
          "vmovntdq %%ymm1, 32(%%rdi)\n"
          "vmovntdq %%ymm2, 64(%%rdi)\n"
          "vmovntdq %%ymm3, 96(%%rdi)\n"
          "vmovntdq %%ymm4, 128(%%rdi)\n"
          "vmovntdq %%ymm5, 160(%%rdi)\n"
          "vmovntdq %%ymm6, 192(%%rdi)\n"
          "vmovntdq %%ymm7, 224(%%rdi)\n"
          "vmovntdq %%ymm8, 256(%%rdi)\n"
          "vmovntdq %%ymm9, 288(%%rdi)\n"
          "vmovntdq %%ymm10, 320(%%rdi)\n"
          "vmovntdq %%ymm11, 352(%%rdi)\n"
          "vmovntdq %%ymm12, 384(%%rdi)\n"
          "vmovntdq %%ymm13, 416(%%rdi)\n"
          "vmovntdq %%ymm14, 448(%%rdi)\n"
          "vmovntdq %%ymm15, 480(%%rdi)\n"

          // Loop iteration
          "add $512, %%rsi\n"
          "add $512, %%rdi\n"
          "sub $512, %%rcx\n"
          "cmp $512, %%rcx\n"
          "jge 1b\n"

          // End of the loop
          "2:\n"

          // Fence
          "sfence\n"
          : : [length] "r"(length), [readBuffer] "r"(this->readBuffers[threadIndex]), [writeBuffer] "r"(this->writeBuffers[threadIndex])
          : "rcx", "rsi", "rdi", "memory", "cc",
            "ymm0", "ymm1", "ymm2", "ymm3", "ymm4", "ymm5", "ymm6", "ymm7",
            "ymm8", "ymm9", "ymm10", "ymm11", "ymm12", "ymm13", "ymm14", "ymm15");
    }
#elif __ARM_NEON
#pragma omp parallel for
    for (std::size_t threadIndex = 0; threadIndex < this->concurrency; threadIndex++)
    {
      __asm__ __volatile__(
          // Load the size of the buffers to x8
          "mov x8, %[length]\n"
          // Load the address of the read buffer to x9
          "mov x9, %[readBuffer]\n"
          // Load the address of the write buffer to x10
          "mov x10, %[writeBuffer]\n"

          // Skip the loop if less than 256 bytes
          "cmp x8, #256\n"
          "blt end\n"

          // Loop
          "1:\n"
          "ldnp x0, x1, [x9]\n"
          "ldnp x2, x3, [x9, #16]\n"
          "ldnp x4, x5, [x9, #32]\n"
          "ldnp x6, x7, [x9, #48]\n"
          "stnp x0, x1, [x10]\n"
          "stnp x2, x3, [x10, #16]\n"
          "stnp x4, x5, [x10, #32]\n"
          "stnp x6, x7, [x10, #48]\n"
          "ldnp x0, x1, [x9, #64]\n"
          "ldnp x2, x3, [x9, #80]\n"
          "ldnp x4, x5, [x9, #96]\n"
          "ldnp x6, x7, [x9, #112]\n"
          "stnp x0, x1, [x10, #64]\n"
          "stnp x2, x3, [x10, #80]\n"
          "stnp x4, x5, [x10, #96]\n"
          "stnp x6, x7, [x10, #112]\n"
          "ldnp x0, x1, [x9, #128]\n"
          "ldnp x2, x3, [x9, #144]\n"
          "ldnp x4, x5, [x9, #160]\n"
          "ldnp x6, x7, [x9, #176]\n"
          "stnp x0, x1, [x10, #128]\n"
          "stnp x2, x3, [x10, #144]\n"
          "stnp x4, x5, [x10, #160]\n"
          "stnp x6, x7, [x10, #176]\n"
          "ldnp x0, x1, [x9, #192]\n"
          "ldnp x2, x3, [x9, #208]\n"
          "ldnp x4, x5, [x9, #224]\n"
          "ldnp x6, x7, [x9, #240]\n"
          "stnp x0, x1, [x10, #192]\n"
          "stnp x2, x3, [x10, #208]\n"
          "stnp x4, x5, [x10, #224]\n"
          "stnp x6, x7, [x10, #240]\n"

          // Loop iteration
          "add x9, x9, #256\n"
          "add x10, x10, #256\n"
          "sub x8, x8, #256\n"
          "cbnz x8, 1b\n"

          // End of the loop
          "2:\n"

          // Fence
          "dsb sy\n"
          : : [length] "r"(length), [readBuffer] "r"(this->readBuffers[threadIndex]), [writeBuffer] "r"(this->writeBuffers[threadIndex])
          : "memory", "cc", "x0", "x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9", "x10");
    }
#else
#error "Unsupported architecture";
#endif

    // // Used to verify the inline assembly works as expected
    // for (std::size_t threadIndex = 0; threadIndex < this->_concurrency; threadIndex++)
    // {
    //   for (std::size_t item = 0; item < length / sizeof(int64_t); item++)
    //   {
    //     int64_t itemA = static_cast<int64_t *>(this->readBuffers[threadIndex])[item];
    //     int64_t itemB = static_cast<int64_t *>(this->writeBuffers[threadIndex])[item];

    //     if (itemA != itemB)
    //     {
    //       throw std::runtime_error(
    //           "Copy failed at index " + std::to_string(item) + " with value " + std::to_string(itemA) + " and " + std::to_string(itemB));
    //     }
    //   }
    // }
  }
  break;

  default:
  {
    throw std::invalid_argument("Invalid/unsupported contention mode");
  }
  break;
  }

  // Get the current time
  auto t1 = std::chrono::steady_clock::now();

  // Calculate the bandwidth
  auto elapsed = std::chrono::duration_cast<std::chrono::nanoseconds>(t1 - t0).count();
  double bandwidth = static_cast<double>(length * this->concurrency) / static_cast<double>(elapsed);

  if (mode == covert_channel::contention_mode::Value::COPY)
  {
    bandwidth *= 2;
  }

  return bandwidth;
}

double covert_channel::contention_generator::run(covert_channel::contention_mode mode)
{
  return this->run(mode, this->bufferSize);
}

std::tuple<double, std::chrono::nanoseconds> covert_channel::contention_generator::run_for(covert_channel::contention_mode mode, std::chrono::nanoseconds duration)
{
  // Validate parameters
  if (duration.count() < CONTENTION_GENERATOR_MINIMUM_DURATION)
  {
    throw std::invalid_argument("Duration is too short");
  }

  // Get the current time
  auto t0 = std::chrono::steady_clock::now();

  // Get the initial bandwidth
  double bandwidth = this->run(mode, CONTENTION_GENERATOR_INITIAL_LENGTH);
  int64_t bandwidthSamples = 1;

  // Calculate the course desired end time
  auto desiredCourseEndTime = t0 + (duration * (CONTENTION_GENERATOR_COURSE_SUBDIVISOR - CONTENTION_GENERATOR_COURSE_OFFSET)) / CONTENTION_GENERATOR_COURSE_SUBDIVISOR;

  //   // Shared variables
  //   bool sharedDone = false;

  //   // Start the threads
  // #pragma omp parallel num_threads(2) shared(sharedDone)
  //   {
  // #pragma omp sections
  //     {
  //       // Control thread
  // #pragma omp section
  //       {
  //         // Sleep for the duration
  //         precise_sleep::sleep_for(duration);

  //         // Signal the worker thread
  // #pragma omp atomic write
  //         sharedDone = true;
  //       }

  //       // Worker thread
  // #pragma omp section
  //       {
  // #pragma omp atomic read
  //         bool localDone = sharedDone;

  //         while (!localDone)
  //         {
  //           // Generate contention
  //         }
  //       }
  //     }
  //   }

  // Course run until the precise time is reached
  while (std::chrono::steady_clock::now() < desiredCourseEndTime)
  {
    // Calculate the run length (in bytes)
    std::size_t length = std::max(static_cast<std::size_t>(static_cast<double>(duration.count()) * bandwidth) / (100 * CONTENTION_GENERATOR_COURSE_SUBDIVISOR), this->bufferSize);

    // Run for the calculated length
    double newBandwidth = this->run(mode, length);

    // Update the bandwidth average
    bandwidth = (bandwidth * static_cast<double>(bandwidthSamples) + newBandwidth) / (static_cast<double>(bandwidthSamples) + 1.0f);
    bandwidthSamples++;
  }

  // // Get the epsilon (time to get the current time)
  // auto t1 = std::chrono::steady_clock::now();
  // auto t2 = std::chrono::steady_clock::now();
  // auto epsilon = t2 - t1;

  // // Calculate the precise desired end time
  // auto desiredFineEndTime = t0 + duration - epsilon;

  // // Precise run until the precise time is reached
  // while (std::chrono::steady_clock::now() < desiredFineEndTime)
  // {
  //   // Calculate the run length (in bytes)
  //   std::size_t length = std::max(static_cast<std::size_t>(static_cast<double>(duration.count()) * bandwidth) / (100 * CONTENTION_GENERATOR_FINE_SUBDIVISOR), this->bufferSize);

  //   // Run for the calculated length
  //   double newBandwidth = this->run(mode, length);

  //   // Update the bandwidth average
  //   bandwidth = (bandwidth * static_cast<double>(bandwidthSamples) + newBandwidth) / (static_cast<double>(bandwidthSamples) + 1.0f);
  //   bandwidthSamples++;
  // }

  // Get the current time
  auto t3 = std::chrono::steady_clock::now();

  // Calculate the error
  auto error = duration - (t3 - t0);

  return std::make_tuple(bandwidth, error);
}

// std::tuple<double, std::chrono::nanoseconds> covert_channel::contention_generator::run_until(covert_channel::contention_mode mode, std::chrono::time_point<std::chrono::steady_clock> time)
// {
// }

covert_channel::contention_generator::~contention_generator()
{
  // Cleanup
  for (std::size_t threadIndex = 0; threadIndex < this->concurrency; threadIndex++)
  {
    std::free(this->readBuffers[threadIndex]);
    std::free(this->writeBuffers[threadIndex]);
  }
}
