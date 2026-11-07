/* SPDX-License-Identifier: Apache-2.0 */
/*
 * Gate logic: raises the USB input current step only after a stable advertised-current reading,
 * sheds load when the hardware gate closes, backs off after brown-out and watchdog resets.
 * Requirements: SW-005, SW-006, SW-007, SW-009, SW-010 (plan 07). Pure C, no Zephyr includes,
 * so that the logic runs unchanged on the host. Hardware access goes through gate_ops.
 *
 * Open values (SW-005 to SW-010 brackets) are fields of struct gate_config, never constants.
 */
#ifndef BUSY_LIGHT_GATE_H
#define BUSY_LIGHT_GATE_H

#include <stdbool.h>
#include <stdint.h>

enum gate_reset_cause {
	GATE_RESET_POWER_ON = 0,
	GATE_RESET_BROWNOUT,
	GATE_RESET_WATCHDOG,
	GATE_RESET_OTHER
};

enum gate_edge {
	GATE_EDGE_GATE_OK = 0, /* falling edge of GATE_OK_RB (HOLD_OK_RB) */
	GATE_EDGE_EN2,
	GATE_EDGE_EN3
};

struct gate_config {
	uint32_t read_period_ms;   /* [100] SW-005 */
	uint32_t stable_reads;     /* [6] SW-005 */
	uint32_t advert_fall_ms;   /* [50] SW-006 */
	uint32_t backoff_s;        /* [60] SW-007 */
	uint32_t brownout_max;     /* [3] SW-007 */
	uint32_t brownout_window_s; /* [600] SW-007 */
	uint8_t advert_step;       /* 2 or 3: step for a 1.5 A or 3 A advertisement */
};

/* Retained over a reset (SW-007). Times are elapsed seconds, never absolute ticks. */
struct gate_store {
	uint32_t brownout_count;
	uint32_t window_elapsed_s;
	uint32_t backoff_remaining_s;
	bool locked;      /* lowest step until the next power-up */
	bool gate_flag;   /* set by the gate-closure edge, cleared after use */
};

struct gate_inputs {
	bool gate_ok;         /* GATE_OK_RB: hold-off ended and no limiter fault */
	bool cc_ok_1a5;       /* advertised 1.5 A or more */
	bool en2_rb;          /* readback of the step 2 gate enable */
	bool en3_rb;          /* readback of the step 3 gate enable */
	bool budget_reached;  /* LED current is at or below the lowest-step budget */
};

struct gate_ops {
	void (*write_selects)(void *user, bool sel2, bool sel3);
	void (*request_budget)(void *user, bool lowest);
	void (*store_save)(void *user, const struct gate_store *store);
	void (*wdt_feed)(void *user);
	void *user;
};

struct gate_ctx {
	struct gate_config cfg;
	struct gate_ops ops;
	struct gate_store store;
	uint8_t step;            /* current step 1..3 */
	bool sel2;
	bool sel3;
	bool last_advert;
	uint32_t equal_reads;
	bool readbacks_valid;
	bool lowering;           /* SW-006: budget requested, selects still up */
	uint32_t lowering_ms;
	bool have_time;
	uint32_t last_ms;
	uint32_t sub_ms;         /* milliseconds not yet added to the second counters */
	uint32_t unknown_count;  /* logged unknown states (SW-005 criterion 4) */
	uint32_t late_budget_count;
	uint32_t edge_count;
};

void gate_init(struct gate_ctx *ctx, const struct gate_config *cfg, const struct gate_ops *ops);

/*
 * Call once after the reset, before the readback pins are configured. The first read of GATE_OK_RB
 * and the retained store come from the caller. A brown-out or watchdog reset counts unless
 * GATE_OK_RB was low at the first read or the retained flag was set (SW-007). The flag is
 * cleared after use.
 */
void gate_boot(struct gate_ctx *ctx, enum gate_reset_cause cause, bool gate_ok_first_read,
	       const struct gate_store *retained);

/* SW-009: the readbacks of EN2 and EN3 count only after GPIO20 and GPIO21 are configured. */
void gate_set_readbacks_valid(struct gate_ctx *ctx, bool valid);

/* Falling edge of GATE_OK_RB, EN2 or EN3 (interrupt context). Lowers the selects at once. */
void gate_on_edge(struct gate_ctx *ctx, enum gate_edge edge);

/* One read period of SW-005. Never feeds the watchdog. */
void gate_step(struct gate_ctx *ctx, const struct gate_inputs *in, uint32_t now_ms);

/* SW-010: the only function that feeds the watchdog: gate_step, then wdt_feed. */
void gate_service(struct gate_ctx *ctx, const struct gate_inputs *in, uint32_t now_ms);

#endif /* BUSY_LIGHT_GATE_H */
