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
 *
 * Contribuciones:
 *
 * Dario Correal - Version inicial
 """


import config as cf
from DISClib.ADT.graph import gr
from DISClib.ADT import list as lt
from DISClib.ADT import map as mp
from DISClib.DataStructures import mapentry as me
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.ADT import list as lt
from DISClib.Utils import error as error
assert cf

"""
Se define la estructura de un catálogo de videos. El catálogo tendrá dos listas, una para los videos, otra para las categorias de
los mismos.
"""

# Construccion de modelos

def initCatalog():
    
    catalog={"AeropuertosRutasGraph": None,
            "Ciudades":None,
            "Aeropuertos":None,
            "CiudadesTabla":None,
            "AeropuertosTabla":None,
            "TablaRutasProv":None}
    
    #hay que ajustar el size de ambos grafos
    #grado dirigido
    catalog["AeropuertosRutasGraph"]= gr.newGraph(datastructure='ADJ_LIST',
                                              directed=True,
                                              size=93000,
                                              comparefunction=compareString) # maté la comparación
    
    #grafo no dirigido
    catalog["AeropuertosRutasDoblesGraph"]= gr.newGraph(datastructure='ADJ_LIST',
                                              directed=False,
                                              size=93000,
                                              comparefunction=compareString)
    
    catalog["CiudadesTabla"]=mp.newMap(numelements=37831, 
                                    maptype="CHAINING",
                                    loadfactor=4.0)
    
    #9075 aeropuertos, 37411 ciudades únicas
    catalog["AeropuertosTabla"]= mp.newMap(numelements=10061,
                                    maptype="CHAINING",
                                    loadfactor=4.0)

    catalog["TablaRutasProv"]= mp.newMap(numelements=95000,
                                    maptype="CHAINING",
                                    loadfactor=4.0)                                  

    return catalog
    


# Funciones para agregar informacion al catalogo

def addCity(catalog,ciudad):
    cityAscii=ciudad["city_ascii"]
    #adminName=ciudad["city_ascii"] ## La ciudad de springfield se repite 17 veces, pero es una ciudad distinta
    keyCity=cityAscii#+"-"+adminName #definir como será la key
    existCity=mp.contains(catalog["CiudadesTabla"],keyCity)
    if existCity:
        lt.addLast(mp.get(catalog["CiudadesTabla"],keyCity)["value"],ciudad)
    else:
        listCitiesId=lt.newList(datastructure="ARRAY_LIST")
        lt.addLast(listCitiesId,ciudad)
        mp.put(catalog["CiudadesTabla"],cityAscii,listCitiesId) 

def addAeropuerto(catalog,aeropuerto):
    #no hay aeropuertos repetidos
    IATA=aeropuerto["IATA"]
    mp.put(catalog["AeropuertosTabla"],IATA,aeropuerto)
    addAeropuertoGraf(catalog,IATA,"AeropuertosRutasGraph") 

###################
# Modificación en grafos
###################

#1. Se crea una tabla de simbolos con las rutas
# con el fin de conocer si la ruta debe agregarse al grafo bireccional o unidireccional
def addRutasAereas(catalog, route):
    aeropuertoSalida=route["Departure"]
    existSalida=mp.contains(catalog["TablaRutasProv"],aeropuertoSalida)
    if existSalida:
        lt.addLast(mp.get(catalog["TablaRutasProv"],aeropuertoSalida)["value"],route)
    else:
        listAeropuertosLlegada=lt.newList(datastructure="ARRAY_LIST",cmpfunction=cmpDestination)
        lt.addLast(listAeropuertosLlegada,route)
        mp.put(catalog["TablaRutasProv"],aeropuertoSalida,listAeropuertosLlegada)

def cmpDestination(aeropuerto1,aeropuerto2):
    return aeropuerto1["Destination"]== aeropuerto2["Destination"]

#2. Se recorren todas las rutas de salida, se va a ir adicionando info al grafo dirigido o no dirigido dependiendo
def addRuta(catalog):
    keySetRutas=mp.keySet(catalog["TablaRutasProv"])
    print("Total rutas de salida: ",keySetRutas["size"])
    for aeropuertoSalida in lt.iterator(keySetRutas):
        aeropuertoSalidaRutas=mp.get(catalog["TablaRutasProv"],aeropuertoSalida)["value"]["elements"]
        #Se adiciona el aeropuerto como vértice a ambos grafos
        addAeropuertoGraf(catalog,aeropuertoSalida,"AeropuertosRutasGraph")
        addAeropuertoGraf(catalog,aeropuertoSalida,"AeropuertosRutasDoblesGraph")
        
        for aeropuertoLlegadaInfo in aeropuertoSalidaRutas:
            peso=float(aeropuertoLlegadaInfo["distance_km"])
            aeropuertoLlegada=aeropuertoLlegadaInfo["Destination"]

            if mp.contains(catalog["TablaRutasProv"],aeropuertoLlegada):
                llegada=mp.get(catalog["TablaRutasProv"],aeropuertoLlegada)["value"] 
                existeRetorno=existeRutaDeRetorno(aeropuertoSalida,llegada)

                #se comprueba si la ruta solo funciona en una dirección, si es verdad se agrega al grafo en solo una dirección
                
                if existeRetorno:
                    addAeropuertoGraf(catalog,aeropuertoLlegada,"AeropuertosRutasDoblesGraph") #se adiciona al graf no dirigido
                    #print(aeropuertoSalida,aeropuertoLlegada,peso)
                    #ambosVertice
                    #if gr.containsVertex(catalog["AeropuertosRutasDoblesGraph"],aeropuertoLlegada) and gr.containsVertex(catalog["AeropuertosRutasDoblesGraph"],aeropuertoSalida):
                    if gr.getEdge(catalog["AeropuertosRutasDoblesGraph"],aeropuertoSalida,aeropuertoLlegada) is None:
                        gr.addEdge(catalog["AeropuertosRutasDoblesGraph"],aeropuertoSalida,aeropuertoLlegada,peso)
                else:
                    #addAeropuertoGraf(catalog,aeropuertoLlegada,"AeropuertosRutasGraph") #se adiciona al graf dirigido
                    gr.addEdge(catalog["AeropuertosRutasGraph"],aeropuertoSalida,aeropuertoLlegada,peso)

def addAeropuertoGraf(catalog, vertice,nombreGrafo):
    """
    Adiciona un aeropuerto como un vertice del grafo
    """
    try:
        if not gr.containsVertex(catalog[nombreGrafo], vertice):
            gr.insertVertex(catalog[nombreGrafo], vertice)
        return catalog
    except Exception as exp:
        error.reraise(exp, 'model:addRoute')

def existeRutaDeRetorno(aeropuerto,listaRutas):
    """
    Si el retorno es distinto 0 es que existe la ruta en dos direcciones
    """
    existe=False
    for ruta in lt.iterator(listaRutas):
        if ruta["Destination"]==aeropuerto:
            existe=True
            break
    return existe#lt.isPresent(listaRutas,aeropuerto)



def addRutaOriginal(catalog,ruta):    

    arco = None
    
    if gr.containsVertex(catalog["AeropuertosRutasGraph"],ruta["Departure"]) and gr.containsVertex(catalog["AeropuertosRutasGraph"],ruta["Departure"]):
        
        arco = gr.getEdge(catalog["AeropuertosRutasGraph"],ruta["Departure"],ruta["Destination"])

    if arco is not None:

            if gr.containsVertex(catalog["AeropuertosRutasGraph"],ruta["Departure"]) and gr.containsVertex(catalog["AeropuertosRutasGraph"],ruta["Departure"]):

                arco_contrario = gr.getEdge(catalog["AeropuertosRutasGraph"],ruta["Destination"],ruta["Departure"])

            if arco_contrario is not None: # Caso que va por los dos lados, grafo no dirigido
        
                arco_no_dir = gr.getEdge(catalog["AeropuertosRutasDoblesGraph"],ruta["Destination"],ruta["Departure"])

                if arco_no_dir is None: # si no está en el grafo no dirigido lo añado

                    if not gr.containsVertex(catalog["AeropuertosRutasDoblesGraph"],ruta["Destination"]):
                        gr.insertVertex(catalog["AeropuertosRutasDoblesGraph"], ruta["Destination"])
                    if not gr.containsVertex(catalog["AeropuertosRutasDoblesGraph"],ruta["Departure"]):
                        gr.insertVertex(catalog["AeropuertosRutasDoblesGraph"], ruta["Departure"])
                    gr.addEdge(catalog["AeropuertosRutasDoblesGraph"],ruta["Destination"],ruta["Departure"],float(ruta["distance_km"]))

                    arco_contrario = None # intento de eliminar el edge que se acaba de añaadir
                    # TODO posibilidad de eliminar del otro lado el vértice
            
    else:
        if not gr.containsVertex(catalog["AeropuertosRutasGraph"],ruta["Destination"]):
            gr.insertVertex(catalog["AeropuertosRutasGraph"], ruta["Destination"])
        if not gr.containsVertex(catalog["AeropuertosRutasGraph"],ruta["Departure"]):
            gr.insertVertex(catalog["AeropuertosRutasGraph"], ruta["Departure"])
        gr.addEdge(catalog["AeropuertosRutasGraph"],ruta["Destination"],ruta["Departure"],float(ruta["distance_km"]))
    

def densidad(catalog):
    print(gr.numVertices(catalog['AeropuertosRutasGraph']))
    print(gr.numVertices(catalog['AeropuertosRutasDoblesGraph']))




# Funciones para creacion de datos

# Funciones de consulta

# Funciones utilizadas para comparar elementos

def compareString(stop, keyvaluestop):
    """
    Compara dos estaciones
    """
    stopcode = keyvaluestop['key']
    if (stop == stopcode):
        return 0
    elif (stop > stopcode):
        return 1
    else:
        return -1



# Funciones de ordenamiento



# ==============================
#FUNCIONES LAB 9
# características específicas de cada uno de los grafos definidos
# ==============================


def connectedComponents(analyzer,nombreGrafo):
    """
    Calcula los componentes conectados del grafo
    Se utiliza el algoritmo de Kosaraju
    """
    analyzer[nombreGrafo] = scc.KosarajuSCC(analyzer[nombreGrafo])
    return scc.connectedComponents(analyzer[nombreGrafo])


def totalAeropuertos(analyzer,nombreGrafo):
    """
    Retorna el total de estaciones (vertices) del grafo
    """
    return gr.numVertices(analyzer[nombreGrafo])


def totalRutas(analyzer,nombreGrafo):
    """
    Retorna el total arcos del grafo
    """
    return gr.numEdges(analyzer[nombreGrafo])

def infoGrafo(analyzer,nombreGrafo):
    vertices=totalAeropuertos(analyzer,nombreGrafo)
    arcos=totalRutas(analyzer,nombreGrafo)
    return vertices,arcos

