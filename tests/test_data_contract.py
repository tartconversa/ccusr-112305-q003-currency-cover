"""校验可供分析的资料关系。"""

import unittest

from scripts.inspect_sources import read_table


class SourceContractTest(unittest.TestCase):
    def test_source_observations_and_references(self):
        from decimal import Decimal
        flows = {row["flow"]:row for row in read_table("flows")}
        known = read_table("actuals")
        self.assertGreaterEqual(len({row["received_day"] for row in known}), 8)
        self.assertTrue(all(row["flow"] in flows for row in known))
        self.assertTrue(any(row["received_day"] > flows[row["flow"]]["due"] for row in known))
        changes = read_table("changes")
        self.assertEqual(len({row["due"] for row in changes}), 2)
        self.assertEqual(sum(Decimal(row["amount"]) for row in changes), Decimal(flows["F100"]["amount"]))
        self.assertTrue(any(row["state"] == "已成交" and row["currency"] == "EUR" for row in read_table("forwards")))
        self.assertEqual(sum(Decimal(row["probability"]) for row in read_table("scenarios")), 1)

    def test_bank_return_inputs(self):
        sources = [read_table(name) for name in ['bank_events', 'offers', 'bridge_transfers', 'flows']]
        events={x["event"]:x for x in sources[0]}
        self.assertEqual(events["B5"]["parent"],"B4")
        self.assertEqual(events["B8"]["parent"],"B7")
        self.assertNotEqual(events["B8"]["value_day"],events["B7"]["value_day"])
        self.assertEqual({x["bank"] for x in sources[1] if x["offer"]=="FX-P3"},{"A","B"})
        ids={x["flow"] for x in sources[3]}
        self.assertTrue(all(set(x["supports"])<=ids for x in sources[2]))

