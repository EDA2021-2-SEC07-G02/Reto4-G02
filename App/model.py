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


from DISClib.DataStructures.arraylist import addLast
import config as cf
import folium
from DISClib.ADT.graph import gr
from DISClib.ADT import list as lt
from DISClib.ADT import map as mp
from DISClib.DataStructures import mapentry as me
from DISClib.ADT import orderedmap as om
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.Algorithms.Trees import traversal as traversal
from DISClib.Utils import error as error
from math import radians, cos, sin, asin, sqrt
assert cf



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

    catalog["NumeroConexionesArbol"]=om.newMap(omaptype='RBT',
                                   comparefunction=compareNConexiones)

    catalog["RankingConexiones"]=lt.newList("ARRAY_LIST")              

    return catalog
    


# -----------------------------------------------------------
# AGREGAR INFORMACIÓN AL CATÁLOGO
# -----------------------------------------------------------

def addCity(catalog,ciudad):
    """
    Añade una ciudad a la tabla de simbolos de ciudades
    """
    cityAscii=ciudad["city_ascii"]
    keyCity=(cityAscii).strip()
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


# -----------------------------------------------------------
# Construcción arcos en grafos (añadiendo rutas aéreas)
# -----------------------------------------------------------

def addRutasGraphDirigido(catalog,route):
    """
    Se añaden TODAS las rutas al grafo dirigido.
    Vértices -> TODOS los aeropuertos que hay en el archivo de airports
    Arcos -> Todas las rutas a->b 
        !Nota: Los arcos representarán si hay una ruta de un AeropuertoA
        a un AeropuertoB, así mismo se tiene un identificador de Aerolínea

    Así mismo, se van añadiendo informaciones a la tabla de 
    aeropuertos como lo es connections, inbound, outbound
    """
    aeropuertoSalida=route["Departure"]
    aeropuertoLlegada=route["Destination"]
    peso=float(route["distance_km"])
    linea=route["Airline"]
    addAeropuertoGraf(catalog,aeropuertoSalida,"AeropuertosRutasGraph")
    agregarNumeroConexiones(catalog,aeropuertoLlegada,aeropuertoSalida) #se añaden keys a la tabla de aeropuertos
    gr.addEdgeLinea(catalog["AeropuertosRutasGraph"],aeropuertoSalida,aeropuertoLlegada,peso,linea)

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
            adyacentes=gr.adjacentEdges(catalog["AeropuertosRutasGraph"],aeropuertoSalida)#gr.adjacents(catalog["AeropuertosRutasGraph"],aeropuertoSalida)
            for aeropuertoLlegadaEdge in lt.iterator(adyacentes):#voy a recorrer los adyacentes
                aeropuertoLlegada=aeropuertoLlegadaEdge["vertexB"]
                linea=aeropuertoLlegadaEdge["lineaA"] #obtengo la línea aérea
                peso=gr.getEdgeLinea(catalog["AeropuertosRutasGraph"],aeropuertoLlegada,aeropuertoSalida,linea) 
                rutaDigraphS_L=gr.getEdgeLinea(catalog["AeropuertosRutasDoblesGraph"],aeropuertoSalida,aeropuertoLlegada,linea)
                rutaDigraphL_S=gr.getEdgeLinea(catalog["AeropuertosRutasDoblesGraph"],aeropuertoLlegada,aeropuertoSalida,linea)
                # print(aeropuertoSalida,aeropuertoLlegada,peso)

                if (peso is not None) and (rutaDigraphS_L is None) and (rutaDigraphL_S is None): #si el camino es bidireccional y aún no existe el arco de a->b y de b-> a se adiciona al grafo no dirigido
                    gr.addEdgeLinea(catalog["AeropuertosRutasDoblesGraph"],aeropuertoSalida,aeropuertoLlegada,peso["weight"],linea)
               
    
    
def pruebasGrafos(catalog): #BORRAR DESPUÉS!!!!!!!!!
    
    print(mp.get(catalog["AeropuertosTabla"],"LED"))
    print("PRUEBA// AEROPUERTOS CONECTADOS: ",catalog["AeropuertosRutasDoblesGraph"]["AeropuertosConConexion"])

    print("****************gr.edges()****************")
    for arco in lt.iterator(gr.edges(catalog["AeropuertosRutasDoblesGraph"])):
        print(arco)

    print("\n\n\n\n")

    keyseta=catalog["AeropuertosRutasDoblesGraph"]["vertices"]["table"]
    print("****************CON FOR IN****************")
    n=0
    for arco in lt.iterator(keyseta):
        if arco["key"] is not None and arco["value"]["first"] is not None:
            print("\n\n\n",n,arco)
        n+=1
    pass



