#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <structmember.h>
#include <string.h>
#include "swisstbl.h"

static PyTypeObject ZDictType;

typedef struct {
    PyObject_HEAD
    SwissTable table;
} ZDict;

/* Utility: insert all items from a dict */
static int insert_from_dict(ZDict *self, PyObject *d) {
    PyObject *key, *value;
    Py_ssize_t pos = 0;
    while (PyDict_Next(d, &pos, &key, &value)) {
        if (swiss_set(&self->table, key, value) < 0)
            return -1;
    }
    return 0;
}
/* Utility: insert from mapping (anything with .items()) */
static int insert_from_mapping(ZDict *self, PyObject *mapping) {
    PyObject *items = PyObject_CallMethod(mapping, "items", NULL);
    if (!items) return -1;
    PyObject *iter = PyObject_GetIter(items);
    Py_DECREF(items);
    if (!iter) return -1;
    PyObject *item;
    while ((item = PyIter_Next(iter))) {
        if (!PyTuple_Check(item) || PyTuple_Size(item) != 2) {
            Py_DECREF(item); Py_DECREF(iter);
            PyErr_SetString(PyExc_ValueError, "Each item must be a 2-tuple");
            return -1;
        }
        PyObject *key = PyTuple_GetItem(item, 0);
        PyObject *value = PyTuple_GetItem(item, 1);
        if (swiss_set(&self->table, key, value) < 0) {
            Py_DECREF(item); Py_DECREF(iter); return -1;
        }
        Py_DECREF(item);
    }
    Py_DECREF(iter);
    if (PyErr_Occurred()) return -1;
    return 0;
}
/* Utility: insert from iterable of pairs */
static int insert_from_iterable(ZDict *self, PyObject *data) {
    PyObject *iter = PyObject_GetIter(data);
    if (!iter) {
        PyErr_SetString(PyExc_TypeError, "data must be dict, mapping, or iterable of pairs");
        return -1;
    }
    PyObject *item;
    while ((item = PyIter_Next(iter))) {
        if (!PyTuple_Check(item) || PyTuple_Size(item) != 2) {
            Py_DECREF(item); Py_DECREF(iter);
            PyErr_SetString(PyExc_ValueError, "Each item must be a 2-tuple");
            return -1;
        }
        PyObject *key = PyTuple_GetItem(item, 0);
        PyObject *value = PyTuple_GetItem(item, 1);
        if (swiss_set(&self->table, key, value) < 0) {
            Py_DECREF(item); Py_DECREF(iter); return -1;
        }
        Py_DECREF(item);
    }
    Py_DECREF(iter);
    if (PyErr_Occurred()) return -1;
    return 0;
}

/* Deallocate */
static void ZDict_dealloc(ZDict *self) {
    swiss_free(&self->table);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

/* New */
static PyObject *ZDict_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    ZDict *self = (ZDict *)type->tp_alloc(type, 0);
    if (self != NULL) {
        if (swiss_init(&self->table, 16) != 0) {
            Py_DECREF(self);
            return NULL;
        }
    }
    return (PyObject *)self;
}

/* Init: real dict API */
static int ZDict_init(ZDict *self, PyObject *args, PyObject *kwds) {
    PyObject *data = NULL;
    if (!PyArg_ParseTuple(args, "|O", &data))
        return -1;

    /* Insert from data arg */
    if (data) {
        if (PyDict_Check(data)) {
            if (insert_from_dict(self, data) < 0) return -1;
        } else if (PyObject_HasAttrString(data, "items")) {
            if (insert_from_mapping(self, data) < 0) return -1;
        } else {
            if (insert_from_iterable(self, data) < 0) return -1;
        }
    }
    /* Insert from keyword args */
    if (kwds && PyDict_Size(kwds) > 0) {
        if (insert_from_dict(self, kwds) < 0) return -1;
    }
    return 0;
}

