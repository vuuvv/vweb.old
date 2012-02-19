"""
Python Makefile System
"""

import os
import sys
import argparse

from functools import wraps, partial
from distutils import log

from pake.config import PAKEFILE_NAME
from pake.globals import app, context
from pake.exceptions import PakeError

class Task(object):
	"""
	A decorator make a function be a sub-command of pake.
	A task function should have 1 argument 'task' at least.
	"""
	def __init__(self, prerequisites=[], target=None, default=False):
		self.target = target
		self.prerequisites = prerequisites
		self.default = default
		self.help = None
		self.options = []
		self.invoked = False

	def __call__(self, func):
		if isinstance(func, Option):
			self.options = func.options
			func = func.func

		if self.target is None:
			self.target = func.__name__

		if func.__doc__:
			self.help = func.__doc__.strip()
		else:
			self.help = self.target
		parser = app.subparser.add_parser(self.target, help=self.help)
		for args, kwargs in self.options:
			parser.add_argument(*args, **kwargs)
		self.parser = parser

		helper = partial(func, self)
		self.func = wraps(func)(helper)
		context.add_task(self)
		return self

	def __repr__(self):
		return self.target

	def execute(self, argv=[]):
		args, argv = self.parser.parse_known_args(argv)
		kwargs = args.__dict__
		self.func(**kwargs)
		self.invoked = True

def task(*args, **kwargs):
	return Task(*args, **kwargs)

class Option(object):
	def __init__(self, *args, **kwargs):
		self.options = [(args, kwargs)]

	def __call__(self, func):
		if isinstance(func, Option):
			self.options += func.options
			self.func = func.func
		else:
			self.func = func
		return self

def option(*args, **kwargs):
	return Option(*args, **kwargs)

class Rule(object):
	def __init__(self, target_suffix, source_suffix):
		self.target_suffix = target_suffix[1:]
		self.source_suffix = source_suffix[1:]

	def __call__(self, func):
		self.func = func
		context.add_rule(self)

def rule(target, source):
	return Rule(target, source)
