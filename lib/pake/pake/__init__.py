__all__ = (
	'task',
	'option',
	'rule',
	'cd',
)

from pake.core import task, option, rule
from pake.globals import app

def cd(*args, **kw):
	app.cd(*args, **kw)

