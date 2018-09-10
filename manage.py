# -*- coding: utf-8 -*-
import os
import urllib
import json
import requests

from flask import Flask
from flask import request
from flask import redirect
from flask import make_response
from flask import render_template

from config import DevelopmentConfig

from handler import recived_message
from handler import recived_postback

from api import call_set_started_button
from api import greeting_text
from api import persistent_menu
from api import get_response
from api import call_ifttt

from models import UserModel

from dialogflow import recibirResponse

app = Flask(__name__, static_url_path = "/images", static_folder = "static")
app.config.from_object( DevelopmentConfig )

@app.route('/facebook', methods = ['GET', 'POST'])
def facebook():
	if request.method == 'GET':
		verify_token = request.args.get('hub.verify_token', '')
		if verify_token == app.config['SECRET_KEY']:
			return request.args.get('hub.challenge', '')
		return 'Error al validar el secreto'

	elif request.method == 'POST':
		payload  = request.get_data()
		data = json.loads(payload)

		print json.dumps(data, indent = 4)

		for page_entry in data['entry']:
			for message_event in page_entry['messaging']:
				#Solo mensaje
				if 'message' in message_event:
					recived_message( message_event , os.environ['PAGE_ACCESS_TOKEN'], app.config['USER_GEONAMES'] )
				
				if 'postback' in message_event:
					recived_postback( message_event, os.environ['PAGE_ACCESS_TOKEN'])

		return "ok"

@app.route('/dialogflow', methods = ['POST'])
def dialogflow():
	# Recibe la solicitud del servidor
	response = request.get_json(silent=True, force=True)

	print "Request:"
	print json.dumps(response, indent=4)

	# Obtiene el status de la solucitud
	status = response.get('status')

	# Valida si esta bien hecha la solicitud
	if status['code'] == 200 :
		# Llama el metodo encargado de procesar
		return recibirResponse(response, os.environ['PAGE_ACCESS_TOKEN'])

@app.route('/', methods = ['GET'])
def index():
	return render_template('index.html')

@app.route('/terminos-condiciones', methods = ['GET'])
def terminos():
	return render_template('terminos-condiciones.html')

@app.route('/politicas', methods = ['GET'])
def politicas():
	return render_template('politicas.html')

@app.route('/v7d7041hph028898xl8ds0wwsvrocu.html', methods = ['GET'])
def v7d7041hph028898xl8ds0wwsvrocu():
	return render_template('v7d7041hph028898xl8ds0wwsvrocu.html')	

@app.route('/autorizacion', methods = ['GET'])
def autorizacion():
	if request.method == 'GET':
		# Obtengo el code
		code = request.args.get('code')
		user_id = request.args.get('state')
		# Id de la aplicación
		cliente_id = os.environ['APP_CLIENT_ID']
		# La url para regresar
		redirect_uri = (request.url_root + 'autorizacion').replace('http://', 'https://')
		# Numero secreto de la app
		client_secret = os.environ['APP_CLIENT_SECRET']
		# Url para enviar
		URI = 'https://graph.facebook.com/v2.12/oauth/access_token?client_id={}&redirect_uri={}&client_secret={}&code={}'.format(cliente_id, redirect_uri, client_secret, code)
		# Llamar la URI
		res = requests.get(URI, headers = { 'Content-type': 'application/json' })
		res = json.loads(res.text)
		# Obtener valores
		access_token = res.get('access_token')
		token_type = res.get('token_type')
		# Token de la app
		token_app = os.environ['APP_TOKEN']
		# Url para comprobar
		urlComprobacion = 'https://graph.facebook.com/debug_token?input_token={}&access_token={}'.format(access_token, token_app)
		res = requests.get(urlComprobacion, headers = { 'Content-type': 'application/json' })
		res = json.loads(res.text)

		# Obtengo el id del usuario de Facebook
		facebook_id = res['data']['user_id']

		# Consulto el usuario
		user = UserModel.find(user_id = user_id)
		# Asigno el facebook id
		user['facebook_id'] = facebook_id
		user['access_token'] = access_token
		# Guardo en la base de datos
		UserModel.save(user)

		#res = requests.get(urlComprobacion, headers = { 'Content-type': 'application/json' })
		print json.dumps(res, indent = 4)

	return "ok"

# https://www.facebook.com/v2.12/dialog/oauth?client_id=153062242154030&redirect_uri=https://a642e299.ngrok.io/autorizacion&state=tote

@app.route('/token', methods = ['GET'])
def token():
	# Id de la aplicación
	cliente_id = os.environ['APP_CLIENT_ID']
	# Numero secreto de la app
	client_secret = os.environ['APP_CLIENT_SECRET']

	URL = 'https://graph.facebook.com/oauth/access_token?client_id={}&client_secret={}&grant_type=client_credentials'.format(cliente_id, client_secret)
	res = requests.get(URL, headers = { 'Content-type': 'application/json' })
	res = json.loads(res.text)
	# Asignar nuevo token a la app
	os.environ['APP_TOKEN'] = res['access_token']
	# Pintar resutlado
	print json.dumps(res, indent = 4)

	return 'ok'

if __name__ == '__main__':
	call_set_started_button( os.environ['PAGE_ACCESS_TOKEN'] )
	greeting_text( os.environ['PAGE_ACCESS_TOKEN'] ) 
	persistent_menu( os.environ['PAGE_ACCESS_TOKEN'] ) 
	app.run(port = 5000, debug = True)
