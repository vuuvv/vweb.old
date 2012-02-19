import os
import sys
import argparse
from distutils import log
from gettext import gettext as _

from pake.config import PAKEFILE_NAME
from pake.context import PakefileContext
from pake.exceptions import PakeError
from pake.globals import context

class Application(object):
	def __init__(self):
		self.arg_parser = self._create_arg_parser()
		self.argv = sys.argv[1:]
		self.options = None
		self.directory = None
		self.target = None

	def _create_arg_parser(self):
		parser = argparse.ArgumentParser(
				description="Python Makefile System", 
				prog="pake", add_help=False)
		parser.add_argument(
				'-f', '--file', 
				type=str, default=None, 
				help='specified a pakefile')
		parser.add_argument(
				'-v', '--verbose', 
				type=int, choices=[0, 1, 2], default=1)
		return parser

	def run(self):
		parser = self.arg_parser
		# parse options --file and --verbose
		self.options, self.argv = parser.parse_known_args(self.argv)
		log.set_verbosity(self.options.verbose)
		parser.add_argument(
				'-h', '--help', 
				action='help', default=argparse.SUPPRESS,
				help=_('show this help message and exit'))
		self.subparser = parser.add_subparsers(help="taget help", dest="target")

		try:
			# load native context
			with PakefileContext(self):
				file = self.options.file
				if file is None:
					if os.path.isfile(PAKEFILE_NAME):
						file = PAKEFILE_NAME
					else:
						self.load()
						return
				# load root context
				with PakefileContext(self, file):
					self.load()
		except PakeError, e:
			log.error("Error: %s" % e.message)

	def load(self, target=None):
		directory = context.directory

		if context.is_native() or context.is_root():
			self.directory = directory
			if len(self.argv) == 0:
				# pake not specify the task name, use the default
				target = context.default
				if target is None:
					self.arg_parser.print_help()
					self.arg_parser.exit()
			else:
				# get the target name in cmd arguments, fake parse
				options, argv = self.arg_parser.parse_known_args(self.argv, self.options)
				target = options.target
		else:
			if target is None:
				target = context.default

		old_dir = os.getcwd()
		os.chdir(directory)
		log.info("-"*70)
		log.info(">> %s" % directory)

		context.run_task(target)

		log.info("<< %s" % directory)
		log.info("*"*70)
		os.chdir(old_dir)

	def cd(self, path, target=None):
		path = os.path.abspath(path)
		if not os.path.isdir(path):
			raise PakeError('Directory "%s" is not exists' % path)
		filepath = os.path.join(path, PAKEFILE_NAME)

		with PakefileContext(self, filepath):
			self.load(target)