/* Sequence protocol */
static Py_ssize_t ZDict_length(ZDict *self) {
    return (Py_ssize_t)self->table.size;
}
static PyObject *ZDict_getitem(ZDict *self, PyObject *key) {
    PyObject *value = swiss_get(&self->table, key);
    if (value == NULL) {
        PyErr_SetObject(PyExc_KeyError, key);
        return NULL;
    }
    return value;
}
static int ZDict_setitem(ZDict *self, PyObject *key, PyObject *value) {
    if (value == NULL) {
        return swiss_del(&self->table, key);
    } else {
        return swiss_set(&self->table, key, value);
    }
}
static int ZDict_contains(ZDict *self, PyObject *key) {
    PyObject *val = swiss_get(&self->table, key);
    if (val) {
        Py_DECREF(val);
        return 1;
    }
    return 0;
}

/* Iter (keys only) */
static PyObject *ZDict_iter(ZDict *self) {
    PyObject *keys_list = PyList_New(0);
    if (!keys_list) return NULL;
    for (size_t i = 0; i < self->table.capacity; ++i) {
        if (self->table.keys[i] && self->table.keys[i] != (PyObject*)-1) {
            PyList_Append(keys_list, self->table.keys[i]);
        }
    }
    PyObject *it = PyObject_GetIter(keys_list);
    Py_DECREF(keys_list);
    return it;
}

static PyObject *ZDict_keys(ZDict *self, PyObject *Py_UNUSED(ignored)) {
    return ZDict_iter(self);
}
static PyObject *ZDict_values(ZDict *self, PyObject *Py_UNUSED(ignored)) {
    PyObject *vals_list = PyList_New(0);
    if (!vals_list) return NULL;
    for (size_t i = 0; i < self->table.capacity; ++i) {
        if (self->table.keys[i] && self->table.keys[i] != (PyObject*)-1)
            PyList_Append(vals_list, self->table.values[i]);
    }
    return vals_list;
}
static PyObject *ZDict_items(ZDict *self, PyObject *Py_UNUSED(ignored)) {
    PyObject *items_list = PyList_New(0);
    if (!items_list) return NULL;
    for (size_t i = 0; i < self->table.capacity; ++i) {
        if (self->table.keys[i] && self->table.keys[i] != (PyObject*)-1) {
            PyObject *t = PyTuple_Pack(2, self->table.keys[i], self->table.values[i]);
            if (t) PyList_Append(items_list, t);
            Py_XDECREF(t);
        }
    }
    return items_list;
}

/* pop(key[, default]) */
static PyObject *ZDict_pop(ZDict *self, PyObject *args) {
    PyObject *key, *default_value = NULL;
    if (!PyArg_ParseTuple(args, "O|O:pop", &key, &default_value))
        return NULL;
    PyObject *val = swiss_get(&self->table, key);
    if (val) {
        if (swiss_del(&self->table, key) == 0)
            return val;
        Py_DECREF(val);
        Py_RETURN_NONE;
    } else if (default_value) {
        Py_INCREF(default_value);
        return default_value;
    } else {
        PyErr_SetObject(PyExc_KeyError, key);
        return NULL;
    }
}

/* popitem() */
static PyObject *ZDict_popitem(ZDict *self, PyObject *Py_UNUSED(ignored)) {
    for (size_t i = 0; i < self->table.capacity; ++i) {
        if (self->table.keys[i] && self->table.keys[i] != (PyObject*)-1) {
            PyObject *key = self->table.keys[i];
            PyObject *val = self->table.values[i];
            Py_INCREF(key); Py_INCREF(val);
            if (swiss_del(&self->table, key) == 0) {
                return PyTuple_Pack(2, key, val);
            }
            Py_DECREF(key); Py_DECREF(val);
        }
    }
    PyErr_SetString(PyExc_KeyError, "popitem(): dictionary is empty");
    return NULL;
}

