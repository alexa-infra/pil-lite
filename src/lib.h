#pragma once

typedef struct {
    unsigned char* buffer;
    int own_memory;
    int width;
    int height;
    int components;
} image;

typedef struct {
    unsigned char* buffer;
    unsigned int size;
} image_compressed;

image* image_open(const unsigned char* data, int size);
void image_free(image* img);

image* image_resize(const image* img, int w, int h);

image_compressed* image_to_bmp(const image* src);
image_compressed* image_to_jpg(const image* src, int quality);
image_compressed* image_to_png(const image* src);
void image_compressed_free(image_compressed* img);
