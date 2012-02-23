from pake import *

@task()
def dbcreate(t):
	import inspect
	from vuuvv.core import Application
	from vuuvv.db import Migrate
	from db import schema
	app = Application(__name__)
	for attr in dir(schema):
		cls = getattr(schema, attr)
		if inspect.isclass(cls) and issubclass(cls, Migrate):
			migrate = cls.from_config(app.config)
			if hasattr(migrate, 'up'):
				migrate.up()

@task()
def runserver(t):
	import app
	app.run()

