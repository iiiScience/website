import unittest
import ConfigParser
from iiiscience.Config import Config

class ConfigTest(unittest.TestCase):

	def setUp(self):
		self.config = Config()
		self.config.config = ConfigParser.RawConfigParser()

	def test_get_string_nodefault(self):
		self.config.set('test', 'foo', 'bar')
		self.assertEqual(self.config.get('test', 'foo'), 'bar')

	def test_get_string_default_notneeded(self):
		self.config.set('test', 'foo', 'bar')
		self.assertEqual(self.config.get('test', 'foo', 'bar2'), 'bar')

	def test_get_string_default_needed(self):
		self.assertEqual(self.config.get('test', 'foo', 'bar2'), 'bar2')

	def test_get_bool_nodefault(self):
		self.config.set('test', 'foo', 'True')
		self.assertEqual(self.config.get_bool('test', 'foo'), True)
		self.config.set('test', 'foo', 'False')
		self.assertEqual(self.config.get_bool('test', 'foo'), False)

	def test_get_bool_default_notneeded(self):
		self.config.set('test', 'foo', 'True')
		self.assertEqual(self.config.get_bool('test', 'foo', False), True)

	def test_get_bool_default_needed(self):
		self.assertEqual(self.config.get_bool('test', 'foo', False), False)