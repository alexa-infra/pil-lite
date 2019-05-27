#include "lib.h"
#include <stdlib.h> // malloc, free
#include <string.h> // memcpy
//#include <stdio.h> // printf
#include "stb_image.h"
#include "stb_image_write.h"
#include "stb_image_resize.h"

image* image_open(const unsigned char* data, int size) {
    image* img = (image*)malloc(sizeof(image));
    img->own_memory = 0;
    img->buffer = stbi_load_from_memory(data, size,
        &img->width, &img->height, &img->components, 0);
    return img;
}

void image_free(image* img) {
    if (!img)
        return;
    if (img->own_memory)
        free(img->buffer);
    else
        stbi_image_free(img->buffer);
    free(img);
}

image* image_resize(const image* src, int w, int h) {
    image* dst = (image*)malloc(sizeof(image));
    dst->own_memory = 1;
    dst->width = w;
    dst->height = h;
    dst->components = src->components;
    dst->buffer = (unsigned char*)malloc(w * h * src->components);
    stbir_resize_uint8(src->buffer, src->width, src->height, src->width * src->components,
        dst->buffer, dst->width, dst->height, dst->width * dst->components,
        dst->components);
    return dst;
}

static void write_bytes(void* context, void* data, int len) {
    image_compressed* img = (image_compressed*)context;
    if (img->buffer) {
        memcpy(img->buffer + img->size, data, len);
    }
    img->size += len;
}

image_compressed* image_to_png(const image* src) {
    image_compressed* dst = (image_compressed*)malloc(sizeof(image_compressed));
    dst->buffer = NULL;
    dst->size = 0;
    stbi_write_png_to_func(write_bytes, dst,
        src->width, src->height, src->components,
        src->buffer, src->width * src->components);
    dst->buffer = (unsigned char*)malloc(dst->size);
    dst->size = 0;
    stbi_write_png_to_func(write_bytes, dst,
        src->width, src->height, src->components,
        src->buffer, src->width * src->components);
    return dst;
}

image_compressed* image_to_jpg(const image* src, int quality) {
    image_compressed* dst = (image_compressed*)malloc(sizeof(image_compressed));
    dst->buffer = NULL;
    dst->size = 0;
    stbi_write_jpg_to_func(write_bytes, dst,
        src->width, src->height, src->components,
        src->buffer, quality);
    dst->buffer = (unsigned char*)malloc(dst->size);
    dst->size = 0;
    stbi_write_jpg_to_func(write_bytes, dst,
        src->width, src->height, src->components,
        src->buffer, quality);
    return dst;
}

image_compressed* image_to_bmp(const image* src) {
    image_compressed* dst = (image_compressed*)malloc(sizeof(image_compressed));
    dst->buffer = NULL;
    dst->size = 0;
    stbi_write_bmp_to_func(write_bytes, dst,
        src->width, src->height, src->components,
        src->buffer);
    dst->buffer = (unsigned char*)malloc(dst->size);
    dst->size = 0;
    stbi_write_bmp_to_func(write_bytes, dst,
        src->width, src->height, src->components,
        src->buffer);
    return dst;
}

void image_compressed_free(image_compressed* img) {
    if (!img)
        return;
    free(img->buffer);
    free(img);
}
