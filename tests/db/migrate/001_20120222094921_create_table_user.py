from sqlalchemy import *
from vuuvv.db import *

class CreateTableUser(Migrate):
	def up(self):
		# add upgrade migrate code here
		print '+001'

	def down(self):
		# add downgrade migrate code here
		print '-001'
