#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <structmember.h>
#include <string.h>
#include "_zdict_modes/zdict_internal.h"

/* Forward declarations */
static PyTypeObject ZDictType;

/* ZDict object structure */
typedef struct {
    PyObject_HEAD
    PyObject *data;      /* Internal dict storage */
    int mode;            /* Current mode */
    Py_hash_t hash;      /* Cached hash for immutable mode */
    int hash_computed;   /* Whether hash has been computed */
} ZDict;

/* Mode constants */
enum {
    MODE_MUTABLE = 0,
    MODE_IMMUTABLE = 1,
    MODE_READONLY = 2,
    MODE_INSERT = 3,
    MODE_ARENA = 4
};

/* Mode names for error messages */
static const char *mode_names[] = {
    "mutable",
    "immutable",
    "readonly",
    "insert",
    "arena"
};

/* Helper function to get mode from string */
static int get_mode_from_string(const char *mode_str) {
    if (strcmp(mode_str, "mutable") == 0) return MODE_MUTABLE;
    if (strcmp(mode_str, "immutable") == 0) return MODE_IMMUTABLE;
    if (strcmp(mode_str, "readonly") == 0) return MODE_READONLY;
    if (strcmp(mode_str, "insert") == 0) return MODE_INSERT;
    if (strcmp(mode_str, "arena") == 0) return MODE_ARENA;
    return -1;
}

/* Check if mutation is allowed */
static int check_mutable(ZDict *self) {
    if (self->mode == MODE_IMMUTABLE || self->mode == MODE_READONLY || self->mode == MODE_INSERT) {
        PyErr_Format(PyExc_TypeError, 
                     "Cannot modify zdict in '%s' mode", 
                     mode_names[self->mode]);
        return 0;
    }
    return 1;
}

/* Check if insertion is allowed */
static int check_insertable(ZDict *self) {
    if (self->mode == MODE_READONLY || self->mode == MODE_IMMUTABLE) {
        PyErr_Format(PyExc_TypeError,
                     "Cannot insert into zdict in '%s' mode",
                     mode_names[self->mode]);
        return 0;
    }
    return 1;
}

/* ZDict methods */
static void
ZDict_dealloc(ZDict *self)
{
    Py_XDECREF(self->data);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject *
ZDict_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    ZDict *self;
    self = (ZDict *)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->data = PyDict_New();
        if (self->data == NULL) {
            Py_DECREF(self);
            return NULL;
        }
        self->mode = MODE_MUTABLE;
        self->hash = 0;
        self->hash_computed = 0;
    }
    return (PyObject *)self;
}