def arbolNConexiones(catalog):
    infoAeropuertos=mp.valueSet(catalog["AeropuertosTabla"])
    for infoAeropuerto in lt.iterator(infoAeropuertos):
        conexiones=infoAeropuerto["connections"] #Número entero
        if conexiones>0: #El árbol quedará solamente con áeropuertos que tengan más de una ruta
            IATA=infoAeropuerto['IATA']
            if om.contains(catalog['NumeroConexionesArbol'],conexiones):
                lt.addLast(om.get(catalog['NumeroConexionesArbol'],conexiones)["value"],IATA)
            else:
                lista=lt.newList("ARRAY_LIST")
                lt.addLast(lista,IATA)
                om.put(catalog['NumeroConexionesArbol'],conexiones,lista)

    catalog["RankingConexiones"]=inorderRanking(catalog['NumeroConexionesArbol'])
    print("TAMAÑO ÁRBOL: ", om.size(catalog['NumeroConexionesArbol']))

def grafoCiudadesAeropuerto():
    """
    Este grafo funcionará para conocer la conexión entre 
    ciudades.

    Los identificadores de los vértices serán:
         " idciudad - IATA (aeropuerto)"
    Los arcos de las conexiones tendrán como peso la distancia
    calculada con la fórmula de haversine

    El grafo es dirigido
    """
    pass

def identificadorCiudadAeropuerto(aeropuerto,ciudad):
    """
    Nombre del vertex
    """

    return aeropuerto + " - " + ciudad

# -----------------------------------------------------------
# REQUERIMIENTOS
# -----------------------------------------------------------

# --------REQ1--------------
def puntosInterconexion(catalog,sample=5):
    """
    Retorna los 5 primeros aeropuertos con mayor conectividad
    Parámetros:
        catalog: carga de datos
        sample (opcional): ranking de los aeropuertos de mayor 
        a menor conectividad (por defecto son 5)
    """
    sizeRanking=lt.size(catalog["RankingConexiones"])
    listaRespuesta=lt.newList("ARRAY_LIST")
    i=sizeRanking
    while listaRespuesta["size"]<sample:
        ranking=lt.getElement(catalog["RankingConexiones"],i)
        for aeropuerto in lt.iterator(ranking["value"]):
            infoAeropuerto=mp.get(catalog["AeropuertosTabla"],aeropuerto)["value"]
            lt.addLast(listaRespuesta,infoAeropuerto)
            if lt.size(listaRespuesta)>=sample:
                break
        i-=1
    return listaRespuesta



# --------REQ2--------------

def clustersTrafico(catalog,aeropuerto1,aeropuerto2):
    sccClusters=scc.KosarajuSCC(catalog["AeropuertosRutasGraph"])
    aeropuertosPertenecen=scc.stronglyConnected(sccClusters,aeropuerto1,aeropuerto2)
    componentesConectados=sccClusters["components"]
    if aeropuertosPertenecen:
        strAeropuertosPertenecen="SÍ"
    else:
        strAeropuertosPertenecen="NO"
    return componentesConectados,strAeropuertosPertenecen,sccClusters,aeropuerto1,aeropuerto2


# --------REQ3--------------

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
    ciudadLista=mp.get(catalog["CiudadesTabla"],ciudad)["value"]
    ciudadEscogida=lt.getElement(ciudadLista,pos)
    coordenadaLat=ciudadEscogida["lat"]
    coordenadaLng=ciudadEscogida["lng"]
    return ciudadEscogida,coordenadaLat,coordenadaLng



