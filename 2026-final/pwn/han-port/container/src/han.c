#include "han.h"

#include <math.h>
#include <stdio.h>
#include <time.h>

#define PI 3.14159265358979323846

/* Approximate angular distance (degrees) between two lat/lon points. */
static double geo_dist_deg(double lat1, double lon1, double lat2, double lon2)
{
    double dlat = lat2 - lat1;
    double dlon = (lon2 - lon1) * cos((lat1 + lat2) * PI / 360.0);
    return sqrt(dlat * dlat + dlon * dlon);
}

/* Sinusoidal oscillation. */
static double wave(double t, double period, double phase, double amplitude)
{
    return amplitude * sin(2.0 * PI * t / period + phase);
}

/* djb2-style hash of a string, mapped to a phase in [0, 2π). */
static double str_phase(const char *s)
{
    unsigned long h = 5381;
    for (; *s; s++)
        h = (h * 33) ^ (unsigned char)*s;
    return fmod((double)h, 2.0 * PI);
}

/* ------------------------------------------------------------------ */

void han_simulate(const han_port_t *ports, int count, int idx,
                  han_reading_t *out)
{
    const han_port_t *p = &ports[idx];
    double t = (double)time(NULL);

    /* --- Grid frequency (Hz) with geographic correlation ----------- */
    /*
     * Each port contributes a frequency deviation weighted by proximity.
     * Close ports pull the local frequency together; distant ones have
     * little influence, mimicking real grid area control behaviour.
     */
    double freq_dev    = 0.0;
    double total_weight = 0.0;

    for (int i = 0; i < count; i++) {
        double dist = (i == idx)
            ? 0.01
            : geo_dist_deg(p->location.lat, p->location.lon,
                           ports[i].location.lat, ports[i].location.lon);
        double w   = 1.0 / (dist + 0.5);
        double phi = str_phase(ports[i].meter_id);
        double dev = wave(t, 13.7, phi,        0.06)
                   + wave(t, 53.3, phi * 1.41, 0.025)
                   + wave(t, 97.1, phi * 2.17, 0.010);
        freq_dev     += w * dev;
        total_weight += w;
    }
    out->frequency = HAN_NOMINAL_FREQUENCY + freq_dev / total_weight;

    /* --- Per-phase seeds ------------------------------------------- */
    double phi1 = str_phase(p->meter_id);
    double phi2 = phi1 * 1.6180339887; /* golden-ratio offset */
    double phi3 = phi1 * 2.3025850929; /* ln(10) offset       */

    /* --- Voltage (V): nominal 230 V ± ~2% -------------------------- */
    out->voltage_l1 = 230.0 + wave(t,  17.3, phi1,        2.8)
                             + wave(t, 131.0, phi1 * 0.7,  1.2);
    out->voltage_l2 = 230.0 + wave(t,  19.1, phi2,        2.8)
                             + wave(t, 113.0, phi2 * 0.7,  1.2);
    out->voltage_l3 = 230.0 + wave(t,  21.7, phi3,        2.8)
                             + wave(t, 107.0, phi3 * 0.7,  1.2);

    /* --- Power factor per phase: 0.92–1.00 ------------------------- */
    out->pf_l1 = 0.96 + wave(t, 43.0, phi1, 0.04);
    out->pf_l2 = 0.96 + wave(t, 41.0, phi2, 0.04);
    out->pf_l3 = 0.95 + wave(t, 39.0, phi3, 0.04);

#define CLAMP(v, lo, hi) ((v) < (lo) ? (lo) : (v) > (hi) ? (hi) : (v))
    out->pf_l1 = CLAMP(out->pf_l1, 0.0, 1.0);
    out->pf_l2 = CLAMP(out->pf_l2, 0.0, 1.0);
    out->pf_l3 = CLAMP(out->pf_l3, 0.0, 1.0);

    /* --- Load factor: daily usage curve (peak ~08:00–20:00) -------- */
    double hour        = fmod(t / 3600.0, 24.0);
    double load_factor = 0.35 + 0.55 * (0.5 + 0.5 * sin(2.0 * PI * (hour - 8.0) / 24.0));

    /* --- Current (A) per phase: 0–16 A ----------------------------- */
    out->current_l1 = load_factor * (8.0 + wave(t, 23.1, phi1, 3.0));
    out->current_l2 = load_factor * (7.5 + wave(t, 27.3, phi2, 2.5));
    out->current_l3 = load_factor * (6.0 + wave(t, 31.7, phi3, 2.0));

    out->current_l1 = CLAMP(out->current_l1, 0.0, HAN_MAX_CURRENT);
    out->current_l2 = CLAMP(out->current_l2, 0.0, HAN_MAX_CURRENT);
    out->current_l3 = CLAMP(out->current_l3, 0.0, HAN_MAX_CURRENT);
#undef CLAMP

    /* --- Apparent power S = U·I (VA) ------------------------------- */
    out->apparent_l1 = out->voltage_l1 * out->current_l1;
    out->apparent_l2 = out->voltage_l2 * out->current_l2;
    out->apparent_l3 = out->voltage_l3 * out->current_l3;

    /* --- Active power P = S·pf (W) --------------------------------- */
    out->active_l1 = out->apparent_l1 * out->pf_l1;
    out->active_l2 = out->apparent_l2 * out->pf_l2;
    out->active_l3 = out->apparent_l3 * out->pf_l3;

    /* --- Reactive power Q = sqrt(S²−P²) (VAr) ---------------------- */
    out->reactive_l1 = sqrt(out->apparent_l1 * out->apparent_l1
                          - out->active_l1   * out->active_l1);
    out->reactive_l2 = sqrt(out->apparent_l2 * out->apparent_l2
                          - out->active_l2   * out->active_l2);
    out->reactive_l3 = sqrt(out->apparent_l3 * out->apparent_l3
                          - out->active_l3   * out->active_l3);

    /* --- Three-phase totals ---------------------------------------- */
    out->total_active   = out->active_l1   + out->active_l2   + out->active_l3;
    out->total_reactive = out->reactive_l1 + out->reactive_l2 + out->reactive_l3;
    out->total_apparent = out->apparent_l1 + out->apparent_l2 + out->apparent_l3;
    out->total_pf       = (out->total_apparent > 0.0)
                        ? (out->total_active / out->total_apparent)
                        : 1.0;

    /* --- Accumulated energy ---------------------------------------- */
    /*
     * Base derived from meter_id hash to give each meter a distinct
     * realistic starting value (5 000–20 000 kWh).  Today's running
     * total is approximated as average power × hours elapsed today.
     */
    double base_wh          = (5000.0 + fmod(str_phase(p->meter_id) * 1e5, 15000.0)) * 1000.0;
    double base_reactive_wh = base_wh * 0.22;

    out->energy_active_import   = base_wh          + out->total_active   * hour;
    out->energy_active_export   = 0.0;
    out->energy_reactive_import = base_reactive_wh + out->total_reactive * hour;
    out->energy_reactive_export = 0.0;
}

