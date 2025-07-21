#ifndef ZDICT_INTERNAL_H
#define ZDICT_INTERNAL_H

#include <Python.h>

/* Mode constants */
typedef enum {
    ZDICT_MODE_MUTABLE = 0,
    ZDICT_MODE_IMMUTABLE = 1,
    ZDICT_MODE_READONLY = 2,
    ZDICT_MODE_INSERT = 3,
    ZDICT_MODE_ARENA = 4
} zdict_mode_t;

/* Internal structure for mode-specific operations */
typedef struct {
    PyObject *data;
    zdict_mode_t mode;
    Py_hash_t hash;
    int hash_computed;
} zdict_internal_t;

/* Mode-specific function prototypes */
int zdict_mutable_init(zdict_internal_t *zdict);
int zdict_immutable_init(zdict_internal_t *zdict);
int zdict_readonly_init(zdict_internal_t *zdict);
int zdict_insert_init(zdict_internal_t *zdict);
int zdict_arena_init(zdict_internal_t *zdict);

#endif /* ZDICT_INTERNAL_H */