def haversine(lon1, lat1, lon2, lat2):
    """
    Esta función se utiliza para hacer los arcos del 
    grafo de ciudades

    #CÓDIGO DE: @Michael Dunn
    #https://stackoverflow.com/questions/4913349/haversine-formula-
    # in-python-bearing-and-distance-between-two-gps-points
    _________
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r

# Funciones para creacion de datos

# Funciones de consulta

# -----------------------------------------------------------
# Controller para ver primer y último item cargado
# -----------------------------------------------------------

def primerItem(file):
    """
    Obtiene el primer item de un archivo y lo agrega
    a una lista
    """
    rtaLista=lt.newList("ARRAY_LIST")
    for item in file:
        print(item)
        addLast(rtaLista,item)
        if lt.size(rtaLista)>=1:
            break
    print("PRIMERFUNCION",rtaLista)
    return rtaLista

def agregarItem(rtaLista,item):
    lt.addLast(rtaLista,item)
    return rtaLista

def verPrimerosYUltimos(item1,item2):
    rtaLista=lt.newList("ARRAY_LIST")
    lt.addLast(rtaLista,item1)
    lt.addLast(rtaLista,item2)
    return rtaLista


# -----------------------------------------------------------
# Funciones utilizadas para comparar elementos
# -----------------------------------------------------------


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

def compareNConexiones(numero1,numero2):
    """
    Compara el número de dos conexiones (ej 5 vs 10)
    """
    if (numero1 == numero2):
        return 0
    elif (numero1 > numero2):
        return 1
    else:
        return -1




# -----------------------------------------------------------
# Funciones view:
# -> Funciones información en grafos
# -> características específicas de cada uno de los grafos definidos
# -> primer y último aeropuerto cargado
# -> primera y última ciudad cargada
# -----------------------------------------------------------

def primerYUltimoElemento(file):
    pass

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

# -----------------------------------------------------------
# BONO GRÁFICAS
# -----------------------------------------------------------   

def bonoRequerimiento1(resultado):
    mapgraf=folium.Map(location=[0,0],zoom_start=1) #Se crea el mapa
    puestoAeropuerto=1
    for aeropuerto in lt.iterator(resultado):
        latitud=aeropuerto["Latitude"]
        longitud=aeropuerto["Longitude"]
        IATA=aeropuerto["IATA"]
        conexiones=aeropuerto["connections"]
        ciudadPais=aeropuerto["City"] +", "+aeropuerto["Country"]
        nAeropuerto="Place #"+str(puestoAeropuerto) + " - " + IATA
        infoPopUp=str("<br><b>"+nAeropuerto+ "&nbsp"+ "</b>"
                            + "<br><b> #Conexiones: </b> "+conexiones
                            + "<br><b> Código IATA: </b> "+IATA
                            + "<br><b> Ciudad, País: </b>"+ciudadPais)
        infoHTML=folium.Html(infoPopUp,script=True)
        (folium.Marker(location=[latitud, longitud], popup=folium.Popup(infoHTML, parse_html=False),
                        icon=folium.Icon(color="darkpurple"),tooltip=nAeropuerto)).add_to(mapgraf)
        puestoAeropuerto+=1

    return mapgraf

def bonoRequerimiento2(catalog,resultado):
    mapgraf=folium.Map(location=[0,0],zoom_start=1) #Se crea el mapa
    infoGraf=masInfoGraf(catalog,resultado) #return info1,info2,componentesInfo1,componentesInfo2
    info1,info2,componentesInfo1,componentesInfo2=infoGraf
    markersReq2(mapgraf,componentesInfo1,info1, "darkblue","lightblue")
    markersReq2(mapgraf,componentesInfo2,info2,"darkgreen","lightgreen")
    return mapgraf

def markersReq2(mapgraf, componente,infon,colorComponente, colorIATA):
    IATAn=infon["IATA"]
    #-> Limpiar código después
    # for aeropuerto in componente:
    #     toolTip="Componentes del aeropuerto: "+IATAn
    #     latitud=aeropuerto["Latitude"]
    #     longitud=aeropuerto["Longitude"]
    #     IATA=aeropuerto["IATA"]
    #     infoPorIata=str("<br><b>"+str(toolTip)+ "</b>"
    #                     +"<br><b>Código IATA </b>"+IATA)
    #     (folium.Marker(location=[latitud, longitud], popup=folium.Popup(infoPorIata, parse_html=False),
    #                     icon=folium.Icon(color=colorComponente),tooltip=toolTip)).add_to(mapgraf)
    
    (folium.Marker(location=[infon["Latitude"], infon["Longitude"]], 
                    popup=folium.Popup(str("<br><b> AEROPUERTO: "+IATAn+ "</b>"+
                    " <br><b> Componentes conectados:  #"+str(componente["value"])+ "</b>"), parse_html=False),
                        icon=folium.Icon(color=colorIATA),tooltip=str("!!!AEROPUERTO ESCOGIDO:"+IATAn))).add_to(mapgraf)
    return mapgraf

def masInfoGraf(catalog,resultado):
    sccClusters=resultado[2]
    aeropuerto1=resultado[3]
    aeropuerto2=resultado[4]
    info1=mp.get(catalog["AeropuertosTabla"],aeropuerto1)["value"]
    info2=mp.get(catalog["AeropuertosTabla"],aeropuerto2)["value"]
    componentes1= mp.get(sccClusters['idscc'], aeropuerto1)
    componentes2=mp.get(sccClusters['idscc'], aeropuerto2)
    componentesInfo1=componentes1#infoAeropuertos(catalog,componentes1)
    componentesInfo2=componentes2#infoAeropuertos(catalog,componentes2)
    return info1,info2,componentesInfo1,componentesInfo2

# def infoAeropuertos(catalog,lista):
#     """
#     Devuelve la información de todos los códigos IATA en una lista
#     """
#     infoLista=lt.newList("ARRAY_LIST")
#     for aeropuerto in lista:
#         elemento=mp.get(catalog["AeropuertosTabla"],aeropuerto)
#         lt.addLast(infoLista,elemento)
#     return infoAeropuertos

# -----------------------------------------------------------
# Funciones complementarias y editadas de la DISClib para árboles
# -----------------------------------------------------------

def inorderRanking(omap):
    """
    Funciones de inorder editadas

    Implementa un recorrido inorder.
    Se guardan los elementos en una array list
    para acceder a posiciones en tiempos O(1)
    """
    lst = lt.newList('ARRAY_LIST', omap['cmpfunction'])
    if (omap is not None):
        lst = inorderTree(omap['root'], lst)
    return lst


def inorderTree(root, lst):
    """
    Se agrega <Key, Value> a la lista de inorder
    """
    if (root is None):
        return None
    else:
        inorderTree(root['left'], lst)
        lt.addLast(lst, root)
        inorderTree(root['right'], lst)
    return lst

