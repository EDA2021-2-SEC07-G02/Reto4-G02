"""
 * Copyright 2020, Departamento de sistemas y Computación, Universidad
 * de Los Andes
 *
 *
 * Desarrolado para el curso ISIS1225 - Estructuras de Datos y Algoritmos
 *
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along withthis program.  If not, see <http://www.gnu.org/licenses/>.
 """

import config as cf
import sys
import controller
from DISClib.ADT import list as lt
from time import process_time
assert cf


"""
La vista se encarga de la interacción con el usuario
Presenta el menu de opciones y por cada seleccion
se hace la solicitud al controlador para ejecutar la
operación solicitada
"""

# ___________________________________________________
#  Variables
# ___________________________________________________

aeropuertosfile="airports_full.csv"
rutasfile="airports_full.csv"
ciudadesfile="worldcities.csv"
catalog = None

# ___________________________________________________
#  Menu principal
# ___________________________________________________


def printMenu():
    print("Bienvenido")
    print("0- Cargar información en el catálogo")
    print("1- Encontrar puntos de interconexión aérea")
    print("2- Encontrar clústeres de tráfico aéreo")
    print("3- Encontrar la ruta más corta entre ciudades")
    print("4- Utilizar las millas de viajero")
    print("5- Cuantificar el efecto de un aeropuerto cerrado")
    print("6- Comparar con servicio WEB externo")
    print("7- Visualizar gráficamente las respuestas anteriores")
    print("8- Salir")


def initCatalog():
    """

    """
    return controller.initCatalog()


def infoCargaCatalogo():
    print("\n"+"*"*50)
    print("*"*10+"Información mapas"+"*"*10)
    print("Tamaño de mapa CiudadesTabla: ",catalog["CiudadesTabla"]["size"])
    print("Tamaño de mapa CiudadesTabla: ",catalog["AeropuertosTabla"]["size"])
    print("*"*10+"Información grafos:"+"*"*10)
    print("--- POR IMPLEMENTAR")
    print("-"*40)
    print("\n"+"*"*10+"FIN Información mapas y grafos"+"*"*10)
    print("*"*50)

"""
Menu principal
"""
while True:
    printMenu()
    inputs = input('Seleccione una opción para continuar\n')
    print("\n")
    tiempoInicial=process_time()
    if int(inputs[0]) == 0:
        catalog=controller.initCatalog()

        controller.loadServices(catalog)
        infoCargaCatalogo()


    elif int(inputs[0]) == 1:
        controller.numero(catalog)
        pass

    elif int(inputs[0]) == 2:
        print("Por implementar......")
        pass

    elif int(inputs[0]) == 3:
        print("Por implementar......")
        pass

    elif int(inputs[0]) == 4:
        print("Por implementar......")
        pass

    elif int(inputs[0]) == 5:
        print("Por implementar......")
        pass

    elif int(inputs[0]) == 6:
        print("Por implementar......")
        pass

    elif int(inputs[0]) == 7:
        print("Por implementar......")
        pass

    else:
        sys.exit(8)
    input("\nDuración: "+str((process_time()-tiempoInicial)*1000)+"ms\nPresione enter para continuar...")
    print("")
sys.exit(8)
