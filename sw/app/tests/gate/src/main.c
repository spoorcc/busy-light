/* SPDX-License-Identifier: Apache-2.0 */
/*
 * Unit tests of the gate logic on native_sim. Each test names the test case it implements
 * (TC-105, TC-106, TC-107, TC-109, TC-110 in docs/verification/test-cases-sw.md).
 * The bracketed values of the requirements are test parameters here, not product values.
 */
#include <zephyr/ztest.h>

#include "gate.h"

#define PERIOD_MS 100U
#define READS 6U
#define BACKOFF_S 60U
#define MAX_BROWNOUT 3U
#define WINDOW_S 600U
#define FALL_MS 50U

struct fake {
	bool sel2;
	bool sel3;
	bool both_seen;
	uint32_t select_writes;
	uint32_t budget_requests;
	uint32_t saves;
	uint32_t wdt_feeds;
	struct gate_store saved;
};

static struct fake fk;
static struct gate_ctx g;
static uint32_t now;

static void fk_write_selects(void *user, bool s2, bool s3)
{
	struct fake *f = user;

	f->sel2 = s2;
	f->sel3 = s3;
	f->select_writes++;
	if (s2 && s3) {
		f->both_seen = true;
	}
}

static void fk_request_budget(void *user, bool lowest)
{
	struct fake *f = user;

	ARG_UNUSED(lowest);
	f->budget_requests++;
}

static void fk_store_save(void *user, const struct gate_store *s)
{
	struct fake *f = user;

	f->saved = *s;
	f->saves++;
}

static void fk_wdt_feed(void *user)
{
	struct fake *f = user;

	f->wdt_feeds++;
}

static struct gate_config cfg(uint8_t advert_step)
{
	return (struct gate_config){.read_period_ms = PERIOD_MS,
				    .stable_reads = READS,
				    .advert_fall_ms = FALL_MS,
				    .backoff_s = BACKOFF_S,
				    .brownout_max = MAX_BROWNOUT,
				    .brownout_window_s = WINDOW_S,
				    .advert_step = advert_step};
}

static void setup_with(uint8_t advert_step)
{
	struct gate_config c = cfg(advert_step);
	struct gate_ops ops = {.write_selects = fk_write_selects,
			       .request_budget = fk_request_budget,
			       .store_save = fk_store_save,
			       .wdt_feed = fk_wdt_feed,
			       .user = &fk};

	fk = (struct fake){0};
	now = 0U;
	gate_init(&g, &c, &ops);
	gate_set_readbacks_valid(&g, true);
}

static void before(void *unused)
{
	ARG_UNUSED(unused);
	setup_with(2U);
}

static struct gate_inputs in_ok(bool advert)
{
	return (struct gate_inputs){
		.gate_ok = true, .cc_ok_1a5 = advert, .en2_rb = g.sel2, .en3_rb = g.sel3,
		.budget_reached = false};
}

static void read_n(struct gate_inputs in, uint32_t n)
{
	for (uint32_t i = 0U; i < n; i++) {
		gate_step(&g, &in, now);
		now += PERIOD_MS;
		in.en2_rb = g.sel2;
		in.en3_rb = g.sel3;
	}
}

ZTEST_SUITE(gate, NULL, NULL, before, NULL, NULL);

/* TC-105 (a): the step is selected at the sixth equal read, not before. */
ZTEST(gate, test_tc105_a_step_at_sixth_equal_read)
{
	read_n(in_ok(true), READS - 1U);
	zassert_false(fk.sel2, "no step before the sixth read");
	read_n(in_ok(true), 1U);
	zassert_true(fk.sel2, "step 2 at the sixth read");
	zassert_false(fk.sel3, "never both");
}

/* TC-105 (b): a change at read 5 restarts the count. */
ZTEST(gate, test_tc105_b_change_restarts_count)
{
	read_n(in_ok(true), 4U);
	read_n(in_ok(false), 1U);
	read_n(in_ok(true), READS - 1U);
	zassert_false(fk.sel2, "the count restarted");
	read_n(in_ok(true), 1U);
	zassert_true(fk.sel2, "six new equal reads give the step");
}

/* TC-105 (c): GATE_OK_RB low during the count restarts it. */
ZTEST(gate, test_tc105_c_gate_low_restarts_count)
{
	struct gate_inputs low = in_ok(true);

	read_n(in_ok(true), 4U);
	low.gate_ok = false;
	read_n(low, 1U);
	read_n(in_ok(true), READS - 1U);
	zassert_false(fk.sel2, "count restarted by the gate");
	read_n(in_ok(true), 1U);
	zassert_true(fk.sel2, "step after a new full count");
}

