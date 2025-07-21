#include "swisstbl.h"
#include <stdlib.h>
#include <string.h>

#define EMPTY_SLOT ((PyObject*)-1)
#define INITIAL_CAPACITY 16
#define LOAD_FACTOR 0.7

static size_t next_power_of_two(size_t n) {
    size_t power = 1;
    while (power < n) power *= 2;
    return power;
}

static size_t probe_index(size_t hash, size_t i, size_t capacity) {
    return (hash + i) & (capacity - 1);
}

static size_t top_hash(Py_hash_t hash) {
    return (uint8_t)(hash >> 56);
}

static int swiss_resize(SwissTable *table, size_t new_capacity);

int swiss_init(SwissTable *table, size_t initial_capacity) {
    table->capacity = next_power_of_two(initial_capacity < INITIAL_CAPACITY ? INITIAL_CAPACITY : initial_capacity);
    table->size = 0;
    table->metadata = (uint8_t*)calloc(table->capacity, sizeof(uint8_t));
    table->keys = (PyObject**)calloc(table->capacity, sizeof(PyObject*));
    table->values = (PyObject**)calloc(table->capacity, sizeof(PyObject*));
    if (!table->metadata || !table->keys || !table->values) return -1;
    return 0;
}

static int needs_resize(SwissTable *table) {
    return (double)(table->size + 1) / (double)table->capacity > LOAD_FACTOR;
}

int swiss_set(SwissTable *table, PyObject *key, PyObject *value) {
    if (needs_resize(table)) {
        if (swiss_resize(table, table->capacity * 2) != 0) {
            PyErr_SetString(PyExc_RuntimeError, "SwissTable resize failed");
            return -1;
        }
    }

    Py_hash_t hash = PyObject_Hash(key);
    if (hash == -1) return -1;

    size_t idx;
    for (size_t i = 0; i < table->capacity; ++i) {
        idx = probe_index((size_t)hash, i, table->capacity);
        if (!table->keys[idx] || table->keys[idx] == EMPTY_SLOT || PyObject_RichCompareBool(table->keys[idx], key, Py_EQ)) {
            if (table->keys[idx] && table->keys[idx] != EMPTY_SLOT) {
                Py_DECREF(table->keys[idx]);
                Py_DECREF(table->values[idx]);
            } else {
                table->size++;
            }
            Py_INCREF(key);
            Py_INCREF(value);
            table->metadata[idx] = top_hash(hash);
            table->keys[idx] = key;
            table->values[idx] = value;
            return 0;
        }
    }
    PyErr_SetString(PyExc_RuntimeError, "SwissTable insert failed after resize");
    return -1;
}

PyObject* swiss_get(SwissTable *table, PyObject *key) {
    Py_hash_t hash = PyObject_Hash(key);
    if (hash == -1) return NULL;

    size_t idx;
    for (size_t i = 0; i < table->capacity; ++i) {
        idx = probe_index((size_t)hash, i, table->capacity);
        if (!table->keys[idx]) return NULL;
        if (table->keys[idx] != EMPTY_SLOT &&
            table->metadata[idx] == top_hash(hash) &&
            PyObject_RichCompareBool(table->keys[idx], key, Py_EQ)) {
            Py_INCREF(table->values[idx]);
            return table->values[idx];
        }
    }
    return NULL;
}

int swiss_del(SwissTable *table, PyObject *key) {
    Py_hash_t hash = PyObject_Hash(key);
    if (hash == -1) return -1;

    size_t idx;
    for (size_t i = 0; i < table->capacity; ++i) {
        idx = probe_index((size_t)hash, i, table->capacity);
        if (!table->keys[idx]) return -1;
        if (table->keys[idx] != EMPTY_SLOT &&
            table->metadata[idx] == top_hash(hash) &&
            PyObject_RichCompareBool(table->keys[idx], key, Py_EQ)) {
            Py_DECREF(table->keys[idx]);
            Py_DECREF(table->values[idx]);
            table->keys[idx] = EMPTY_SLOT;
            table->values[idx] = NULL;
            table->metadata[idx] = 0;
            table->size--;
            return 0;
        }
    }
    return -1;
}

void swiss_clear(SwissTable *table) {
    for (size_t i = 0; i < table->capacity; ++i) {
        if (table->keys[i] && table->keys[i] != EMPTY_SLOT) {
            Py_DECREF(table->keys[i]);
            Py_DECREF(table->values[i]);
        }
        table->keys[i] = NULL;
        table->values[i] = NULL;
        table->metadata[i] = 0;
    }
    table->size = 0;
}

void swiss_free(SwissTable *table) {
    swiss_clear(table);
    free(table->metadata);
    free(table->keys);
    free(table->values);
    table->metadata = NULL;
    table->keys = NULL;
    table->values = NULL;
}

static int swiss_resize(SwissTable *table, size_t new_capacity) {
    // Backup old data
    size_t old_capacity = table->capacity;
    uint8_t *old_metadata = table->metadata;
    PyObject **old_keys = table->keys;
    PyObject **old_values = table->values;

    // Allocate new
    table->capacity = new_capacity;
    table->metadata = (uint8_t*)calloc(new_capacity, sizeof(uint8_t));
    table->keys = (PyObject**)calloc(new_capacity, sizeof(PyObject*));
    table->values = (PyObject**)calloc(new_capacity, sizeof(PyObject*));
    size_t old_size = table->size;
    table->size = 0;

    if (!table->metadata || !table->keys || !table->values) {
        // Clean up partial alloc
        free(table->metadata);
        free(table->keys);
        free(table->values);
        // Restore old (so free doesn't segfault)
        table->metadata = old_metadata;
        table->keys = old_keys;
        table->values = old_values;
        table->capacity = old_capacity;
        table->size = old_size;
        return -1;
    }

    // Re-insert old elements
    for (size_t i = 0; i < old_capacity; ++i) {
        if (old_keys[i] && old_keys[i] != EMPTY_SLOT) {
            int rc = swiss_set(table, old_keys[i], old_values[i]);
            // New table should never fill up since it's bigger
            if (rc != 0) {
                // Memory leak on error, but rare
                continue;
            }
            Py_DECREF(old_keys[i]);
            Py_DECREF(old_values[i]);
        }
    }
    free(old_metadata);
    free(old_keys);
    free(old_values);
    return 0;
}
