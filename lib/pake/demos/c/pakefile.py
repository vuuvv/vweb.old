import os

test_attr = "test attribute"

@task()
@option('-t', '--too')
@option('-b', '--baz')
def test(depends, target, too, baz):
	print depends, target
	cd("src")
	print too, baz
	print test_attr
#from pake import cc, task, cd
#
#src = ['hello.c', 'main.c']
#
#hello_obj = cfile('hello.c', ['hello.h'])
#main_obj = cfile('main.c')
#
#@task([hello_obj, main_obj], default=True)
#def main(depends, target):
#	cd("src")
#	cc.link(target, depends)
