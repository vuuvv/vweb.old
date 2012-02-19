
@rule('.o', '.c')
def action(target, source):
	print target, source

@task(["file:a.o", "file:b.o"], "file:a.a")
def action(t):
	print t.target
