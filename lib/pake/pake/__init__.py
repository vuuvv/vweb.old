__all__ = (
	'task',
	'option',
	'rule',
	'cd',
	'from_camel',
	'to_camel',
	'touch',
)

from pake.core import task, option, rule
from pake.util import from_camel, to_camel, touch
from pake.globals import app

def cd(*args, **kw):
	app.cd(*args, **kw)

