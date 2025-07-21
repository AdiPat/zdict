#include "zdict_internal.h"

/* Arena mode implementation */
int zdict_arena_init(zdict_internal_t *zdict) {
    /* Arena mode uses pre-allocated memory */
    /* Could implement custom memory allocator here */
    return 0;
}