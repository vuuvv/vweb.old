from vuuvv.db import *
from sqlalchemy import *

@create_table('user')
def user(t):
	t.column('id', Integer, primary_key=True)
	t.column('username', String(50), nullable=False)
	t.column('age', Integer)
