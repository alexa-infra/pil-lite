Pil-Lite
=========

*lightweight and limited version of PIL/Pillow library*

* no native external dependencies (like libjpeg, zlib etc)
* supports only trivial subset of formats (JPEG, PNG, BMP, 8 bit per channel)
* no image editing functionality (as well as many other things)
* basically interface has only *open*, *save*, *resize* and *thumbnail* functions

.. code:: python

    from PilLite import Image
    img = Image.open('ich.png')
    print(img.size)
    img.thumbnail((200, 200))
    img.save('ich.jpg')


* supports python 2/3 (tested only 2.7, 3.7)
* library is existed thanks to `stb_image.h, stb_image_write.h, stb_image_resize.h libraries <https://github.com/nothings/stb>`_

.. image:: https://travis-ci.org/alexa-infra/pil-lite.svg
   :target: https://travis-ci.org/alexa-infra/pil-lite
   :alt: Travis CI build status