/* setdefault(key[, default]) */
static PyObject *ZDict_setdefault(ZDict *self, PyObject *args) {
    PyObject *key, *default_value = Py_None;
    if (!PyArg_ParseTuple(args, "O|O:setdefault", &key, &default_value))
        return NULL;
    PyObject *val = swiss_get(&self->table, key);
    if (val) return val;
    if (swiss_set(&self->table, key, default_value) == 0) {
        Py_INCREF(default_value);
        return default_value;
    }
    return NULL;
}

/* update(other) */
static PyObject *ZDict_update(ZDict *self, PyObject *args, PyObject *kwds) {
    if (args && PyTuple_Size(args) > 0) {
        PyObject *other = PyTuple_GetItem(args, 0);
        if (PyDict_Check(other)) {
            if (insert_from_dict(self, other) < 0) return NULL;
        } else if (PyObject_HasAttrString(other, "items")) {
            if (insert_from_mapping(self, other) < 0) return NULL;
        } else {
            if (insert_from_iterable(self, other) < 0) return NULL;
        }
    }
    if (kwds && PyDict_Size(kwds) > 0) {
        if (insert_from_dict(self, kwds) < 0) return NULL;
    }
    Py_RETURN_NONE;
}

/* copy() */
static PyObject *ZDict_copy(ZDict *self, PyObject *Py_UNUSED(ignored)) {
    PyObject *new_obj = ZDict_new(&ZDictType, NULL, NULL);
    if (!new_obj) return NULL;
    PyObject *items = ZDict_items(self, NULL);
    if (!items) return NULL;
    ZDict_init((ZDict *)new_obj, PyTuple_Pack(1, items), NULL);
    Py_DECREF(items);
    return new_obj;
}

/* get(key[, default]) */
static PyObject *ZDict_get(ZDict *self, PyObject *args) {
    PyObject *key;
    PyObject *default_value = Py_None;
    if (!PyArg_ParseTuple(args, "O|O:get", &key, &default_value))
        return NULL;
    PyObject *value = swiss_get(&self->table, key);
    if (value == NULL) {
        Py_INCREF(default_value);
        return default_value;
    }
    return value;
}

static PyObject *ZDict_clear(ZDict *self, PyObject *Py_UNUSED(ignored)) {
    swiss_clear(&self->table);
    Py_RETURN_NONE;
}

/* Rich comparison */
static PyObject *ZDict_richcompare(PyObject *self, PyObject *other, int op) {
    if (op != Py_EQ && op != Py_NE) {
        Py_RETURN_NOTIMPLEMENTED;
    }
    ZDict *zd_self = (ZDict *)self;
    PyObject *self_items = ZDict_items(zd_self, NULL);
    PyObject *other_items = NULL;
    if (Py_TYPE(other) == &ZDictType)
        other_items = ZDict_items((ZDict *)other, NULL);
    else if (PyDict_Check(other))
        other_items = PyMapping_Items(other);
    else {
        Py_RETURN_NOTIMPLEMENTED;
    }
    int result = PyObject_RichCompareBool(self_items, other_items, Py_EQ);
    Py_DECREF(self_items);
    Py_DECREF(other_items);
    if (result < 0) return NULL;
    if (op == Py_EQ)
        return PyBool_FromLong(result);
    else
        return PyBool_FromLong(!result);
}

static Py_hash_t ZDict_hash(ZDict *self) {
    PyErr_SetString(PyExc_TypeError, "unhashable type: 'zdict'");
    return -1;
}

static PyObject *ZDict_repr(ZDict *self) {
    PyObject *items = ZDict_items(self, NULL);
    PyObject *dict_repr = PyObject_Repr(items);
    Py_DECREF(items);
    if (dict_repr == NULL)
        return NULL;
    PyObject *result = PyUnicode_FromFormat("zdict(%U)", dict_repr);
    Py_DECREF(dict_repr);
    return result;
}

