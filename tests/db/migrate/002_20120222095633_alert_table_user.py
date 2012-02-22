from sqlalchemy import *
from vuuvv.db import *

class AlertTableUser(Migrate):
	def up(self):
		# add upgrade migrate code here
		self.add_column('user', Column('age', Integer))

	def down(self):
		self.remove_column('user', 'age')
