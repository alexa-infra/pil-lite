#include <cmath>
#include <Python.h>
#include "image.h"

using namespace inf;

typedef struct {
    PyObject_HEAD
    Image* image;
} ImagingObject;

extern PyTypeObject Imaging_Type;

PyObject* PyImagingNew(Image* imOut)
{
    ImagingObject* imagep;

    if (!imOut)
        return NULL;

    imagep = PyObject_New(ImagingObject, &Imaging_Type);
    if (imagep == NULL) {
        delete imOut;
        return NULL;
    }

    imagep->image = imOut;

    return (PyObject*) imagep;
}

static void _dealloc(ImagingObject* imagep)
{
    delete imagep->image;
    PyObject_Del(imagep);
}

#define PyImaging_Check(op) (Py_TYPE(op) == &Imaging_Type)

Image* PyImaging_AsImaging(PyObject *op)
{
    if (!PyImaging_Check(op)) {
        PyErr_BadInternalCall();
        return NULL;
    }

    return ((ImagingObject *)op)->image;
}

static PyObject* openImage(PyObject* self, PyObject* args)
{
    PyObject* python_file;

    if (!PyArg_ParseTuple(args, "O", &python_file))
        return NULL;

    PyObject* py_read = PyObject_GetAttrString(python_file, "read");
    if (py_read == NULL) {
        PyErr_SetString(PyExc_AttributeError,
            "That Python file object has no 'read' attribute");
        return NULL;
    }
    PyObject* read_buffer = PyObject_CallObject(py_read, NULL);

    const void* read_buffer_data;
    Py_ssize_t n_read;
    if (PyObject_AsReadBuffer(read_buffer,
        &read_buffer_data, &n_read) == -1) {
            PyErr_SetString(PyErr_Occurred(),
                "The method 'read' of the Python file object "
                "did not return a buffer.");
            return NULL;
    }

    Image* image = new Image((u8*)read_buffer_data, (u32)n_read);
    return PyImagingNew(image);
}

