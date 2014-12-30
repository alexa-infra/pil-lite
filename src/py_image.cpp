#include <cmath>
#include <boost/python.hpp>
#include "image.h"

using namespace boost::python;
using namespace inf;

Image* openImage(object& python_file)
{
    object py_read = getattr(python_file, "read", object());
    if (py_read == object()) {
        PyErr_SetString(PyExc_AttributeError,
            "That Python file object has no 'read' attribute");
        throw_error_already_set();
    }

    object read_buffer = py_read();
    const void* read_buffer_data;
    Py_ssize_t n_read;
    if (PyObject_AsReadBuffer(read_buffer.ptr(),
        &read_buffer_data, &n_read) == -1) {
        PyErr_SetString(PyErr_Occurred(),
            "The method 'read' of the Python file object "
            "did not return a buffer.");
        throw_error_already_set();
    }
    Image* image = new Image((u8*)read_buffer_data, n_read);
    return image;
}

void writeImageJpeg(Image* img, object& python_file)
{
    object py_write = getattr(python_file, "write", object());
    if (py_write == object()) {
        PyErr_SetString(PyExc_AttributeError,
            "That Python file object has no 'write' attribute");
        throw_error_already_set();
    }
    ImageCompressed* compress = ImageCompressed::Jpeg(*img, 100);
#if PY_VERSION_HEX < 0x03000000
    PyObject* bufObj = PyBuffer_FromReadWriteMemory((char*)compress->buffer(), compress->size());
#else
    PyObject* bufObj = PyMemoryView_FromMemory((char*)compress->buffer(), compress->size(), PyBUF_READ);
#endif
    object buf = object(boost::python::handle<PyObject>(bufObj));
    py_write(buf);
    delete compress;
}

void writeImagePng(Image* img, object& python_file)
{
    object py_write = getattr(python_file, "write", object());
    if (py_write == object()) {
        PyErr_SetString(PyExc_AttributeError,
            "That Python file object has no 'write' attribute");
        throw_error_already_set();
    }
    ImageCompressed* compress = ImageCompressed::Png(*img);
#if PY_VERSION_HEX < 0x03000000
    PyObject* bufObj = PyBuffer_FromReadWriteMemory((char*)compress->buffer(), compress->size());
#else
    PyObject* bufObj = PyMemoryView_FromMemory((char*)compress->buffer(), compress->size(), PyBUF_READ);
#endif
    object buf = object(boost::python::handle<PyObject>(bufObj));
    py_write(buf);
    delete compress;
}

BOOST_PYTHON_MODULE(PilLiteExt)
{
    def("openImage", &openImage, return_value_policy<manage_new_object>());
    def("writeImageJpeg", &writeImageJpeg);
    def("writeImagePng", &writeImagePng);
    class_<Image>("Image", no_init)
        .add_property("isOk", &Image::isOk)
        .add_property("width", &Image::width)
        .add_property("height", &Image::height)
        .add_property("componentCount", &Image::componentCount)
        .add_property("failureReason", &Image::failureReason)
        .def("resize", &Image::resize, return_value_policy<manage_new_object>())
        ;
}
