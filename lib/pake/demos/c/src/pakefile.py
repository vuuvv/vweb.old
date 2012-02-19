import os

@task(default=True)
def test(depends, target):
	print "test"
	print test_attr
	t()
	print test_attr

def t():
	global test_attr
	test_attr = "test attribute 1"
#from pake import cc, task
#
#src = ['hello.c']
#
#hello_obj = cfile('hello.c', ['hello.h'], default=True)

