**PilLite** - lightweight and limited version of PIL/Pillow library

* No native external dependencies (like libjpeg, zlib etc)
* supports only trivial subset of formats (JPEG, PNG, 8bit per channel)
* No image editing functionality (as well as many other things)
* basically interface has only **open** and **save** functions


    from PilLite import Image
    img = Image.open('ich.png')
    print(img.size)
    img.save('ich.jpg')


* supports python 2/3 (tested only 2.7 and 3.3)
* note, **open** functionality supports more formats (like TGA, BMP - see notes in stb_image.h), and **save** supports only JPEG and PNG
* library is existed thanks to
  * [stb_image.h and stb_image_write.h libraries](https://github.com/nothings/stb)
  * [jpeg-compressor](https://code.google.com/p/jpeg-compressor)
  * [Boost.Python]( http://www.boost.org/doc/libs/1_57_0/libs/python/doc/)
