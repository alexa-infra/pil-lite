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

image* image_new(int w, int h, int components);
unsigned int image_get_pixel(const image* src, int x, int y);
void image_put_pixel(image* dst, int x, int y, unsigned int color);
void image_draw_rect(image* dst, int x1, int y1, int w, int h, unsigned int color);

image* image_new_raw(const unsigned char* data, int w, int h, int components);
