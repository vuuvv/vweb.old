import os
import imp
import inspect

from pake import *
from vuuvv.db import Migrate
from vuuvv.core import Application

migrate_directory = 'db/migrate'

@task()
@option('action', nargs='?')
def dbmigrate(t):
	"""
	Database migrate like a rails project.
	"""
	app = Application(__name__)
	action = t.option.action
	if not action:
		Migration('migrate').run(config=app.config)
	else:
		try:
			version = int(action)
			Migration('migrate').run(config=app.config, version=version)
		except ValueError:
			Migration(action).run(config=app.config)

def parser_options(t):
	subparsers = t.parser.add_subparsers(dest='migrate')
	parser_up = subparsers.add_parser('up', help='migrate up to a version')
	parser_up.add_argument("version", nargs='?')
	parser_down = subparsers.add_parser('down', help='migrate down to a version')
	parser_down.add_argument("version", nargs='?')
	parser_new = subparsers.add_parser('new', help='make a new migrate directory')
	options, argv = t.parser.parse_known_args(t.argv)
	return options

class Migration(object):
	def __init__(self, action, directory=None):
		if directory is None:
			directory = migrate_directory
		self.directory = directory
		self.versions = self.get_versions(directory)
		self.action = action
		self.version = self.load_current_version()

	def get_versions(self, directory):
		filenames = os.listdir(directory)
		versions = {}
		latest_version = 0

		for filename in filenames:
			try:
				version = int(filename.split("_")[0])
				versions[version] = os.path.splitext(filename)[0]
				if version > latest_version:
					latest_version = version
			except ValueError:
				continue
		self.latest_version = latest_version
		return versions

	def load_current_version(self):
		path = os.path.join(self.directory, 'version')
		with open(path, 'r') as file:
			return int(file.read().strip())

	def dump_version(self, version):
		path = os.path.join(self.directory, 'version')
		with open(path, 'w') as file:
			return file.write(str(version))

	def run(self, config=None, **kw):
		self.config = config
		meth = getattr(self, self.action)
		meth(**kw)

	def new(self):
		if not os.path.isdir('db'):
			os.mkdir('db')
		if not os.path.isdir(migrate_directory):
			os.mkdir(migrate_directory)
		if not os.path.isfile(os.path.join(migrate_directory, "__init__.py")):
			with open(os.path.join(migrate_directory, "__init__.py"), "w"):
				pass
		if not os.path.isfile(os.path.join(migrate_directory, "version")):
			with open(os.path.join(migrate_directory, "version"), "w") as f:
				f.write("0")

	def up(self):
		version = self.version + 1
		if version > self.latest_version:
			return
		while version not in self.versions and version < self.latest_version:
			version += 1
		self.run_version(version, 'up')
		self.dump_version(version)

	def down(self):
		version = self.version
		while version not in self.versions and version > 0:
			version -= 1
		self.run_version(version, 'down')
		self.dump_version(version - 1)

	def migrate(self, version=None):
		if version is None or version > self.latest_version:
			version = self.latest_version
		if version == self.version:
			return
		if version > self.version:
			direct, floor, ceiling = 'up', self.version, version
		else:
			direct, floor, ceiling = 'down', version, self.version

		for v in range(floor, ceiling + 1):
			if v in self.versions:
				self.run_version(v, direct)
		self.dump_version(version)

	def run_version(self, version, direct):
		module_name = self.versions[version]
		m = imp.find_module(module_name, [migrate_directory])
		module = imp.load_module(module_name, *m)
		for attr in dir(module):
			cls = getattr(module, attr)
			if inspect.isclass(cls) and issubclass(cls, Migrate):
				migrate = cls.from_config(self.config)
				if hasattr(migrate, direct):
					getattr(migrate, direct)()

