cmake_minimum_required(VERSION 3.10)
project(covert-channel)

# Error if running on Windows
if(WIN32)
  message(FATAL_ERROR "This project is not supported on Windows")
endif()

# Configure the C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Get source files
file(GLOB_RECURSE ALL_SOURCES src/*.hpp src/*.cpp)

set(LIBRARY_SOURCES ${ALL_SOURCES})
list(FILTER LIBRARY_SOURCES EXCLUDE REGEX "src/experiments/.*")

# Set compiler flags (See https://stackoverflow.com/a/3376483)
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

set(CMAKE_CXX_FLAGS "-Ofast -march=native -mtune=native")

set_source_files_properties(${ALL_SOURCES} PROPERTIES COMPILE_FLAGS "-Wall -Wcast-align -Wcast-qual -Wconversion -Wextra -Wformat=2 -Wpedantic -Wpointer-arith -Wshadow -Wswitch-default -Wswitch-enum -Wundef -Wunreachable-code -Wwrite-strings")
set_source_files_properties(${ALL_SOURCES} PROPERTIES LINK_FLAGS "-Wl,--no-undefined -fsanitize=address -fsanitize=leak -fsanitize=undefined")

# Include directories
include_directories(src/lib)

# Entrypoints
add_executable(receiver src/experiments/receiver/main.cpp)
add_executable(timing-consistency src/experiments/timing-consistency/main.cpp)
add_executable(transmitter src/experiments/transmitter/main.cpp)

# Libraries
add_library(covert-channel ${LIBRARY_SOURCES})
target_link_libraries(receiver covert-channel)
target_link_libraries(timing-consistency covert-channel)
target_link_libraries(transmitter covert-channel)

find_package(OpenMP REQUIRED)
target_link_libraries(covert-channel OpenMP::OpenMP_CXX)
