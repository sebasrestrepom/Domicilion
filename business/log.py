#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Imports de python
import threading
import datetime

# Capa de acceso de datos
from api import log_ifttt

""" 
Metodo para registrar el log 

Atributos
	user_id: Identificador del usuario
	user_name: Nombre completo de la persona
	clase: Clase que esta ejecutando
	metodo: Metodo que disparo
	mensaje: Mensaje que se mostro

Retorna
	
"""
def registrarLogAsync(user_id, clase, metodo, mensaje, restaurante = ''):
	def registrarLog(user_id, clase, metodo, mensaje, restaurante = ''):
		# Obtengo la fecha del sistema
		fecha = datetime.datetime.now().strftime("%d/%m/%Y %H:%M") 

		# Cadena para construir el log
		log = '{} ||| {} ||| {} ||| {} ||| {} ||| {}'.format(fecha,
			user_id,
			clase, 
			metodo, 
			mensaje,
			restaurante
		)

		# Registrar el log
		log_ifttt(log)

	async = threading.Thread(name='registrarLog', target= registrarLog, args=(user_id, clase, metodo, mensaje, restaurante))
	async.start()	
