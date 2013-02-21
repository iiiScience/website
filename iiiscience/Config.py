import ConfigParser

class Config:

	def __init__(self, filepath='config.txt'):
		self.config = ConfigParser.ConfigParser()
		self.config.read(filepath)

	def get(self, section, option, default=None):
		try:
			return self.config.get(section, option)
		except Exception as e:
			if default:
				return default
			raise e

	def get_bool(self, section, option, default=None):
		try:
			return self.config.getboolean(section, option)
		except Exception as e:
			if default is not None:
				return default
			raise e

	def set(self, section, option, value):
		try:
			self.config.set(section, option, value)
		except:
			self.config.add_section(section)
			self.config.set(section, option, value)