static PyObject* writeImageJpeg(PyObject* self, PyObject* args)
{
    PyObject* imgobj;
    PyObject* python_file;

    if (!PyArg_ParseTuple(args, "OO", &imgobj, &python_file))
        return NULL;

    Image* img = PyImaging_AsImaging(imgobj);

    PyObject* py_write = PyObject_GetAttrString(python_file, "write");
    if (py_write == NULL) {
        PyErr_SetString(PyExc_AttributeError,
            "That Python file object has no 'write' attribute");
        return NULL;
    }
    ImageCompressed* compress = ImageCompressed::Jpeg(*img, 100);
#if PY_VERSION_HEX < 0x03000000
    PyObject* bufObj = PyBuffer_FromReadWriteMemory((char*)compress->buffer(), compress->size());
#else
    PyObject* bufObj = PyMemoryView_FromMemory((char*)compress->buffer(), compress->size(), PyBUF_READ);
#endif
    PyObject* callArgs = PyTuple_New(1);
    PyTuple_SetItem(callArgs, 0, bufObj);
    PyObject_CallObject(py_write, callArgs);
    Py_DECREF(callArgs);

    delete compress;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* writeImagePng(PyObject* self, PyObject* args)
{
    PyObject* imgobj;
    PyObject* python_file;

    if (!PyArg_ParseTuple(args, "OO", &imgobj, &python_file))
        return NULL;

    Image* img = PyImaging_AsImaging(imgobj);

    PyObject* py_write = PyObject_GetAttrString(python_file, "write");
    if (py_write == NULL) {
        PyErr_SetString(PyExc_AttributeError,
            "That Python file object has no 'write' attribute");
        return NULL;
    }
    ImageCompressed* compress = ImageCompressed::Png(*img);
#if PY_VERSION_HEX < 0x03000000
    PyObject* bufObj = PyBuffer_FromReadWriteMemory((char*)compress->buffer(), compress->size());
#else
    PyObject* bufObj = PyMemoryView_FromMemory((char*)compress->buffer(), compress->size(), PyBUF_READ);
#endif
    PyObject* callArgs = PyTuple_New(1);
    PyTuple_SetItem(callArgs, 0, bufObj);
    PyObject_CallObject(py_write, callArgs);
    Py_DECREF(callArgs);

    delete compress;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject* img_resize(PyObject* self, PyObject* args)
{
    int width;
    int height;

    if (!PyArg_ParseTuple(args, "ii", &width, &height))
        return NULL;

    Image* img = PyImaging_AsImaging(self);

    Image* newImg = img->resize(width, height);

    return PyImagingNew(newImg);
}

static PyObject* _getattr_is_ok(ImagingObject* self, void* closure)
{
    return PyBool_FromLong(self->image->isOk());
}

static PyObject* _getattr_width(ImagingObject* self, void* closure)
{
    return PyLong_FromUnsignedLong(self->image->width());
}

static PyObject* _getattr_height(ImagingObject* self, void* closure)
{
    return PyLong_FromUnsignedLong(self->image->height());
}

static PyObject* _getattr_components(ImagingObject* self, void* closure)
{
    return PyLong_FromUnsignedLong(self->image->componentCount());
}

static PyObject* _getattr_failreason(ImagingObject* self, void* closure)
{
    return PyUnicode_FromString(self->image->failureReason());
}

static struct PyGetSetDef getsetters[] = {
    { "isOk",           (getter) _getattr_is_ok },
    { "width",          (getter) _getattr_width },
    { "height",         (getter) _getattr_height },
    { "componentCount", (getter) _getattr_components },
    { "failureReason",  (getter) _getattr_failreason },
    { NULL }
};

static struct PyMethodDef methods[] = {
    { "resize", img_resize, METH_VARARGS },
    { NULL, NULL }
};

PyTypeObject Imaging_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "Imaging",                /*tp_name*/
    sizeof(ImagingObject),    /*tp_size*/
    0,                        /*tp_itemsize*/
    /* methods */
    (destructor)_dealloc,       /*tp_dealloc*/
    0,                          /*tp_print*/
    0,                          /*tp_getattr*/
    0,                          /*tp_setattr*/
    0,                          /*tp_compare*/
    0,                          /*tp_repr*/
    0,                          /*tp_as_number */
    0,                          /*tp_as_sequence */
    0,                          /*tp_as_mapping */
    0,                          /*tp_hash*/
    0,                          /*tp_call*/
    0,                          /*tp_str*/
    0,                          /*tp_getattro*/
    0,                          /*tp_setattro*/
    0,                          /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,         /*tp_flags*/
    0,                          /*tp_doc*/
    0,                          /*tp_traverse*/
    0,                          /*tp_clear*/
    0,                          /*tp_richcompare*/
    0,                          /*tp_weaklistoffset*/
    0,                          /*tp_iter*/
    0,                          /*tp_iternext*/
    methods,                    /*tp_methods*/
    0,                          /*tp_members*/
    getsetters,                 /*tp_getset*/
};

static PyMethodDef functions[] = {
    {"openImage", (PyCFunction)openImage, METH_VARARGS},
    {"writeImageJpeg", (PyCFunction)writeImageJpeg, METH_VARARGS},
    {"writeImagePng", (PyCFunction)writeImagePng, METH_VARARGS},
    {NULL, NULL}
};

static int setup_module(PyObject* m) {
    PyObject* d = PyModule_GetDict(m);

    /* Ready object types */
    if (PyType_Ready(&Imaging_Type) < 0)
        return -1;

    return 0;
}

#if PY_VERSION_HEX >= 0x03000000
PyMODINIT_FUNC PyInit_PilLiteExt(void) {
    PyObject* m;

    static PyModuleDef module_def = {
        PyModuleDef_HEAD_INIT,
        "PilLiteExt",       /* m_name */
        NULL,               /* m_doc */
        -1,                 /* m_size */
        functions,          /* m_methods */
    };

    m = PyModule_Create(&module_def);

    if (setup_module(m) < 0)
        return NULL;

    return m;
}
#else
PyMODINIT_FUNC initPilLiteExt(void)
{
    PyObject* m = Py_InitModule("PilLiteExt", functions);
    setup_module(m);
}
#endif
