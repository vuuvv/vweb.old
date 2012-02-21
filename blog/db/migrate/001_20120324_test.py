from sqlalchemy import *
from vuuvv.db import *

class CreateTable(Migrate):
	def up(self):
		@self.create_table('user')
		def user(t):
			t.column('id', Integer, primary_key=True)
			t.column('username', String(50), nullable=False)
			t.column('age', Integer)

	def down(self):
		self.drop_table('user')
