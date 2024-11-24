Pil-Lite
=========

*lightweight and limited version of PIL/Pillow library*

* no native external dependencies (like libjpeg, zlib etc)
* supports only trivial subset of formats (JPEG, PNG, BMP, 8 bit per channel)
* no image editing functionality (as well as many other things)
* basically interface has only *open*, *save*, *resize* and *thumbnail* functions
* is based on `stb_image.h, stb_image_write.h, stb_image_resize.h libraries <https://github.com/nothings/stb>`_
* provides cffi python bindings for stb_image libraries
* potentially **insecure**, should be used only with well-known sources of images
* **in production it's recommended to use PIL/Pillow libraries**

.. code:: python

    from PilLite import Image
    img = Image.open('ich.png')
    print(img.size)
    img.thumbnail((200, 200))
    img.save('ich.jpg')


Powered by ❤️
