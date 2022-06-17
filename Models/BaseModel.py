#!/usr/bin/env python3

# Articulate ORM
import psycopg2
import psycopg2.extras
import yaml
import hashlib
from Helpers.Collection import Collection

class BaseModel:
	def __init__(self: object):
		with open('config.yaml', 'r') as cfgfile:
			settings = yaml.safe_load(cfgfile)
		self.db_username = settings['db']['username']
		self.db_password = settings['db']['password']
		self.db_hostname = settings['db']['hostname']
		self.db_database = settings['db']['database']

		self.con = psycopg2.connect(f"postgres://{self.db_username}:{self.db_password}@{self.db_hostname}/{self.db_database}")
		self.cursor = self.con.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
		self.columns = 'SELECT *'
		self.table_name = type(self).__name__.lower() + 's'
		self.primary_key = 'pk1'
		self.ordering = ''
		self.mode = 'none'
		self.filename = None
		self.delimeter = ','
		self.distinct = ''
		self._constraints = ''
		self.nooutput = False
		try:
			self.overrides()
		except:
			pass
		self.query = f"FROM {self.table_name}"

	def __iter__(self: object):
		return iter(self.__props__)

	def _asdict(self: object):
		return self.__props__

	def _aslist(self: object):
		return list(self.__props__.values())

	def _id(self: object):
		return hashlib.sha256(bytes(str(self._asdict()), encoding='utf8')).digest()

	def ingest(self: object, ntup: tuple):
		self.__props__ = {}
		self.__props__.update(ntup._asdict())
		try:
			to_casts = self.casts()
			for key, to_type in self.__props__.items():
				if key in to_casts:
					self.__props__[key] = to_casts[key](self.__props__[key])
		except AttributeError:
			pass
		return self

	def find(self: object, pk: int):
		self.constraints = f"pk1 = {pk}"
		return self.get()

	def get(self: object):
		self.cursor.execute(self.query)
		results = self.cursor.fetchall()
		collection = Collection()
		for record in results:
			cls = self.ingest(record)
			newobj = type(cls)()
			collection.add(newobj.ingest(record))
	
		if len(collection) == 0:
			print("Empty result set")
			return
		if self.mode == 'none':
			return collection
		if self.filename:
			with open(self.filename, 'w') as file:
				for record in collection:
					file.write(f"{self.delimeter.join(record)}\n")
		if self.mode == 'csv':
			payload = ''
			for record in collection:
				payload = f"{payload}{self.delimeter.join(record._aslist())}\n"
				if not self.nooutput:
					print(self.delimeter.join(record._aslist()))
			return payload

		if self.mode == 'table':
			if self.nooutput:
				return
			def longest_element():
				longest = 0
				for item in collection:
					for key, value in item._asdict().items():
						if len(str(key)) > longest:
							longest = len(key)
						if len(str(value)) > longest:
							longest = len(value)
				return longest + 4

			def top_row():
				for element in collection[0]:
					print(f"{'+'.ljust(longest_element(), '-')}", end='')
				print('+')

			def header_element_builder():
				for element in collection[0]:
					print(f"| {str(element).ljust(longest_element() - 3, ' ')} ", end = '')
				print("|")

			top_row()
			header_element_builder()
			top_row()

			# Body
			for item in collection:
				for element in item._aslist():
					element = str(element) or "none"
					print(f"| {element.ljust(longest_element() - 3, ' ')} ", end = '')
				print("|")

			# Last row
			top_row()

	def first(self: object):
		self.cursor.execute(self.query)
		result = self.cursor.fetchone()
		return self.ingest(result)

	def preview(self: object):
		if self.nooutput:
			print("noout and preview conflict. Remove one or the other")
			quit()
		print(self.query)

	def select(self: object, *params: tuple):
		self.columns = ''
		for column in params:
			if not self.columns:
				self.columns = f"SELECT {self.distinct} {column}"
			else:
				self.columns = f"{self.columns}, {column}"
		return self

	def distinct(self: object):
		self.distinct = 'DISTINCT'
		return self

	def orderBy(self: object, ordering_column: str = 'pk1', order: str = 'ASC'):
		self.ordering = f"ORDER BY {ordering_column} {order}"
		return self
	
	def where(self: object, *params: tuple):
		if len(params) == 3:
			field = params[0]
			op = params[1]
			matcher = params[2]
		else:
			field = params[0]
			op = '='
			matcher = params[1]
		if "to_timestamp" in matcher:
			self.constraints = f"AND {field} {op} {matcher}"
		else:
			self.constraints = f"AND {field} {op} '{matcher}'"
		return self

	def orWhere(self: object, *params: tuple):
		if len(params) == 3:
			field = params[0]
			op = params[1]
			matcher = params[2]
		else:
			field = params[0]
			op = '='
			matcher = params[1]
		self.constraints = f"OR {field} {op} '{matcher}'"
		return self

	def whereLike(self: object, column: str, matcher: str):
		self.constraints = f"AND {column} LIKE '{matcher}'"
		return self

	def whereNotLike(self: object, column: str, matcher: str):
		self.constraints = f"AND {column} NOT LIKE '{matcher}'"
		return self
	
	def whereIn(self: object, column: str, in_list: list):
		if len(in_list) == 1:
			self.constraints = f"AND {column} IN ('{in_list[0]}')"
		else:
			self.constraints = f"AND {column} IN {tuple(in_list)}"
		return self

	def whereNotIn(self: object, column: str, in_list: list):
		if len(in_list) == 1:
			self.constraints = f"AND {column} NOT IN ('{in_list[0]}')"
		else:
			self.constraints = f"AND {column} NOT IN {tuple(in_list)}"
		return self

	def whereLikeAny(self: object, column: str, in_list: list):
		self.constraints = f"AND {column} ~ '{'|'.join(in_list)}'"
		return self

	def whereNotLikeAny(self: object, column: str, in_list: list):
		self.constraints = f"AND {column} !~ '{'|'.join(in_list)}'"
		return self

	def hasOne(self: object, table: object, custom_column = None):
		foreign_table = table()
		foreign_key = custom_column or f"{foreign_table.table_name}_{foreign_table.primary_key}"
		if not self.query:
			self.query = f"FROM {self.table_name} JOIN {foreign_table.table_name} ON {self.table_name}.{foreign_key} = {foreign_table.table_name}.{foreign_table.primary_key}"
		else:
			self.query = f"{self.query} JOIN {foreign_table.table_name} ON {self.table_name}.{foreign_key} = {foreign_table.table_name}.{foreign_table.primary_key}"
		return self

	def hasMany(self: object, table: object, linking_table = None, close_column_name: str = None, far_column_name: str = None):
		t = table()
		table = t.table_name
		table_list = [self.table_name, table]
		table_list.sort()
		if not linking_table:
			linking_table = f"{table_list[0]}_{table_list[1]}"
		if not close_column_name:
			close_column_name = f"{self.table_name}_pk1"
		if not far_column_name:
			far_column_name = f"{table}_pk1"

		self.query = f"FROM {self.table_name} JOIN {linking_table} ON {self.table_name}.{self.primary_key} = {linking_table}.{close_column_name} JOIN {table} ON {table}.{self.primary_key} = {linking_table}.{far_column_name}"
		return self

	def belongsTo(self: object, foreign_table: str):
		pass # not ready yet

	def csv(self: object, delimeter = ','):
		self.mode = 'csv'
		self.delimeter = delimeter
		return self

	def writeToFile(self: object, filename: str):
		self.filename = filename
		return self

	def table(self: object):
		self.mode = 'table'
		return self

	def noout(self: object):
		self.nooutput = True
		return self

	@property
	def constraints(self: object):
		return self._constraints

	@constraints.setter
	def constraints(self: object, new_constraint: str):
		if self._constraints != '':
			self._constraints = f"{self._constraints} {new_constraint}"
		else:
			new_constraint = new_constraint.replace('AND', '').replace('OR', '')
			self._constraints = f"{self._constraints} {new_constraint}"
		return self

	@property
	def query(self: object):
		if self.constraints:
			query = f"{self.columns} {self._query} WHERE {self.constraints} {self.ordering}"
		else:
			query = f"{self.columns} {self._query} {self.ordering}"	
		return query

	@query.setter
	def query(self: object, query_body: str):
		self._query = query_body

