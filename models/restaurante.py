from model import Model
from pymongo import ASCENDING

class Restaurante(Model):
	def __init__(self, database, collection_name):
		super(Restaurante, self).__init__(database, collection_name)

	def find_by_order(self, **kwargs):
		return self.find_all(**kwargs).sort('order', ASCENDING)
