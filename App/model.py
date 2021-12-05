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
            "AeropuertosTabla":None}
    

    ###GRAFOS
    #grado dirigido
    catalog["AeropuertosRutasGraph"]= gr.newGraph(datastructure='ADJ_LIST',
                                              directed=True,
                                              size=10061,
                                              comparefunction=compareString)
    
    #grafo no dirigido
    catalog["AeropuertosRutasDoblesGraph"]= gr.newGraph(datastructure='ADJ_LIST',
                                              directed=False,
                                              size=10061,
                                              comparefunction=compareString)
    

    ###Tablas de simbolos
    catalog["CiudadesTabla"]=mp.newMap(numelements=37831, 
                                    maptype="CHAINING",
                                    loadfactor=4.0)

    #9075 aeropuertos, 37411 ciudades únicas
    catalog["AeropuertosTabla"]= mp.newMap(numelements=10061,
                                    maptype="CHAINING",
                                    loadfactor=4.0)

                                

    return catalog
    


# Funciones para agregar informacion al catalogo

def addCity(catalog,ciudad):
    """
    Añade una ciudad a la tabla de simbolos de ciudades
    """
    cityAscii=ciudad["city_ascii"]
    keyCity=cityAscii
    existCity=mp.contains(catalog["CiudadesTabla"],keyCity)
    if existCity:
        lt.addLast(mp.get(catalog["CiudadesTabla"],keyCity)["value"],ciudad)
    else:
        listCitiesId=lt.newList(datastructure="ARRAY_LIST")
        lt.addLast(listCitiesId,ciudad)
        mp.put(catalog["CiudadesTabla"],cityAscii,listCitiesId) 

def addAeropuerto(catalog,aeropuerto): #Nota: en el archivo no hay aeropuertos repetidos
    """
    Añade a un aeropuerto a ambos grafos y a la tabla de simbolos de aeropuertos
    """
    IATA=aeropuerto["IATA"]
    #Se adiciona info de si el aeropuerto sirve como punto de conexión
    aeropuerto["connections"]=0
    aeropuerto["inbound"]=0
    aeropuerto["outbound"]=0
    mp.put(catalog["AeropuertosTabla"],IATA,aeropuerto)
    addAeropuertoGraf(catalog,IATA,"AeropuertosRutasGraph") 
    addAeropuertoGraf(catalog,IATA,"AeropuertosRutasDoblesGraph")


def addAeropuertoGraf(catalog, vertice,nombreGrafo): #añade un aeropuerto como vértice
    """
    Adiciona un aeropuerto como un vertice del grafo
    """
    try:
        if not gr.containsVertex(catalog[nombreGrafo], vertice):
            gr.insertVertex(catalog[nombreGrafo], vertice)
        return catalog
    except Exception as exp:
        error.reraise(exp, 'model: ERROR No se puede añadir el vértice')

def numeroAeropuertosConectados(catalog):
    """
    Se añade una key a ambos grafos para saber cuantos aeropuertos
    tienen por lo menos una ruta de conexión con otro aeropuerto
    """
    catalog["AeropuertosRutasGraph"]["AeropuertosConConexion"]=0
    catalog["AeropuertosRutasDoblesGraph"]["AeropuertosConConexion"]=0

###################
# Construcción arcos en grafos
###################


def addRutasGraphDirigido(catalog,route):
    """
    Se añaden TODAS las rutas al grafo dirigido.
    Vértices -> TODOS los aeropuertos que hay en el archivo de airports
    Arcos -> Todas las rutas a->b 
        !Nota: Los arcos representarán si hay una ruta de un AeropuertoA
        a un AeropuertoB, no importará la aerolínea (es decir que no hay
        repetición de rutas áereas)

    Así mismo, se van añadiendo informaciones a la tabla de 
    aeropuertos como lo es connections, inbound, outbound
    """
    aeropuertoSalida=route["Departure"]
    aeropuertoLlegada=route["Destination"]
    peso=float(route["distance_km"])
    addAeropuertoGraf(catalog,aeropuertoSalida,"AeropuertosRutasGraph")
    
    if gr.getEdge(catalog["AeropuertosRutasGraph"],aeropuertoSalida,aeropuertoLlegada) is None:
        gr.addEdge(catalog["AeropuertosRutasGraph"],aeropuertoSalida,aeropuertoLlegada,peso)
        agregarNumeroConexiones(catalog,aeropuertoLlegada,aeropuertoSalida) #se añaden keys a la tabla de aeropuertos


def agregarNumeroConexiones(catalog,aeropuertoLlegada,aeropuertoSalida):
    """
    Se acceden a los aeropuertos (tabla) y se les va sumando connections, inbound, outbound 
    """
    dictLlegada=mp.get(catalog["AeropuertosTabla"],aeropuertoLlegada)["value"]
    dictSalida=mp.get(catalog["AeropuertosTabla"],aeropuertoSalida)["value"]
    dictLlegada["connections"]+=1
    dictSalida["connections"]+=1
    dictLlegada["inbound"]+=1
    dictSalida["outbound"]+=1

def agregarAeropuertosConConexiones(catalog,aeropuertoSalida):
    """
    Va a sumar +1 en el contador de aeropuertos conectados si el aeropuerto
    cuenta con por lo menos una conexión
    Así mismo retorna si el aeropuerto tiene una conexión o no
    """
    dictSalida=mp.get(catalog["AeropuertosTabla"],aeropuertoSalida)["value"]
    if dictSalida["connections"]>0:
        catalog["AeropuertosRutasGraph"]["AeropuertosConConexion"]+=1
        catalog["AeropuertosRutasDoblesGraph"]["AeropuertosConConexion"]+=1
        conectado=True
    else:
        conectado=False
    return conectado


