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
            "Aeropuertos":None}
    
    catalog["AeropuertosRutasGraph"]= gr.newGraph(datastructure='ADJ_LIST',
                                              directed=True,
                                              size=93000,
                                              comparefunction=compareString) # maté la comparación
    
    catalog["AeropuertosRutasDoblesGraph"]= gr.newGraph(datastructure='ADJ_LIST',
                                              directed=False,
                                              size=93000,
                                              comparefunction=compareString)
    return catalog
    


# Funciones para agregar informacion al catalogo

def addAeropuerto(catalog,aeropuerto): 
    pass

def addRuta(catalog,ruta):    

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


def addRouteConnection(catalog, route):
    """
    Adiciona una estación como un vertice del grafo
    """
    try:
        if not gr.containsVertex(catalog['AeropuertosRutasGraph'], route):
            gr.insertVertex(catalog['AeropuertosRutasGraph'], route)
        return catalog
    except Exception as exp:
        error.reraise(exp, 'model:addRoute')


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


def connectedComponents(analyzer):
    """
    Calcula los componentes conectados del grafo
    Se utiliza el algoritmo de Kosaraju
    """
    analyzer['components'] = scc.KosarajuSCC(analyzer['connections'])
    return scc.connectedComponents(analyzer['components'])


def totalStops(analyzer):
    """
    Retorna el total de estaciones (vertices) del grafo
    """
    return gr.numVertices(analyzer['connections'])


def totalConnections(analyzer):
    """
    Retorna el total arcos del grafo
    """
    return gr.numEdges(analyzer['connections'])



