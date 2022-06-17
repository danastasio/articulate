
# Articulate ORM Collections

class Collection:
	def __init__(self: object) -> None:
		self._collection = []

	def __iter__(self: object):
		return iter(self._collection)

	def __len__(self: object):
		return len(self._collection)

	def __getitem__(self: object, index: int):
		return self._collection[index]

	def add(self: object, new_obj: object) -> None:
		self._collection.append(new_obj)

	def contains(self: object, find_obj: object) -> bool:
		for item in self._collection:
			if item._id() == find_obj._id():
				return True
		return False

