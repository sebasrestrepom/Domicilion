#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Imports de python
import random
from flask import request
from pathlib import Path

# Capa de acceso de datos
from models import RestauranteModel
from models import OrdenModel

# Capa de negocio
from log import registrarLogAsync
from business.apiai import Apiai
from business.mensaje import Mensaje
import business

class Restaurante(Apiai):

	""" 
	Muestra los productos pedidos

	Atributos
		user: Datos del usuario
		parametros: parametros de dialogflow
		orden: datos de la orden

	Retorna
		Mensaje de respuesta formateado para enviar
	"""	
	@staticmethod
	def consultarNombre(slug):
		return RestauranteModel.find(slug = slug)['nombre']

	""" 
	Retorna recomendaciones para el cliente

	Atributos
		user: Datos del usuario
		parametros: parametros de dialogflow
		orden: datos de la orden

	Retorna
		Mensaje de respuesta formateado para enviar
	"""	
	# def queTiene(self, user, parametros, orden):
	# 	# Variable para los mensajes
	# 	messages = []
	# 	# Llamar al metodo
	# 	return self.recomendarIndeciso(user, parametros, orden, messages)

	""" 
	Retorna recomendaciones para el cliente

	Atributos
		user: Datos del usuario
		parametros: parametros de dialogflow
		orden: datos de la orden

	Retorna
		Mensaje de respuesta formateado para enviar
	"""	
	def permanecerRestaurante(self,user, parametros, orden):
		print "parametros"
		print parametros
		

		return self.recomendarIndeciso(user, parametros, orden)
	def recomendarIndeciso(self, user, parametros, orden, saludar = False):

		# Consulta la jornada, el día y la hora
		jornada, dia, hora = business.Orden().consultarDiaHora()

		messages = []

		# Variable restaurante
		nomRestaurante = orden['restaurante'] if 'restaurante' in orden else ''

		# Si no hay restaurante
		if nomRestaurante == '' :
			# Consulta los restaurantes abiertos 
			restaurantes = RestauranteModel.find_all(horarios = {
					'$elemMatch' : {
						'dia' : dia,
						'{}.horainicio'.format(jornada) : { '$lte' : hora },
						'{}.horafin'.format(jornada) : { '$gte' : hora }
					}
				},
				ciudad = user['ciudad'].lower())
		else :
			# Consulta las comidas en el restaurante
			restaurantes = RestauranteModel.find_all(slug = nomRestaurante,
				horarios = {
					'$elemMatch' : {
						'dia' : dia,
						'{}.horainicio'.format(jornada) : { '$lte' : hora },
						'{}.horafin'.format(jornada) : { '$gte' : hora }
					}
				},
				ciudad = user['ciudad'].lower())

		# Array para guardar las sugerencias
		categorias = []

		# No retorna nada
		if restaurantes.count() == 0 :

			if nomRestaurante == '' :
				# Todos los restaurantes estan cerrados
				msgs = Mensaje.consultarMensaje("recomendarIndeciso", "nohay")

				# Recorro todos los mensajes
				for msg in msgs :

					data = {
						'genero' : business.User.devolverGenero(user['gender'], False) 
					}

					msg['speech'] = Mensaje.pegarTexto(msg, data)

					# Agregar al mensaje otra tarjeta
					messages.append(msg)

				# Registrar el log
				registrarLogAsync(user['user_id'], 'restaurante', 'recomendarIndeciso', 'no hay restaurantes abiertos')
			else :
				# Todos los restaurantes estan cerrados
				msgs = Mensaje.consultarMensaje("recomendarIndeciso", "restauranteCerrado")

				# Recorro todos los mensajes
				for msg in msgs :

					data = {
						'genero' : business.User.devolverGenero(user['gender'], true),
						'restaurante' : self.consultarNombre(orden['restaurante'])
					}

					msg['speech'] = Mensaje.pegarTexto(msg, data)

					# Agregar al mensaje otra tarjeta
					messages.append(msg)

				# Registrar el log
				registrarLogAsync(user['user_id'], 'restaurante', 'recomendarIndeciso', 'restaurante cerrado', nomRestaurante)

			# Construye el mensaje y retorna para enviar
			return Mensaje.crearMensaje(messages)
		else :
			# Recorro los restaurantes
			for restaurante in restaurantes :
				# Validar si viene el restaurante en la orden
				if nomRestaurante == '' :
					# Carga las categorias
					categorias.append("👉 {}".format(restaurante['categoria']))
				else :
					# Recorre los platos
					for plato in restaurante["platos"] :
						# Valida si el plato esta en la categoria
						if "👉 {}".format(plato['slug'].lower()) not in categorias:
							# Carga los platos
							categorias.append("👉 {}".format(plato['slug'].lower()))

			# Si la cantidad de categorias es mayor a tres
			if len(categorias) > 3 :
				# Obtengo categorias al azar
				categorias = random.sample(categorias,  3)

			# Consultar el mensaje que debo mandar
			msgs = Mensaje.consultarMensaje("saludar", "recurrente") if saludar else Mensaje.consultarMensaje("recomendarIndeciso", "existe")

			# Recorro todos los mensajes
			for msg in msgs : 		

				if msg['type'] == 2 :
					msg['replies'] = Mensaje.pegarTextoReply(msg, categorias)	
				else :
					# Contruyo el array a mandar
					data = { 'first_name' : user['first_name'] }
					msg['speech'] = Mensaje.pegarTexto(msg, data)

				# Agregar al mensaje otra tarjeta
				messages.append(msg)

			# Registrar el log
			registrarLogAsync(user['user_id'], 'restaurante', 'recomendarIndeciso', 'muestra opciones al usuario')

			# Construye el mensaje y retorna para enviar
			return Mensaje.crearMensaje(messages)

	""" 
	Retorna lista de ciudades donde operamos

	Atributos

	Retorna
		Lista ciudades
	"""	
	@staticmethod
	def consultarCiudades():
		return ['📍 Cartago', '📍 Pereira próximamente...']


	""" 
	Captura el restaurante seleccionado por el usuario

	Atributos
		user : usuario con quien se esta sosteniendo conversación
		parametros: obtenidos a través de dialogflow

	Retorna
		Mensaje de respuesta 
	"""
	@staticmethod
	def seleccionarRestaurante(user, parametros, orden, nomRestaurante = ''):
		# El nombre de la comida pudo haber cambiado
		# Obtener el parametro de comida
		nomComida = parametros['comidas'].lower()

		# Tengo el parametro en dialogflow
		if 'restaurantes' in parametros :
			# Sobre escribo la variable
			nomRestaurante = parametros['restaurantes']
			# Carga el restaurante desde la orden
		 	orden['restaurante'] = nomRestaurante 
		 	# Guardar el nombre del restaurante
			OrdenModel.save(orden)
		else :
			# El parametro no esta en dialogflow
			# No viene desde el flo de domicilio
			if nomRestaurante == '' :
				# Consulto de la orden
				nomRestaurante = orden['restaurante']
			else : 
			 	# Carga el restaurante desde la orden
			 	orden['restaurante'] = nomRestaurante 
			 	# Guardar el nombre del restaurante
				OrdenModel.save(orden)

		# Consultar jornada, dia y hora del sistema
		jornada, dia, hora = business.Orden().consultarDiaHora()

		# Consultar que restaurantes tienen esa comida
		restaurantes = RestauranteModel.find_all(slug = nomRestaurante, 
			platos = { '$elemMatch' : {'slug': {'$regex' : nomComida, '$options' : 'i'} } },
			# Consulta la jornada el día y la hora del sistema
			horarios = {
				'$elemMatch' : {
					'dia' : dia,
					'{}.horainicio'.format(jornada) : { '$lte' : hora },
					'{}.horafin'.format(jornada) : { '$gte' : hora }
				}
			},
			ciudad = user['ciudad'].lower()
			)
		# Contar cantidad de restaurante
		nroRestaurante = restaurantes.count()
		
		# Variable para almacenar los mensajes a enviar
		messages = []

		# No existe la comida en el restaurante
		if nroRestaurante == 0:
			# Consultar el mensaje que debo mandar
			msgs = Mensaje.consultarMensaje("seleccionarRestaurante", "error")

			# Recorro todos los mensajes
			for msg in msgs :
				# Contruyo el array a mandar
				dataComida = { 
					'genero' : business.User.devolverGenero(user['gender'], True),
					'nomComida' : nomComida

				}

				
				msg['title'] = Mensaje.pegarTexto(msg, dataComida, 'title')

				# Agregar al mensaje otra tarjeta
				messages.append(msg)

			# Registrar el log
			registrarLogAsync(user['user_id'], 'restaurante', 'seleccionarRestaurante', 'no existe la comida en el restaurante', nomRestaurante)

			# Retorna el mensaje de respuesta
			return Mensaje.crearMensaje(messages)

		else:
			# Consultar el mensaje que debo mandar
			msgs = Mensaje.consultarMensaje("seleccionarRestaurante", "mensaje")

			# Recorro todos los mensajes
			for msg in msgs :
				# Convertir el mensaje
				msg['speech'] = Mensaje.pegarTexto(msg)

				# Agregar al mensaje otra tarjeta
				messages.append(msg)


			# Recorre todos los restaurantes
			for restaurante in iter(restaurantes.next, None):
				# Carga los platos
				platos = [ x for x in restaurante['platos']]

				countPlato = 0

				# Recorre los platos del restaurante
				for plato in restaurante['platos']:	

					# Solo pintar los platos que pertenecen a la comida
					if plato['slug'].lower() == nomComida :
						
						if countPlato < 10 :
							#formula para buscar nuevos usuarios
							estados = OrdenModel.find_all(user_id= user['user_id'], estado = 'FINALIZADO')
							nroestados = estados.count()
							if nroestados < 1:
								# descuento_1compra = restaurante['descuento_1compra']
								# if restaurante['descuento_1compra'] == 'si':
								# 	# Contruye el path del archivo
								# 	validateImage = Path('static/images/' + plato['codigo'] + '.jpg')
								# 	# Validar si la imagen existe
								# 	imagen = 'images/images/' + plato['codigo'] + '.jpg' if validateImage.exists() else 'images/images/default.jpg'
								# 	print "aca viene el descuento"
								# 	text = 'Por solo ${:,.0f}'.format(plato['precio'] - (plato['precio'] * 10/100)) if 'precio' in plato else plato['comida']

								# 	print "si tiene descuento"
								# 	# Consulto el mensaje de salida
								# 	msgs = Mensaje.consultarMensaje("seleccionarRestaurante", "descuento")
									
								# 	# Recorre cada mensaje y lo pinta
								# 	for msg in msgs :

								# 		# Contruyo el array a mandar
								# 		data = { 
								# 			'genero' : business.User.devolverGenero(user['gender'], True)
								# 		}

								# 		msg['speech'] = Mensaje.pegarTexto(msg, data)

								# 		# Agregar al mensaje otra tarjeta
								# 		messages.append(msg)

									


									
								# else:
								print "no tiene descuento"
								# Contruye el path del archivo
								validateImage = Path('static/images/' + plato['codigo'] + '.jpg')
								# Validar si la imagen existe
								imagen = 'images/images/' + plato['codigo'] + '.jpg' if validateImage.exists() else 'images/images/default.jpg'
							
								text = 'Por solo ${:,.0f}'.format(plato['precio']) if 'precio' in plato else plato['comida']
								
							else:
								print "no tiene descuento"
								# Contruye el path del archivo
								validateImage = Path('static/images/' + plato['codigo'] + '.jpg')
								# Validar si la imagen existe
								imagen = 'images/images/' + plato['codigo'] + '.jpg' if validateImage.exists() else 'images/images/default.jpg'
								
								text = 'Por solo ${:,.0f}'.format(plato['precio']) if 'precio' in plato else plato['comida']


							# Consulto el mensaje de salida
							msgs = Mensaje.consultarMensaje("seleccionarRestaurante", "platos")

							# Url donde se almacena la ruta de la imagen
							imageURI = request.url_root + imagen

							# Recorre cada mensaje y lo pinta
							for msg in msgs :

								# Contruyo el array a mandar
								data = { 
									'postback' : plato['codigo'], 
									'text' : text,
									'imageUrl' : imageURI,
									'title' : plato['comida'],
									'subtitle' : plato['descripcion']
								}

								msg = Mensaje.pegarTextoArray(msg, data)

								# Agregar al mensaje otra tarjeta
								messages.append(msg)

							# Aumentar contador
							countPlato += 1

			# Registrar el log
			registrarLogAsync(user['user_id'], 'restaurante', 'seleccionarRestaurante', 'muestra platos', nomRestaurante)

			# Retorna el mensaje de respuesta
			return Mensaje.crearMensaje(messages)

	""" 
	Captura el restaurante seleccionado por el usuario

	Atributos
		user : usuario con quien se esta sosteniendo conversación
		parametros: obtenidos a través de dialogflow

	Retorna
		Mensaje de respuesta 
	"""
	@staticmethod
	def seleccionarRestauranteAlmuerzo(user, parametros, orden):

		print 'parametros ----------------------------------'
		print parametros

		# El nombre de la comida pudo haber cambiado
		# Obtener el parametro de comida
		nomAlmuerzo = 'almuerzo'
		# Declarar nombre restaurante
		nomRestaurante = []

		# Trampa para cargar el nombre del restaurante
		try:
			# Verificar si el restaurante esta en parametro
			if 'restaurantes' in parametros :
				# Obtener el parametro de restaurante

				nomRestaurante = parametros['restaurantes']

				print 'nomRestaurante ----------------------------------'
				print nomRestaurante

				orden['restaurante'] = nomRestaurante

				OrdenModel.save(orden)
		except ValueError:
			print ValueError
			# Carga el restaurante desde la orden
			nomRestaurante = orden['restaurante']

		# Consultar que restaurantes tienen esa comida
		print "este es el nomAlmuerzo"
		print nomAlmuerzo
		restaurantes = restauranteComida = RestauranteModel.find_all(almuerzos = { '$elemMatch' : {'slug': nomAlmuerzo}},
				ciudad = user['ciudad'].lower()
				).sort('nombre',1)
		print "esta es la consulta"
		print restaurantes
		# Contar cantidad de restaurante
		nroRestaurante = restaurantes.count()
		print "numero restaurantes"
		print nroRestaurante
		
		
		
		if nroRestaurante == 0:
			# Consultar el mensaje que debo mandar
			messages = []
			msgs = Mensaje.consultarMensaje("seleccionarRestauranteAlmuerzo", "error")

			# Recorro todos los mensajes
			for msg in msgs :
				# Contruyo el array a mandar
				dataComida = { 
					'nomComida' : nomComida
				}

				print "dataComida ------------------------------------------"
				print dataComida

				msg['speech'] = Mensaje.pegarTexto(msg, dataComida)

				# Agregar al mensaje otra tarjeta
				messages.append(msg)

			# Registrar el log
			registrarLogAsync(user['user_id'], 'restaurante', 'seleccionarRestauranteAlmuerzo', 'no hay almuerzos', nomRestaurante)

			# Retorna el mensaje de respuesta
			return Mensaje.crearMensaje(messages)

		else:

			almuerzos = ''
			principios = ''
			messages = []
			# Consultar el mensaje que debo mandar
			msgs = Mensaje.consultarMensaje("seleccionarRestauranteAlmuerzo", "textoindicio")

			# Recorro todos los mensajes
			for msg in msgs :
				# Convertir el mensaje
				msg['speech'] = Mensaje.pegarTexto(msg)

				# Agregar al mensaje otra tarjeta
				messages.append(msg)

			# Recorre todos los restaurantes

			# Busco el plato en los restaurantes
			restaurantes = RestauranteModel.find_all(almuerzos = { '$elemMatch' : {'slug': nomAlmuerzo}})
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
				principios = p.get('principios')


			# Recorro los tamaños
			for principio in principios :
				validateImage = Path('images/' + principio['nombre'].encode('utf8') + '.jpg')
				# Validar si la imagen existe
				imagen = 'images/images/' + principio['nombre'].encode('utf8') + '.jpg' if validateImage.exists() else 'images/images/default.jpg'
				# URL completa de la imagen
				imageURI = request.url_root + imagen

				# Consulto el mensaje de salida
				msgs = Mensaje.consultarMensaje("seleccionarRestauranteAlmuerzo", "principio")

				# Recorre cada mensaje y lo pinta
				for msg in msgs :

					# Contruyo el array a mandar
					data = { 
						'postback' : principio['codigo'].encode('utf8'), 
						'text' : principio['nombre'].encode('utf8'),
						'imageUrl' : imageURI,
						'title' : principio['nombre'].encode('utf8'),
						'subtitle' : principio['descripcion'].encode('utf8')
					}

					msg = Mensaje.pegarTextoArray(msg, data)

					# Agregar al mensaje otra tarjeta
					messages.append(msg)

		# Registrar el log
		registrarLogAsync(user['user_id'], 'restaurante', 'seleccionarRestauranteAlmuerzo', 'muestra los almuerzos', nomRestaurante)

		return Mensaje.crearMensaje(messages)

	""" 
	Consulta si el restaurante tiene domicilio

	Atributos
		user: Datos del usuario
		parametros: parametros de dialogflow
		orden: datos de la orden

	Retorna
		Mensaje de respuesta formateado para enviar
	"""	
	def consultarDomicilio(self, user, parametros, orden):
		# Variable para almacenar los mensajes a enviar
		messages = [] 

		# Obtengo el parametro de restaurante
		nomRestaurante = parametros['nomRestaurante']
		anyCosita = parametros['any']

		if anyCosita != '' :
			# No tenemos el restaurante pero vamos a intentar tenerlo
			msgs = Mensaje.consultarMensaje("consultarDomicilio", "noExiste")

			# Recorro todos los mensajes
			for msg in msgs :

				data = {
					'genero' : business.User.devolverGenero(user['gender'], True),
					'restaurante' : anyCosita
				}

				msg['speech'] = Mensaje.pegarTexto(msg, data)

				# Agregar al mensaje otra tarjeta
				messages.append(msg)

			# Registrar el log
			registrarLogAsync(user['user_id'], 'restaurante', 'consultarDomicilio', 'no identifica restaurante')

			# Construye el mensaje y retorna para enviar
			return self.recomendarIndeciso(user, parametros, orden, messages)

		# Consulto si contamos con el restaurante
		restaurantes = RestauranteModel.find_all(slug = {'$regex' : nomRestaurante, '$options' : 'i'})

		if restaurantes.count() > 0:

			# Consulta la jornada, el día y la hora
			jornada, dia, hora = business.Orden().consultarDiaHora()

			# Consulta si el restaurante esta abierto 
			restaurantes = RestauranteModel.find_all(slug = {'$regex' : nomRestaurante, '$options' : 'i'},
				horarios = {
					'$elemMatch' : {
						'dia' : dia,
						'{}.horainicio'.format(jornada) : { '$lte' : hora },
						'{}.horafin'.format(jornada) : { '$gte' : hora }
					}
				}
			)

			# Esta abierto?
			if restaurantes.count() > 0 :
				
				# Mensaje diciendo que si, está abierto y que puede pedir la comida favorita
				msgs = Mensaje.consultarMensaje("consultarDomicilio", "abierto")

				for restaurante in restaurantes :
					# Recorro todos los mensajes
					for msg in msgs :

						data = {
							'genero' : business.User.devolverGenero(user['gender'], True),
							'restaurante' : restaurante['nombre']
						}

						msg['speech'] = Mensaje.pegarTexto(msg, data)

						# Agregar al mensaje otra tarjeta
						messages.append(msg)

					# Registrar el log
					registrarLogAsync(user['user_id'], 'restaurante', 'consultarDomicilio', 'restaurante abierto', nomRestaurante)				

					# Construye el mensaje y retorna para enviar
					return Mensaje.crearMensaje(messages)
			else :
				# Consulto si contamos con el restaurante
				restaurante = RestauranteModel.find(slug = {'$regex' : nomRestaurante, '$options' : 'i'})

				# Esta cerrado
				msgs = Mensaje.consultarMensaje("consultarDomicilio", "cerrado")

				# Recorro todos los mensajes
				for msg in msgs :

					data = {
						'restaurante' : restaurante['nombre']
					}

					msg['speech'] = Mensaje.pegarTexto(msg, data)

					# Agregar al mensaje otra tarjeta
					messages.append(msg)

				# Registrar el log
				registrarLogAsync(user['user_id'], 'restaurante', 'consultarDomicilio', 'restaurante cerrado', nomRestaurante)				

				# Construye el mensaje y retorna para enviar
				return Mensaje.crearMensaje(messages)
		