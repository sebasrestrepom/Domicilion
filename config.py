import os

class Config(object):
	SECRET_KEY = 'LA_MEGA-SECRET_KEY_DE.DON,BONACHON-SEBASTIAN-RESTREPO{Y_GIORGIO_ORATE'
	#Token Domicilion
	#os.environ['PAGE_ACCESS_TOKEN'] = 'EAACCslKuqdQBAFe8UDdskmAZBBUAViWT7IQ2iO37VMfZCCZCNKBrSjXAzbnOgCXTimVeoxZBNZAtsNZALryvb6RdJ3nGO1ZA0pLfkCZAKSzE33bZBmDGaEyj5k8KsRy1XuZAEliKd1clZALoRCvHA1nCIfYFCUrgyGaVG6MIZBPskSfDkgZDZD'

	# Token Don Bonachon
	os.environ['PAGE_ACCESS_TOKEN'] = 'EAAWvxZBZA1fTkBAAOYpnQpmYGSMQkcFu9TEcURf0ArTArfvhdowUqA0ZB85QCUFHfJ9SXilcZCiuH40ZCmT5TvQm3SWqMtwrJAdD8rP9BEnHlgXqgBOzMwM0zsvoEJM1V18h6lM5Y7hrbQZABYQfulNNmdsyHypFqc0H9vvcMEkAZDZD'
	# Cliente id DEV
	os.environ['APP_CLIENT_ID'] = '153062242154030'
	# ID secreto
	os.environ['APP_CLIENT_SECRET'] = '665982f763f1b2fcc8bad78dac699548'
	# Token de la app
	os.environ['APP_TOKEN'] = '153062242154030|nQSnxKS_A0hYLRPluBQN4Huvs7c'
	# Variable codigo viejo
	USER_GEONAMES = os.environ.get('USER_GEONAMES')

class DevelopmentConfig(Config):
	DEBUG = True
	