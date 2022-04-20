# -----------------------------------------------------------
# Juego simple para entender la inteligencia artificial
#
# (C) 2022 Iván García Ferreira,
# Released under MIT License
# -----------------------------------------------------------

import numpy as np
import random
import os
from os.path import exists
import pickle

# Con esta variable se controla el funcionamiento del programa:
# 1: Tu juegas contra el programa viendo las estadísticas
# 0: El programa juega contra si mismo generando su propia inteligencia
DEBUG = 1

# Inicializamos el número de filas y columnas que queremos 
FILAS = 3
COLUMNAS = 3

###
class juego():
	"""Clase principal del juego."""
	def __init__(self):
		self.fin = False
		# Creamos una array de cerosa con las filas y columnas para recrear el tablero
		self.tablero = np.zeros((FILAS, COLUMNAS), dtype=int)

	def limpiar_pantalla(self):
		os.system ("cls")

	def dibujar_tablero(self):
		contador_fila=0
		print("  1 2 3")
		for fila in self.tablero:
			contador_fila+=1
			print(str(contador_fila)+" ", end="")
			for columna in fila:
				if columna == 0:
					print("| ", end="")
				if columna == 1:
					print("|O", end="")
				if columna == 2:
					print("|X", end="")
			print("|")
	
	def comprobar_ganador(self):
		for jugador in range(1,3):
			for i in range(3):
				# Comprobamos las horizontales
				if self.tablero[i,0] == jugador and self.tablero[i,1] == jugador and self.tablero[i,2] == jugador:
					self.fin = True
					return jugador
			for i in range(3):
				# Comprobamos las verticales
				if self.tablero[0, i] == jugador and self.tablero[1, i] == jugador and self.tablero[2, i] == jugador:
					self.fin = True
					return jugador
			# Comprobamos la primera diagonal
			if self.tablero[0, 0] == jugador and self.tablero[1, 1] == jugador and self.tablero[2, 2] == jugador:
				self.fin = True
				return jugador
			# Comprobamos la segunda diagonal
			if self.tablero[2, 0] == jugador and self.tablero[1, 1] == jugador and self.tablero[0, 2] == jugador:
				self.fin = True
				return jugador
		return 0

	def partida(self, j1, j2):
		"""Clase para inicializar la partida.

		Se inicializa para jugar una partida de tres en raya

		:param j1: Primer jugador
		:param j2: Segundo jugador
		:return: Sin valor de retorno
		"""
		turno = 0
		# Hacemos que el comienzo sea aleatorio para que empiece uno u otro indistintamente 
		comienzo_aleatorio = random.randint(0, 1) 
		while self.fin == False:
			turno+=1
			if DEBUG:
				self.limpiar_pantalla()
				self.dibujar_tablero()
				print(comienzo_aleatorio)
				print("Turno "+str(turno))
			if (comienzo_aleatorio+turno) % 2 != 0:
				if DEBUG:
					print("Jugador 1:")
				self.tablero = j1.turno(self.tablero)
			else:
				if DEBUG:
					print("Jugador 2:")
				self.tablero = j2.turno(self.tablero)
			ganador = self.comprobar_ganador()
			if ganador != 0:
				self.limpiar_pantalla()
				if j1.comprobar_ficha() == ganador:
					j1.ganador(self.tablero)
					if DEBUG:
						print("Ganador el jugador 1")
				else:
					j2.ganador(self.tablero)
					if DEBUG:
						print("Ganador el jugador 2")
						self.dibujar_tablero()
			if turno == 9 and ganador == 0:
				self.limpiar_pantalla()
				if DEBUG:
					print("Se ha producido un empate")
					self.dibujar_tablero()
				self.fin = True


class jugador_humano():
	"""Clase para jugar una partida un humano.
	
	Te va pidiendo valores de fila y columna para que pongas donde quieres colocar la ficha
	"""
	def __init__(self, eleccion):
		if eleccion == "O":
			self.ficha = 1
		else:
			self.ficha = 2

	def turno(self, tablero):
		colocada = False
		while colocada == False:
			print("Indica tu jugada")
			fila = int(input('¿Fila? '))
			columna = int(input('¿Columna? '))
			if tablero[fila-1, columna-1] == 0:
				tablero[fila-1, columna-1] = self.ficha
				colocada = True
		return tablero

	def comprobar_ficha(self):
		return self.ficha
	
	def ganador(self, tablero):
		print("Has ganado, humano!")


class jugador_aleatorio():
	"""Clase para jugar una partida con una IA aleatoria."""
	def __init__(self, eleccion):
		if eleccion == "O":
			self.ficha = 1
		else:
			self.ficha = 2

	def turno(self, tablero):
		colocada = False
		while colocada == False:
			fila = random.randint(1, 3)
			columna = random.randint(1, 3)
			if tablero[fila-1, columna-1] == 0:
				tablero[fila-1, columna-1] = self.ficha
				colocada = True
		return tablero
	
	def ganador(self, tablero):
		if DEBUG:
			print("Ha ganado un aleatorio")
	
	def comprobar_ficha(self):
		return self.ficha

