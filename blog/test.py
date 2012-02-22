from sqlalchemy import *
import migrate

engine = create_engine("sqlite://", echo=True)
meta = MetaData(bind=engine)
table = Table('mytable', meta,
    Column('id', Integer, primary_key=True),
)
table.create()

col = Column('col1', String, default='foobar')
col.create(table, populate_default=True)
i = Index('test_index', table.c.col1)
i.create()
import pdb;pdb.set_trace()
col.drop()