/* ------------------------------------------------------------------ */

void han_print_telegram(const han_port_t *port, const han_reading_t *r)
{
    time_t    now    = time(NULL);
    struct tm *utc   = gmtime(&now);
    char       ts[16];
    strftime(ts, sizeof(ts), "%y%m%d%H%M%S", utc);

    /* Header: /manufacturer\meter_id */
    printf("/HAN-SIM\\%s\n\n", port->meter_id);

    /* Identification */
    printf("0-0:1.0.0(%sW)\n",    ts);            /* timestamp (W = UTC/winter) */
    printf("0-0:96.1.0(%s)\n",    port->meter_id);
    printf("0-0:96.1.1(%s)\n",    port->name);
    printf("0-0:96.7.21(%05u)\n", 0u);             /* power failures             */
    printf("0-0:96.7.9(%05u)\n",  0u);             /* long power failures        */
    printf("\n");

    /* Accumulated energy */
    printf("1-0:1.8.0(%011.3f*kWh)\n",   r->energy_active_import   / 1000.0);
    printf("1-0:2.8.0(%011.3f*kWh)\n",   r->energy_active_export   / 1000.0);
    printf("1-0:3.8.0(%011.3f*kVArh)\n", r->energy_reactive_import / 1000.0);
    printf("1-0:4.8.0(%011.3f*kVArh)\n", r->energy_reactive_export / 1000.0);
    printf("\n");

    /* Three-phase totals (instantaneous) */
    printf("1-0:1.7.0(%07.3f*kW)\n",   r->total_active   / 1000.0);
    printf("1-0:2.7.0(%07.3f*kW)\n",   0.0);
    printf("1-0:3.7.0(%07.3f*kVAr)\n", r->total_reactive / 1000.0);
    printf("1-0:4.7.0(%07.3f*kVAr)\n", 0.0);
    printf("1-0:9.7.0(%07.3f*kVA)\n",  r->total_apparent / 1000.0);
    printf("1-0:13.7.0(%06.4f)\n",      r->total_pf);
    printf("1-0:14.7.0(%06.2f*Hz)\n",  r->frequency);
    printf("\n");

    /* Phase L1 */
    printf("1-0:21.7.0(%07.3f*kW)\n",   r->active_l1   / 1000.0);
    printf("1-0:22.7.0(%07.3f*kW)\n",   0.0);
    printf("1-0:23.7.0(%07.3f*kVAr)\n", r->reactive_l1 / 1000.0);
    printf("1-0:24.7.0(%07.3f*kVAr)\n", 0.0);
    printf("1-0:29.7.0(%07.3f*kVA)\n",  r->apparent_l1 / 1000.0);
    printf("1-0:33.7.0(%06.4f)\n",       r->pf_l1);
    printf("1-0:32.7.0(%06.1f*V)\n",    r->voltage_l1);
    printf("1-0:31.7.0(%06.3f*A)\n",    r->current_l1);
    printf("\n");

    /* Phase L2 */
    printf("1-0:41.7.0(%07.3f*kW)\n",   r->active_l2   / 1000.0);
    printf("1-0:42.7.0(%07.3f*kW)\n",   0.0);
    printf("1-0:43.7.0(%07.3f*kVAr)\n", r->reactive_l2 / 1000.0);
    printf("1-0:44.7.0(%07.3f*kVAr)\n", 0.0);
    printf("1-0:49.7.0(%07.3f*kVA)\n",  r->apparent_l2 / 1000.0);
    printf("1-0:53.7.0(%06.4f)\n",       r->pf_l2);
    printf("1-0:52.7.0(%06.1f*V)\n",    r->voltage_l2);
    printf("1-0:51.7.0(%06.3f*A)\n",    r->current_l2);
    printf("\n");

    /* Phase L3 */
    printf("1-0:61.7.0(%07.3f*kW)\n",   r->active_l3   / 1000.0);
    printf("1-0:62.7.0(%07.3f*kW)\n",   0.0);
    printf("1-0:63.7.0(%07.3f*kVAr)\n", r->reactive_l3 / 1000.0);
    printf("1-0:64.7.0(%07.3f*kVAr)\n", 0.0);
    printf("1-0:69.7.0(%07.3f*kVA)\n",  r->apparent_l3 / 1000.0);
    printf("1-0:73.7.0(%06.4f)\n",       r->pf_l3);
    printf("1-0:72.7.0(%06.1f*V)\n",    r->voltage_l3);
    printf("1-0:71.7.0(%06.3f*A)\n",    r->current_l3);
    printf("\n");

    printf("!\n");
}
