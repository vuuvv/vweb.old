import os
import sys
import imp
import inspect
import argparse
from datetime import datetime

from pake import *
from distutils import log
from vuuvv.db import Migrate
from vuuvv.core import Application

class MigrateVersionError(Exception):
	pass

migrate_directory = 'db/migrate'
file_tpl="""from sqlalchemy import *
from vuuvv.db import *

class %s(Migrate):
	def up(self):
		# add upgrade migrate code here
		pass

	def down(self):
		# add downgrade migrate code here
		pass
"""

cmd_options = [
	('up', 
		{'help': 'migrate up to a version'}, 
		[
			[
				('step',), 
				{'nargs': '?', 'type': int, 'default': 1}
			],
		]
	),
	('down', 
		{'help': 'migrate down to a version'}, 
		[
			[
				('step',), 
				{'nargs': '?', 'type': int, 'default': 1}
			],
		]
	),
	('new', 
		{'help': 'make a new migrate directory'}, 
		[]
	),
	('add', 
		{'help': 'add a version for migrate'}, 
		[
			[
				('description',), 
				{}
			],
		]
	),
	('version', 
		{'help': 'show migrate version'}, 
		[]
	),
]

@task()
@option('action', nargs='?')
def migrate(t):
	"""
	Database migrate like a rails project.
	"""
	app = Application(__name__)
	action = t.option.action
	options = argparse.Namespace()
	if not action:
		# no argument, then migrate version to latest
		options.version = None
		Migration('go').run(config=app.config, options=options)
	else:
		try:
			# specified the version, then migrate to it
			version = int(action)
			options.version = version
			Migration('go').run(config=app.config, options=options)
		except ValueError:
			# specified some command to run, push the 'action' back first.
			t.argv.insert(0, action)
			options = parser_options(t)
			Migration(options.migrate).run(options=options, config=app.config)

def parser_options(t):
	parser = argparse.ArgumentParser()
	subparsers = parser.add_subparsers(dest='migrate')
	for cmd_name, kw1, option2 in cmd_options:
		subparser = subparsers.add_parser(cmd_name, **kw1)
		for arg2, kw2 in option2:
			subparser.add_argument(*arg2, **kw2)
	options, argv = parser.parse_known_args(t.argv)
	return options

def interior_command(func):
	def wrap(self, *arg, **kw):
		if self.has_migrate():
			func(self, *arg, **kw)
		else:
			log.error("You should have a migrate directory to run the command."
					"Run 'pake migrate new' first.")
	return wrap

class Migration(object):
	def __init__(self, action, directory=None):
		if directory is None:
			directory = migrate_directory
		self.directory = directory
		self.action = action
		if self.has_migrate():
			self.versions = self.get_versions(directory)
			self._version = self.load_current_version()

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

	def has_migrate(self):
		return os.path.isdir(self.directory)

	def load_current_version(self):
		path = os.path.join(self.directory, 'version')
		with open(path, 'r') as file:
			return int(file.read().strip())

	def dump_version(self, version):
		path = os.path.join(self.directory, 'version')
		with open(path, 'w') as file:
			return file.write(str(version))

	def touch(self, filename, content=""):
		path = os.path.join(self.directory, filename)
		if touch(path, content):
			log.info(path)

	def run(self, config=None, **kw):
		self.config = config
		meth = getattr(self, self.action)
		meth(**kw)

	def new(self, options):
		try:
			if not os.path.isdir('db'):
				os.mkdir('db')
			if not os.path.isdir(self.directory):
				os.mkdir(self.directory)
			self.touch("__init__.py")
			self.touch("version", "0")
		except Exception as e:
			import shutil, traceback
			shutil.rmtree(self.directory)
			traceback.print_exc()

	@interior_command
	def version(self, options):
		log.error(self._version)

	@interior_command
	def add(self, options):
		desc = options.description
		filename = "%03d_%s_%s.py" % (self.latest_version + 1,
			datetime.now().strftime("%Y%m%d%H%M%S"),
			desc.replace(" ", "_"))
		self.touch(filename, file_tpl % to_camel(desc, ' '))

	@interior_command
	def up(self, options):
		step = 1 if options.step is None else options.step
		version = self._version
		for x in range(step):
			version = self.up_next(version)
			if version is None:
				break

	@interior_command
	def down(self, options):
		step = 1 if options.step is None else options.step
		version = self._version
		for x in range(step):
			version = self.down_next(version)
			if version is None or version == 0:
				break

	@interior_command
	def go(self, options):
		target_version = options.version
		if target_version is None:
			target_version = self.latest_version
		if target_version != 0 and target_version not in self.versions:
			raise MigrateVersionError("Wrong version '%d'" % target_version)
		if target_version == self._version:
			return
		if target_version > self._version:
			direct, func = 'up', self.up_next
		else:
			direct, func = 'down', self.down_next

		version = self._version
		while version != target_version:
			version = func(version)

	def run_version(self, version, direct):
		module_name = self.versions[version]
		m = imp.find_module(module_name, [self.directory])
		module = imp.load_module(module_name, *m)
		for attr in dir(module):
			cls = getattr(module, attr)
			if inspect.isclass(cls) and issubclass(cls, Migrate):
				migrate = cls.from_config(self.config)
				if hasattr(migrate, direct):
					getattr(migrate, direct)()

	def get_next_up_version(self, version):
		latest = self.latest_version
		version += 1
		if version > latest:
			return None
		while version not in self.versions and version < latest:
			version += 1
		return version

	def get_next_down_version(self, version):
		version -= 1
		if version < 0:
			return None
		while version not in self.versions and version > 0:
			version -= 1
		return version

	def up_next(self, version):
		version = self.get_next_up_version(version)
		if version is not None:
			self.run_version(version, 'up')
			self.dump_version(version)
		return version

	def down_next(self, version):
		self.run_version(version, 'down')
		version = self.get_next_down_version(version)
		self.dump_version(version)
		return version
