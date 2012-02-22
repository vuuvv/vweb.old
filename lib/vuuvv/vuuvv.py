import os
import sys
import argparse

sub_commands = [
	(
		'new', 'create a project', [
			(['name'], {'help': 'specified the project name'}),
		],
	),
]

config_tpl = """
BLUEPRINTS = (
	#'home',
)

# If this value is None, we will set this value set
# the first element of BLUE_PRINTS tuple.
DEFAULT_BLUEPRINT = None

# Database settings
DRIVERNAME = "sqlite"
USERNAME = None
PASSWORD = None
HOST = None
PORT = None
DATABASE = "db/test.db"
"""

files = (
	("pakefile.py", """import vuuvv.tasks"""),
	("config.py", config_tpl),
	("__init__.py", ""),
)

def new(options):
	if not os.path.isdir(options.name):
		os.mkdir(options.name)
	for file in files:
		name, content = file
		with open(os.path.join(options.name, name), "w") as f:
			f.write(content)
			sys.stdout.write("%s\n" % os.path.join(options.name, name))

def main():
	parser = argparse.ArgumentParser(description='vuuvv command line tool')
	subparsers = parser.add_subparsers(dest="subcommand")
	for sub in sub_commands:
		cmd, help, opts = sub
		subparser = subparsers.add_parser(cmd, help=help)
		for opt in opts:
			a, kw = opt
			subparser.add_argument(*a, **kw)
	options = parser.parse_args(sys.argv[1:])
	globals()[options.subcommand](options)

main()

