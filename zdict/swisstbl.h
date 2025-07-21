#pragma once

#include <Python.h>
#include <stdint.h>
#include <stddef.h>

typedef struct {
    size_t capacity;
    size_t size;
    uint8_t *metadata;
    PyObject **keys;
    PyObject **values;
} SwissTable;

int swiss_init(SwissTable *table, size_t initial_capacity);
int swiss_set(SwissTable *table, PyObject *key, PyObject *value);
PyObject* swiss_get(SwissTable *table, PyObject *key);
int swiss_del(SwissTable *table, PyObject *key);
void swiss_clear(SwissTable *table);
void swiss_free(SwissTable *table);
