from sqlalchemy.schema import Table, DDLElement, Column, Constraint, MetaData
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.util import OrderedProperties

from flask import current_app as app

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

def create_table(table_name):
	def wrap(fn):
		table_definition = TableDefinition()
		fn(table_definition)
		table = Table(table_name, app.db_meta)
		print table_definition.keys()
		for attrname in table_definition.keys():
			args, kw = table_definition.fields[attrname]
			table.append_column(Column(attrname, *args, **kw))
		table.create(app.db_engine)

	return wrap

def drop_table(table_name):
	table = app.db_meta.tables[table_name]
	table.drop()

def add_column(table, column):
	app.db_engine.execute(AddColumn(table, column))

def remove_column(table, column):
	app.db_engine.execute(RemoveColumn(table, column))

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

