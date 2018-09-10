import requests
import json

def get_dialog_message(messages):
	data = { 
		"messages": messages 
	}
	return data

def get_persistent_menu():
	data = { 
		"setting_type":"persistent_menu",
	  	"persistent_menu":
	  	[
    		{
      			"locale":"default",
      			"composer_input_disabled": False,
      			"call_to_actions":
      			[
      				{
	      				"title":"Sobre tu pedido",
	          			"type":"nested",
	          			"call_to_actions":[
		          			{
		          				"title":"Confirmar pedido",
		      					"type":"postback",
		          				"payload":"confirmar_pedido"
		        			},
		        			{
		          				"title":"Consultar pedido",
		      					"type":"postback",
		          				"payload":"consultar_pedido"
		        			},
		        			{
		          				"title":"Cancelar pedido",
		          				"type":"postback",
		          				"payload":"cancelar_pedido"
		        			}
	          			]
          			},
          			{
          				"title":"Cambiar ciudad",
          				"type":"postback",
          				"payload":"cambiar_ciudad"
        			},
        			{
          				"title":"Ayuda",
          				"type":"postback",
          				"payload":"ayuda"
        			}
      			]
    		}
  		]
	}
	return data

def get_ifttt(telefono, mensaje):
	data = { 
		"value1" : telefono, 
		"value2" : mensaje
	}

	return data

def call_ifttt(telefono = '+573017516045', mensaje = 'Se recibio pedido'):
	res = requests.post('https://maker.ifttt.com/trigger/dondomicilion/with/key/kIigIzb06l8f7Usf0ZarknKjAAaBdUxbmW4G4dNA4YB',
				data = json.dumps(get_ifttt(telefono, mensaje)),
				headers = { 'Content-type': 'application/json' })

	if res.status_code == 200:
		print "SMS enviado exitosamente"

def get_log(log):
	data = { 
		"value1" : log
	}

	return data

def log_ifttt(log):
	res = requests.post('https://maker.ifttt.com/trigger/log/with/key/kIigIzb06l8f7Usf0ZarknKjAAaBdUxbmW4G4dNA4YB',
				data = json.dumps(get_log(log)),
				headers = { 'Content-type': 'application/json' })

	if res.status_code == 200:
		print "Log registrado"

def get_response():
	data = {
		"speech": "",
		"displayText": "hola mundo",
		"source" : "webhook"
	}

	return data

def get_data():
	data = { 
				'setting_type': 'call_to_actions',
				'thread_state': 'new_thread', 
				'call_to_actions' : [ { "payload":"hola" } ]
			}
	return data


def get_greeting_text():
	data = { "setting_type":"greeting",
		"greeting": { 
			"text":"Mijito, tu pedido en par boliones" 
		}
	}
	return data


def call_geoname_API(lat, lng, username):
	res = requests.get('http://api.geonames.org/findNearByWeatherJSON',
					params = {'lat': lat, 'lng': lng, 'username': username } )

	if res.status_code == 200:
		res = json.loads(res.text)

		city = res['weatherObservation']['stationName']
		temperature = res['weatherObservation']['temperature']
		return {'city': city, 'temperature': temperature}		

def call_send_API( data, token ):
	res = requests.post('https://graph.facebook.com/v3.0/me/messages',
					params = {'access_token': token },
					data = json.dumps(data),
					headers = { 'Content-type': 'application/json' }
					)
	if res.status_code == 200:
		print "El mensaje fue enviado exitosamente!"

def call_user_API(user_id, token):
	res = requests.get('https://graph.facebook.com/v3.0/' + user_id ,
					params = {'access_token': token },
					headers = { 'Content-type': 'application/json' } )

	data = json.loads(res.text)
	return data


def call_set_started_button(token):
	res = requests.post('https://graph.facebook.com/v3.0/me/thread_settings',
				params = {'access_token': token},
				data = json.dumps( get_data()  ),
				headers = { 'Content-type': 'application/json' }
				)
 	
 	if res.status_code == 200:
 		print(json.loads(res.text) )

def call_delete_started_button(token):
	res = requests.delete('https://graph.facebook.com/v3.0/me/thread_settings',
				params = {'access_token' : token},
				data = json.dumps( get_data() ),
				headers = { 'Content-type': 'application/json' } )

	if res.status_code == 200:
		print(json.loads(res.text) )

def greeting_text(token):
	res = requests.post('https://graph.facebook.com/v3.0/me/thread_settings',
				params = {'access_token' : token},
				data = json.dumps( get_greeting_text() ),
				headers = { 'Content-type': 'application/json' } )

	if res.status_code == 200:
		print(json.loads(res.text) )

def persistent_menu(token):
	res = requests.post('https://graph.facebook.com/v3.0/me/messenger_profile',
				params = {'access_token' : token},
				data = json.dumps( get_persistent_menu() ),
				headers = { 'Content-type': 'application/json' } )

	if res.status_code == 200:
		print(json.loads(res.text) )		