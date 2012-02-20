from sqlalchemy import *

engine = create_engine("mysql://root:@localhost:3306/sqltest", echo=True)
meta = MetaData()

element = Table('element', meta,
	Column('element_id', Integer, primary_key=True),
	Column('parent_node_id', Integer),
	ForeignKeyConstraint(
		['parent_node_id'],
		['node.node_id'],
		use_alter=True,
		name='fk_element_parent_node_id'
	)
)
node = Table('node', meta,
	Column('node_id', Integer, primary_key=True),
	Column('primary_element', Integer,
		ForeignKey('element.element_id', use_alter=True, name='fk_node_element_id')
	)
)

invoice = Table('invoice', meta,
	Column('invoice_id', Integer, primary_key=True),
	Column('ref_num', Integer, primary_key=True),
	Column('description', String(60), nullable=False)
)
invoice_item = Table('invoice_item', meta,
	Column('item_id', Integer, primary_key=True),
	Column('item_name', String(60), nullable=False),
	Column('invoice_id', Integer, nullable=False),
	Column('ref_num', Integer, nullable=False),
	ForeignKeyConstraint(['invoice_id', 'ref_num'], ['invoice.invoice_id', 'invoice.ref_num'])
)
user = Table('user', meta,
	Column('user_id', Integer, primary_key = True),
	Column('user_name', String(16), nullable = False),
	Column('email_address', String(60)),
	Column('password', String(20), nullable = False)
)
user_preference = Table('user_preference', meta,
	Column('pref_id', Integer, primary_key=True),
	Column('user_id', Integer, ForeignKey("user.user_id", use_alter=True, name='fk_node1_element_id'), nullable=False),
	Column('pref_name', String(40), nullable=False),
	Column('pref_value', String(100))
)
meta.create_all(bind=engine)