class jugador_IA():
	"""Clase para jugar una partida con una IA que se puede entrenar."""
	def __init__(self, eleccion):
		if eleccion == "O":
			self.ficha = 1
		else:
			self.ficha = 2
		self.tasa_aprendizaje = 0.2
		# Inicializamos un diccionario para almacenar las posibilidades de ganar de cada posicion
		self.estado_valor = {}
		self.cargar_politica()
		self.ultima_posicion_jugada = np.zeros((FILAS, COLUMNAS), dtype=int)
		
	def comprobar_ficha(self):
		return self.ficha

	def turno(self, tablero):
		aleatorio = random.randint(0, 1)
		# aleatorio = 0
		if self.serializar(tablero) != "000000000":
			self.estado_valor[self.serializar(self.ultima_posicion_jugada)] = self.probabilidad(self.ultima_posicion_jugada)+self.tasa_aprendizaje*(self.probabilidad(tablero)-self.probabilidad(self.ultima_posicion_jugada))
			if DEBUG:
				print("Guardo la anterior: " + str(self.serializar(self.ultima_posicion_jugada)) +" con probabilidad: " + str(self.probabilidad(self.ultima_posicion_jugada)))
		if aleatorio:
			colocada = False
			tablero_antiguo = tablero.copy()
			while colocada == False:
				fila = random.randint(1, 3)
				columna = random.randint(1, 3)
				if tablero[fila-1, columna-1] == 0:
					tablero[fila-1, columna-1] = self.ficha
					colocada = True
			# Se actualiza el diccionario donde se guardan las probabilidades de ganar
			self.estado_valor[self.serializar(tablero_antiguo)] = self.probabilidad(tablero_antiguo)+self.tasa_aprendizaje*(self.probabilidad(tablero)-self.probabilidad(tablero_antiguo))
			if DEBUG:
				print("Juego aleatorio")
				input('Pulsa')
			return tablero
		else:
			# Ver las posibles posiciones que puedo tomar
			posiciones = self.conseguir_posiciones(tablero)
			mejor_valor = 0
			mejor_jugada = np.zeros((FILAS, COLUMNAS), dtype=int)
			# Para cada posición que se puede jugar
			for posicion in posiciones:
				# Ver la probabilidad de ganar
				valor = self.probabilidad(posicion)
				# Si esta posición es mayor que la anterior se guarda
				if valor > mejor_valor:
					mejor_valor = valor
					mejor_jugada = posicion
			# Se actualiza el diccionario donde se guardan las probabilidades de ganar
			self.estado_valor[self.serializar(tablero)] = self.probabilidad(tablero)+self.tasa_aprendizaje*(self.probabilidad(mejor_jugada)-self.probabilidad(tablero))
			if DEBUG:
				print("Guardo: " + str(self.serializar(tablero)) + " con probabilidad: " + str(self.estado_valor.get(self.serializar(tablero))))
				print("Probabilidad de ganar de esta posición("+self.serializar(tablero)+"): " + str(self.probabilidad(tablero)))
				print("Probabilidad de ganar de la próxima posición ("+self.serializar(mejor_jugada)+"): " + str(self.probabilidad(mejor_jugada)))
				print("He decidido")
				print(mejor_jugada)
				print(self.probabilidad(tablero)+self.tasa_aprendizaje*(self.probabilidad(mejor_jugada)-self.probabilidad(tablero)))
				input('Pulsa')
			self.guardar_politica()
			self.ultima_posicion_jugada = mejor_jugada.copy()
			return mejor_jugada

	def conseguir_posiciones(self, tablero):
		"""Devuelve una lista con las posiciones posibles para jugar en el tablero actual"""
		contador= 0
		jugadas = []
		for i in tablero.reshape(FILAS*COLUMNAS):
			copia_tablero = tablero.reshape(FILAS*COLUMNAS).copy()
			if i == 0:
				copia_tablero[contador] = self.ficha
				jugadas.append(copia_tablero.reshape((3, 3)))
			contador+=1
		return jugadas

	def cargar_politica(self):
		if exists("politica"+str(self.ficha)+".pkl"):
			fr = open("politica"+str(self.ficha)+".pkl",'rb')
			self.estado_valor = pickle.load(fr)
			fr.close()

	def guardar_politica(self):
		with open("politica"+str(self.ficha)+".pkl", "wb") as f:
			pickle.dump(self.estado_valor, f)
	
	def probabilidad(self, posicion):
		"""Devuelve la probabilidad de ganar de una posicion"""
		if self.estado_valor.get(self.serializar(posicion)) == None:
			return 0.5
		else:
			return self.estado_valor[self.serializar(posicion)]

	def serializar(self, posic):
		"""Devuelve el valor serializado de una posición"""
		aux = posic.reshape(FILAS*COLUMNAS)
		return ''.join([str(item) for item in aux])

	def ganador(self, tablero):
		self.estado_valor[self.serializar(tablero)] = 1
		if DEBUG:
			print("ha ganado la IA")
		self.guardar_politica()

# Comienza la partida según esté en modo debug o no
# Si no está en modo debug juega 50.000 veces contra si mismo
if __name__ == '__main__':
	if DEBUG == 1:
		j1 = jugador_humano("X")
		j2 = jugador_IA("O")
		tres_raya = juego()
		tres_raya.partida(j1,j2)
	else:
		cont = 0
		while cont < 50000:
			j1 = jugador_IA("X")
			j2 = jugador_IA("O")
			tres_raya = juego()
			tres_raya.partida(j1,j2)
			print(cont)
			cont+=1