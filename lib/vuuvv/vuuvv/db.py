from sqlalchemy.schema import Table, DDLElement, Column, Constraint, MetaData
from sqlalchemy.engine.base import Engine
from sqlalchemy.engine.url import URL
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.util import OrderedProperties

def engine_from_config(config):
	args = [config[name] for name in ('DRIVERNAME', 'USERNAME', 
		'PASSWORD', 'HOST', 'PORT', 'DATABASE')]
	url = str(URL(*args))
	return create_engine(url, echo=config['DEBUG'])

class Model(object):
	relations = {}

def belongs_to(self):
	pass

def has_many(self):
	pass

def has_one(self):
	pass

def has_and_belongs_to_many(self):
	pass

class TableDefinition(object):
	def __init__(self):
		self.fields = OrderedProperties()
	
	def column(self, name, *args, **kw):
		setattr(self.fields, name, (args, kw))

	def keys(self):
		return self.fields.keys()

class Migrate(object):
	def __init__(self, engine):
		self.engine = engine
		self.meta = meta = MetaData()
		meta.reflect(bind=engine)

	@classmethod
	def from_config(cls, config):
		return cls(engine_from_config(config))

	def create_table(self, name):
		def wrap(fn):
			table_definition = TableDefinition()
			fn(table_definition)
			table = Table(name, self.meta)
			for attrname in table_definition.keys():
				args, kw = table_definition.fields[attrname]
				table.append_column(Column(attrname, *args, **kw))
			table.create(self.engine)

		return wrap

	def drop_table(self, name):
		self.meta.tables[name].drop(self.engine)

	def add_column(self, table, column):
		self.engine.execute(AddColumn(table, column))

	def remove_column(self, table, column):
		self.engine.execute(RemoveColumn(table, column))

class AddColumn(DDLElement):
	def __init__(self, table, column):
		self.table = table
		self.column = column

@compiles(AddColumn)
def visit_add_column(element, compiler, **kw):
	return "ALTER TABLE %s ADD %s" %(
		element.table, 
		compiler.get_column_specification(element.column)
	)

class RemoveColumn(DDLElement):
	def __init__(self, table, column):
		self.table = table
		self.column = column

@compiles(RemoveColumn)
def visit_remove_column(element, compiler, **kw):
	return "ALTER TABLE %s DROP %s" %(
			element.table, element.column)