def addRutasNoDirigido(catalog):
    """
    Se construye el grafo no dirigido
    Vértices -> TODOS los aeropuertos que hay en el archivo de airports
    Arcos -> Rutas que funcionen en ambas direcciones a->b y b->a
    """
    numeroAeropuertosConectados(catalog)
    listaAeropuertos=gr.vertices(catalog["AeropuertosRutasGraph"])
    for aeropuertoSalida in lt.iterator(listaAeropuertos): #recorro todos los vértices del grafo
        conectado=agregarAeropuertosConConexiones(catalog,aeropuertoSalida) #compruebo si el aeropuerto tiene conexiones o no
        if conectado:
            adyacentes=gr.adjacents(catalog["AeropuertosRutasGraph"],aeropuertoSalida)
            for aeropuertoLlegada in lt.iterator(adyacentes):#voy a recorrer los adyacentes
                peso=gr.getEdge(catalog["AeropuertosRutasGraph"],aeropuertoLlegada,aeropuertoSalida) 
                rutaDigraphS_L=gr.getEdge(catalog["AeropuertosRutasDoblesGraph"],aeropuertoSalida,aeropuertoLlegada)
                rutaDigraphL_S=gr.getEdge(catalog["AeropuertosRutasDoblesGraph"],aeropuertoLlegada,aeropuertoSalida)
                # print(aeropuertoSalida,aeropuertoLlegada,peso)

                if (peso is not None) and (rutaDigraphS_L is None) and (rutaDigraphL_S is None): #si el camino es bidireccional y aún no existe el arco de a->b y de b-> a se adiciona al digrafo
                    gr.addEdge(catalog["AeropuertosRutasDoblesGraph"],aeropuertoSalida,aeropuertoLlegada,peso["weight"])
               
    #No borrar estos prints porfis
    
    #print(mp.get(catalog["AeropuertosTabla"],"LED"))
    # print("PRUEBA// AEROPUERTOS CONECTADOS: ",catalog["AeropuertosRutasDoblesGraph"]["AeropuertosConConexion"])

    # print("****************gr.edges()****************")
    # for arco in lt.iterator(gr.edges(catalog["AeropuertosRutasDoblesGraph"])):
    #     print(arco)

    # print("\n\n\n\n")

    # keyseta=catalog["AeropuertosRutasDoblesGraph"]["vertices"]["table"]
    # print("****************CON FOR IN****************")
    # n=0
    # for arco in lt.iterator(keyseta):
    #     if arco["key"] is not None and arco["value"]["first"] is not None:
    #         print("\n\n\n",n,arco)
    #     n+=1



####### avance del requerimiento 3

def buscarCiudad(catalog,ciudad):
    """
    Se buscará una ciudad en el catálogo para mostrarle las opciones
    disponibles al usuario. 

    Los retornos de esta función serán:
        ciudadRepetida: Representa si la ciudad es homónima o no
        ciudadLista: Una lista con la/s ciudade/s con este nombre

    El retorno de ciudadRepetida será:
        0: La ciudad no existe
        1: La ciudad existe y no es homónimas
        2: La ciudad es homónima / está repetida
    """
    ciudadRepetida=None
    ciudadLista=None
    if mp.contains(catalog["CiudadesTabla"],ciudad):
        ciudadLista=mp.get(catalog["CiudadesTabla"],ciudad)["value"] #retorna una lista
        if lt.size(ciudadLista)>1:
            ciudadRepetida=2 #El nombre de la ciudad se repite
        else:
            ciudadRepetida=1 #La ciudad existe pero no está repetida

    else:
        ciudadRepetida=0 #La ciudad no existe
        ciudadLista=lt.newList("ARRAY_LIST")
        elemento={"city": "La ciudad no existe",
                "city_ascii":None,
                "lat":None,
                "lng":None,
                "country":None,
                "admin_name":None,
                "capital":None}
        lt.addLast(ciudadLista,elemento)
    
    pos=1
    for ciudadHom in lt.iterator(ciudadLista): #Se agrega una llave para que el usuario pueda escoger la ciudad que desea
        #la cantidad de ciudades máxima que se repiten son 17, por lo tanto esta operación es O(17) = O(K)
        ciudadHom["opcion"]=pos
        pos+=1
    return ciudadRepetida,ciudadLista

def coordenadasCiudad(catalog,ciudad,pos=1):
    """
    Esta función retornará la coordenada de la ciudad escogida
    por el usuario
    """
    #listCiudad=lt.newList("ARRAY_LIST") #lista con solo un elemento para que haya un print bonito en el view
    ciudadLista=mp.get(catalog["CiudadesTabla"],ciudad)["value"]
    ciudadEscogida=lt.getElement(ciudadLista,pos)
    #lt.addLast(listCiudad,ciudadEscogida)
    coordenadaLat=ciudadEscogida["lat"]
    coordenadaLng=ciudadEscogida["lng"]
    return ciudadEscogida,coordenadaLat,coordenadaLng


# Funciones para creacion de datos

# Funciones de consulta

def ultimaCiudadCargada(file):
    pass

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
#FUNCIONES  INFO EN GRAFOS
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
    


