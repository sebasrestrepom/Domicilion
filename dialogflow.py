#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import make_response
from flask import request

from models import MessageModel
from models import UserModel
from models import RestauranteModel

import json

# Imports de python
from bson import Binary, Code
from bson.json_util import dumps

# Capa de negocio
from business.factory import Factory
from business.orden import Orden
from business.user import User

""" 
Encargado de recibir los mensajes de dialogflow

Atributos
	response : Respuesta dada por dialogflow
	token: Token de facebook

Retorna
	Mensaje de respeusta para el usuario
"""
def recibirResponse(response, token):

	# Obtiene el id del usuarioo que escricio
	sender_id = response['originalRequest']['data']['sender']['id']
	# Obtengo el intent
	intent = response['result']['metadata']
	# Obtener los parametros
	parametros = response['result']['parameters'] 

	# Instanciar el objeto usuario
	objUser = User()
	# Consulta si el usuario existe en la base de datos
	user = objUser.buscarUsuario(sender_id)
	# Validar si el usuario esta en el sistema
	if user is None :
		# Si no existe, crea el usuario
		user = objUser.crearUsuario(sender_id, token)
	else :
		# Validar si existe
		if 'es_nuevo' not in user :
			# El usuario ya es recurrente
			user['es_nuevo'] = True
			# Guarda el usuario
			UserModel.save(user)
			# 
			nomClase, intentName = 'smartTalk', 'saludar'
		else :
			# Si existe y es la segunda vez que viene
			if user['es_nuevo'] == True:
				# El usuario ya es recurrente
				user['es_nuevo'] = False
				# Guarda el usuario
				UserModel.save(user)

			# Si no han puesto la ciudad
			if 'ciudad' not in user :
				# El usuario ya es recurrente
				user['es_nuevo'] = True
				# Guarda el usuario
				UserModel.save(user)

	objOrden = Orden()
	# Consulta del usuario por estado orden
	orden = objOrden.consultarOrden(sender_id, "EN_PROCESO")
	# Valido si la orden existe
	orden = objOrden.crearOrden(user) if orden is None else objOrden.confirmarOrden(orden,user)

	if 'ciudades' in parametros :
		if parametros['ciudades'] != "" :
			print "entre 1"
			# Agrego la ciudad al usuario
			user['ciudad'] = parametros['ciudades'].lower()
			# Grabo el usuario
			UserModel.save(user)

	#Separar el intent
	if 'ciudad' not in user:
		print "entre2"
		nomClase, intentName = 'smartTalk', 'saludar'

	else :
		# Saco los nombres
		nomClase, intentName = intent['intentName'].split(".")
		# Valido si existe
		if user['ciudad'] != 'cartago':
			print "NO ERES DE CARTAGO"
			# Si el usuario decide cambiar de ciudad
			if nomClase == 'user' and intentName == 'cambiarCiudad' :
				nomClase, intentName = 'user','cambiarCiudad' 
			else :
				nomClase, intentName = 'user','noHayCiudad' 

	# variable para almacenar las respuestas
	mensajeSalida = ''
	# Obtiene el objeto de la clase que viene de dialogflow
	obj = Factory().crearObjeto(nomClase)
	# Se encarga de llamar el intent correspondiente
	mensajeSalida = getattr(obj, intentName)(user, parametros, orden)

	# Retorna mensaje de salida
	return generarRespuesta(mensajeSalida)

def generarRespuesta(respuesta):
	print "respuesta:"
	print respuesta

	# Convertir la respuesta para poder enviar al servidor
	respuesta = dumps(respuesta)

	# Generar 
	r = make_response(respuesta)
	# Agregar encabezado
	r.headers['Content-Type'] = 'application/json'
	# Retorna la respuesta
	return r	