static int
ZDict_init(ZDict *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"data", "mode", NULL};
    PyObject *data = NULL;
    const char *mode_str = "mutable";
    
    /* Parse only the known arguments first */
    PyObject *filtered_kwds = PyDict_New();
    if (filtered_kwds == NULL)
        return -1;
        
    if (kwds != NULL) {
        PyObject *mode_obj = PyDict_GetItemString(kwds, "mode");
        if (mode_obj != NULL) {
            if (PyDict_SetItemString(filtered_kwds, "mode", mode_obj) < 0) {
                Py_DECREF(filtered_kwds);
                return -1;
            }
        }
    }
    
    if (!PyArg_ParseTupleAndKeywords(args, filtered_kwds, "|Os", kwlist, &data, &mode_str)) {
        Py_DECREF(filtered_kwds);
        return -1;
    }
    Py_DECREF(filtered_kwds);
    
    /* Set mode */
    int mode = get_mode_from_string(mode_str);
    if (mode == -1) {
        PyErr_Format(PyExc_ValueError, "Unsupported mode '%s'", mode_str);
        return -1;
    }
    self->mode = mode;
    
    /* Initialize data */
    if (data != NULL) {
        if (PyDict_Check(data)) {
            if (PyDict_Update(self->data, data) < 0)
                return -1;
        } else {
            /* Check if it has items() method (mapping-like) */
            PyObject *items_method = PyObject_GetAttrString(data, "items");
            if (items_method != NULL) {
                Py_DECREF(items_method);
                PyObject *items = PyMapping_Items(data);
                if (items == NULL)
                    return -1;
                
                Py_ssize_t size = PyList_Size(items);
                for (Py_ssize_t i = 0; i < size; i++) {
                    PyObject *item = PyList_GetItem(items, i);
                    PyObject *key = PyTuple_GetItem(item, 0);
                    PyObject *value = PyTuple_GetItem(item, 1);
                    if (PyDict_SetItem(self->data, key, value) < 0) {
                        Py_DECREF(items);
                        return -1;
                    }
                }
                Py_DECREF(items);
            } else {
                /* Clear the AttributeError */
                PyErr_Clear();
                
                /* Try as iterable of pairs */
                PyObject *iter = PyObject_GetIter(data);
                if (iter == NULL) {
                    PyErr_SetString(PyExc_TypeError, "data must be dict, mapping, or iterable of pairs");
                    return -1;
                }
                
                PyObject *item;
                while ((item = PyIter_Next(iter)) != NULL) {
                    if (!PyTuple_Check(item) || PyTuple_Size(item) != 2) {
                        Py_DECREF(item);
                        Py_DECREF(iter);
                        PyErr_SetString(PyExc_ValueError, "Each item must be a 2-tuple");
                        return -1;
                    }
                    
                    PyObject *key = PyTuple_GetItem(item, 0);
                    PyObject *value = PyTuple_GetItem(item, 1);
                    if (PyDict_SetItem(self->data, key, value) < 0) {
                        Py_DECREF(item);
                        Py_DECREF(iter);
                        return -1;
                    }
                    Py_DECREF(item);
                }
                Py_DECREF(iter);
                
                if (PyErr_Occurred())
                    return -1;
            }
        }
    }
    
    /* Add keyword arguments */
    if (kwds != NULL) {
        PyObject *key, *value;
        Py_ssize_t pos = 0;
        
        while (PyDict_Next(kwds, &pos, &key, &value)) {
            const char *key_str = PyUnicode_AsUTF8AndSize(key, NULL);
            if (key_str && (strcmp(key_str, "data") == 0 || strcmp(key_str, "mode") == 0))
                continue;
            
            if (PyDict_SetItem(self->data, key, value) < 0)
                return -1;
        }
    }
    
    return 0;
}

/* Sequence protocol */
static Py_ssize_t
ZDict_length(ZDict *self)
{
    return PyDict_Size(self->data);
}

static PyObject *
ZDict_getitem(ZDict *self, PyObject *key)
{
    PyObject *value = PyDict_GetItem(self->data, key);
    if (value == NULL) {
        PyErr_SetObject(PyExc_KeyError, key);
        return NULL;
    }
    Py_INCREF(value);
    return value;
}

static int
ZDict_setitem(ZDict *self, PyObject *key, PyObject *value)
{
    if (value == NULL) {
        /* Delete item */
        if (!check_mutable(self))
            return -1;
        return PyDict_DelItem(self->data, key);
    } else {
        /* Set item */
        if (self->mode == MODE_INSERT && PyDict_Contains(self->data, key)) {
            PyErr_SetString(PyExc_TypeError, "Cannot update existing keys in 'insert' mode");
            return -1;
        }
        
        if (!check_insertable(self))
            return -1;
        
        return PyDict_SetItem(self->data, key, value);
    }
}

static int
ZDict_contains(ZDict *self, PyObject *key)
{
    return PyDict_Contains(self->data, key);
}

/* Iterator support */
static PyObject *
ZDict_iter(ZDict *self)
{
    return PyObject_GetIter(self->data);
}

/* Methods */
static PyObject *
ZDict_keys(ZDict *self, PyObject *Py_UNUSED(ignored))
{
    return PyDict_Keys(self->data);
}

static PyObject *
ZDict_values(ZDict *self, PyObject *Py_UNUSED(ignored))
{
    return PyDict_Values(self->data);
}

static PyObject *
ZDict_items(ZDict *self, PyObject *Py_UNUSED(ignored))
{
    return PyDict_Items(self->data);
}

static PyObject *
ZDict_get(ZDict *self, PyObject *args)
{
    PyObject *key;
    PyObject *default_value = Py_None;
    
    if (!PyArg_ParseTuple(args, "O|O:get", &key, &default_value))
        return NULL;
    
    PyObject *value = PyDict_GetItem(self->data, key);
    if (value == NULL) {
        Py_INCREF(default_value);
        return default_value;
    }
    Py_INCREF(value);
    return value;
}

