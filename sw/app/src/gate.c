/* SPDX-License-Identifier: Apache-2.0 */
/* Gate logic, see gate.h. Requirements SW-005, SW-006, SW-007, SW-009, SW-010. */
#include "gate.h"

#define GATE_STEP_LOW 1U
#define GATE_STEP_MID 2U
#define GATE_STEP_TOP 3U
#define GATE_MS_PER_S 1000U

/* The only writer of the select pins. Never drives both outputs (SW-009). */
static void gate_set_selects(struct gate_ctx *ctx, bool sel2, bool sel3)
{
	if (sel2 && sel3) {
		sel2 = false;
		sel3 = false;
	}
	if ((sel2 != ctx->sel2) || (sel3 != ctx->sel3)) {
		ctx->sel2 = sel2;
		ctx->sel3 = sel3;
		ctx->ops.write_selects(ctx->ops.user, sel2, sel3);
	}
	if (sel3) {
		ctx->step = GATE_STEP_TOP;
	} else if (sel2) {
		ctx->step = GATE_STEP_MID;
	} else {
		ctx->step = GATE_STEP_LOW;
	}
}

static void gate_save(struct gate_ctx *ctx)
{
	ctx->ops.store_save(ctx->ops.user, &ctx->store);
}

static void gate_restart_count(struct gate_ctx *ctx)
{
	ctx->equal_reads = 0U;
	ctx->lowering = false;
}

void gate_init(struct gate_ctx *ctx, const struct gate_config *cfg, const struct gate_ops *ops)
{
	ctx->cfg = *cfg;
	ctx->ops = *ops;
	ctx->store = (struct gate_store){0};
	ctx->step = GATE_STEP_LOW;
	ctx->sel2 = false;
	ctx->sel3 = false;
	ctx->last_advert = false;
	ctx->equal_reads = 0U;
	ctx->readbacks_valid = false;
	ctx->lowering = false;
	ctx->lowering_ms = 0U;
	ctx->have_time = false;
	ctx->last_ms = 0U;
	ctx->sub_ms = 0U;
	ctx->unknown_count = 0U;
	ctx->late_budget_count = 0U;
	ctx->edge_count = 0U;
	/* Start with the lowest step: both selects low (SW-005). */
	ctx->ops.write_selects(ctx->ops.user, false, false);
}

void gate_boot(struct gate_ctx *ctx, enum gate_reset_cause cause, bool gate_ok_first_read,
	       const struct gate_store *retained)
{
	bool counted;

	if (cause == GATE_RESET_POWER_ON) {
		/* A power-up clears the back-off and the lock (SW-007). */
		ctx->store = (struct gate_store){0};
		gate_save(ctx);
		return;
	}
	ctx->store = *retained;
	counted = ((cause == GATE_RESET_BROWNOUT) || (cause == GATE_RESET_WATCHDOG)) &&
		  gate_ok_first_read && !ctx->store.gate_flag;
	/* The flag is cleared only after it has been used. */
	ctx->store.gate_flag = false;
	if (counted) {
		if (ctx->store.window_elapsed_s > ctx->cfg.brownout_window_s) {
			ctx->store.brownout_count = 0U;
		}
		if (ctx->store.brownout_count == 0U) {
			/* the window starts at the first counted reset */
			ctx->store.window_elapsed_s = 0U;
		}
		ctx->store.brownout_count++;
		ctx->store.backoff_remaining_s = ctx->cfg.backoff_s;
		if (ctx->store.brownout_count >= ctx->cfg.brownout_max) {
			ctx->store.locked = true;
		}
	}
	gate_save(ctx);
}

void gate_set_readbacks_valid(struct gate_ctx *ctx, bool valid)
{
	ctx->readbacks_valid = valid;
}

void gate_on_edge(struct gate_ctx *ctx, enum gate_edge edge)
{
	(void)edge;
	/* Selects low at once, new count, shed request, retained flag (SW-005 (2), SW-009). */
	gate_set_selects(ctx, false, false);
	gate_restart_count(ctx);
	ctx->edge_count++;
	ctx->ops.request_budget(ctx->ops.user, true);
	ctx->store.gate_flag = true;
	gate_save(ctx);
}

