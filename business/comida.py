#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Imports de python
from flask import request
import datetime
import random
from pathlib import Path
from operator import itemgetter, attrgetter, methodcaller

# Capa de acceso de datos
from models import UserModel
from models import RestauranteModel
from models import OrdenModel

# Capa de negocio
from log import registrarLogAsync
from apiai import Apiai
from business.mensaje import Mensaje
from business.orden import Orden
from business.restaurante import Restaurante
from business.user import User
import business

class Comida(Apiai):

	""" 
	Captura la comida ingresada por el usuario

	Atributos
		user : usuario con quien se esta sosteniendo conversación
		parametros: obtenidos a través de dialogflow

	Retorna
		Mensaje de respuesta 
	"""
	def pedirComidaInicio(self, user, parametros, orden):
		return self.pedirComida(user, parametros, orden)

	""" 
	Captura la comida ingresada por el usuario

	Atributos
		user : usuario con quien se esta sosteniendo conversación
		parametros: obtenidos a través de dialogflow

	Retorna
		Mensaje de respuesta 
	"""
	def administradoresRestaurantes(self, user, parametros, orden):
		print "hola soy un dueño"
		print orden
		compras = OrdenModel.find_all(restaurante= 'hamburguesana', estado = 'FINALIZADO' )
		for compra in compras :
			
			print "compras"
			print compra
		print "|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||"
		senderito = orden['user_id']
		name = orden['first_name']
		estado = orden['estado']
		print "este es el user_id"
		print senderito
		print "este es el nombre"
		print name
		print "este es el estado"
		print estado
		ordenes = OrdenModel.find_all(user_id = { '$elemMatch' : {'user_id' : senderito}})
		estados = OrdenModel.find_all(user_id= user['user_id'], estado = 'FINALIZADO')
		print "estados"
		print estados
		#de esta manera podemos recorrer el cursor o consulta sacando el numero de veces que está
		nroestados = estados.count()
		print "# estados"
		print nroestados
		
		if nroestados > 0:
			print "el contador dice que ya has hecho una compra"
		else:
			print "eres nuevo"


		# de esta manera recorro el cursor o consulta mostrandolos gracias a la variable o que recibe el valor de la consulta
		for o in estados :
			print "nueva consulta"
			print o
			print "||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||"
			if o['estado'].count :
				print "es viejo"




					#formula para buscar nuevos usuarios
					#estados = OrdenModel.find_all(user_id= user['user_id'], estado = 'FINALIZADO')
					#nroestados = estados.count()
					#if nroestados > 0:
					#descuento_1compra = restaurante['descuento_1compra']
					#if restaurante['descuento_1compra'] == 'si'

	def pedirComida(self, user, parametros, orden):
		nuevo = user['es_nuevo']
		print "nuevo"
		print nuevo

		ciudad = user['ciudad']
		
		#Instancio el objeto usuario
		genero = User.devolverGenero(user['gender'], False)

		# Variable para almacenar los mensajes a enviar
		messages = []

		# Variable con el mensaje de respuesta
		respuesta = ''
		# Obtener el parametro de comida
		nomComida = parametros['comidas'].lower()

		print nomComida

		anyComida = parametros['any']

		# Si el parametro viene lo cargo
		nomRestaurante = parametros['nomRestaurante'] if 'nomRestaurante' in parametros else ''

		if nomComida == '':

			if anyComida != '':
				
				# No hay, enviar mensaje de salida y volver a pedir comida
				genero = User.devolverGenero(user['gender'], True)

				# Consultar el mensaje que debo mandar
				msgs = Mensaje.consultarMensaje("pedirComida", "sinComida")

				# Recorro todos los mensajes
				for msg in msgs :
					# Contruyo el array a mandar
					data = { 
						'genero' : genero, 
						'anyComida' : anyComida.encode('utf8')
					}

					msg['speech'] = Mensaje.pegarTexto(msg, data)

					# Agregar al mensaje otra tarjeta
					messages.append(msg)

				# Registrar el log
				registrarLogAsync(user['user_id'], 'comida', 'pedirComida', 'sinComida')

				# Construye el mensaje y retorna para enviar
				return Mensaje.crearMensaje(messages)
				
		# Verifico si la orden ya tiene comida
		if ('restaurante' in orden and orden['restaurante'] != '') or nomRestaurante != '':
			# Si tengo el nombre del restaurante
			if nomRestaurante != '' :
				# Recompongo el nombre del restaurante
				restaurante = RestauranteModel.find(slug = {'$regex' : nomRestaurante, '$options' : 'i'})
				# Asigno el slug
				nomRestaurante = restaurante['slug']

			# Aquí tengo que almacenar el nuevo valor de la comida
			orden['comida'].append(nomComida)
			# Guardo la orden en la base de datos
			OrdenModel.save(orden)
			# Redirecciona al flujo de 
			return Restaurante.seleccionarRestaurante(user, parametros, orden, nomRestaurante) 
		else:
			# Si no tiene comida
			# Agrego la comida a la orden
			orden['comida'].append(nomComida)
			# Guardo la orden en la base de datos
			OrdenModel.save(orden)

			# Si el programa tiene un problema con la ciudad
			ciudad = user['ciudad'] if 'ciudad' in user else 'cartago'

			# Consultar que restaurantes tienen esa comida
			restauranteComida = RestauranteModel.find_all(platos = { '$elemMatch' : {'slug': nomComida}},
				ciudad = ciudad.lower()
				).sort('nombre',1)
			
			# Contar cantidad de restaurante
			nroRestaurante = restauranteComida.count()

			# Si hay restaurante mostrar los restaurantes
			if nroRestaurante >= 1 :

				# Consulta la jornada el día y la hora del sistema
				jornada, dia, hora = Orden.consultarDiaHora()

				# Consulta del restaurante a ver si esta abierto o no
				restaurantes = RestauranteModel.find_all(
					platos = { 
						'$elemMatch' : {
							'slug': nomComida
						}
					},
					horarios = {
						'$elemMatch' : {
							'dia' : dia,
							'{}.horainicio'.format(jornada) : { '$lte' : hora },
							'{}.horafin'.format(jornada) : { '$gte' : hora }
						}
					},
					ciudad = user['ciudad'].lower()
				).sort('nombre',1)

				# Cuantos registros trae la consulta
				restAbierto = restaurantes.count()

				# Si hay restaurantes
				if restAbierto >= 1:

					# Consulto el mensaje de salida
					msgs = Mensaje.consultarMensaje("pedirComida", "claro")

					for msg in msgs :
						# Contruyo el array a mandar
						data = { 
							'genero' : genero, 
							'nomComida' : nomComida
						}

						msg['speech'] = Mensaje.pegarTexto(msg, data)

						# Agregar al mensaje otra tarjeta
						messages.append(msg)

					# Recorre todos los restaurantes
					for restaurante in iter(restaurantes.next, None):

						# Contruye el path del archivo
						validateImage = Path('static/images/' + restaurante['slug'] + '.jpg')
						# Validar si la imagen existe
						imagen = 'images/images/' + restaurante['slug'] + '.jpg' if validateImage.exists() else 'images/images/default.jpg'
						# URL completa de la imagen
						imageURI = request.url_root + imagen

						# Consulto el mensaje de salida
						msgs = Mensaje.consultarMensaje("pedirComida", "restaurantes")

						# Recorre cada mensaje y lo pinta
						for msg in msgs :

							# Contruyo el array a mandar
							data = { 
								'postback' : restaurante['slug'], 
								'text' : '👉 {}'.format(restaurante['nombre'].encode('utf8')),
								'imageUrl' : imageURI,
								'title' : restaurante['nombre'],
								'subtitle' : restaurante['descripcion']
							}

							msg = Mensaje.pegarTextoArray(msg, data)

							# Agregar al mensaje otra tarjeta
							messages.append(msg)

					# Registrar el log
					registrarLogAsync(user['user_id'], 'comida', 'pedirComida', 'mostrar restaurantes')

				else :
					# No hay, enviar mensaje de salida y volver a pedir comida
					genero = User.devolverGenero(user['gender'], True)

					# Consulto el mensaje de salida
					msgs = Mensaje.consultarMensaje("pedirComida", "cerrado")

					# Recorre cada mensaje y lo pinta
					for msg in msgs :
						# Contruyo el array a mandar
						data = { 
							'genero' : genero
						}

						msg['speech'] = Mensaje.pegarTexto(msg, data) 

						# Agregar al mensaje otra tarjeta
						messages.append(msg)

					# Registrar el log
					registrarLogAsync(user['user_id'], 'comida', 'pedirComida', 'restaurantes cerrados')
			else :
				print "ole"
				# Consulta la jornada, el día y la hora
				jornada, dia, hora = business.Orden().consultarDiaHora()

				print user['ciudad']

				# Consulta los restaurantes abiertos 


				restaurantes = RestauranteModel.find_all(horarios = {
					'$elemMatch' : {
						'dia' : dia,
						'{}.horainicio'.format(jornada) : { '$lte' : hora },
						'{}.horafin'.format(jornada) : { '$gte' : hora }
					}
				},
				ciudad = user['ciudad'].lower())

				# Array para guardar las sugerencias
				categorias = []

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
					print "categorias"
					print categorias
				msgs = Mensaje.consultarMensaje("pedirComida", "sinComida")

				# Recorro todos los mensajes
				for msg in msgs :

					if msg['type'] == 0 :
						# Contruyo el array a mandar
						data = { 
							'genero' : User.devolverGenero(user['gender'], True), 
							'anyComida' : nomComida.encode('utf8')
								}
						msg['speech'] = Mensaje.pegarTexto(msg, data)

					if msg['type'] == 2 :
						print "hola"
						msg['replies'] = Mensaje.pegarTextoReply(msg, categorias)

					# Agregar al mensaje otra tarjeta
					messages.append(msg)

				# Registrar el log
				registrarLogAsync(user['user_id'], 'comida', 'pedirComida', 'no hay comida en la ciudad')

				# Construye el mensaje y retorna para enviar
				return Mensaje.crearMensaje(messages)

			# Retorna el mensaje de respuesta
			return Mensaje.crearMensaje(messages)


	""" 
	Guardar el plato en la orden y envia mensaje de si quiere continuar comprando

	Atributos
		user : usuario con quien se esta sosteniendo conversación
		parametros: obtenidos a través de dialogflow

	Retorna
		Mensaje de respuesta 
	"""
	def seleccionarComida(self, user, parametros, orden):
		print "acá se muestra la comida"
		# Obtener el parametro de comida
		nomPlato = parametros['platos']

		# Variable para los platos y tamano
		plato = ''
		tamano = ''
		precio = 0
		nombre =''

		# Validar si viene platos
		if nomPlato == '' :
				# Variable para almacenar los mensajes a enviar
				messages = []

				# Consultar el mensaje que debo mandar
				msgs = Mensaje.consultarMensaje("seleccionarComida", "error")

				# Recorro todos los mensajes
				for msg in msgs :
					# Contruyo el array a mandar
					data = { 
						'genero' : User.devolverGenero(user['gender'], False)
					}

					msg['speech'] = Mensaje.pegarTexto(msg, data)

					# Agregar al mensaje otra tarjeta
					messages.append(msg)

				# Registrar el log
				registrarLogAsync(user['user_id'], 'comida', 'seleccionarComida', 'no entiende comida', '')

				# Construye el mensaje y retorna para enviar
				return Mensaje.crearMensaje(messages)
		else :
			
			# Consultar el plato
			restaurantes = RestauranteModel.find_all(platos = { '$elemMatch' : {'codigo': nomPlato}}).limit(6);

			# Recorre todos los restaurantes
			for restaurante in iter(restaurantes.next, None):
				# Busca el plato
				plato = [platos for platos in restaurante['platos'] if platos['codigo'] == nomPlato]

			# Encuentra los tamaños de los platos
			for p in plato :
				tamano = p.get('tamanos')
				precio = p.get('precio')
				nombre = p.get('comida')

			if tamano is not None :
				# Si el plato tiene tamaños
				if len(tamano) > 0 :
					# Redireccionar al mensaje de seleccionar tamaño, nuevo intent
					return self.mostrarTamanos(user, parametros, orden)

			# La estructura del plato a guardar
			return self.mostrarCantidadPlatos(user, orden)


	""" 
	Construye el mensaje de los tamaños de las comidas

	Atributos
		user : usuario con quien se esta sosteniendo conversación
		parametros: obtenidos a través de dialogflow
		orden: la orden de compra que tiene el cliente

	Retorna
		Mensaje de respuesta 
	"""
	def mostrarTamanos(self, user, parametros, orden):
		# No hay, enviar mensaje de salida y volver a pedir comida
		genero = User.devolverGenero(user['gender'], True)

		# Asignar valor de acuerdo a si existe o no en los parametros
		nomPlato = parametros['platos'] if 'platos' in parametros else ''

		promocion = ''
		if 'promociones' in parametros :
			if parametros['promociones'] != '' :
				promocion = parametros['promociones']

		print nomPlato
		print promocion

		# Variable para almacenar los mensajes a enviar
		messages = []

		# Consulto el mensaje de salida
		msgs = Mensaje.consultarMensaje("seleccionarTamano", "mensaje")

		# Recorro todos los mensajes
		for msg in msgs :
			# Contruyo el array a mandar
			data = { 
				'genero' : genero, 
				
			}

			msg['speech'] = Mensaje.pegarTexto(msg, data)

			# Agregar al mensaje otra tarjeta
			messages.append(msg)

		# Busco el plato en los restaurantes
		restaurantes = RestauranteModel.find_all(platos = { '$elemMatch' : {'codigo': nomPlato}}) if nomPlato != '' else RestauranteModel.find_all(platos = { '$elemMatch' : {'promocion': promocion}})

		# Recorre todos los restaurantes
		for restaurante in iter(restaurantes.next, None):
			# Asigna los platos
			for platos in restaurante['platos'] :
				# Pregunta si tengo plato para consultar
				if nomPlato != '' :
					# Pregunto si el plato existe
					if platos['codigo'] == nomPlato :
						# Asignar los tamaños
						tamanos = platos['tamanos']
				else :
					if 'promocion' in platos :
						# Pregunto si el plato existe
						if platos['promocion'] == promocion :
							# Asignar los tamaños
							tamanos = platos['tamanos']

		# Ordenar de mayor precio a menor precio el producto
		tamanos.sort(key=itemgetter('precio'), reverse=True)

		# Recorro los tamaños
		for tamano in tamanos :

			# Consulto el mensaje de salida
			msgs = Mensaje.consultarMensaje("seleccionarTamano", "mostrarTamano")

			# Recorre cada mensaje y lo pinta
			for msg in msgs :

				# Contruye el path del archivo
				validateImage = Path('static/images/' + tamano['codigo'] + '.jpg')
				# Validar si la imagen existe
				imagen = 'images/images/' + tamano['codigo'] + '.jpg' if validateImage.exists() else 'images/images/default.jpg'
				# URL completa de la imagen
				imageURI = request.url_root + imagen

				print imageURI
				#formula para buscar nuevos usuarios
				estados = OrdenModel.find_all(user_id= user['user_id'], estado = 'FINALIZADO')
				nroestados = estados.count()
				if nroestados < 1:
					# descuento_1compra = restaurante['descuento_1compra']
					# if restaurante['descuento_1compra'] == 'si':
					# 	print "si tiene descuento"
					# 	# Contruyo el array a mandar
					# 	data = { 
					# 		'postback' : tamano['codigo'], 
					# 		'text' : "Por solo ${:,.0f}".format(tamano['precio'] - (tamano['precio'] * 10/100)),
					# 		'imageUrl' : imageURI,
					# 		'title' : tamano['nombre'],
					# 		'subtitle' : tamano['descripcion']
					# 	}
					# else:
						# Contruyo el array a mandar
					data = { 
						'postback' : tamano['codigo'], 
						'text' : "Por solo ${:,.0f}".format(tamano['precio']),
						'imageUrl' : imageURI,
						'title' : tamano['nombre'],
						'subtitle' : tamano['descripcion']
					}
				else:
					# Contruyo el array a mandar
						data = { 
							'postback' : tamano['codigo'], 
							'text' : "Por solo ${:,.0f}".format(tamano['precio']),
							'imageUrl' : imageURI,
							'title' : tamano['nombre'],
							'subtitle' : tamano['descripcion']
						}

				msg = Mensaje.pegarTextoArray(msg, data)

				# Agregar al mensaje otra tarjeta
				messages.append(msg)

		# Registrar el log
		registrarLogAsync(user['user_id'], 'comida', 'mostrarTamanos', 'muestra tamaños', orden['restaurante'])

		# Retorna el mensaje de respuesta
		return Mensaje.crearMensaje(messages) 

	""" 
	Toma el tamaño seleccionado por el usuario

	Atributos
		user : usuario con quien se esta sosteniendo conversación
		parametros: obtenidos a través de dialogflow
		orden: la orden de compra que tiene el cliente

	Retorna
		Mensaje de respuesta 
	"""
	def seleccionarTamano(self, user, parametros, orden):
		# Toma el tamaño de dialogflow
		nomTamano = parametros['tamanos']

		# Muestra el siguiente mensaje
		return self.mostrarCantidadPlatos(user, orden)


	""" 
	Muestra las cantidades que puede pedir de la comida

	Atributos
		orden: información de la orden

	Retorna
		El genero de la persona
	"""	
	def mostrarCantidadPlatos(self, user, orden):
		# Genero
		genero = User.devolverGenero(user['gender'], True)

		# Variable de mensajes
		messages = []

		# Consulto el mensaje de salida
		msgs = Mensaje.consultarMensaje("mostrarCantidadPlatos")

		# Recorre cada mensaje y lo pinta
		for msg in msgs :

			# Contruyo el array a mandar
			data = { 
				'genero' : genero
			}

			msg['title'] = Mensaje.pegarTexto(msg, data, 'title')

			# Agregar al mensaje otra tarjeta
			messages.append(msg)

		# Registrar el log
		registrarLogAsync(user['user_id'], 'comida', 'mostrarCantidadPlatos', 'muestra cantidad a consumir', orden['restaurante'])			

		# Retorna el mensaje de respuesta
		return Mensaje.crearMensaje(messages)

	""" 
	Muestra las cantidades que puede pedir de la comida

	Atributos
		user: información del usuario
		parametros: de dialogflow
		orden: información de la orden

	Retorna
		Mensaje
	"""	
	def cantidadPlatos(self, user, parametros, orden):
		# Obtiene los parametros de dialogflow
		cantidad = parametros['number']
		nomTamano = parametros['tamanos']

		# Asignar valor de acuerdo a si existe o no en los parametros
		nomPlato = parametros['platos'] if parametros['platos'] != '' else ''
		promocion = parametros['promociones'] if parametros['promociones'] != '' else ''

		print nomPlato
		print promocion

		# Consulta el restaurante
		restaurantes = RestauranteModel.find_all(slug = orden['restaurante']);

		for restaurante in iter(restaurantes.next, None):
			# Busca el plato
			#tamano = [tamanos for tamanos in restaurante['platos']['tamanos'] if tamanos['codigo'] == nomTamano]
			for platos in restaurante['platos'] :
				#formula para buscar nuevos usuarios
				estados = OrdenModel.find_all(user_id= user['user_id'], estado = 'FINALIZADO')
				nroestados = estados.count()
				if nroestados < 1:
					# descuento_1compra = restaurante['descuento_1compra']
					# if restaurante['descuento_1compra'] == 'si':
					# 	#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
					# 	# Consulto el mensaje de salida
					# 	genero = User.devolverGenero(user['gender'], True)
					# 	msgs = Mensaje.consultarMensaje("cantidadPlatos", "descuento")

					# 	# Recorre cada mensaje y lo pinta
					# 	for msg in msgs :

					# 		# Contruyo el array a mandar
					# 		data = { 'genero' : genero }

					# 		msg['speech'] = Mensaje.pegarTexto(msg, data)

					# 		# Agregar al mensaje otra tarjeta
					# 		messages.append(msg)

					# 	# Registrar el log
					# 	registrarLogAsync(user['user_id'], 'comida', 'cantidadPlatos', 'descuento')			

					# 	# Retorna el mensaje de respuesta
					# 	return Mensaje.crearMensaje(messages)
					# 	print "si tiene descuento"
					# 	# Preguntar si tamano existe
					# 	if 'tamanos' in platos :
					# 		# Busca todos los platos que tienen tamaño
					# 		for i in range(len(platos['tamanos'])):
					# 			# Busca el tamaño que coincide con la decision del usuario
					# 			if platos['tamanos'][i]['codigo'] == nomTamano :
					# 				# Construyo el array para agregar a la orden
					# 				data = {
					# 					'codigo' : nomTamano,
					# 					'nombre' : platos['tamanos'][i]['nombre'],
					# 					'precio' : platos['tamanos'][i]['precio'] - (platos['tamanos'][i]['precio'] * 10/100),
					# 					'cantidad' : cantidad
					# 				}

					# 				# Registrar el log
					# 				registrarLogAsync(user['user_id'], 'comida', 'cantidadPlatos', 'guarda plato en la orden', orden['restaurante'])			

					# 				# Agrega el plato 
					# 				orden['plato'].append(data)
					# 				# Guardo la orden en la base de datos
					# 				OrdenModel.save(orden)
					# 	else:

					# 		if 'promocion' in platos :
					# 			if platos['promocion'] == promocion :
					# 				data = {
					# 					'codigo' : platos['codigo'],
					# 					'nombre' : platos['comida'],
					# 					'precio' : platos['precio'] - (platos['precio'] * 10/100),
					# 					'cantidad' : cantidad
					# 				}

					# 				# Registrar el log
					# 				registrarLogAsync(user['user_id'], 'comida', 'cantidadPlatos', 'guarda plato en la orden', orden['restaurante'])			

					# 				# Agrega el plato 
					# 				orden['plato'].append(data)
					# 				# Guardo la orden en la base de datos
					# 				OrdenModel.save(orden)


					# 		if (platos['codigo'] == nomPlato) :
					# 			# Construyo el array para guardar en la orden
					# 			data = {
					# 				'codigo' : platos['codigo'],
					# 				'nombre' : platos['comida'],
					# 				'precio' : platos['precio'] - (platos['precio'] * 10/100),
					# 				'cantidad' : cantidad
					# 			}

					# 			# Registrar el log
					# 			registrarLogAsync(user['user_id'], 'comida', 'cantidadPlatos', 'guarda plato en la orden', orden['restaurante'])			

					# 			# Agrega el plato 
					# 			orden['plato'].append(data)
					# 			# Guardo la orden en la base de datos
					
					# 			OrdenModel.save(orden)
					# else:
						# Preguntar si tamano existe
						if 'tamanos' in platos :
							# Busca todos los platos que tienen tamaño
							for i in range(len(platos['tamanos'])):
								# Busca el tamaño que coincide con la decision del usuario
								if platos['tamanos'][i]['codigo'] == nomTamano :
									# Construyo el array para agregar a la orden
									data = {
										'codigo' : nomTamano,
										'nombre' : platos['tamanos'][i]['nombre'],
										'precio' : platos['tamanos'][i]['precio'],
										'cantidad' : cantidad
									}

									# Registrar el log
									registrarLogAsync(user['user_id'], 'comida', 'cantidadPlatos', 'guarda plato en la orden', orden['restaurante'])			

									# Agrega el plato 
									orden['plato'].append(data)
									# Guardo la orden en la base de datos
									OrdenModel.save(orden)
						else:

							if 'promocion' in platos :
								if platos['promocion'] == promocion :
									data = {
										'codigo' : platos['codigo'],
										'nombre' : platos['comida'],
										'precio' : platos['precio'],
										'cantidad' : cantidad
									}

									# Registrar el log
									registrarLogAsync(user['user_id'], 'comida', 'cantidadPlatos', 'guarda plato en la orden', orden['restaurante'])			

									# Agrega el plato 
									orden['plato'].append(data)
									# Guardo la orden en la base de datos
									OrdenModel.save(orden)


							if (platos['codigo'] == nomPlato) :
								# Construyo el array para guardar en la orden
								data = {
									'codigo' : platos['codigo'],
									'nombre' : platos['comida'],
									'precio' : platos['precio'],
									'cantidad' : cantidad
								}

								# Registrar el log
								registrarLogAsync(user['user_id'], 'comida', 'cantidadPlatos', 'guarda plato en la orden', orden['restaurante'])			

								# Agrega el plato 
								orden['plato'].append(data)
								# Guardo la orden en la base de datos
								OrdenModel.save(orden)


				else:
					# Preguntar si tamano existe
						if 'tamanos' in platos :
							# Busca todos los platos que tienen tamaño
							for i in range(len(platos['tamanos'])):
								# Busca el tamaño que coincide con la decision del usuario
								if platos['tamanos'][i]['codigo'] == nomTamano :
									# Construyo el array para agregar a la orden
									data = {
										'codigo' : nomTamano,
										'nombre' : platos['tamanos'][i]['nombre'],
										'precio' : platos['tamanos'][i]['precio'],
										'cantidad' : cantidad
									}

									# Registrar el log
									registrarLogAsync(user['user_id'], 'comida', 'cantidadPlatos', 'guarda plato en la orden', orden['restaurante'])			

									# Agrega el plato 
									orden['plato'].append(data)
									# Guardo la orden en la base de datos
									OrdenModel.save(orden)
						else:

							if 'promocion' in platos :
								if platos['promocion'] == promocion :
									data = {
										'codigo' : platos['codigo'],
										'nombre' : platos['comida'],
										'precio' : platos['precio'],
										'cantidad' : cantidad
									}

									# Registrar el log
									registrarLogAsync(user['user_id'], 'comida', 'cantidadPlatos', 'guarda plato en la orden', orden['restaurante'])			

									# Agrega el plato 
									orden['plato'].append(data)
									# Guardo la orden en la base de datos
									OrdenModel.save(orden)


							if (platos['codigo'] == nomPlato) :
								# Construyo el array para guardar en la orden
								data = {
									'codigo' : platos['codigo'],
									'nombre' : platos['comida'],
									'precio' : platos['precio'],
									'cantidad' : cantidad
								}

								# Registrar el log
								registrarLogAsync(user['user_id'], 'comida', 'cantidadPlatos', 'guarda plato en la orden', orden['restaurante'])			

								# Agrega el plato 
								orden['plato'].append(data)
								# Guardo la orden en la base de datos
								OrdenModel.save(orden)

		
		return self.noSeleccionarComida(user, parametros, orden)

	""" 
	Muestra mensaje de selección si quiere o no aprobar el pedido

	Atributos
		user : usuario con quien se esta sosteniendo conversación
		parametros: obtenidos a través de dialogflow
		orden: la orden de compra que tiene el cliente

	Retorna
		Mensaje de respuesta 
	"""
	def mostrarAgregarComida(self, user, orden):
		genero = User.devolverGenero(user['gender'], True)

		# Variable para almacenar los mensajes a enviar
		messages = []

		# Consulto el mensaje de salida
		msgs = Mensaje.consultarMensaje("mostrarAgregarComida")

		# Recorre cada mensaje y lo pinta
		for msg in msgs :

			# Contruyo el array a mandar
			data = { 'genero' : genero }

			msg['title'] = Mensaje.pegarTexto(msg, data, 'title')

			# Agregar al mensaje otra tarjeta
			messages.append(msg)

		# Registrar el log
		registrarLogAsync(user['user_id'], 'comida', 'mostrarAgregarComida', 'mostrar si quiere agregar mas comida', orden['restaurante'])			

		# Retorna el mensaje de respuesta
		return Mensaje.crearMensaje(messages)

	""" 
	Muestra el mensaje de selección si quiere seguir pidiendo comida

	Atributos
		user : usuario con quien se esta sosteniendo conversación
		parametros: obtenidos a través de dialogflow
		orden: la orden de compra que tiene el cliente

	Retorna
		Mensaje de respuesta 
	"""
	def siSeleccionarComida(self, user, parametros, orden):

		restaurante = Restaurante()

		# Llamar el metodo encargado de recomendar indeciso
		return restaurante.recomendarIndeciso(user, parametros, orden)


		# # Variable para almacenar los mensajes a enviar
		# messages = [] 

		# restaurante = RestauranteModel.find(slug = orden['restaurante'], ciudad = user['ciudad'].lower())

		# # Consulto el mensaje de salida
		# msgs = Mensaje.consultarMensaje("siSeleccionarComida")

		# # Recorre cada mensaje y lo pinta
		# for msg in msgs :

		# 	# Contruyo el array a mandar
		# 	data = { 'restaurante' : restaurante['nombre'] }

		# 	msg['speech'] = Mensaje.pegarTexto(msg, data)

		# 	# Agregar al mensaje otra tarjeta
		# 	messages.append(msg)

		# # Registrar el log
		# registrarLogAsync(user['user_id'], 'comida', 'siSeleccionarComida', 'otra comida para agregar al pedido', orden['restaurante'])			

		# # Retorna el mensaje de respuesta
		# return Mensaje.crearMensaje(messages)
		

	""" 
	Metodo encargado de generar la respuesta para dialogflow

	Atributos
		respuesta: Mensaje configurado para enviar

	Retorna
		Mensaje de respuesta formateado para enviar
	"""
	def noSeleccionarComida(self, user, parametros, orden):
		genero = User.devolverGenero(user['gender'], True)

		# Variable para almacenar los mensajes
		messages = []

		# Si no tiene plato
		if orden['plato'] == [] and orden['almuerzo'] == [] :

			# Consulto el mensaje de salida
			msgs = Mensaje.consultarMensaje("noSeleccionarComida", "error")

			# Recorre cada mensaje y lo pinta
			for msg in msgs :

				# Contruyo el array a mandar
				data = { 'genero' : genero }

				msg['speech'] = Mensaje.pegarTexto(msg, data)

				# Agregar al mensaje otra tarjeta
				messages.append(msg)

			# Registrar el log
			registrarLogAsync(user['user_id'], 'comida', 'noSeleccionarComida', 'sin comida en el pedido')			

			# Retorna el mensaje de respuesta
			return Mensaje.crearMensaje(messages)

		# Consulto el mensaje de salida
		msgs = Mensaje.consultarMensaje("noSeleccionarComida", "domicilio")
		# Consulto el restaurante
		restaurante = RestauranteModel.find(slug = orden['restaurante'])
		print "valor minimo"
		minimo = restaurante['minimo']
		print minimo
		# Recorre cada mensaje y lo pinta
		for msg in msgs :

			# Mensaje del valor del comicilio
			msg['speech'] = restaurante['mensajedomicilio']

			# Contruyo el array a mandar
			data = { 
				'genero' : genero,
				'restaurante' : restaurante['nombre']
			}

			msg['speech'] = Mensaje.pegarTexto(msg, data)

			# Agregar al mensaje otra tarjeta
			messages.append(msg)
		total, subFactura = Orden.mostrarSubfactura(orden)
		print "este es el total"
		print total
		if total < minimo:
			# Consulto el mensaje de salida
			msgs = Mensaje.consultarMensaje("noSeleccionarComida", "minimo")		

			# Recorre cada mensaje y lo pinta
			for msg in msgs :

				total, subFactura = Orden.mostrarSubfactura(orden)

				# Contruyo el array a mandar
				data = { 
					'msg' : subFactura,
					'total' : "{:,.0f}".format(total)
				}

				msg['title'] = Mensaje.pegarTexto(msg, data, 'title')

				# Agregar al mensaje otra tarjeta
				messages.append(msg)
		else:
			# Consulto el mensaje de salida
			msgs = Mensaje.consultarMensaje("noSeleccionarComida", "factura")		

			# Recorre cada mensaje y lo pinta
			for msg in msgs :

				total, subFactura = Orden.mostrarSubfactura(orden)

				# Contruyo el array a mandar
				data = { 
					'msg' : subFactura,
					'total' : "{:,.0f}".format(total)
				}

				msg['title'] = Mensaje.pegarTexto(msg, data, 'title')

				# Agregar al mensaje otra tarjeta
				messages.append(msg)	

		# Registrar el log
		registrarLogAsync(user['user_id'], 'comida', 'noSeleccionarComida', 'mostrar factura venta', orden['restaurante'])

		# Retorna el mensaje de respuesta
		return Mensaje.crearMensaje(messages)


	""" 
	Metodo encargado de generar la respuesta para dialogflow

	Atributos
		respuesta: Mensaje configurado para enviar

	Retorna
		Mensaje de respuesta formateado para enviar
	"""
	def mostrarPedido(self, user, parametros, orden):
		return self.noSeleccionarComida(user, parametros, orden)

	""" 
	Cancela el pedido 

	Atributos
		user: Datos del usuario
		parametros: parametros de dialogflow
		orden: datos de la orden

	Retorna
		Mensaje de respuesta formateado para enviar
	"""
	def cancelarPedidoYa(self, user, parametros, orden):
		return self.cancelarPedido(user, parametros, orden)

	""" 
	Cancela el pedido 

	Atributos
		user: Datos del usuario
		parametros: parametros de dialogflow
		orden: datos de la orden

	Retorna
		Mensaje de respuesta formateado para enviar
	"""
	def cancelarPedido(self, user, parametros, orden):
		# Cambio el estado de la orden
		orden['estado'] = 'CANCELADO'
		# Guardo la orden en la base de datos
		OrdenModel.save(orden)

		# Variable para pintar el mensaje
		messages = []

		# Consulto el mensaje de salida
		msgs = Mensaje.consultarMensaje("cancelarPedido")

		# Recorre cada mensaje y lo pinta
		for msg in msgs :

			# Contruyo el array a mandar
			data = { 'genero' : User.devolverGenero(user['gender'], True) }

			msg['speech'] = Mensaje.pegarTexto(msg, data)

			# Agregar al mensaje otra tarjeta
			messages.append(msg)

		# Registrar el log
		registrarLogAsync(user['user_id'], 'comida', 'cancelarPedido', 'cancela el pedido en curso', '')

		# Retorna el mensaje de respuesta
		return Mensaje.crearMensaje(messages)

	""" 
	Muestra los productos pedidos

	Atributos
		user: Datos del usuario
		parametros: parametros de dialogflow
		orden: datos de la orden

	Retorna
		Mensaje de respuesta formateado para enviar
	"""	
	def cambiarRestaurante(self,user, parametros, orden):

		print "parametros cambiarRestaurante"
		print parametros
		orden['restaurante'] = ""
		orden['plato'] = []
		parametros['restaurantes'] = ""
		print "esta es la segunda impresión"
		print parametros
		print "esta es la impresión orden"
		print orden
		return self.pedirComida(user, parametros, orden)
	
	def consultarPedido(self, user, parametros, orden):
		# Variable para almacenar los mensajes 
		messages = []

		# Consultaar la fecha del sistema
		now = datetime.datetime.now()

		# Consultar la ultima orden que este en estado FINALIZADO
		ordenTemp = OrdenModel.find_all(user_id= user['user_id'], estado = 'FINALIZADO').sort('fecha_pedido',-1).limit(1)

		# Obtengo la primera orden
		for o in ordenTemp :

			# Si no ha pasado 30 minutos
			if  (now - o['fecha_pedido']).seconds <= 1800:

				# Consulto el mensaje de salida
				msgs = Mensaje.consultarMensaje("consultarPedido", "finalizado")	

				# Recorre cada mensaje y lo pinta
				for msg in msgs :

					total, subFactura = Orden.mostrarSubfactura(o)

					# Contruyo el array a mandar
					data = { 
						'restaurante' : Restaurante.consultarNombre(o['restaurante']),
						'msg' : subFactura, 
						'total' : "{:,.0f}".format(total)
					}

					msg['speech'] = Mensaje.pegarTexto(msg, data)

					# Agregar al mensaje otra tarjeta
					messages.append(msg)		

		if len(orden['plato']) > 0 or len(orden['almuerzo']) > 0 : 

			# Consulto el mensaje de salida
			msgs = Mensaje.consultarMensaje("consultarPedido", "en_proceso")		

			# Recorre cada mensaje y lo pinta
			for msg in msgs :

				total, subFactura = Orden.mostrarSubfactura(orden)

				# Contruyo el array a mandar
				data = { 
					'restaurante' : Restaurante.consultarNombre(orden['restaurante']),
					'genero' : User.devolverGenero(user['gender'], True),
					'msg' : subFactura, 
					'total' : "{:,.0f}".format(total)
				}

				msg['speech'] = Mensaje.pegarTexto(msg, data)

				# Agregar al mensaje otra tarjeta
				messages.append(msg)	

			# Registrar el log
			registrarLogAsync(user['user_id'], 'comida', 'consultarPedido', 'muestra los pedidos en curso', orden['restaurante'])

			# Retorna el mensaje de respuesta
			return Mensaje.crearMensaje(messages)
		else :
			# No hay pedidos
			msgs = Mensaje.consultarMensaje("consultarPedido", "sinDatos")		

			# Recorre cada mensaje y lo pinta
			for msg in msgs :
				# Contruyo el array a mandar
				data = { 
					'genero' : User.devolverGenero(user['gender'], True)
				}

				msg['speech'] = Mensaje.pegarTexto(msg, data)

				# Agregar al mensaje otra tarjeta
				messages.append(msg)	

			# Registrar el log
			registrarLogAsync(user['user_id'], 'comida', 'consultarPedido', 'no hay pedidos')

			# Retorna el mensaje de respuesta
			return Mensaje.crearMensaje(messages)

	""" 
	Consulta la promo

	Atributos
		user: Datos del usuario
		parametros: parametros de dialogflow
		orden: datos de la orden

	Retorna
		Mensaje de respuesta formateado para enviar
	"""	
	def promo(self,user,parametros,orden):

		# Obtener el codigo de la promocion
		promocion = parametros['promociones']

		print promocion

		# Consulta la promocion
		restaurantes = RestauranteModel.find_all(platos = { '$elemMatch' : {'promocion': promocion}})

		# Contar cantidad de restaurante
		nroRestaurante = restaurantes.count()

		# Si hay restaurante mostrar los restaurantes
		if nroRestaurante >= 1 :

			print nroRestaurante

			# Recorre todos los restaurantes
			for restaurante in iter(restaurantes.next, None):

				# Asignar el plato y recorre los platos
				for platos in restaurante['platos'] :

					# Preguntar si existe la proomocion
					if 'promocion' in platos and platos['promocion'] == promocion :

						print restaurante['slug']	

						# Registrar el log
						registrarLogAsync(user['user_id'], 'comida', 'promo', 'capturar promocion', restaurante['slug'])					

						# Obtiene el slug del restaurante
						orden['restaurante'] = restaurante['slug']
					 	# Guardar el nombre del restaurante
						OrdenModel.save(orden)

						# Asigno ciudad a la persona
						user['ciudad'] = 'cartago'
						# Cambio el estado del usuario
						user['es_nuevo'] = False
						# Guardo al usuario
						UserModel.save(user)

						if 'tamanos' in platos :
							tamano = platos['tamanos']
							# Redireccionar al mensaje de seleccionar tamaño, nuevo intent
							return self.mostrarTamanos(user, parametros, orden)

		return self.mostrarCantidadPlatos(user, orden)


