#include "zdict_internal.h"

/* Readonly mode implementation */
int zdict_readonly_init(zdict_internal_t *zdict) {
    /* Readonly mode optimizes for fast access */
    /* Could implement lookup optimizations here */
    return 0;
}