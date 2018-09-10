#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Imports de python
from itertools import izip

# Capa acceso a datos
from models import MessageModel

# Capa negocio
from business.apiai import Apiai

class Mensaje(Apiai):

	""" 
	Consulta los mensajes para pintar

	Atributos
		intent: En cual intent se encuentra
		context: El contexto al cual debe responder

	Retorna
		El formato del mensaje
	"""
	@staticmethod
	def consultarMensaje(intent, context = ''):
		return MessageModel.find_by_order(intent = intent) if context == '' else MessageModel.find_by_order(intent = intent, context = context)

	""" 
	Adjunta texto al mensaje

	Atributos
		message: Estructura del mensaje
		data_model: Datos con los cuales va a ser reemplazado

	Retorna
		El mensaje con el texto formateado
	"""
	@staticmethod
	def pegarTexto(message, data_model = {}, label = 'speech'):
		speech = message[label]
		# Si el texto se le puede pegar texto
		if 'format' in message:
			# Adjunta el texto
			speech = speech.format(**data_model)
		# Retorna el mensaje formateado
		return speech

	""" 
	Adjunta texto al mensaje a las respuestas

	Atributos
		message: Estructura del mensaje
		data_model: Datos con los cuales va a ser reemplazado

	Retorna
		El mensaje con el texto formateado
	"""
	@staticmethod
	def pegarTextoReply(message, data_model = {}, label = 'replies'):
		speech = message[label]

		# Si el texto se le puede pegar texto
		if 'format' in message:
			# Adjunta el texto
			speech = data_model
		# Retorna el mensaje formateado
		return speech		

	""" 
	Adjunta texto de un array al mensaje

	Atributos
		message: Estructura del mensaje
		data_model: Datos con los cuales va a ser reemplazado

	Retorna
		El mensaje con el texto formateado
	"""
	@staticmethod
	def pegarTextoArray(message, data_model = {}):
		# Si el texto se le puede pegar texto
		for key, value in message.items():
			# Si en el valor hay un subelemento
			if type(value) is list : 
				# Convierto la lista a un tipo dict
				valueN = dict([(k,d[k]) for d in value for k in d])

				# Recorro el nuevo dict
				for kv, vv in valueN.items():
					# Recorro el modelo de datos
					for kd, vd in data_model.items() :
						# Si coinciden las llaves
						if kv == kd :
							# Actualizo el valor
							valueN[kv] = vd 

				# Convierto el dict en un list
				message[key] = [ valueN ]
			else :
				# Recorro los modelos
				for k, v in data_model.items() :
					if key == k :
						# Actualizo la llave
						message[key] = v

		# Regreso el mensaje
		return message

	""" 
	Crea el mensaje definitivo a enviar de respuesta

	Atributos
		message: Estructura del mensaje

	Retorna
		Mensaje de respuesta
	"""
	@staticmethod
	def crearMensaje(messages):
		# Todo el mensaje contruido
		respuesta = { "messages": messages }
		# Retorna el mensaje de respuesta
		return respuesta