/* TC-105 (d): a falling edge sets the selects low; the next raise needs a new count. */
ZTEST(gate, test_tc105_d_edge_lowers_and_recounts)
{
	read_n(in_ok(true), READS);
	zassert_true(fk.sel2, "precondition");
	gate_on_edge(&g, GATE_EDGE_GATE_OK);
	zassert_false(fk.sel2, "selects low at once");
	read_n(in_ok(true), READS - 1U);
	zassert_false(fk.sel2, "needs a new count");
	read_n(in_ok(true), 1U);
	zassert_true(fk.sel2, "raised after a new count");
}

/* TC-105 (e): a default reading never sets a select output. */
ZTEST(gate, test_tc105_e_default_never_raises)
{
	read_n(in_ok(false), 50U);
	zassert_false(fk.sel2, "sel2");
	zassert_false(fk.sel3, "sel3");
}

/* TC-105 (g): each unknown state gives step 1 and a logged count. */
ZTEST(gate, test_tc105_g_unknown_states)
{
	struct gate_inputs a = in_ok(true);

	read_n(in_ok(true), READS);
	zassert_true(fk.sel2, "precondition");
	a.en3_rb = true; /* EN3 high while select 3 is low */
	read_n(a, 1U);
	zassert_false(fk.sel2, "step 1");
	zassert_equal(g.unknown_count, 1U, "counted");
	a = in_ok(true);
	a.en2_rb = true;
	a.en3_rb = true;
	read_n(a, 1U);
	zassert_equal(g.unknown_count, 2U, "both readbacks high is unknown");
}

/* SW-009: readbacks count only after the pins are configured. */
ZTEST(gate, test_tc109_readbacks_invalid_until_configured)
{
	struct gate_inputs a = in_ok(true);

	gate_set_readbacks_valid(&g, false);
	a.en2_rb = true; /* garbage before configuration */
	read_n(a, 1U);
	zassert_equal(g.unknown_count, 0U, "ignored while invalid");
}

/* TC-105 (h): the table, step 2 or step 3 by configuration, never both. */
ZTEST(gate, test_tc105_h_table_step3_when_configured)
{
	setup_with(3U);
	read_n(in_ok(true), READS);
	zassert_true(fk.sel3, "step 3");
	zassert_false(fk.sel2, "not both");
	zassert_false(fk.both_seen, "no write ever drove both selects");
}

/* TC-106 (a), (b): lowering asks for the budget first and waits for it. */
ZTEST(gate, test_tc106_budget_before_select_low)
{
	struct gate_inputs fall = in_ok(false);

	read_n(in_ok(true), READS);
	zassert_true(fk.sel2, "precondition");
	fk.budget_requests = 0U;
	read_n(fall, 1U);
	zassert_equal(fk.budget_requests, 1U, "budget requested");
	zassert_true(fk.sel2, "select still up until the budget is reached");
	fall.budget_reached = true;
	read_n(fall, 1U);
	zassert_false(fk.sel2, "select low after the budget");
}

/* TC-106: the LED layer is late: the select goes low after the limit anyway. */
ZTEST(gate, test_tc106_late_budget_forces_low)
{
	read_n(in_ok(true), READS);
	read_n(in_ok(false), 1U);
	zassert_true(fk.sel2, "waiting");
	read_n(in_ok(false), 2U); /* 100 ms later */
	zassert_false(fk.sel2, "forced low after the limit");
	zassert_equal(g.late_budget_count, 1U, "late budget logged");
}

/* TC-107 (a): a counted brown-out holds the lowest step for the back-off time. */
ZTEST(gate, test_tc107_a_backoff_blocks_raise)
{
	struct gate_store s = {0};
	struct gate_inputs in = in_ok(true);

	gate_boot(&g, GATE_RESET_BROWNOUT, true, &s);
	zassert_equal(g.store.brownout_count, 1U, "counted");
	for (uint32_t t = 0U; t < (BACKOFF_S * 1000U) - PERIOD_MS; t += PERIOD_MS) {
		gate_step(&g, &in, now);
		now += PERIOD_MS;
	}
	zassert_false(fk.sel2, "no raise inside the back-off");
	for (uint32_t i = 0U; i < 3U * READS; i++) {
		gate_step(&g, &in, now);
		now += PERIOD_MS;
	}
	zassert_true(fk.sel2, "raise after the back-off");
}

/* TC-107 (b): [3] counted resets inside the window lock the lowest step. */
ZTEST(gate, test_tc107_b_three_resets_lock)
{
	struct gate_store s = {0};

	for (uint32_t i = 0U; i < MAX_BROWNOUT; i++) {
		gate_boot(&g, GATE_RESET_BROWNOUT, true, &s);
		s = g.store;
	}
	zassert_true(g.store.locked, "locked");
	read_n(in_ok(true), 3U * BACKOFF_S * 10U);
	zassert_false(fk.sel2, "lowest until power-up");
	gate_boot(&g, GATE_RESET_POWER_ON, true, &s);
	zassert_false(g.store.locked, "power-up clears the lock");
}

