from sqlalchemy import *
from vuuvv.db import *

class CreateTablePermission(Migrate):
	def up(self):
		# add upgrade migrate code here
		print "+005"

	def down(self):
		# add downgrade migrate code here
		print "-005"
