from sqlalchemy import *
from vuuvv.db import *

class AlertTableUser(Migrate):
	def up(self):
		# add upgrade migrate code here
		print "+003"

	def down(self):
		# add downgrade migrate code here
		print "-003"
