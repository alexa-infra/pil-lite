#pragma once

#if defined(_MSC_VER)
#   include <winsdkver.h>
#   if WINVER_MAXVER >= 0x0602
#       include <stdint.h>
#   else
#       include "msvc-stdint/stdint.h"
#   endif
#else
#   include <stdint.h>
#endif

namespace inf
{
  typedef int8_t      i8;
  typedef uint8_t     u8;
  typedef int16_t     i16;
  typedef uint16_t    u16;
  typedef int32_t     i32;
  typedef uint32_t    u32;
  typedef int64_t     i64;
  typedef uint64_t    u64;
}
