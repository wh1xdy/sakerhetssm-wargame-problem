#pragma once

#define HAN_NOMINAL_VOLTAGE    230.0   /* V  */
#define HAN_NOMINAL_FREQUENCY   50.0   /* Hz */
#define HAN_MAX_CURRENT         16.0   /* A  */

typedef struct han_port han_port_t;

typedef void (*han_handler_t)(han_port_t *port, const char *cmd);

typedef struct {
    double lat;  /* degrees North */
    double lon;  /* degrees East  */
} geo_loc_t;

struct han_port {
    const char    *name;      /* Human-readable label      */
    const char    *meter_id;  /* Meter serial / identifier */
    geo_loc_t      location;
    han_handler_t  handler;
};

typedef struct {
    /* Grid */
    double frequency;                               /* Hz  */

    /* Per-phase instantaneous */
    double voltage_l1,  voltage_l2,  voltage_l3;   /* V   */
    double current_l1,  current_l2,  current_l3;   /* A   */
    double active_l1,   active_l2,   active_l3;    /* W   */
    double reactive_l1, reactive_l2, reactive_l3;  /* VAr */
    double apparent_l1, apparent_l2, apparent_l3;  /* VA  */
    double pf_l1,       pf_l2,       pf_l3;        /* –   */

    /* Three-phase totals (instantaneous) */
    double total_active;    /* W   */
    double total_reactive;  /* VAr */
    double total_apparent;  /* VA  */
    double total_pf;        /* –   */

    /* Accumulated energy (Wh / VArh) */
    double energy_active_import;    /* Wh   */
    double energy_active_export;    /* Wh   */
    double energy_reactive_import;  /* VArh */
    double energy_reactive_export;  /* VArh */
} han_reading_t;

void han_simulate(const han_port_t *ports, int count, int idx,
                  han_reading_t *out);

/* Print a P1-style telegram to stdout. */
void han_print_telegram(const han_port_t *port, const han_reading_t *r);
