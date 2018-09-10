#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Imports de python
import sys
from flask import request
import threading
import datetime
import smtplib
from api import call_ifttt

# Capa de acceso de datos
from models import OrdenModel
from models import RestauranteModel
from models import UserModel

# Capa de negocio
from log import registrarLogAsync
from business.apiai import Apiai
from business.mensaje import Mensaje
from business.user import User
import business

class Orden(Apiai):

	""" 
	Consulta el dia, hora y jornada del restaurante

	Atributos

	Retorna
		La jornada, el día y la hora
	"""
	@staticmethod
	def consultarDiaHora():
		# Cual día de la semana es
		dia =  int(datetime.datetime.now().strftime("%w"))
		# Hora exacta del sistema
		hora = datetime.datetime.now().strftime("%H:%M") 
		# Cual es la jornada que se va a consultar
		jornada = 'manana' if datetime.datetime.now().hour >= 0 and datetime.datetime.now().hour < 14 else 'tarde'

		return jornada, dia, hora

	""" 
	Crea una orden

	Atributos
		sender_id : Id del usuario en facebook

	Retorna
		El usuario creado
	"""
	def crearOrden(self, user) :
		# Crea la orden
		orden = OrdenModel.new(first_name= user['first_name'], 
			last_name = user['last_name'], 
			gender = user['gender'], 
			user_id = user['user_id'], 
			fecha_pedido = datetime.datetime.now(), 
			comida = [],
			plato = [], 
			almuerzo = [], 
			estado = "EN_PROCESO"
		)
		#Retorna la orden
		return orden

	""" 
	Verificar si ha pasado 30 minutos para cancelar la orden

	Atributos
		user: Datos del usuario
		parametros: parametros de dialogflow
		orden: datos de la orden

	Retorna
		Mensaje de respuesta formateado para enviar
	"""	
	def confirmarOrden(self, orden, user):
		# Obtiene la fecha del pedido
		last_time = orden.get('fecha_pedido')
		# Consultaar la fecha del sistema
		now = datetime.datetime.now()
		# Si diferencia entre las fechas es de 30 minutos
		if (now - last_time).seconds >= 1800:
				# Cancela el pedido
				orden['estado'] = 'CANCELADO'
				# Guarda la orden
				OrdenModel.save(orden)
				# Retorna una nueva orden
				return self.crearOrden(user)
		
		# Sino, retorna la orden actual
		return orden

	""" 
	Consulta la orden del usuario y el estado

	Atributos
		sender_id: ID del usuario que tiene la orden
		estado: Estado de la orden

	Retorna
		Orden
	"""	
	def consultarOrden(self, sender_id, estado):
		return OrdenModel.find(user_id = sender_id, estado = estado)


	""" 
	Consulta la orden del usuario y el estado

	Atributos
		sender_id: ID del usuario que tiene la orden
		estado: Estado de la orden

	Retorna
		Orden
	"""	
	@staticmethod
	def mostrarSubfactura(orden):

		# sys.setdefaultencoding() does not exist, here!
		reload(sys)  # Reload does the trick!
		sys.setdefaultencoding('UTF8')

		# Variables necesarias para el proceso
		msg = ''
		total = 0

		# Ciclo para construir la factura
		for plato in orden['plato'] : 
			# Mensaje a mostrar

			print plato['precio']

			print plato['cantidad']

			msg += '* {} de ${:,.0f}, {} unidades por ${:,.0f} \n'.format(
				plato['nombre'].capitalize(),
				plato['precio'], 
				plato['cantidad'], 
				int(plato['precio']) * int(plato['cantidad'])
			)
			# Total de la factura
			total += int(plato['precio']) * int(plato['cantidad'])

		# Pinta el almuerzo
		for almuerzo in orden['almuerzo'] :
			subtotal = int(almuerzo['precio']) * int(almuerzo['cantidad'])
			subtotal = str(subtotal)

			msg += '*{} almuerzo con {}, {}, {} por ${:,.0f}\n'.format(
				almuerzo['cantidad'], 
				almuerzo['principio'],
				almuerzo['carne'],
				almuerzo['jugo'],
				almuerzo['precio']
			)
			total += int(almuerzo['precio']) * int(almuerzo['cantidad'])

		comision = (total * 5)/100
		orden['comision_5'] = comision

		# Si la comisión es menor a $1000 asigno ese valor, sino el 5%
		orden['comision'] = 1000 if comision < 1000 else comision

		# Guardar el total de la factura
		orden['total'] = total

		# Guardo la orden en la base de datos
		OrdenModel.save(orden)

		return total, msg

	""" 
	Confirma el pedido hecho por el cliente

	Atributos
		user: Datos del usuario
		parametros: parametros de dialogflow
		orden: datos de la orden

	Retorna
		Mensaje de respuesta formateado para enviar
	"""
	def confirmarPedido(self, user, parametros, orden):
		restaurante = RestauranteModel.find(slug = orden['restaurante'])
		print "valor minimo"
		minimo = restaurante['minimo']
		print minimo
		total, subFactura = Orden.mostrarSubfactura(orden)
		print "este es el total"
		print total
		messages = []
		if total < minimo:
			
		

			return business.Comida().noSeleccionarComida(user, parametros, orden)
		else:

			

			# Consulto el mensaje de salida
			msgs = Mensaje.consultarMensaje("confirmarPedido")		

			# Recorre cada mensaje y lo pinta
			for msg in msgs :

				# Contruyo el array a mandar
				data = { 
					'genero' : User.devolverGenero(user['gender'], True)
				}

				msg['speech'] = Mensaje.pegarTexto(msg, data, 'speech')

				# Agregar al mensaje otra tarjeta
				messages.append(msg)	

			# Registrar el log
			registrarLogAsync(user['user_id'], 'orden', 'confirmarPedido', 'mensaje confirmacion', orden['restaurante'])

		# Retorna el mensaje de respuesta
		return Mensaje.crearMensaje(messages) 

	""" 
	Agrega la observación al pedido

	Atributos
		user: Datos del usuario
		parametros: parametros de dialogflow
		orden: datos de la orden

	Retorna
		Mensaje de respuesta formateado para enviar
	"""
	def agregarObservacion(self, user, parametros, orden):

		# toma la observación de dialogflow
		observacion = parametros['any']
		# Asgina la observación a la orden
		orden['observaciones'] = observacion
		# Guardo la orden en la base de datos
		OrdenModel.save(orden)

		# Variable para mostrar el mensaje
		messages = []

		# Consulto el mensaje de salida
		msgs = Mensaje.consultarMensaje("agregarObservacion")		

		# Recorre cada mensaje y lo pinta
		for msg in msgs :

			msg['speech'] = Mensaje.pegarTexto(msg)

			# Agregar al mensaje otra tarjeta
			messages.append(msg)	

		# Registrar el log
		registrarLogAsync(user['user_id'], 'orden', 'agregarObservacion', 'mensaje observacion', orden['restaurante'])

		# Retorna el mensaje de respuesta
		return Mensaje.crearMensaje(messages)		

	""" 
	Agrega la direccion al pedido

	Atributos
		user: Datos del usuario
		parametros: parametros de dialogflow
		orden: datos de la orden

	Retorna
		Mensaje de respuesta formateado para enviar
	"""
	def ingresarDireccion(self, user, parametros, orden):
		# Toma la dirección de dialogflow
		direccion = parametros['any']	
		# Agrega la dirección a la orden
		orden['direccion'] = direccion
		# Guardo la orden en la base de datos
		OrdenModel.save(orden)
			
		# Variable para mostrar el mensaje
		messages = []

		# Consulto el mensaje de salida
		msgs = Mensaje.consultarMensaje("ingresarDireccion")		

		# Recorre cada mensaje y lo pinta
		for msg in msgs :

			msg['speech'] = Mensaje.pegarTexto(msg)

			# Agregar al mensaje otra tarjeta
			messages.append(msg)	

		# Registrar el log
		registrarLogAsync(user['user_id'], 'orden', 'ingresarDireccion', 'mensaje direccion', orden['restaurante'])

		# Retorna el mensaje de respuesta
		return Mensaje.crearMensaje(messages)

	""" 
	Agrega el telefono al pedido y los datos al usuario

	Atributos
		user: Datos del usuario
		parametros: parametros de dialogflow
		orden: datos de la orden

	Retorna
		Mensaje de respuesta formateado para enviar
	"""
	def ingresarTelefono(self, user, parametros, orden):
		# Toma el telefono de dialogflow
		telefono = parametros['phone-number']
		# Asigna el telefono a la orden
		orden['telefono'] = telefono
		# Cambia el estado de la orden
		orden['estado'] = 'FINALIZADO'
		# Guardo la orden en la base de datos
		OrdenModel.save(orden)

		
		# Agregar dirección al usuario
		user['telefono'] = telefono
		# Agregar el teléfono al usuario
		user['direccion'] = orden['direccion']
		# Guardo la orden en la base de datos
		UserModel.save(user)

		# Metodo encargado de enviar el correo electronico
		self.enviarEmailAsync(orden)

		# Variable para pintar los ultimos mensajes
		messages = []

		# Consulto el mensaje de salida
		msgs = Mensaje.consultarMensaje("ingresarTelefono", "imagen")		

		# Recorre cada mensaje y lo pinta
		for msg in msgs :

			data = {
				"imagen" : request.url_root + 'images/images/enviar-domicilio.gif'
			}

			msg['imageUrl'] = Mensaje.pegarTexto(msg, data, 'imageUrl')

			# Agregar al mensaje otra tarjeta
			messages.append(msg)	

		# Consulto el mensaje de salida
		msgs = Mensaje.consultarMensaje("ingresarTelefono", "final")		

		# Recorre cada mensaje y lo pinta
		for msg in msgs :

			data = {
				"genero" : User.devolverGenero(user['gender'], True)
			}

			msg['speech'] = Mensaje.pegarTexto(msg, data)

			# Agregar al mensaje otra tarjeta
			messages.append(msg)	

		# Registrar el log
		registrarLogAsync(user['user_id'], 'orden', 'ingresarTelefono', 'mensaje telefono', orden['restaurante'])

		# Retorna el mensaje de respuesta
		return Mensaje.crearMensaje(messages)

	""" 
	Envia el email de confirmación

	Atributos
		user: Datos del usuario
		parametros: parametros de dialogflow
		orden: datos de la orden

	Retorna
		Mensaje de respuesta formateado para enviar
	"""	
	def enviarEmailAsync(self, orden):
		def enviarEmail(orden) :

			# Consultar información para enviar al restaurante
			restaurante = RestauranteModel.find(slug = orden['restaurante'])

			# Obtener los datos de contacto del restaurante
			SMS = restaurante['SMS']
			email = restaurante['email']

			# sys.setdefaultencoding() does not exist, here!
			reload(sys)  # Reload does the trick!
			sys.setdefaultencoding('UTF8')

			total = 0

			message = ''
			message += "{}\n\n".format(orden['restaurante'].encode('utf8'))
			message += "Para: {} {}\n".format(orden['first_name'].encode('utf8'), orden['last_name'].encode('utf8'))
			message += "Dir: {}\n".format(orden['direccion'].encode('utf8'))
			message += "Tel: {}\n\n".format(orden['telefono'].encode('utf8'))
			message += "Pedido:\n"

			# Pintar los almuerzo
			for plato in orden['plato'] :
				subtotal = int(plato['precio']) * int(plato['cantidad'])
				subtotal = str(subtotal)

				message += '*{}, {} unidades de ${:,.0f}\n'.format(
					plato['nombre'].encode('utf8'),
					plato['cantidad'], 
					plato['precio']
				)
				total += int(plato['precio']) * int(plato['cantidad'])

			# Pintar la comida
			for almuerzo in orden['almuerzo'] :
				subtotal = int(almuerzo['precio']) * int(almuerzo['cantidad'])
				subtotal = str(subtotal)

				message += '*{} almuerzo con {}, {}, {} por ${:,.0f}\n'.format(
					almuerzo['cantidad'], 
					almuerzo['principio'],
					almuerzo['carne'],
					almuerzo['jugo'],
					almuerzo['precio']
				)
				total += int(almuerzo['precio']) * int(almuerzo['cantidad'])				

			message += 'Total: ${:,.0f} \n\n'.format(total)

			message +="Obs: {}".format(orden['observaciones'].encode('utf8'))

			header  = 'From: hambre@dondomicilion.co\n'
			header += 'To: [hambre@dondomicilion.co, {}]\n'.format(email)
			header += 'Subject: Pedido para {} {} \n\n'.format(orden['first_name'].encode('utf8'), orden['last_name'].encode('utf8'))

			# Envia el SMS
			call_ifttt(SMS, message)

			# Url para hacer tracking
			urltracking = 'http://www.google-analytics.com/collect?v=1&tid={}&cid={}&uid={}&t=event&ec=email&ea=open&cn={}&cs={}&cm={}'.format(
				'UA-116276042-1',
				'116276042',
				orden['restaurante'],
				'notify',
				'direct',
				'email')

			print urltracking

			# Pixel para agregar tracking al correo
			message += '<img src="{}" />'.format(urltracking)

			# Concatenar la información a enviar
			message = header + message.encode('utf8')

			# Conexión al servidor  
			server = smtplib.SMTP('smtp-relay.sendinblue.com:587')
			server.starttls()
			server.login('hambre@dondomicilion.co','7vxpra3qJ9cgzwK2')

			problems = server.sendmail('hambre@dondomicilion.co', ['hambre@dondomicilion.co', email], message)

			print problems

			# Cierra conexión con el email
			server.quit()

			# Registrar el log
			registrarLogAsync(orden['user_id'], 'orden', 'enviarEmailAsync', 'envia email', orden['restaurante'])

		async = threading.Thread(name='enviarEmail', target= enviarEmail, args=(orden, ))
		async.start()		
		