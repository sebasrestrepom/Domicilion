#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Imports de python
import os
import random
import datetime
import json
from flask import request

# Capa de acceso de datos
from models import UserModel

# Capa de negocio
from log import registrarLogAsync
from business.apiai import Apiai
from business.mensaje import Mensaje
from restaurante import Restaurante

# Clase encargada de conectarse a la API
from api import call_user_API

class User(Apiai):

	""" 
	Crear un uusario nuevo en el sistema

	Atributos
		sender_id : Id del usuario en facebook

	Retorna
		El usuario creado
	"""
	def crearUsuario(self, sender_id, token) :
		# Voy a consultar el usuario
		data = call_user_API(sender_id, token)

		print json.dumps(data, indent = 4)

		# Si el campo no existe en la estructura
		gender = data['gender'] if 'gender' in data else 'male'

		# Creo el usuario en el sistema
		user = UserModel.new(first_name = data['first_name'], 
			last_name = data['last_name'], 
			gender = gender,
			user_id = sender_id, 
			created_at = datetime.datetime.now(), 
			es_nuevo = True
			)
		# Regresa el usaurio creado
		return user

	""" 
	Buscar el usuario

	Atributos 
		sender_id : Id del usuario en facebook

	Retorna
		El usuario creado
	"""		
	def buscarUsuario(self, sender_id):
		return UserModel.find(user_id = sender_id)

	""" 
	Metodo encargado de devolver el genero del usuario

	Atributos
		genero: si es hombre o mujer
		mayuscula: si empieza en mayuscula o no

	Retorna
		El genero de la persona
	"""	
	@staticmethod
	def devolverGenero(genero, mayuscula = True):
		hombre = ['mijito', 'hijito', 'hijo', 'pelaito', 'chinito']
		mujer = ['mijita', 'hijita', 'hija']

		# Obtiene el pronombre para llamar a la persona
		generoHombre = random.choice(hombre)
		generoMujer = random.choice(mujer)

		# Pone o no el texto en mayuscula
		generoHombre = generoHombre.capitalize() if mayuscula else generoHombre
		generoMujer = generoMujer.capitalize() if mayuscula else generoMujer

		# Regresa el pronombre
		return generoMujer if genero == "female" else generoHombre

	""" 
	Metodo encargado de devolver el genero del usuario

	Atributos
		genero: si es hombre o mujer
		mayuscula: si empieza en mayuscula o no

	Retorna
		El genero de la persona
	"""	
	def darPermisos(self, user, parametros, orden):
		# Variable para almacenar los mensajes a enviar
		messages = [] 

		# Consultar el mensaje que debo mandar
		msgs = Mensaje.consultarMensaje("darPermisos")

		# Recorro todos los mensajes
		for msg in msgs :
			# URL de regreso de autorizacion
			# https://a642e299.ngrok.io/autorizacion
			autorizacion = (request.url_root + 'autorizacion').replace('http://', 'https://')
			print autorizacion

			# ID de la aplicación
			client_id = os.environ['APP_CLIENT_ID']
			print client_id

			# https://www.facebook.com/v2.12/dialog/oauth?client_id={}&redirect_uri={}&state={}
			URL = 'https://www.facebook.com/v2.12/dialog/oauth?client_id={}&redirect_uri={}&state={}'.format(client_id, autorizacion, user['user_id'])
			print URL

			imageURI = request.url_root + 'images/images/default.jpg'

			# Contruyo el array a mandar
			data = { 
				'postback' : URL, 
				'text' : 'Autorizar',
				'imageUrl' : imageURI,
				'title' : 'Permisos especiales',
				'subtitle' : 'Por favor dame permisos'
			}

			msg = Mensaje.pegarTextoArray(msg, data)

			# Agregar al mensaje otra tarjeta
			messages.append(msg)

		# Construye el mensaje y retorna para enviar
		return Mensaje.crearMensaje(messages)

	def noHayCiudad(self, user, parametros, orden):

		# Variable para almacenar los mensajes a enviar
		messages = []
		if user['ciudad'] == 'pereira':
			msgs = Mensaje.consultarMensaje("noHayCiudad", "pereira")
		else:

			msgs = Mensaje.consultarMensaje("noHayCiudad", "cerrado")

			# Recorro todos los mensajes
		for msg in msgs :
			# Contruyo el array a mandar
			data = { 
				'genero' : User.devolverGenero(True)
			}
			
			msg['speech'] = Mensaje.pegarTexto(msg, data, 'speech')

			# Agregar al mensaje otra tarjeta
			messages.append(msg)

		

		# Retorna el mensaje de respuesta
		return Mensaje.crearMensaje(messages)

	def cambiarCiudad(self, user, parametros, orden):
		# Variable para almacenar los mensajes a enviar
		messages = []

		# Saludar y mostrar mensaje de donde se encuentra
		msgs = Mensaje.consultarMensaje("cambiarCiudad")

		# Recorro todos los mensajes
		for msg in msgs :
			# Contruyo el array a mandar
			data = { 'genero' : User.devolverGenero(True) }
			# Concateno el genero al mensaje
			msg['title'] = Mensaje.pegarTexto(msg, data, 'title')

			# Concateno las ciudades al mensaje
			msg['replies'] = Mensaje.pegarTextoReply(msg, Restaurante.consultarCiudades())

			# Pego el mensaje
			messages.append(msg)

			# Construye el mensaje y retorna para enviar
			return Mensaje.crearMensaje(messages)

	""" 
	Guarda la ciudad en el usuario

	Atributos
		user: info usuario
		parametros: de dialogflow
		orden : datos de la orden

	Retorna
		Mensaje de respuesta
	"""	

	def agregarCiudad(self, user, parametros, orden):
		# Obtengo la ciudad de los parametros
		ciudad = parametros['ciudades'].lower()
		# Agrego la ciudad al usuario
		user['ciudad'] = ciudad
		# Cambio el estado del usuario
		user['es_nuevo'] = False
		# Guardo al usuario
		UserModel.save(user)
		restaurante = Restaurante()
		return restaurante.recomendarIndeciso(user, parametros, orden, True)

		# # Variable para almacenar los mensajes a enviar
		# messages = []

		# # Consultar el mensaje que debo mandar
		# msgs = Mensaje.consultarMensaje("saludar", "recurrente")

		# # Recorro todos los mensajes
		# for msg in msgs :

		# 	# Contruyo el array a mandar
		# 	data = { 'first_name' : user['first_name'] }

		# 	msg['speech'] = Mensaje.pegarTexto(msg, data)

		# 	# Pego el mensaje
		# 	messages.append(msg)

		# # Construye el mensaje y retorna para enviar
		# return Mensaje.crearMensaje(messages)