from pake.context import PakefileContext, pakefile
from pake.core import TasksNode

#ctx1 = PakefileContext("examples/c/pakefile.py")
#ctx2 = PakefileContext("examples/c/src/pakefile.py")
#
#with ctx1:
#	with ctx2:
#		print pakefile
#	print pakefile
#
#print pakefile

t = TasksNode()
t1 = TasksNode(t)

print t.tasks
print t.tt
