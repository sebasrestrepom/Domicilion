#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Imports de python
from flask import request
import datetime
from operator import itemgetter, attrgetter, methodcaller
from pathlib import Path
import smtplib
import threading

# Capa de acceso de datos
from models import UserModel
from models import RestauranteModel
from models import OrdenModel

# Capa de negocio
from apiai import Apiai
from business.mensaje import Mensaje
from business.orden import Orden
from business.restaurante import Restaurante
from business.user import User


class Almuerzo(Apiai):


	def pedirAlmuerzo(self,user, parametros, orden):
		nomAlmuerzo = 'almuerzo'

		# Obtener la hora del sistema
		jornada, dia, hora = Orden.consultarDiaHora()
		
		genero = User.devolverGenero(user['gender'], False) 

		# Variable para almacenar los mensajes a enviar
		messages = []

		# Variable con el mensaje de respuesta
		respuesta = ''
		# Obtener el parametro de comida
		# Obtener el parametro de comida
		nomComida = 'almuerzo'

		print 'restaurante' in orden

		# Verifico si la orden ya tiene comida
		if 'restaurante' in orden and orden['restaurante'] != '':

			print "entre al primero"
			# Aquí tengo que almacenar el nuevo valor de la comida
			print "me quede aqui"
			# Redirecciona al flujo de 
			return Restaurante.seleccionarRestauranteAlmuerzo(user, parametros, orden) 
		
		print "entre al segundo"
		# Si no tiene comida
		# Agrego la comida a la orden
		orden['comida'].append(nomAlmuerzo)
		# Guardo la orden en la base de datos
		OrdenModel.save(orden)

		# Consultar que restaurantes tienen esa comida
		restauranteAlmuerzo = RestauranteModel.find_all(almuerzos = { '$elemMatch' : {'slug': nomAlmuerzo}},
			ciudad = user['ciudad'].lower()
			).sort('nombre',1)
		
		print 'nomAlmuerzo-----------------------------------'
		print nomAlmuerzo

		# Contar cantidad de restaurante
		nroRestaurante = restauranteAlmuerzo.count()
		
		print "nroRestaurante"
		print nroRestaurante
		# Si hay restaurante mostrar los restaurantes
		if nroRestaurante >= 1 :
			print "entre al 2.1"

			# consultar si el restaurante esta abierto
			restaurantes = restauranteComida = RestauranteModel.find_all(almuerzos = { '$elemMatch' : {'slug': nomAlmuerzo}},
			ciudad = user['ciudad'].lower()
			).sort('nombre',1)

			# Cuantos registros trae la consulta
			restAbierto = restaurantes.count()
			print "estos son los abiertos"
			print restAbierto
			# Si hay restaurantes
			if restAbierto >= 1:
				print "entre al 2.2"

				# Mensaje para decirle al usuario que tiene que hacer
				messages = []
				# Consulto el mensaje de salida
				msgs = Mensaje.consultarMensaje("pedirAlmuerzo", "claroDonde")

				for msg in msgs :
					# Contruyo el array a mandar
					data = { 
						'genero' : genero, 
						'nomAlmuerzo' : nomAlmuerzo
					}

					msg['speech'] = Mensaje.pegarTexto(msg, data)

					# Agregar al mensaje otra tarjeta
					messages.append(msg)

				# Recorre todos los restaurantes

				# Recorre todos los restaurantes
				for restaurante in iter(restaurantes.next, None):
					
					# Contruye el path del archivo
					validateImage = Path('images/' + restaurante['slug'] + '.jpg')
					# Validar si la imagen existe
					imagen = 'images/images/' + restaurante['slug'] + '.jpg' if validateImage.exists() else 'images/images/default.jpg'
					# URL completa de la imagen
					imageURI = request.url_root + imagen

					# Consulto el mensaje de salida
					msgs = Mensaje.consultarMensaje("pedirAlmuerzo", "restaurantes")

					# Recorre cada mensaje y lo pinta
					for msg in msgs :

						# Contruyo el array a mandar
						data = { 
							'postback' : restaurante['slug'], 
							'text' : restaurante['nombre'],
							'imageUrl' : imageURI,
							'title' : restaurante['nombre'],
							'subtitle' : restaurante['descripcion']
						}

						msg = Mensaje.pegarTextoArray(msg, data)

						# Agregar al mensaje otra tarjeta
						messages.append(msg)
			else :
				# No hay, enviar mensaje de salida y volver a pedir comida
				genero = User.devolverGenero(user['gender'], False)

				msgs = Mensaje.consultarMensaje("pedirAlmuerzo", "malaSuerte")

				# Recorre cada mensaje y lo pinta
				for msg in msgs :
					# Contruyo el array a mandar
					data = { 
						'genero' : genero
					}

					msg['speech'] = Mensaje.pegarTexto(msg, data) 

					# Agregar al mensaje otra tarjeta
					messages.append(msg)
		else :
		# No hay, enviar mensaje de salida y volver a pedir comida
			genero = User.devolverGenero(user['gender'], True)

			# Consultar el mensaje que debo mandar
			msgs = Mensaje.consultarMensaje("pedirAlmuerzo", "sinComida")

			# Recorro todos los mensajes
			for msg in msgs :
				# Contruyo el array a mandar
				data = { 
					'genero' : genero, 
					'anyComida' : nomComida.encode('utf8')
				}

				msg['speech'] = Mensaje.pegarTexto(msg, data)

				# Agregar al mensaje otra tarjeta
				messages.append(msg)

			# Construye el mensaje y retorna para enviar
			return Mensaje.crearMensaje(messages)

		# Retorna el mensaje de respuesta
		return Mensaje.crearMensaje(messages)

				
	def seleccionarCarneAlmuerzo(self,user, parametros, orden):
		nomPrincipio = parametros['principio']
		slugRestaurante = parametros['restaurantes']


		print 'slugRestaurante-------------------------------------------------'
		print slugRestaurante
	
		nomAlmuerzo = 'almuerzo'
		
		almuerzos = ''
		carne = ''

		messages = []

		msgs = Mensaje.consultarMensaje("seleccionarCarneAlmuerzo", "textocarne")

			# Recorro todos los mensajes
		for msg in msgs :
			# Convertir el mensaje
			msg['speech'] = Mensaje.pegarTexto(msg)

			# Agregar al mensaje otra tarjeta
			messages.append(msg)

		# Busco el plato en los restaurantes
		restaurantes = RestauranteModel.find_all(almuerzos = {
				'$elemMatch' : {
					'slug': nomAlmuerzo
				}
			},
			ciudad = user['ciudad'].lower()
		).sort('nombre',1)

		print restaurantes
		print nomAlmuerzo

		# Recorre todos los restaurantes
		for restaurante in iter(restaurantes.next, None):

			print "estoy en 1"
			# Busca el plato
			almuerzo = [almuerzos for almuerzos in restaurante['almuerzos'] if almuerzos['slug'] == nomAlmuerzo]
			
			print "este es la busquyedad"
			print almuerzo

		# Encuentra los principios de los platos
		for p in almuerzo :
			print "estoy en 2"
			carne = p.get('carne')		

		# Recorro los tamaños
		for carne in carne :
			print "estoy en 3"
			# Concateno las respuestas a mostrar en el mensaje
			validateImage = Path('images/' + carne['nombre'].encode('utf8') + '.jpg')
			# Validar si la imagen existe
			imagen = 'images/images/' + carne['nombre'].encode('utf8') + '.jpg' if validateImage.exists() else 'images/images/default.jpg'
			# URL completa de la imagen
			imageURI = request.url_root + imagen

			# Consulto el mensaje de salida
			msgs = Mensaje.consultarMensaje("seleccionarCarneAlmuerzo", "carne")

			# Recorre cada mensaje y lo pinta
			for msg in msgs :

				# Contruyo el array a mandar
				data = { 
					'postback' : carne['codigo'].encode('utf8'), 
					'text' : carne['nombre'].encode('utf8'),
					'imageUrl' : imageURI,
					'title' : carne['nombre'].encode('utf8'),
					'subtitle' : carne['descripcion'].encode('utf8')
				}

				msg = Mensaje.pegarTextoArray(msg, data)

				# Agregar al mensaje otra tarjeta
				messages.append(msg)
			

		# Retorna el mensaje de respuesta
		return Mensaje.crearMensaje(messages)

	def seleccionarJugoAlmuerzo(self,user, parametros, orden):
		print "estoy en carne"
		nomCarne = parametros['carne']
		messages = []

		nomAlmuerzo = 'almuerzo'
		
		almuerzos = ''
		jugo = ''

		msgs = Mensaje.consultarMensaje("seleccionarJugoAlmuerzo", "textojugo")

			# Recorro todos los mensajes
		for msg in msgs :
			# Convertir el mensaje
			msg['speech'] = Mensaje.pegarTexto(msg)

			# Agregar al mensaje otra tarjeta
			messages.append(msg)

		# Busco el plato en los restaurantes
		restaurantes = RestauranteModel.find_all(almuerzos = { '$elemMatch' : {'slug': nomAlmuerzo}},
				ciudad = user['ciudad'].lower()
				).sort('nombre',1)
		print restaurantes
		print nomAlmuerzo
		# Recorre todos los restaurantes
		for restaurante in iter(restaurantes.next, None):
			print "estoy en 1"
			# Busca el plato
			almuerzo = [almuerzos for almuerzos in restaurante['almuerzos'] if almuerzos['slug'] == nomAlmuerzo]
			
			print "este es la busquyedad"
			print almuerzo

		# Encuentra los principios de los platos
		for p in almuerzo :
			print "estoy en 2"
			jugo = p.get('jugo')


		# Recorro los tamaños
		for jugo in jugo :
			print "estoy en 3"
			# Concateno las respuestas a mostrar en el mensaje
			validateImage = Path('images/' + jugo['nombre'].encode('utf8') + '.jpg')
			# Validar si la imagen existe
			imagen = 'images/images/' + jugo['nombre'].encode('utf8') + '.jpg' if validateImage.exists() else 'images/images/default.jpg'
			# URL completa de la imagen
			imageURI = request.url_root + imagen

			# Consulto el mensaje de salida
			msgs = Mensaje.consultarMensaje("seleccionarJugoAlmuerzo", "jugo")

			# Recorre cada mensaje y lo pinta
			for msg in msgs :

				# Contruyo el array a mandar
				data = { 
					'postback' : jugo['codigo'].encode('utf8'), 
					'text' : jugo['nombre'].encode('utf8'),
					'imageUrl' : imageURI,
					'title' : jugo['nombre'].encode('utf8'),
					'subtitle' : jugo['descripcion'].encode('utf8')
				}

				msg = Mensaje.pegarTextoArray(msg, data)

				# Agregar al mensaje otra tarjeta
				messages.append(msg)
			
		# Retorna el mensaje de respuesta
		return Mensaje.crearMensaje(messages)


	def  cantidadPlatosAlmuerzo(self,user, parametros, orden):
		nomJugo = parametros['jugo']
		print nomJugo
		genero = User.devolverGenero(user['gender'], True)

		# Variable de mensajes
		messages = []

		# Consulto el mensaje de salida
		msgs = Mensaje.consultarMensaje("cantidadPlatosAlmuerzo")

		# Recorre cada mensaje y lo pinta
		for msg in msgs :

			# Contruyo el array a mandar
			data = { 
				'genero' : genero
			}

			msg['title'] = Mensaje.pegarTexto(msg, data, 'title')

			# Agregar al mensaje otra tarjeta
			messages.append(msg)

		# Retorna el mensaje de respuesta
		return Mensaje.crearMensaje(messages)

	def recibirCantidadAlmuerzo(self,user, parametros, orden):
		cantidad = parametros['number']
		nomAlmuerzo = 'almuerzo'
		nomPrincipio = parametros['principio']
		nomRestaurante = parametros['restaurantes']
		nomRestaurante2 = orden['restaurante']
		
		nomCarne = parametros['carne']
		nomJugo = parametros['jugo']
		print "este es el restaurante"
		print nomRestaurante
		print "este es el restaurante 2"
		print nomRestaurante2
		print "esta es la cantidad"
		print cantidad
		print "este es el almuerzo"
		print nomAlmuerzo
		print "este es el principio"
		print nomPrincipio
		print "esta es la carne"
		print nomCarne
		print "este es el jugo"
		print nomJugo

		print "primero"
		
		restaurantes = RestauranteModel.find_all(slug = nomRestaurante2);

		print restaurantes

		for restaurante in iter(restaurantes.next, None):
			print "segundo"
			# Busca el plato
			#tamano = [tamanos for tamanos in restaurante['platos']['tamanos'] if tamanos['codigo'] == nomTamano]
			for almuerzos in restaurante['almuerzos'] :
				print "tercero"
				# Preguntar si principio existe
				if 'principios' in almuerzos :
					data = {
						'principio' : nomPrincipio,
						'carne' : nomCarne,
						'jugo' : nomJugo,
						'cantidad' : cantidad,
						'precio' : almuerzos['precio']
					}

					# Agrega el almuerzo
					orden['almuerzo'].append(data)
					# Guardo la orden en la base de datos
					OrdenModel.save(orden)

				else:
					print"-------------------entre al primero--------------"
					restaurantes = RestauranteModel.find_all(slug = nomRestaurante);
				
					print "-------------------entre al segudo---------------------------"
					# Busca el plato
					#tamano = [tamanos for tamanos in restaurante['platos']['tamanos'] if tamanos['codigo'] == nomTamano]
					

					if platos['codigo'] == nomPlato :
						print "este es el mega chupapijas"
						print "---------------------entre al tercero----------------"
						data = {
							'codigo' : nomPlato,
							'nombre' : platos['comida'],
							'precio' : platos['precio'],
							'cantidad' : cantidad
						}

						# Agrega el plato 
						orden['almuerzo'].append(data)
						# Guardo la orden en la base de datos
						OrdenModel.save(orden)

		return self.mostrarAgregarAlmuerzo(user,orden)

	def mostrarAgregarAlmuerzo(self,user,orden):
		genero = User.devolverGenero(user['gender'], True)

		# Variable para almacenar los mensajes a enviar
		messages = []

		# Consulto el mensaje de salida
		msgs = Mensaje.consultarMensaje("mostrarAgregarAlmuerzo")

		# Recorre cada mensaje y lo pinta
		for msg in msgs :

			# Contruyo el array a mandar
			data = { 'genero' : genero }

			msg['title'] = Mensaje.pegarTexto(msg, data, 'title')

			# Agregar al mensaje otra tarjeta
			messages.append(msg)

		# Retorna el mensaje de respuesta
		return Mensaje.crearMensaje(messages)


	
	

		
	
	