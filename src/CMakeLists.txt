cmake_minimum_required(VERSION 2.8)
project(PilLite)

set(Python_ADDITIONAL_VERSIONS 3.7)
find_package(PythonLibs REQUIRED)

set(SRC_PATH ${CMAKE_CURRENT_SOURCE_DIR})
set(THIRDPARTY_PATH ${CMAKE_CURRENT_SOURCE_DIR}/thirdparty)
set(STB_PATH ${THIRDPARTY_PATH}/stb)

file(GLOB MAIN_SRC ${SRC_PATH}/*.cpp)
file(GLOB MAIN_HDR ${SRC_PATH}/*.h)
source_group("main" FILES ${MAIN_SRC} ${MAIN_HDR})

file(GLOB STB_IMAGE_SRC ${STB_PATH}/*.c)
file(GLOB STB_IMAGE_HDR ${STB_PATH}/*.h)
source_group("stb_image" FILES ${STB_IMAGE_SRC} ${STB_IMAGE_HDR})

set(SRC ${MAIN_SRC} ${STB_IMAGE_SRC})
set(HDR ${MAIN_HDR} ${STB_IMAGE_HDR})

set(SIZEOF_VOIDP ${CMAKE_SIZEOF_VOID_P})
if(CMAKE_SIZEOF_VOID_P EQUAL 8)
  set(ARCH_64 TRUE)
else()
  set(ARCH_64 FALSE)
endif(CMAKE_SIZEOF_VOID_P EQUAL 8)

add_definitions(-DSTBI_NO_PSD -DSTBI_NO_TGA -DSTBI_NO_GIF -DSTBI_NO_HDR -DSTBI_NO_PIC -DSTBI_NO_PNM)
if(UNIX OR MINGW)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g -Werror")
endif()
if(WIN32 AND MSVC)
  #set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /WX")
  add_definitions(-D_CRT_SECURE_NO_WARNINGS -D_CRT_NONSTDC_NO_DEPRECATE)
  add_definitions(-DWIN32 -DHAVE_ROUND)
endif()
if(WIN32 AND ARCH_64 AND NOT MSVC)
  add_definitions(-DMS_WIN64)
endif()
if(WIN32)
  add_definitions(-DMS_NO_COREDLL -DPy_ENABLE_SHARED)
endif()

include_directories(
    ${SRC_PATH}
    ${THIRDPARTY_PATH}
    ${STB_PATH}
    ${PYTHON_INCLUDE_DIRS}
)

add_library(PilLite SHARED ${SRC} ${HDR})

target_link_libraries(PilLite
    debug ${PYTHON_LIBRARY_DEBUG}
    optimized ${PYTHON_LIBRARY_RELEASE})
