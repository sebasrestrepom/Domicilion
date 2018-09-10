#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Imports de python
import datetime
import random

# Capa de acceso de datos
from models import RestauranteModel

# Capa de negocio
from log import registrarLogAsync
from business.apiai import Apiai
from business.mensaje import Mensaje
from business.restaurante import Restaurante
from business.user import User
import business

class SmartTalk(Apiai):

	""" 
	Metodo encargado de saludar al usuario

	Atributos
		user : usuario con quien se esta sosteniendo conversación

	Retorna
		Mensaje de respuesta 
	"""
	def saludar(self, user, parametros, orden): 
		# Variable para almacenar los mensajes a enviar
		messages = []

		# Si es la primera vez que llega
		if user['es_nuevo'] == True :
			# Saludar y mostrar mensaje de donde se encuentra
			msgs = Mensaje.consultarMensaje("saludar", "primeraVez")

			# Recorro todos los mensajes
			for msg in msgs :
				# Contruyo el array a mandar
				data = { 'genero' : User.devolverGenero(user['gender'], True) }
				# Concateno el genero al mensaje
				msg['title'] = Mensaje.pegarTexto(msg, data, 'title')

				# Concateno las ciudades al mensaje
				msg['replies'] = Mensaje.pegarTextoReply(msg, Restaurante.consultarCiudades())

				# Pego el mensaje
				messages.append(msg)

			# Registrar el log
			registrarLogAsync(user['user_id'], 'smartTalk', 'saludar', 'primeraVez')

			# Construye el mensaje y retorna para enviar
			return Mensaje.crearMensaje(messages)

		# Llama a recomendar indeciso
		restaurante = Restaurante()
		return restaurante.recomendarIndeciso(user, parametros, orden, True)	

		# # Consultar el mensaje que debo mandar
		# msgs = Mensaje.consultarMensaje("saludar", "recurrente")

		# # Recorro todos los mensajes
		# for msg in msgs :

		# 	# Contruyo el array a mandar
		# 	data = { 'first_name' : user['first_name'] }

		# 	msg['speech'] = Mensaje.pegarTexto(msg, data)

		# 	# Pego el mensaje
		# 	messages.append(msg)

		# # Registrar el log
		# registrarLogAsync(user['user_id'], 'smartTalk', 'saludar', 'recurrente')

		# # Construye el mensaje y retorna para enviar
		# return Mensaje.crearMensaje(messages)

	""" 
	Retorna la hora del servidor

	Atributos
		user : usuario con quien se esta sosteniendo conversación
		parametros: Los parametros que vienen de dialogflow
		orden: Datos de la orden

	Retorna
		Mensaje de respuesta 
	"""
	def sinRespuesta(self, user, parametros, orden):
		genero = User.devolverGenero(orden['gender'], False)
		messages = []
		print "1"

		# Consultar el mensaje que debo mandar
		msgs = Mensaje.consultarMensaje("sinRespuesta")


		# Recorro todos los mensajes
		for msg in msgs :

			# Contruyo el array a mandar
			data = { 
				'genero' : genero
				
			}

			msg['speech'] = Mensaje.pegarTexto(msg, data)
			print "2"
			# Pego el mensaje
			messages.append(msg)

			print "3"
		# Registrar el log
		registrarLogAsync(user['user_id'], 'smartTalk', 'sinRespuesta', '')
		return Mensaje.crearMensaje(messages)

			



	def queHoraEs(self, user, parametros, orden):
		# No hay, enviar mensaje de salida y volver a pedir comida
		genero = User.devolverGenero(orden['gender'], False)

		dia =  int(datetime.datetime.now().strftime("%w"))
		# Hora exacta del sistema
		hora = datetime.datetime.now().strftime("%H:%M") 
		
		# Variable para almacenar los mensajes a enviar
		messages = []

		# Consultar el mensaje que debo mandar
		msgs = Mensaje.consultarMensaje("queHoraEs")

		# Recorro todos los mensajes
		for msg in msgs :

			# Contruyo el array a mandar
			data = { 
				'genero' : genero,
				'dia' : dia,
				'hora' : hora
			}

			msg['speech'] = Mensaje.pegarTexto(msg, data)

			# Pego el mensaje
			messages.append(msg)

		# Registrar el log
		registrarLogAsync(user['user_id'], 'smartTalk', 'queHoraEs', '')

		# Construye el mensaje y retorna para enviar
		return Mensaje.crearMensaje(messages)