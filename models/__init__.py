from pymongo import MongoClient
from user import User
from message import Message
from topic import Topic
from restaurante import Restaurante
from orden import Orden

import json
import os

def get_path():
	return os.path.dirname( os.path.realpath(__file__))

def pluralize_class(instance):
	return "{class_name}s".format( class_name = instance.__class__.__name__ )


def load_data(model, folder = 'data'):
	path = "models/{folder}/{file_name}.json".format( folder = folder, file_name =  pluralize_class(model))
	with open(path) as data:
		list_data = json.load(data)
		for json_data in list_data:
			model.save(json_data)


#URI = 'mongodb://heroku_01fb25zl:kcnaoo0asd6k9c6fovth6iuv5r@ds247688.mlab.com:47688/heroku_01fb25zl'

URL = 'localhost'
PORT = 27017

USER_COLLECTION = 'users'
MESSAGE_COLLECTION = 'messages'
TOPIC_COLLECTION = 'topics'
RESTAURANTE_COLLECTION = 'restaurantes'
ORDEN_COLLECTION = 'ordenes'

#--------------------------------------este es para utilizarlo con el servidor online--------
#client = MongoClient(URI)
#database = client.get_default_database()
#---------------------------------------esto ers para utilizarlo desde mongodb----------------
client = MongoClient(URL, PORT)
database = client.domicilion

TopicModel = Topic(database, TOPIC_COLLECTION)

UserModel = User(database, USER_COLLECTION)

OrdenModel = Orden(database, ORDEN_COLLECTION)

RestauranteModel = Restaurante(database, RESTAURANTE_COLLECTION)
RestauranteModel.delete_collection() 
load_data(RestauranteModel)

MessageModel = Message(database, MESSAGE_COLLECTION)
MessageModel.delete_collection() 
load_data(MessageModel)