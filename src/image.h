#pragma once

#include "types.h"
#include <string>

namespace inf
{
  class Image
  {
  public:
    Image(const u8* data, u32 size);
    Image(const Image& img);
    Image(u32 w, u32 h, u32 comp);
    void operator=(const Image& img);
    ~Image();
    bool isOk() const { return buffer_ != NULL; }
    const char* failureReason() const;
    u32 width() const { return width_; }
    u32 height() const { return height_; }
    u32 componentCount() const { return componentCount_; }
    u32 rowStride() const { return width_ * componentCount_; }
    const u8* buffer() const { return buffer_; }
    u32 size() const { return width_ * height_ * componentCount_; }
    Image* resize(u32 w, u32 h) const;
  private:
    u32 width_;
    u32 height_;
    u32 componentCount_;
    u8* buffer_;
    bool ownMemory_;
  };

  class ImageCompressed
  {
  public:
    ~ImageCompressed();

    static ImageCompressed* Jpeg(const Image& img, u32 quality);
    static ImageCompressed* Png(const Image& img);
    const void* buffer() const { return buffer_; }
    u32 size() const { return size_; }
  private:
    ImageCompressed();
    void* buffer_;
    u32 size_;
  private:
    ImageCompressed(const ImageCompressed&);
    void operator=(const Image&);
  };
}
