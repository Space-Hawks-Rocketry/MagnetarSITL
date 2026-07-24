cmake_minimum_required(VERSION 3.31)
project(FlightComputer)

set(CMAKE_CXX_STANDARD 20)        # Options: 11, 14, 17, 20, 23, 26
set(CMAKE_CXX_STANDARD_REQUIRED ON) # Forces error if the compiler doesn't support it

# Recursive globbing (includes subfolders)
file(GLOB_RECURSE SOURCES "src/*.cpp")

# Add the found files to your executable or library
add_executable(FlightComputer ${SOURCES})

# Add necessary libraries
target_link_libraries(FlightComputer PRIVATE zmq)


# 1. Recursively find all header files (.h, .hpp, etc.)
file(GLOB_RECURSE ALL_HEADERS "${CMAKE_CURRENT_SOURCE_DIR}/include/*.h" "${CMAKE_CURRENT_SOURCE_DIR}/include/*.hpp")

# 2. Extract unique directories from those file paths
set(INCLUDE_DIRS "")
foreach(HEADER_FILE ${ALL_HEADERS})
    get_filename_component(HEADER_DIR ${HEADER_FILE} DIRECTORY)
    list(APPEND INCLUDE_DIRS ${HEADER_DIR})
endforeach()

# 3. Remove duplicate directory paths
list(REMOVE_DUPLICATES INCLUDE_DIRS)

# 4. Add the directories to your target
# target_include_directories(FlightComputer PRIVATE ${INCLUDE_DIRS})
target_include_directories(FlightComputer PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)