static PyObject *
ZDict_pop(ZDict *self, PyObject *args)
{
    PyObject *key;
    PyObject *default_value = NULL;
    
    if (!PyArg_ParseTuple(args, "O|O:pop", &key, &default_value))
        return NULL;
    
    if (!check_mutable(self))
        return NULL;
    
    PyObject *value = PyDict_GetItem(self->data, key);
    if (value == NULL) {
        if (default_value == NULL) {
            PyErr_SetObject(PyExc_KeyError, key);
            return NULL;
        }
        Py_INCREF(default_value);
        return default_value;
    }
    
    Py_INCREF(value);
    if (PyDict_DelItem(self->data, key) < 0) {
        Py_DECREF(value);
        return NULL;
    }
    
    return value;
}

static PyObject *
ZDict_popitem(ZDict *self, PyObject *Py_UNUSED(ignored))
{
    if (!check_mutable(self))
        return NULL;
    
    PyObject *key, *value;
    Py_ssize_t pos = 0;
    
    if (!PyDict_Next(self->data, &pos, &key, &value)) {
        PyErr_SetString(PyExc_KeyError, "popitem(): dictionary is empty");
        return NULL;
    }
    
    PyObject *result = PyTuple_Pack(2, key, value);
    if (result == NULL)
        return NULL;
    
    if (PyDict_DelItem(self->data, key) < 0) {
        Py_DECREF(result);
        return NULL;
    }
    
    return result;
}

static PyObject *
ZDict_clear(ZDict *self, PyObject *Py_UNUSED(ignored))
{
    if (!check_mutable(self))
        return NULL;
    
    PyDict_Clear(self->data);
    Py_RETURN_NONE;
}

static PyObject *
ZDict_update(ZDict *self, PyObject *args, PyObject *kwds)
{
    if (self->mode == MODE_READONLY || self->mode == MODE_IMMUTABLE) {
        PyErr_Format(PyExc_TypeError, "Cannot update zdict in '%s' mode", mode_names[self->mode]);
        return NULL;
    }
    
    /* Handle insert mode special case */
    if (self->mode == MODE_INSERT) {
        /* First collect all updates */
        PyObject *temp_dict = PyDict_New();
        if (temp_dict == NULL)
            return NULL;
        
        /* Process positional argument */
        if (PyTuple_Size(args) > 0) {
            PyObject *other = PyTuple_GetItem(args, 0);
            if (PyDict_Check(other)) {
                if (PyDict_Update(temp_dict, other) < 0) {
                    Py_DECREF(temp_dict);
                    return NULL;
                }
            } else if (PyMapping_Check(other)) {
                PyObject *items = PyMapping_Items(other);
                if (items == NULL) {
                    Py_DECREF(temp_dict);
                    return NULL;
                }
                
                Py_ssize_t size = PyList_Size(items);
                for (Py_ssize_t i = 0; i < size; i++) {
                    PyObject *item = PyList_GetItem(items, i);
                    PyObject *key = PyTuple_GetItem(item, 0);
                    PyObject *value = PyTuple_GetItem(item, 1);
                    if (PyDict_SetItem(temp_dict, key, value) < 0) {
                        Py_DECREF(items);
                        Py_DECREF(temp_dict);
                        return NULL;
                    }
                }
                Py_DECREF(items);
            }
        }
        
        /* Process keyword arguments */
        if (kwds && PyDict_Update(temp_dict, kwds) < 0) {
            Py_DECREF(temp_dict);
            return NULL;
        }
        
        /* Check for existing keys */
        PyObject *key, *value;
        Py_ssize_t pos = 0;
        while (PyDict_Next(temp_dict, &pos, &key, &value)) {
            if (PyDict_Contains(self->data, key)) {
                Py_DECREF(temp_dict);
                PyErr_SetString(PyExc_TypeError, "Cannot update existing keys in 'insert' mode");
                return NULL;
            }
        }
        
        /* All good, perform update */
        if (PyDict_Update(self->data, temp_dict) < 0) {
            Py_DECREF(temp_dict);
            return NULL;
        }
        Py_DECREF(temp_dict);
    } else {
        /* Normal update for mutable/arena modes */
        if (PyTuple_Size(args) > 0) {
            PyObject *other = PyTuple_GetItem(args, 0);
            
            if (PyDict_Check(other)) {
                if (PyDict_Update(self->data, other) < 0)
                    return NULL;
            } else {
                /* Try as mapping or iterable */
                PyObject *keys_method = PyObject_GetAttrString(other, "keys");
                if (keys_method != NULL) {
                    Py_DECREF(keys_method);
                    /* It's a mapping */
                    if (PyDict_Update(self->data, other) < 0)
                        return NULL;
                } else {
                    /* Clear AttributeError */
                    PyErr_Clear();
                    
                    /* Try as iterable of pairs */
                    PyObject *iter = PyObject_GetIter(other);
                    if (iter == NULL) {
                        PyErr_SetString(PyExc_TypeError, 
                                        "update() argument must be dict, mapping, or iterable of pairs");
                        return NULL;
                    }
                    
                    PyObject *item;
                    while ((item = PyIter_Next(iter)) != NULL) {
                        if (!PyTuple_Check(item) || PyTuple_Size(item) != 2) {
                            Py_DECREF(item);
                            Py_DECREF(iter);
                            PyErr_SetString(PyExc_ValueError, "update sequence element must be 2-tuple");
                            return NULL;
                        }
                        
                        PyObject *key = PyTuple_GetItem(item, 0);
                        PyObject *value = PyTuple_GetItem(item, 1);
                        if (PyDict_SetItem(self->data, key, value) < 0) {
                            Py_DECREF(item);
                            Py_DECREF(iter);
                            return NULL;
                        }
                        Py_DECREF(item);
                    }
                    Py_DECREF(iter);
                }
            }
        }
        
        if (kwds && PyDict_Update(self->data, kwds) < 0)
            return NULL;
    }
    
    Py_RETURN_NONE;
}

