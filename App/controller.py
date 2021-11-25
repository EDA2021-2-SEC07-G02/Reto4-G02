"""
 * Copyright 2020, Departamento de sistemas y Computación,
 * Universidad de Los Andes
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
import model
import csv


"""
El controlador se encarga de mediar entre la vista y el modelo.
"""

# Inicialización del Catálogo de libros


def initCatalog():
    return model.initCatalog()


def loadServices(analyzer):
    """
    aa
    """

    archivo_aeropuertos = cf.data_dir + "Skylines/airports_full.csv"
    archivo_rutas = cf.data_dir + "Skylines/routes_full.csv"
    archivo_ciudades = cf.data_dir + "Skylines/worldcities.csv"

    ###tablas de simbolos
    input_file_aeropuerts = csv.DictReader(open(archivo_aeropuertos, encoding="utf-8"),
                                delimiter=",")
    input_file_ciudades= csv.DictReader(open(archivo_ciudades, encoding="utf-8"),
                                delimiter=",")
    print(type(input_file_ciudades))
    for aeropuerto in input_file_aeropuerts:
        model.addAeropuerto(analyzer,aeropuerto)
    
    for ciudad in input_file_ciudades:
        model.addCity(analyzer,ciudad)
    
    ### grafos
    
    input_file_rutas = csv.DictReader(open(archivo_rutas, encoding="utf-8"),
                                delimiter=",")
    for ruta in input_file_rutas:
        model.addRutasAereas(analyzer,ruta)
    
    infoView=model.addRuta(analyzer) #primeros aeropuertos cargados

    ultimaCiudad=ciudad

    return analyzer,infoView,ultimaCiudad

def numero(catalog):
    model.densidad(catalog)

def infoGrafo(catalog,nombreGrafo):
    model.infoGrafo(catalog,nombreGrafo)

# Funciones para la carga de datos

# Funciones de ordenamiento

# Funciones de consulta sobre el catálogo
