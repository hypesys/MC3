/**
 * @file Contention generator definition
 */

#pragma once

#include <chrono>
#include <cstddef>
#include <cstdint>
#include <string>
#include <tuple>
#include <vector>

#ifdef __AVX2__
/**
 * @brief Vector lane size
 */
#define CONTENTION_GENERATOR_LANE_SIZE 32
#elif __ARM_NEON
/**
 * @brief Vector lane size
 */
#define CONTENTION_GENERATOR_LANE_SIZE 16
#else
/**
 * @brief Vector lane size
 */
#define CONTENTION_GENERATOR_LANE_SIZE 16
#endif

/**
 * @brief Minimum run duration (in nanoseconds)
 *
 * @details This should be large enough to ensure that it's incredibly unlikely
 * that the contention generator is run for a duration shorter than the
 * duration of calling the functions without them actually running (and just
 * delaying things with the overhead of the functions, such as the error
 * calcuation). Currently this is empirically derived by running the contention
 * generator with a duration of 0 and observing the error (which is the total
 * overhead of the function) and then using a normal distribution to calculate
 * a value that has a Z-score >= 4 (which is gives an equivalent probability of
 * no more than 1 in 30,000 that the function will be called and run for longer
 * than the duration of the function overhead itself).
 */
#define CONTENTION_GENERATOR_MINIMUM_DURATION 500

/**
 * @brief Initial run length (in bytes)
 */
#define CONTENTION_GENERATOR_INITIAL_LENGTH 10000000

/**
 * @brief Course run subdivision
 *
 * @details The total estimated run length is divided by this value to
 * determine the individual run lengths. A higher value will result in more,
 * shorter runs which increases the duration accuracy but decreases the
 * contention consistency (since we need to stop more frequently to check the
 * time).
 */
#define CONTENTION_GENERATOR_COURSE_SUBDIVISOR 100

/**
 * @brief Course run offset (in subdivisions)
 *
 * @details This is the number of course run subdivisions to run as fine runs
 * instead. A higher value will result in a more accurate run but will also
 * increase the overhead of the function.
 */
#define CONTENTION_GENERATOR_COURSE_OFFSET 0

/**
 * @brief Fine run subdivision
 *
 * @details The total estimated run length after the course run is divided by
 * this value to determine the individual run lengths. A higher value will
 * result in more, shorter runs which increases the duration accuracy but
 * decreases the contention consistency (since we need to stop more frequently
 * to check the time).
 */
#define CONTENTION_GENERATOR_FINE_SUBDIVISOR 1000

/**
 * @brief Covert channel namespace
 */
namespace covert_channel
{
  /**
   * @brief Contention mode class
   */
  class contention_mode
  {
  public:
    /**
     * @brief Contention mode
     */
    enum Value
    {
      /**
       * @brief Only read from the buffer
       */
      READ,

      /**
       * @brief Only write to the buffer
       */
      WRITE,

      /**
       * @brief Read from and write to the buffer
       */
      COPY
    };

    /**
     * @brief Contention mode value constructor
     * @param _value Enum value
     */
    constexpr contention_mode(Value _value) : value(_value) {}

    /**
     * @brief Contention mode string constructor
     * @param mode Contention mode string
     * @throws std::invalid_argument Invalid contention mode
     */
    contention_mode(std::string mode);

    /**
     * @brief Contention mode value operator
     */
    constexpr operator Value() const { return value; }

    /**
     * @brief Contention mode boolean operator (deleted)
     */
    explicit operator bool() const = delete;

    /**
     * @brief Convert a string to a contention mode
     * @param mode Contention mode string
     * @return Contention mode
     */
    const std::string to_string();

  private:
    /**
     * @brief Contention mode
     */
    Value value;
  };

  /**
   * @brief Contention generator class
   */
  class contention_generator
  {
  private:
    /**
     * @brief Buffer alignment (in bytes)
     */
    static const std::size_t alignment = 16 * CONTENTION_GENERATOR_LANE_SIZE;

    /**
     * @brief Concurrency level
     */
    std::size_t concurrency;

    /**
     * @brief Buffer size (in bytes)
     */
    std::size_t bufferSize;

    /**
     * @brief Read buffers
     */
    std::vector<void *> readBuffers;

    /**
     * @brief Write buffers
     */
    std::vector<void *> writeBuffers;

    /**
     * @brief Run the contention generator for the specified length
     * @param mode Contention mode
     * @param length Length to run for (in bytes; must be less than or equal to the buffer size)
     * @return Bandwidth (GB/s)
     */
    double run(contention_mode mode, std::size_t length);

  public:
    /**
     * @brief Construct a new contention generator object
     * @param concurrency Concurrency level
     * @param bufferSize Buffer size (in bytes)
     */
    contention_generator(std::size_t _concurrency, std::size_t _bufferSize);

    /**
     * @brief Run the contention generator for the total buffer size
     * @param mode Contention mode
     * @return Bandwidth (GB/s)
     */
    double run(contention_mode mode);

    /**
     * @brief Run the contention generator for a duration
     * @param mode Contention mode
     * @param duration Duration to run for
     * @return Bandwidth (GB/s) and error
     */
    std::tuple<double, std::chrono::nanoseconds> run_for(contention_mode mode, std::chrono::nanoseconds duration);

    // /**
    //  * @brief Run the contention generator until a time
    //  * @param mode Contention mode
    //  * @param time Time to run until
    //  * @return Bandwidth (GB/s) and error
    //  */
    // std::tuple<double, std::chrono::nanoseconds> run_until(contention_mode mode, std::chrono::time_point<std::chrono::steady_clock> time);

    /**
     * @brief Destroy the contention generator object
     */
    ~contention_generator();
  };
} // namespace contention_generator
