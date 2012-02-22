from sqlalchemy import *
from vuuvv.db import *

class CreateTableRole(Migrate):
	def up(self):
		# add upgrade migrate code here
		print "+004"

	def down(self):
		# add downgrade migrate code here
		print "-004"
