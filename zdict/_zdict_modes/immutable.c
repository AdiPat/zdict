#include "zdict_internal.h"

/* Immutable mode implementation */
int zdict_immutable_init(zdict_internal_t *zdict) {
    /* Immutable mode freezes the dict after initialization */
    /* Hash will be computed on first access */
    zdict->hash = 0;
    zdict->hash_computed = 0;
    return 0;
}