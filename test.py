from solvers import optimal_distribution_bruteforce, optimal_distribution_heuristic
from market import Market
import random


def test_heuristic_matches_bruteforce():
	# https://www.desmos.com/calculator/gogr5nc2k0
	markets = [
		Market(6000, 10000, "MarketUno"),
		Market(50000, 50000, "MarketDois"),
		Market(2000, 5000, "MarketTres")
	]
	amount_in = 10_000
	chunks = 10

	brute_optimal_path = optimal_distribution_bruteforce(amount_in, chunks, markets)
	heuristic_optimal_path = optimal_distribution_heuristic(amount_in, chunks, markets)

	assert len(brute_optimal_path) == len(heuristic_optimal_path)
	for (k, v) in brute_optimal_path.items():
		assert heuristic_optimal_path[k] == v


def stress_test_heuristic():	
	for i in range(5000):
		amount_in = 10_000
		chunks = int(random.randint(2, 1000))
		market_count = random.randint(2, 1000)
		max_split = random.choice([None, random.randint(2, 10)])

		mid_price = 1.
		max_price_dev = random.uniform(0.1, 0.9)
		mid_liq = amount_in * 100
		max_liq_dev = random.uniform(2, 20)

		get_rnd_price = lambda: mid_price * random.uniform(1-max_price_dev/2, 1+max_price_dev/2)
		get_rnd_liq = lambda: ((x := mid_liq*random.uniform(1-max_liq_dev/2, 1+max_liq_dev/2)), x*get_rnd_price())
		create_rnd_market = lambda id_: Market(*get_rnd_liq(), f"Market{id_}")

		markets = [ create_rnd_market(i) for i in range(market_count) ]

		heuristic_optimal_path = optimal_distribution_heuristic(amount_in, chunks, markets, max_split)
		total_touches = sum([ m.get_touch_count() for m in markets ])
 
		assert total_touches == chunks + market_count - 1
		assert len(heuristic_optimal_path) >= 1
		assert 0.99 <= sum(heuristic_optimal_path.values()) <= 1.01
		if max_split:
			assert len(heuristic_optimal_path) <= max_split


if __name__ == "__main__":
	print("Testing heuristics matches bruteforce ...", end="")
	print(" OK!")
	test_heuristic_matches_bruteforce()
	print("Testing heuristics stress test ...", end="")
	stress_test_heuristic()
	print(" OK!")
	print("All tests passed! ✨")
