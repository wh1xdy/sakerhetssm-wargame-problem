#include <Python.h>
#include <stdlib.h>
#include <string.h>

static PyObject *buildvalue(PyObject *self, PyObject *args) {
    const char *input;
    if (!PyArg_ParseTuple(args, "s", &input))
        return NULL;

    char *buf = strdup(input);
    char *saveptr;
    char *fmt = strtok_r(buf, " ", &saveptr);
    if (!fmt) {
        free(buf);
        PyErr_SetString(PyExc_ValueError, "empty input");
        return NULL;
    }

    unsigned long a[8] = {0};
    int n = 0;
    for (; n < 8; n++) {
        char *tok = strtok_r(NULL, " ", &saveptr);
        if (!tok) break;
        a[n] = strtoul(tok, NULL, 0);
    }

    PyObject *result;
    switch (n) {
        case 0: result = Py_BuildValue(fmt); break;
        case 1: result = Py_BuildValue(fmt, a[0]); break;
        case 2: result = Py_BuildValue(fmt, a[0], a[1]); break;
        case 3: result = Py_BuildValue(fmt, a[0], a[1], a[2]); break;
        case 4: result = Py_BuildValue(fmt, a[0], a[1], a[2], a[3]); break;
        case 5: result = Py_BuildValue(fmt, a[0], a[1], a[2], a[3], a[4]); break;
        case 6: result = Py_BuildValue(fmt, a[0], a[1], a[2], a[3], a[4], a[5]); break;
        case 7: result = Py_BuildValue(fmt, a[0], a[1], a[2], a[3], a[4], a[5], a[6]); break;
        case 8: result = Py_BuildValue(fmt, a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7]); break;
        default: result = NULL; break;
    }

    free(buf);
    return result;
}

static PyMethodDef methods[] = {
    {"buildvalue", buildvalue, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT, "chall", NULL, -1, methods
};

PyMODINIT_FUNC PyInit_chall(void) {
    return PyModule_Create(&module);
}