static PyObject *
ZDict_copy(ZDict *self, PyObject *Py_UNUSED(ignored))
{
    /* Create a new ZDict instance */
    ZDict *new_zdict = (ZDict *)ZDict_new(&ZDictType, NULL, NULL);
    if (new_zdict == NULL)
        return NULL;
    
    /* Copy the data */
    Py_DECREF(new_zdict->data);
    new_zdict->data = PyDict_Copy(self->data);
    if (new_zdict->data == NULL) {
        Py_DECREF(new_zdict);
        return NULL;
    }
    
    /* Copy the mode */
    new_zdict->mode = self->mode;
    
    /* Copy hash info for immutable mode */
    if (self->mode == MODE_IMMUTABLE) {
        new_zdict->hash = self->hash;
        new_zdict->hash_computed = self->hash_computed;
    }
    
    return (PyObject *)new_zdict;
}

static PyObject *
ZDict_setdefault(ZDict *self, PyObject *args)
{
    PyObject *key;
    PyObject *default_value = Py_None;
    
    if (!PyArg_ParseTuple(args, "O|O:setdefault", &key, &default_value))
        return NULL;
    
    PyObject *value = PyDict_GetItem(self->data, key);
    if (value == NULL) {
        if (!check_insertable(self))
            return NULL;
        
        if (PyDict_SetItem(self->data, key, default_value) < 0)
            return NULL;
        
        Py_INCREF(default_value);
        return default_value;
    }
    
    Py_INCREF(value);
    return value;
}

/* Rich comparison */
static PyObject *
ZDict_richcompare(PyObject *self, PyObject *other, int op)
{
    if (op != Py_EQ && op != Py_NE) {
        Py_RETURN_NOTIMPLEMENTED;
    }
    
    ZDict *zd_self = (ZDict *)self;
    PyObject *self_dict = zd_self->data;
    PyObject *other_dict = NULL;
    
    if (Py_TYPE(other) == &ZDictType) {
        other_dict = ((ZDict *)other)->data;
    } else if (PyDict_Check(other)) {
        other_dict = other;
    } else {
        if (op == Py_EQ)
            Py_RETURN_FALSE;
        else
            Py_RETURN_TRUE;
    }
    
    int result = PyObject_RichCompareBool(self_dict, other_dict, Py_EQ);
    if (result < 0)
        return NULL;
    
    if (op == Py_EQ)
        return PyBool_FromLong(result);
    else
        return PyBool_FromLong(!result);
}