/* TC-107 (b): a reset after the window starts a new window. */
ZTEST(gate, test_tc107_b_window_expires)
{
	struct gate_store s = {.brownout_count = 2U, .window_elapsed_s = WINDOW_S + 1U};

	gate_boot(&g, GATE_RESET_BROWNOUT, true, &s);
	zassert_equal(g.store.brownout_count, 1U, "old resets forgotten");
	zassert_false(g.store.locked, "not locked");
}

/* TC-107 (c): HOLD_OK_RB low at the first read is not counted. */
ZTEST(gate, test_tc107_c_gate_low_not_counted)
{
	struct gate_store s = {0};

	gate_boot(&g, GATE_RESET_BROWNOUT, false, &s);
	zassert_equal(g.store.brownout_count, 0U, "not counted");
}

/* TC-107 (d): a set retained flag is not counted and is cleared after use. */
ZTEST(gate, test_tc107_d_flag_not_counted_and_cleared)
{
	struct gate_store s = {.gate_flag = true};

	gate_boot(&g, GATE_RESET_BROWNOUT, true, &s);
	zassert_equal(g.store.brownout_count, 0U, "not counted");
	zassert_false(g.store.gate_flag, "cleared after use");
}

/* TC-107 (g): a stale flag is cleared when the gate is ok again; a later brown-out counts. */
ZTEST(gate, test_tc107_g_stale_flag_cleared)
{
	struct gate_store s;
	struct gate_inputs ok = in_ok(false);

	gate_on_edge(&g, GATE_EDGE_GATE_OK);
	zassert_true(g.store.gate_flag, "flag set by the edge");
	read_n(ok, 1U);
	zassert_false(g.store.gate_flag, "cleared when the gate is ok");
	s = g.store;
	gate_boot(&g, GATE_RESET_BROWNOUT, true, &s);
	zassert_equal(g.store.brownout_count, 1U, "a later real brown-out counts");
}

/* TC-107 (h): time is stored elapsed time: a clock restart at 0 keeps the remaining back-off. */
ZTEST(gate, test_tc107_h_elapsed_time_survives_clock_restart)
{
	struct gate_store s = {.brownout_count = 1U, .backoff_remaining_s = 30U};
	struct gate_inputs in = in_ok(true);

	gate_boot(&g, GATE_RESET_BROWNOUT, false, &s); /* not counted, store kept */
	zassert_equal(g.store.backoff_remaining_s, 30U, "remaining time restored");
	now = 0U;
	for (uint32_t t = 0U; t < 29U * 1000U; t += PERIOD_MS) {
		gate_step(&g, &in, now);
		now += PERIOD_MS;
	}
	zassert_false(fk.sel2, "still inside the remaining 30 s");
	for (uint32_t i = 0U; i < 40U; i++) {
		gate_step(&g, &in, now);
		now += PERIOD_MS;
	}
	zassert_true(fk.sel2, "raised after the remaining time");
}

/* TC-107 (i) and SW-010: watchdog resets count like brown-outs. */
ZTEST(gate, test_tc107_i_watchdog_reset_counts)
{
	struct gate_store s = {0};

	for (uint32_t i = 0U; i < MAX_BROWNOUT; i++) {
		gate_boot(&g, GATE_RESET_WATCHDOG, true, &s);
		s = g.store;
	}
	zassert_true(g.store.locked, "three watchdog resets lock the lowest step");
}

/* TC-109: an edge sheds at once and never feeds the watchdog. */
ZTEST(gate, test_tc109_edge_sheds_and_does_not_feed)
{
	read_n(in_ok(true), READS);
	fk.budget_requests = 0U;
	gate_on_edge(&g, GATE_EDGE_EN2);
	zassert_equal(fk.budget_requests, 1U, "shed requested");
	zassert_false(fk.sel2, "selects low");
	zassert_equal(fk.wdt_feeds, 0U, "the edge does not feed the watchdog");
}

/* TC-110: the watchdog is fed only by gate_service. */
ZTEST(gate, test_tc110_only_service_feeds_watchdog)
{
	struct gate_inputs in = in_ok(true);

	gate_step(&g, &in, now);
	zassert_equal(fk.wdt_feeds, 0U, "gate_step does not feed");
	gate_service(&g, &in, now + PERIOD_MS);
	zassert_equal(fk.wdt_feeds, 1U, "gate_service feeds once");
}
