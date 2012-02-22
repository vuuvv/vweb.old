from sqlalchemy.schema import Table, DDLElement, Column, Constraint, MetaData
from sqlalchemy.engine.base import Engine
from sqlalchemy.engine.url import URL
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.util import OrderedProperties

import migrate

def engine_from_config(config):
	args = [config[name] for name in ('DRIVERNAME', 'USERNAME', 
		'PASSWORD', 'HOST', 'PORT', 'DATABASE')]
	url = str(URL(*args))
	return create_engine(url, echo=config['DEBUG'])

class Model(object):
	relations = {}

class TableDefinition(object):
	def __init__(self):
		self.fields = OrderedProperties()
		self.relations = []
	
	def column(self, name, *args, **kw):
		setattr(self.fields, name, (args, kw))

	def relationship(self, *args, **kw):
		self.relations.append((args, kw))

class Migrate(object):
	def __init__(self, engine):
		self.engine = engine
		self.meta = meta = MetaData(bind=engine)
		meta.reflect()

	@classmethod
	def from_config(cls, config):
		return cls(engine_from_config(config))

	def create_table(self, name):
		def wrap(fn):
			table_definition = TableDefinition()
			fn(table_definition)
			table = Table(name, self.meta)
			for attrname in table_definition.fields.keys():
				args, kw = table_definition.fields[attrname]
				table.append_column(Column(attrname, *args, **kw))
			table.create()

		return wrap

	def drop_table(self, name):
		self.meta.tables[name].drop()

	def add_column(self, table, column):
		if not isinstance(table, Table):
			table = self.meta.tables[name]
		column.create(table)

	def remove_column(self, table, column):
		if not isinstance(table, Table):
			table = self.meta.tables[table]
		if not isinstance(column, Column):
			column = table.columns[column]
		column.drop(table)

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
	return "ALTER TABLE %s DROP COLUMN %s" %(
			element.table, element.column)

