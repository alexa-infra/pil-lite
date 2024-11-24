#include "lib.h"
#include <stdlib.h> // malloc, free
#include <string.h> // memcpy
//#include <stdio.h> // printf
#include "stb_image.h"
#include "stb_image_write.h"
#include "stb_image_resize2.h"

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
    image* dst = image_new(w, h, src->components);
    stbir_resize_uint8_linear(src->buffer, src->width, src->height, src->width * src->components,
        dst->buffer, dst->width, dst->height, dst->width * dst->components,
        (stbir_pixel_layout)dst->components);
    return dst;
}

static void write_bytes(void* context, void* data, int len) {
    image_compressed* img = (image_compressed*)context;
    if (img->buffer) {
        memcpy(img->buffer + img->size, data, len);
    }
    img->size += len;
}

static image_compressed* image_compressed_new() {
    image_compressed* dst = (image_compressed*)malloc(sizeof(image_compressed));
    dst->buffer = NULL;
    dst->size = 0;
    return dst;
}

image_compressed* image_to_png(const image* src) {
    image_compressed* dst = image_compressed_new();
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
    image_compressed* dst = image_compressed_new();
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
    image_compressed* dst = image_compressed_new();
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

image* image_new(int w, int h, int components) {
    image* dst = (image*)malloc(sizeof(image));
    dst->own_memory = 1;
    dst->width = w;
    dst->height = h;
    dst->components = components;
    dst->buffer = (unsigned char*)malloc(w * h * components);
    return dst;
}

static int point_in_image(const image* src, int x, int y) {
    if (x < 0 || x >= src->width)
        return 0;
    if (y < 0 || y >= src->height)
        return 0;
    return 1;
}

unsigned int image_get_pixel(const image* src, int x, int y) {
    if (!point_in_image(src, x, y))
        return (unsigned char)-1;
    int coord = (src->width * y + x) * src->components;
    if (src->components == 3) {
        unsigned char r = src->buffer[coord + 0];
        unsigned char g = src->buffer[coord + 1];
        unsigned char b = src->buffer[coord + 2];
        return (r << 16) | (g << 8) | (b << 0);
    }
    if (src->components == 4) {
        unsigned char r = src->buffer[coord + 0];
        unsigned char g = src->buffer[coord + 1];
        unsigned char b = src->buffer[coord + 2];
        unsigned char a = src->buffer[coord + 3];
        return (r << 24) | (g << 16) | (b << 8) | (a << 0);
    }
    if (src->components == 1) {
        return src->buffer[coord];
    }
    if (src->components == 2) {
        unsigned char l = src->buffer[coord + 0];
        unsigned char a = src->buffer[coord + 1];
        return (l << 8) | (a << 0);
    }
    return (unsigned int)-1;
}

void image_put_pixel(image* dst, int x, int y, unsigned int color) {
    if (!point_in_image(dst, x, y))
        return;
    int coord = (dst->width * y + x) * dst->components;
    if (dst->components == 3) {
        dst->buffer[coord + 0] = (color >> 16) & 0xff; // r
        dst->buffer[coord + 1] = (color >>  8) & 0xff; // g
        dst->buffer[coord + 2] = (color >>  0) & 0xff; // b
    }
    else if (dst->components == 2) {
        dst->buffer[coord + 0] = (color >> 8) & 0xff; // l
        dst->buffer[coord + 1] = (color >> 0) & 0xff; // a
    }
    else if (dst->components == 1) {
        dst->buffer[coord] = color & 0xff;
    }
    else if (dst->components == 4) {
        dst->buffer[coord + 0] = (color >> 24) & 0xff; // r
        dst->buffer[coord + 1] = (color >> 16) & 0xff; // g
        dst->buffer[coord + 2] = (color >>  8) & 0xff; // b
        dst->buffer[coord + 3] = (color >>  0) & 0xff; // a
    }
}

void image_draw_rect(image* dst, int x1, int y1, int w, int h, unsigned int color) {
    for (int y = 0; y < h; y++) {
        for (int x = 0; x < w; x++) {
            image_put_pixel(dst, x1 + x, y1 + y, color);
        }
    }
}

image* image_new_raw(const unsigned char* data, int w, int h, int components) {
    image* dst = (image*)malloc(sizeof(image));
    dst->own_memory = 1;
    dst->width = w;
    dst->height = h;
    dst->components = components;
    dst->buffer = (unsigned char*)malloc(w * h * components);
    memcpy(dst->buffer, data, w * h * components);
    return dst;
}
