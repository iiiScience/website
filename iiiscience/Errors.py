class APIError(Exception):
	
	def __init__(self, reason):
		self.reason = reason

class ModelError(Exception):
	
	def __init__(self, reason):
		self.reason = reason