static PyObject *ZDict_str(ZDict *self) {
    PyObject *py_dict = PyDict_New();
    for (size_t i = 0; i < self->table.capacity; ++i) {
        if (self->table.keys[i] && self->table.keys[i] != (PyObject*)-1) {
            PyDict_SetItem(py_dict, self->table.keys[i], self->table.values[i]);
        }
    }
    PyObject *result = PyObject_Str(py_dict);
    Py_DECREF(py_dict);
    return result;
}


/* Methods */
static PyMethodDef ZDict_methods[] = {
    {"keys",      (PyCFunction)ZDict_keys,      METH_NOARGS,  "Return a view of the dict's keys"},
    {"values",    (PyCFunction)ZDict_values,    METH_NOARGS,  "Return a view of the dict's values"},
    {"items",     (PyCFunction)ZDict_items,     METH_NOARGS,  "Return a view of the dict's items"},
    {"get",       (PyCFunction)ZDict_get,       METH_VARARGS, "Get item with default"},
    {"clear",     (PyCFunction)ZDict_clear,     METH_NOARGS,  "Remove all items"},
    {"pop",       (PyCFunction)ZDict_pop,       METH_VARARGS, "Pop an item"},
    {"popitem",   (PyCFunction)ZDict_popitem,   METH_NOARGS,  "Pop any item"},
    {"setdefault",(PyCFunction)ZDict_setdefault,METH_VARARGS, "Set default for key"},
    {"update",    (PyCFunction)ZDict_update,    METH_VARARGS | METH_KEYWORDS, "Update from another dict or iterable"},
    {"copy",      (PyCFunction)ZDict_copy,      METH_NOARGS,  "Shallow copy"},
    {NULL}  /* Sentinel */
};

static PyMappingMethods ZDict_as_mapping = {
    (lenfunc)ZDict_length,          /* mp_length */
    (binaryfunc)ZDict_getitem,      /* mp_subscript */
    (objobjargproc)ZDict_setitem    /* mp_ass_subscript */
};

static PySequenceMethods ZDict_as_sequence = {
    0,                              /* sq_length */
    0,                              /* sq_concat */
    0,                              /* sq_repeat */
    0,                              /* sq_item */
    0,                              /* sq_slice */
    0,                              /* sq_ass_item */
    0,                              /* sq_ass_slice */
    (objobjproc)ZDict_contains,     /* sq_contains */
};

static PyTypeObject ZDictType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "zdict.zdict",
    .tp_doc = "High-performance dict implementation (SwissTable)",
    .tp_basicsize = sizeof(ZDict),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = ZDict_new,
    .tp_init = (initproc)ZDict_init,
    .tp_dealloc = (destructor)ZDict_dealloc,
    .tp_repr = (reprfunc)ZDict_repr,
    .tp_str = (reprfunc)ZDict_str,
    .tp_as_mapping = &ZDict_as_mapping,
    .tp_as_sequence = &ZDict_as_sequence,
    .tp_hash = (hashfunc)ZDict_hash,
    .tp_iter = (getiterfunc)ZDict_iter,
    .tp_methods = ZDict_methods,
    .tp_richcompare = ZDict_richcompare,
};

static PyModuleDef zdictmodule = {
    PyModuleDef_HEAD_INIT,
    .m_name = "_zdictcore",
    .m_doc = "C extension for zdict using Swiss Table backend",
    .m_size = -1,
};

PyMODINIT_FUNC
PyInit__zdictcore(void)
{
    PyObject *m;
    if (PyType_Ready(&ZDictType) < 0)
        return NULL;
    m = PyModule_Create(&zdictmodule);
    if (m == NULL)
        return NULL;
    Py_INCREF(&ZDictType);
    if (PyModule_AddObject(m, "ZDict", (PyObject *)&ZDictType) < 0) {
        Py_DECREF(&ZDictType);
        Py_DECREF(m);
        return NULL;
    }
    return m;
}
