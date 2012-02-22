from sqlalchemy import *
from vuuvv.db import *

class CreateTableUser(Migrate):
	def up(self):
		@self.create_table('user')
		def create_user(t):
			t.column('id', Integer, primary_key=True)
			t.column('name', String(50), nullable=False)
			t.column('password', String(50), nullable=False)

	def down(self):
		self.drop_table('user')
