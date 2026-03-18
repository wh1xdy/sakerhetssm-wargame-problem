#include "han.h"
#include "ports.h"
#include "handler.h"

/*
 * Port definitions.  Add or remove entries here to change the set of
 * simulated HAN ports — port_count is derived automatically from the
 * array size, so no other file needs to be touched.
 */
han_port_t ports[] = {
    {
        .name     = "SE-Grid-Malmö",
        .meter_id = "HAN-SE-001",
        .location = { .lat = 55.6050, .lon = 13.0038 },
        .handler  = meter_handler,
    },
    {
        .name     = "SE-Grid-Göteborg",
        .meter_id = "HAN-SE-002",
        .location = { .lat = 57.7089, .lon = 11.9746 },
        .handler  = meter_handler,
    },
    {
        .name     = "SE-Grid-Stockholm",
        .meter_id = "HAN-SE-003",
        .location = { .lat = 59.3293, .lon = 18.0686 },
        .handler  = meter_handler,
    },
    {
        .name     = "NO-Grid-Oslo",
        .meter_id = "HAN-NO-001",
        .location = { .lat = 59.9139, .lon = 10.7522 },
        .handler  = meter_handler,
    },
    {
        .name     = "DK-Grid-Copenhagen",
        .meter_id = "HAN-DK-001",
        .location = { .lat = 55.6761, .lon = 12.5683 },
        .handler  = meter_handler,
    },
};

const int port_count = (int)(sizeof(ports) / sizeof(ports[0]));
