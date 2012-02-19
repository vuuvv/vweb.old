from functools import wraps, partial

from pake.local import LocalStack, LocalProxy

def _lookup_object(name):
	top = _pakefile_ctx_stack.top
	if top is None:
		raise RuntimeError('working outside of request context')
	return getattr(top, name)

_pakefile_ctx_stack = LocalStack()
context = LocalProxy(lambda: _pakefile_ctx_stack.top)
context_stack = LocalProxy(lambda: _pakefile_ctx_stack.stack())
app = LocalProxy(partial(_lookup_object, 'app'))

