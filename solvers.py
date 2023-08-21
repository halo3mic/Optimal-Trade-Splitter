import copy


def optimal_distribution_bruteforce(amount_in, chunks, markets):
	chunk_size = amount_in / chunks

	def find_optimal_path(chunks_left, markets):

		if chunks_left <= 0:
			return ([], 0)

		best_option = None # (path, amount_out)
		for i in range(len(markets)):
			markets_copy = copy.deepcopy(markets)
			market_amount_out = markets_copy[i].simulate_swap(chunk_size, True)

			(path, path_amount_out) = find_optimal_path(chunks_left-1, markets_copy)
			
			full_path_amount_out = market_amount_out + path_amount_out
			if not best_option or best_option[1] < full_path_amount_out:
				full_path = [ markets_copy[i].id, *path ]
				best_option = (full_path, full_path_amount_out)

		return best_option


	(optimal_path, _) = find_optimal_path(chunks, markets)

	distribution = {}
	for unique_market in set(optimal_path):
		distribution[unique_market] = optimal_path.count(unique_market) / chunks

	return distribution


def optimal_distribution_heuristic(amount_in, chunks, markets, max_split=None):
	assert len(markets) > 1, "At least two markets required"
	assert not max_split or max_split > 1, "`max_split` must be greater than one"
	assert chunks > 1, "At least two chunks required"

	chunk_size = amount_in / chunks

	def get_markets_quotes(amount_in):
		return [ get_market_quote(m, amount_in) for m in markets ]

	def get_market_quote(market, amount_in):
		return {
			"market": market, 
			"amount_out": market.get_amount_out(amount_in, True), 
			"amount_in": amount_in,
		}

	def get_next_quote(old_quote):
		next_amount_in = old_quote["amount_in"] + chunk_size
		return get_market_quote(old_quote["market"], next_amount_in)

	market_quotes = get_markets_quotes(chunk_size)
	market_quotes.sort(key=lambda quote: -quote["amount_out"]) # sort desc
	market_quotes = [ { "last_chunk_out": q["amount_out"], **q } for q in market_quotes ]

	distribution = {} # mapping(market => quote)
	win_quote = market_quotes.pop(0)
	chunks_left = chunks
	while 1: 
		market = win_quote["market"]
		distribution[market.id] = win_quote
		if max_split and len(distribution) == max_split:
			market_quotes = [ q for q in market_quotes if q["market"].id in distribution.keys() ]

		chunks_left -= 1
		if chunks_left == 0:
			break

		next_quote = get_next_quote(win_quote)
		next_quote["last_chunk_out"] = next_quote["amount_out"] - win_quote["amount_out"]

		scnd_best = market_quotes[0]
		if next_quote["last_chunk_out"] >= scnd_best["last_chunk_out"]:
			win_quote = next_quote
		else:
			win_quote = market_quotes.pop(0)
			insert_idx = next((i for (i, q) in enumerate(market_quotes) if next_quote["last_chunk_out"] > q["last_chunk_out"]), -1)
			if insert_idx == -1:
				market_quotes.append(next_quote)
			else:
				market_quotes.insert(insert_idx, next_quote)

	return dict((m, q["amount_in"]/amount_in) for (m, q) in distribution.items())