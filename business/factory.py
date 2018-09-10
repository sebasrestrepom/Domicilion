#!/usr/bin/env python
# -*- coding: utf-8 -*-

from almuerzo import Almuerzo
from comida import Comida
from orden import Orden
from restaurante import Restaurante
from smartTalk import SmartTalk
from user import User

class Factory(object):

	@staticmethod
	def crearObjeto(clase):
		if clase == 'smartTalk' :
			return SmartTalk()
		if clase == 'comida' :
			return Comida()			
		if clase == 'orden' :
			return Orden()				
		if clase == 'restaurante' :
			return Restaurante()	
		if clase == 'user' :
			return User()	
		if clase == 'almuerzo' :
			return Almuerzo()				