

class Toucher:

	def __init__(self):
		self._touch_count = 0

	def toucher(fn):
		def touch(self, *args, **kwargs):
			self._touch_count += 1
			return fn(self, *args, **kwargs)
		return touch

	def get_touch_count(self):
		return self._touch_count


class Market(Toucher):

	def __init__(self, _R0, _R1, _id):
		super().__init__()
		self.R0 = _R0
		self.R1 = _R1
		self.id = _id

	
	@Toucher.toucher
	def get_amount_out(self, amount_in, zero_to_one):
		if zero_to_one:
			return self.R1 * amount_in / (self.R0 + amount_in)
		else:
			raise Exception("Unimplemented")

	@Toucher.toucher
	def simulate_swap(self, amount_in, zero_to_one):
		if zero_to_one:
			amount_out = self.get_amount_out(amount_in, True)
			self.R0 += amount_in
			self.R1 -= amount_out
			return amount_out
		else:
			raise Exception("Unimplemented")
