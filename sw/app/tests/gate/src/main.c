/* SPDX-License-Identifier: Apache-2.0 */
/*
 * Smoke test of the gate test setup (plan 07, first increment). It shows that a ztest builds and
 * runs on native_sim. It tests no requirement; TC-105 to TC-110 follow in later increments.
 */
#include <zephyr/ztest.h>

ZTEST(gate_smoke, test_ztest_runs)
{
	zassert_true(true, "ztest must run on native_sim");
}

ZTEST_SUITE(gate_smoke, NULL, NULL, NULL, NULL, NULL);