/* Hash support */
static Py_hash_t
ZDict_hash(ZDict *self)
{
    if (self->mode != MODE_IMMUTABLE) {
        PyErr_Format(PyExc_TypeError, 
                     "unhashable type: 'zdict' (mode='%s')", 
                     mode_names[self->mode]);
        return -1;
    }
    
    if (!self->hash_computed) {
        /* Compute hash from sorted items */
        PyObject *items = PyDict_Items(self->data);
        if (items == NULL)
            return -1;
        
        if (PyList_Sort(items) < 0) {
            Py_DECREF(items);
            return -1;
        }
        
        /* Convert to tuple for hashing */
        PyObject *items_tuple = PyList_AsTuple(items);
        Py_DECREF(items);
        if (items_tuple == NULL)
            return -1;
        
        self->hash = PyObject_Hash(items_tuple);
        Py_DECREF(items_tuple);
        
        if (self->hash == -1)
            return -1;
        
        self->hash_computed = 1;
    }
    
    return self->hash;
}

/* String representation */
static PyObject *
ZDict_repr(ZDict *self)
{
    PyObject *dict_repr = PyObject_Repr(self->data);
    if (dict_repr == NULL)
        return NULL;
    
    PyObject *result = PyUnicode_FromFormat("zdict(%U, mode='%s')", 
                                            dict_repr, 
                                            mode_names[self->mode]);
    Py_DECREF(dict_repr);
    return result;
}

static PyObject *
ZDict_str(ZDict *self)
{
    return PyObject_Str(self->data);
}

/* Property getter for mode */
static PyObject *
ZDict_get_mode(ZDict *self, void *closure)
{
    return PyUnicode_FromString(mode_names[self->mode]);
}

/* Method definitions */
static PyMethodDef ZDict_methods[] = {
    {"keys", (PyCFunction)ZDict_keys, METH_NOARGS, "Return a view of the dict's keys"},
    {"values", (PyCFunction)ZDict_values, METH_NOARGS, "Return a view of the dict's values"},
    {"items", (PyCFunction)ZDict_items, METH_NOARGS, "Return a view of the dict's items"},
    {"get", (PyCFunction)ZDict_get, METH_VARARGS, "Get item with default"},
    {"pop", (PyCFunction)ZDict_pop, METH_VARARGS, "Remove and return item"},
    {"popitem", (PyCFunction)ZDict_popitem, METH_NOARGS, "Remove and return arbitrary item"},
    {"clear", (PyCFunction)ZDict_clear, METH_NOARGS, "Remove all items"},
    {"update", (PyCFunction)ZDict_update, METH_VARARGS | METH_KEYWORDS, "Update dict with items from another dict or iterable"},
    {"copy", (PyCFunction)ZDict_copy, METH_NOARGS, "Return a shallow copy"},
    {"setdefault", (PyCFunction)ZDict_setdefault, METH_VARARGS, "Insert key with default if not present"},
    {NULL}  /* Sentinel */
};

/* Property definitions */
static PyGetSetDef ZDict_getsetters[] = {
    {"mode", (getter)ZDict_get_mode, NULL, "Current mode", NULL},
    {NULL}  /* Sentinel */
};

/* Mapping methods */
static PyMappingMethods ZDict_as_mapping = {
    (lenfunc)ZDict_length,          /* mp_length */
    (binaryfunc)ZDict_getitem,      /* mp_subscript */
    (objobjargproc)ZDict_setitem    /* mp_ass_subscript */
};

/* Sequence methods (for 'in' operator) */
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

/* Type object */
static PyTypeObject ZDictType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "zdict.zdict",
    .tp_doc = "High-performance dict implementation with configurable modes",
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
    .tp_getset = ZDict_getsetters,
    .tp_richcompare = ZDict_richcompare,
};

/* Module definition */
static PyModuleDef zdictmodule = {
    PyModuleDef_HEAD_INIT,
    .m_name = "_zdictcore",
    .m_doc = "C extension for zdict",
    .m_size = -1,
};

/* Module initialization */
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
    
    /* Add mode constants */
    PyModule_AddIntConstant(m, "MODE_MUTABLE", MODE_MUTABLE);
    PyModule_AddIntConstant(m, "MODE_IMMUTABLE", MODE_IMMUTABLE);
    PyModule_AddIntConstant(m, "MODE_READONLY", MODE_READONLY);
    PyModule_AddIntConstant(m, "MODE_INSERT", MODE_INSERT);
    PyModule_AddIntConstant(m, "MODE_ARENA", MODE_ARENA);
    
    return m;
}