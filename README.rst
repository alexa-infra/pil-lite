Pil-Lite
=========

*lightweight and limited version of PIL/Pillow library*

* no native external dependencies (like libjpeg, zlib etc)
* supports only trivial subset of formats (JPEG, PNG, 8bit per channel)
* no image editing functionality (as well as many other things)
* basically interface has only *open*, *save*, *resize* and *thumbnail* functions

.. code:: python

    from PilLite import Image
    img = Image.open('ich.png')
    print(img.size)
    img.thumbnail((200, 200))
    img.save('ich.jpg')


* supports python 2/3 (tested only 2.7, 3.3 and 3.4)
* note, *open* functionality supports more formats (like TGA, BMP - see notes in stb_image.h), and *save* supports only JPEG and PNG
* library is existed thanks to

  * `stb_image.h, stb_image_write.h, stb_image_resize.h libraries <https://github.com/nothings/stb>`_
  * `jpeg-compressor <https://code.google.com/p/jpeg-compressor>`_
  * `Boost.Python <http://www.boost.org/doc/libs/1_57_0/libs/python/doc/>`_

.. image:: https://travis-ci.org/alexa-infra/pil-lite.svg
   :target: https://travis-ci.org/alexa-infra/pil-lite
   :alt: Travis CI build status

