import os
import re

def to_camel(s, separator="_"):
	return ''.join([part.title() for part in s.split(separator)])

def from_camel(s, separator='_'):
	s1 = re.sub('(.)([A-Z][a-z]+)', r'\1%s\2' % separator, s)
	return re.sub('([a-z0-9])([A-Z])', r'\1%s\2' % separator, s1).lower()

def touch(path, content=""):
	if not os.path.isfile(path):
		with open(path, "w") as f:
			f.write(content)
		return True
	return False
