#include "image.h"
#include <string.h>
#include <stdlib.h>

#include "stb_image.h"
#include "stb_image_write.h"
#include "stb_image_resize.h"

namespace inf {

Image::Image(const u8* data, u32 size)
  : width_(0u)
  , height_(0u)
  , componentCount_(0u)
  , ownMemory_(false)
{
  buffer_ = stbi_load_from_memory(data, size,
    reinterpret_cast<int*>(&width_), reinterpret_cast<int*>(&height_),
    reinterpret_cast<int*>(&componentCount_), 0);
}

Image::Image(u32 w, u32 h, u32 comp)
  : width_(w)
  , height_(h)
  , componentCount_(comp)
  , ownMemory_(true)
{
  u32 s = width_ * height_ * componentCount_;
  buffer_ = new unsigned char[s];
}

Image::Image(const Image& img)
  : width_(img.width_)
  , height_(img.height_)
  , componentCount_(img.componentCount_)
  , ownMemory_(true)
{
  u32 s = width_ * height_ * componentCount_;
  buffer_ = new unsigned char[s];
  memcpy(buffer_, img.buffer_, s);
}

void Image::operator=(const Image& img)
{
  if (ownMemory_) {
    delete[] buffer_;
  }
  else {
    if (buffer_ != NULL)
      stbi_image_free(buffer_);
  }
  width_ = img.width_;
  height_ = img.height_;
  componentCount_ = img.componentCount_;
  ownMemory_ = true;
  u32 s = width_ * height_ * componentCount_;
  buffer_ = new unsigned char[s];
  memcpy(buffer_, img.buffer_, s);
}

Image::~Image()
{
  if (ownMemory_) {
    delete[] buffer_;
  } else {
    if (buffer_ != NULL)
      stbi_image_free(buffer_);
  }
}

const char* Image::failureReason() const
{
  return stbi_failure_reason();
}

Image* Image::resize(u32 w, u32 h) const
{
  Image* img = new Image(w, h, componentCount_);
  stbir_resize_uint8(buffer_, width_, height_, rowStride(),
    img->buffer_, w, h, img->rowStride(), componentCount_);
  return img;
}

struct Temp {
  void* buffer;
  int len;
};

static void write_bytes(void *context, void *data, int len)
{
  Temp* tmp = reinterpret_cast<Temp*>(context);
  if (tmp->buffer) {
    memcpy(tmp->buffer + tmp->len, data, len);
  }
  tmp->len += len;
}

static void* compress_png(const Image& img, u32 &size)
{
  Temp tmp;
  tmp.buffer = NULL;
  tmp.len = 0;
  stbi_write_png_to_func(write_bytes, &tmp,
      img.width(), img.height(), img.componentCount(),
      img.buffer(), img.rowStride());
  size = tmp.len;
  if (tmp.len == 0)
    return NULL;
  tmp.buffer = malloc(tmp.len);
  tmp.len = 0;
  stbi_write_png_to_func(write_bytes, &tmp,
      img.width(), img.height(), img.componentCount(),
      img.buffer(), img.rowStride());
  return tmp.buffer;
}

static void* compress_jpeg(const Image& img, u32 &size, u32 quality)
{
  Temp tmp;
  tmp.buffer = NULL;
  tmp.len = 0;
  stbi_write_jpg_to_func(write_bytes, &tmp,
      img.width(), img.height(), img.componentCount(),
      img.buffer(), quality);
  size = tmp.len;
  if (tmp.len == 0)
    return NULL;
  tmp.buffer = malloc(tmp.len);
  tmp.len = 0;
  stbi_write_jpg_to_func(write_bytes, &tmp,
      img.width(), img.height(), img.componentCount(),
      img.buffer(), quality);
  return tmp.buffer;
}

static void free_compress_image(void *buffer)
{
  free(buffer);
}

ImageCompressed::ImageCompressed()
  : buffer_(NULL)
  , size_(0u)
{
}

ImageCompressed::~ImageCompressed()
{
  free_compress_image(buffer_);
}

ImageCompressed* ImageCompressed::Jpeg(const Image& img, u32 quality)
{
  ImageCompressed* target = new ImageCompressed();
  target->buffer_ = compress_jpeg(img, target->size_, quality);
  return target;
}

ImageCompressed* ImageCompressed::Png(const Image& img)
{
  ImageCompressed* target = new ImageCompressed();
  target->buffer_ = compress_png(img, target->size_);
  return target;
}

} // namespace inf
