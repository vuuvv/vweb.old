from pake.exceptions import PakeError

class InvokeChain(object):
	def __init__(self, value, chain=None):
		self.value = value
		self.tail = EmptyChain() if chain is None else chain

	def __contains__(self, value):
		return value == self.value or value in self.tail

	def append(self, value):
		if value in self:
			raise PakeError("Circular dependency detected: %s => %s" % (
				self.value, value))
		return InvokeChain(value, self)

class EmptyChain(InvokeChain):
	def __init__(self):
		pass

	def __contains__(self, value):
		return False

	def append(self, value):
		return InvokeChain(value, self)

