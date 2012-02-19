import os

@task()
def d1(t):
	print t.target,

@task(['d1'])
def d2(t):
	print t.target,

@task(['d1'])
def d3(t):
	print t.target,

@task(['d3', 'd2', 'd3'])
def test(t):
	print t.target,

@task(default=True)
def test_next(t):
	print t.target
	cd('next', 'next')
