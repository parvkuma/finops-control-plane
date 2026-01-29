from finops.cost_aggregator import CostAggregator


def test_total_cost():
    agg = CostAggregator(100, 150, "SBE")
    agg.add_cost({"estimated_cost_usd": 10})
    agg.add_cost({"estimated_cost_usd": 20})
    assert agg.total_cost() == 30
