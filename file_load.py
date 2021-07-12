class FileLoader:
	def __init__(self, path, scope=None):
		self._path=path
		self._scope=scope
	@property
	def value(self):
		with open(self._path, encoding='UTF-8') as f:
			return eval(f.read(), self._scope)

	@value.setter
	def value(self, new_value):
		with open(self._path, mode='w', encoding='UTF-8') as f:
			f.write(repr(new_value))