static void gate_advance_time(struct gate_ctx *ctx, uint32_t now_ms)
{
	uint32_t dt;
	uint32_t secs;

	if (!ctx->have_time) {
		ctx->have_time = true;
		ctx->last_ms = now_ms;
		return;
	}
	dt = now_ms - ctx->last_ms; /* unsigned wrap is defined */
	ctx->last_ms = now_ms;
	if (ctx->lowering) {
		ctx->lowering_ms += dt;
	}
	ctx->sub_ms += dt;
	secs = ctx->sub_ms / GATE_MS_PER_S;
	if (secs == 0U) {
		return;
	}
	ctx->sub_ms -= secs * GATE_MS_PER_S;
	ctx->store.window_elapsed_s += secs;
	if (ctx->store.backoff_remaining_s > secs) {
		ctx->store.backoff_remaining_s -= secs;
	} else {
		ctx->store.backoff_remaining_s = 0U;
	}
	gate_save(ctx);
}

static bool gate_unknown_state(const struct gate_ctx *ctx, const struct gate_inputs *in)
{
	if (!in->gate_ok) {
		return true;
	}
	if (!ctx->readbacks_valid) {
		return false;
	}
	return (in->en2_rb && !ctx->sel2) || (in->en3_rb && !ctx->sel3) ||
	       (in->en2_rb && in->en3_rb);
}

static uint8_t gate_target_step(const struct gate_ctx *ctx)
{
	if (ctx->store.locked || (ctx->store.backoff_remaining_s > 0U)) {
		return GATE_STEP_LOW;
	}
	if (ctx->equal_reads < ctx->cfg.stable_reads) {
		return GATE_STEP_LOW;
	}
	return (ctx->cfg.advert_step >= GATE_STEP_TOP) ? GATE_STEP_TOP : GATE_STEP_MID;
}

static void gate_apply_target(struct gate_ctx *ctx, uint8_t target, const struct gate_inputs *in)
{
	if (target > ctx->step) {
		gate_set_selects(ctx, target == GATE_STEP_MID, target == GATE_STEP_TOP);
		return;
	}
	if (target == ctx->step) {
		return;
	}
	/* SW-006: reduce the load first, then lower the step. */
	if (!ctx->lowering) {
		ctx->lowering = true;
		ctx->lowering_ms = 0U;
		ctx->ops.request_budget(ctx->ops.user, true);
	}
	if (in->budget_reached) {
		ctx->lowering = false;
		gate_set_selects(ctx, target == GATE_STEP_MID, target == GATE_STEP_TOP);
	} else if (ctx->lowering_ms >= ctx->cfg.advert_fall_ms) {
		ctx->late_budget_count++;
		ctx->lowering = false;
		gate_set_selects(ctx, target == GATE_STEP_MID, target == GATE_STEP_TOP);
	} else {
		/* still waiting for the LED layer */
	}
}

void gate_step(struct gate_ctx *ctx, const struct gate_inputs *in, uint32_t now_ms)
{
	gate_advance_time(ctx, now_ms);

	if (gate_unknown_state(ctx, in)) {
		if (in->gate_ok) {
			ctx->unknown_count++; /* inconsistent readback, logged (SW-005 (4)) */
		}
		gate_set_selects(ctx, false, false);
		gate_restart_count(ctx);
		ctx->last_advert = in->cc_ok_1a5;
		return;
	}
	/* The stale-flag rule: the gate is ok again, so the flag has no meaning left (SW-007). */
	if (ctx->store.gate_flag) {
		ctx->store.gate_flag = false;
		gate_save(ctx);
	}
	if (in->cc_ok_1a5 != ctx->last_advert) {
		ctx->last_advert = in->cc_ok_1a5;
		ctx->equal_reads = 1U;
	} else if (ctx->equal_reads < UINT32_MAX) {
		ctx->equal_reads++;
	} else {
		/* saturated */
	}
	if (!in->cc_ok_1a5) {
		gate_apply_target(ctx, GATE_STEP_LOW, in);
		return;
	}
	gate_apply_target(ctx, gate_target_step(ctx), in);
}

void gate_service(struct gate_ctx *ctx, const struct gate_inputs *in, uint32_t now_ms)
{
	gate_step(ctx, in, now_ms);
	/* SW-010: the watchdog is fed only here, from the loop that drives the selects. */
	ctx->ops.wdt_feed(ctx->ops.user);
}
