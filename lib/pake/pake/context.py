import os
import sys
import imp
import copy
import inspect
from functools import partial

from pake.exceptions import PakeError
from pake.core import Task
from pake.globals import _pakefile_ctx_stack, app, context_stack
from pake.invoke_chain import EmptyChain, InvokeChain

def is_file(s):
	return s.startswith("file:")

def get_file(s):
	return s.split(":")[1]

def newer(source, target):
	if not os.path.exists(source) or not os.path.exists(target):
		return True
	return os.stat(source).st_mtime > os.stat(target).st_mtime

class PakefileContext(object):
	def __init__(self, app, path=None):
		self.app = app
		self.tasks = {}
		self.rules = {}
		self.module = None
		self.default = None
		self._set_path(path)

	def _set_path(self, path):
		# path is None mean native context
		if path is not None:
			if os.path.isfile(path):
				self.path = os.path.abspath(path)
				self.directory = os.path.dirname(self.path)
				#self.relative_path = directory[directory.index(app.directory):] 
			else:
				raise PakeError('File "%s" is not exists' % path)
		else:
			self.path = None
			self.directory = os.path.abspath(path)

	def find_task(self, name):
		for ctx in reversed(context_stack):
			t = ctx.tasks.get(name, None)
			if t is not None:
				return t
		raise PakeError("Can't find target '%s'" % name)

	def add_task(self, task):
		self.tasks[task.target] = task
		if task.default:
			self.default = task.target

	def run_task(self, target):
		t = self.find_task(target)
		chain = InvokeChain(t)
		self._run_prerequisite(t, chain)
		t.execute(app.argv)

	def _invoke_task(self, target, invoke_chain):
		t = self.find_task(target)
		if not t.invoked:
			chain = invoke_chain.append(t)
			self._run_prerequisite(t, chain)
			t.execute()

	def _run_prerequisite(self, t, invoke_chain):
		target = t.target
		for pre in t.prerequisites:
			if is_file(target) and is_file(pre):
				media = os.path.abspath(get_file(pre))
				tar = os.path.abspath(get_file(target))
				if newer(media, tar):
					r = self.match_rule(media)
					if r is None:
						self._invoke_task(pre, invoke_chain)
					else:
						src = os.path.splitext(media)[0] + '.' + r.source_suffix
						if newer(src, media):
							r.func(media, src)
						else:
							log.info("'%s' is up to date" % media)
					continue
				else:
					log.info("'%s' is up to date" % tar)
					continue
			self._invoke_task(pre, invoke_chain)

	def add_rule(self, rule):
		self.rules[rule.target_suffix] = rule

	def match_rule(self, filename):
		name, ext = os.path.splitext(filename)

		for ctx in reversed(context_stack):
			rule = self.rules.get(ext[1:], None)
			if rule is not None:
				return rule
		return None

	def is_native(self):
		return context_stack.index(self) == 0

	def is_root(self):
		return context_stack.index(self) == 1

	def _load_module(self, path):
		"""
		Load module the path specified.
		"""
		# for native context
		if self.is_native():
			__import__("pake.builtins")
			# the return value of __import__ function is not the pake.builtins module,(why), 
			# so get it from sys.modules
			return sys.modules['pake.builtins']

		module = imp.new_module('pakefile')
		self._init_module(module)
		try:
			execfile(path, module.__dict__)
		except IOError, e:
			raise PakeError('Unable to load configuration file (%s): %s' % (
				e.strerror, os.path.abspath(path)))
		return module

	def _init_module(self, module):
		for ctx in reversed(context_stack[:-1]):
			m = ctx.module
			for name in dir(m):
				if not name.startswith('__'):
					v = getattr(m, name)
					if inspect.ismodule(v) or isinstance(v, Task):
						continue
					setattr(module, name, v)

		return module

	def __enter__(self):
		_pakefile_ctx_stack.push(self)
		self.module = self._load_module(self.path)
		return self

	def __exit__(self, exc_type, exc_value, tb):
		_pakefile_ctx_stack.pop()

	def __repr__(self):
		return '<%s of %s>' % (self.__class__.__name__, self.path)

