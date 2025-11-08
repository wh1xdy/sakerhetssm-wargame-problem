#include <stdbool.h>
#include "httpd.h"
#include "http_config.h"
#include "http_protocol.h"
#include "http_request.h"
#include "apr_hash.h"
#include "apr_time.h"
#include "http_core.h"
#include "http_log.h"
#include "apr_tables.h"

#define MAX_KEY_SIZE 0x32
#define MAX_KEY_VAL_SIZE 0x100

typedef struct apr_hash_entry_t apr_hash_entry_t;

struct apr_hash_entry_t {
    apr_hash_entry_t *next;
    unsigned int      hash;
    const void       *key;
    apr_ssize_t       klen;
    const void       *val;
};

struct apr_hash_index_t {
    apr_hash_t         *ht;
    apr_hash_entry_t   *this, *next;
    unsigned int        index;
};

struct apr_hash_t {
    apr_pool_t          *pool;
    apr_hash_entry_t   **array;
    apr_hash_index_t     iterator;
    unsigned int         count, max, seed;
    apr_hashfunc_t       hash_func;
    apr_hash_entry_t    *free;
};


static int vuln_handler(request_rec *r) {
    if (!r->handler || strcmp(r->handler, "vuln_module")) {
        return DECLINED;
    }

    apr_time_t now = apr_time_now();
    apr_hash_t *ht = apr_hash_make(r->pool);

    char numStr[20];
    int* is_pro = apr_pcalloc(r->pool, sizeof(int));
    *is_pro = 5555;
    
    sprintf(numStr, "0x%lx", ht->seed);
    apr_pool_userdata_set(is_pro, numStr, NULL, r->pool);

    ap_set_content_type(r, "text/html");
    ap_rprintf(r, "<meta charset='UTF-8'>");
    ap_rprintf(r, "<link rel='stylesheet' type='text/css' href='style.css'>");

    ap_rprintf(r, "<main>");
    ap_rprintf(r, "<h1>😈😈😈 Windows Web Defender 😈😈😈</h1>");
    ap_rprintf(r, "<p>idk what to put here so here are some cool pictures 😁</p>");
    ap_rprintf(r, "<div id='img-container'>");
    ap_rprintf(r, "<img src='./cool_picture1.png' width='400px' height='auto'>");
    ap_rprintf(r, "<img src='./cool_picture2.png' width='400px' height='auto'>");
    ap_rprintf(r, "<img src='./cool_picture3.png' width='400px' height='auto'>");
    ap_rprintf(r, "<img src='./cool_picture4.png' width='400px' height='auto'>");
    ap_rprintf(r, "</div>");

    apr_table_t *headers = r->headers_in;
    const apr_array_header_t *arr = apr_table_elts(headers);
    apr_table_entry_t *elts = (apr_table_entry_t *)arr->elts;
    bool debug = false;

    for (int i = 0; i < arr->nelts; i++) {
        if (strcmp(elts[i].key, "DEBUG") == 0) debug = true;

        if (elts[i].key && elts[i].val) {
            // i aint storing all dat 💀💀
            if (strlen(elts[i].val) > MAX_KEY_VAL_SIZE || strlen(elts[i].key) > MAX_KEY_SIZE) 
                continue;

            char* temp = apr_pcalloc(r->pool, strlen(elts[i].val));
            memcpy(temp, elts[i].val, strlen(elts[i].val));
            apr_pool_userdata_set(temp, elts[i].key, NULL, r->pool);
        }
    }

    if (debug) {
        // print debug info
        // OBS DEVLOPR ONLY!!1! 😊😊😊
        ap_rprintf(r, "<h3>--- DEBUG INFO ---</h3>");
        ap_rprintf(r, "<p>request: %s </p>", r);
        ap_rprintf(r, "<p>time: %ld </p>", now);
        ap_rprintf(r, "<p>ht->seed: 0x%x </p>", ht->seed);
    }

    int* random_seed = NULL;
    apr_pool_userdata_get(&random_seed, numStr, r->pool);

    if (*random_seed != 5555) {
        FILE *file = fopen("/flag.txt", "r");
        if (file == NULL) {
            ap_rprintf(r, "<p>Error: Unable to open file</p>");
            return 1;
        }
    
        char buffer[256];
        while (fgets(buffer, sizeof(buffer), file) != NULL) {
            ap_rprintf(r, "<p>%s</p>", buffer);
        }
    
        fclose(file);
    }
    ap_rprintf(r, "</main>");
    ap_rprintf(r, "<footer>Copyright © 2012 - 2025. All rights reserved.</footer>");

    return OK;
}

static void register_hooks(apr_pool_t *p) {
    ap_hook_handler(vuln_handler, NULL, NULL, APR_HOOK_MIDDLE);
}

module AP_MODULE_DECLARE_DATA vuln_module = {
    STANDARD20_MODULE_STUFF,
    NULL,          /* Per-directory config creator */
    NULL,          /* Directory config merger */
    NULL,          /* Per-server config creator */
    NULL,          /* Server config merger */
    NULL,          /* Command table */
    register_hooks /* Hooks registration */
};
