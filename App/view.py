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
import prettytable
from prettytable import PrettyTable
from IPython.display import display
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

def printInput(requerimiento,tipo):
    if tipo=="Input":
        print("-"*14 + "Requerimiento "+str(requerimiento)+" " + tipo+"s"+"-"*14)
    elif tipo=="Resultado":
        print("\n"+"-"*12 + "Requerimiento "+str(requerimiento)+" " + tipo+"s"+"-"*12)

def printPrettyTable(lista, keys, field_names, max_width, sample=3, ultimas=False):
    artPretty=PrettyTable(hrules=prettytable.ALL)
    artPretty.field_names=field_names
    artPretty._max_width = max_width

    cont=1

    for elemento in lt.iterator(lista):
        valoresFila=[]
        for key in keys:
            valoresFila.append(elemento[key])
        artPretty.add_row(tuple(valoresFila))
        if cont>=sample:
            break
        cont+=1
    
    if ultimas:
        ultimo_index=lt.size(lista) # aRRAY LIST
        cont2=1
        while cont2<=sample:
            indice=ultimo_index-sample+cont2
            if indice>cont and indice>=0 and lt.size(lista)>=indice:
                elemento=lt.getElement(lista,indice)
                valoresFila=[]
                for key in keys:
                    valoresFila.append(elemento[key])
                artPretty.add_row(valoresFila)
            cont2+=1
    
    print(artPretty)

def printAeropuertos(respuesta):
    keys=["Name","City","Country","IATA", "Latitude","Longitude"]
    fieldNames=["Name","City","Country","IATA", "Latitude","Longitude"]
    maxWidth = {"Name":20,"City":20,"Country":15,"IATA":6,"Latitude":10, "Longitude":10}
    printPrettyTable(respuesta,keys,fieldNames,maxWidth,sample=lt.size(respuesta),ultimas=False)

def printConexiones(respuesta):
    totalAeropuertosConectados=catalog["AeropuertosRutasGraph"]["AeropuertosConConexion"]
    print("\nLa cantidad de aeropuertos que están conectados en el aeropuerto son: "+str(totalAeropuertosConectados))

    print("\nEl top 5 de aeropuertos conectados son: \n")

    keys=["Name","City","Country","IATA","connections", "inbound","outbound"]
    fieldNames=["Name","City","Country","IATA","Connections", "Inbound","Outbound"]
    maxWidth = {"Name":20,"City":20,"Country":15,"IATA":6,"Connections":5, "Inbound":5,"Outbound":5}
    printPrettyTable(respuesta,keys,fieldNames,maxWidth,sample=5,ultimas=False)

###REQ 2###
def printCluster(respuesta,aeropuerto1,aeropuerto2):
    nComponentes=respuesta[0]
    aeropuertosPertenecen=respuesta[1]
    print("El número de componentes fuertemente conectados es: "+str(nComponentes))
    print("Los aeropuertos con código IATA: "+aeropuerto1 +" y "+aeropuerto2 + 
        " pertenecen al mismo componente? : "+aeropuertosPertenecen)

###REQ 3###
def printMenuCiudad(respuesta):
    ciudadRepetida=respuesta[0]
    listaCiudades=respuesta[1]
    sizeCiudades=listaCiudades["size"]

    if ciudadRepetida==0:
        print("El nombre de la ciudad buscada no existe")
    elif ciudadRepetida==1:
        print("La ciudad existe. La información de la ciudad es la siguiente: ")
    elif ciudadRepetida==2:
        print("Hay ",sizeCiudades," ciudades con este nombre.")
        print("La información de las ciudades es la siguiente: ")
        #print("Por favor seleccione la ciudad que desea: ")
    printTablaCiudades(listaCiudades)

def printTablaCiudades(listaCiudadesPrev):
    if "opcion" not in listaCiudadesPrev:
        listaCiudadesPrev["opcion"]=0
    
    if "size" not in listaCiudadesPrev:
        listaCiudades=lt.newList("ARRAY_LIST")
        lt.addLast(listaCiudades,listaCiudadesPrev)
    else:
        if "opcion" not in lt.getElement(listaCiudadesPrev,1):
            for city in lt.iterator(listaCiudadesPrev):
                city["opcion"]=0
            listaCiudades=listaCiudadesPrev
        else:
            listaCiudades=listaCiudadesPrev
    sizeCiudades=listaCiudades["size"]
    keys=["opcion","city","capital","lat","lng", "country"]
    fieldNames=["opcion","city","capital","lat","lng", "country"]
    maxWidth = {"opcion":3,"city": 20,"capital":20,"lat":10,"lng":10,"country":15}
    printPrettyTable(listaCiudades,keys,fieldNames,maxWidth,sample=sizeCiudades,ultimas=False)

def printEscogerCiudad(tipoCiudad):
    inputCiudad="Ingrese el nombre de la ciudad de "+tipoCiudad +":  "
    ciudadOr=input(inputCiudad) #Springfield
    resultadoCiudad=controller.buscarCiudad(catalog,ciudadOr)

    printMenuCiudad(resultadoCiudad)
    ciudadRepetida=resultadoCiudad[0]
    ciudadLista=resultadoCiudad[1]
    if ciudadRepetida>0:
        continuar=True
        if lt.size(ciudadLista)>1:
            posicion=int(input("Escoga que ciudad de "+tipoCiudad+" desea elegir. \nIngrese el número de la ciudad de la columna opción: "))
            ciudadOrigen=controller.coordenadasCiudad(catalog,ciudadOr,posicion)
        else:
            ciudadOrigen=controller.coordenadasCiudad(catalog,ciudadOr,pos=1)
        
        print("Información ciudad "+tipoCiudad+" elegida: \n")
        printTablaCiudades(ciudadOrigen[0])
    else:
        continuar=False
        ciudadOrigen=None
    
    return continuar,ciudadOrigen[1]



def infoCargaCatalogo():
    print("\n"+"*"*50)

    print("*"*10+"Información mapas"+"*"*10)
    print("Total de ciudades con nombre único: ",catalog["CiudadesTabla"]["size"])
    print("Tamaño de mapa AeropuertosTabla: ",catalog["AeropuertosTabla"]["size"])

    print("*"*10+"Información grafos:"+"*"*10)
    #print("--- POR IMPLEMENTAR")
    try:
        vertices=catalog["AeropuertosRutasGraph"]['vertices']["size"]
        arcos=catalog["AeropuertosRutasGraph"]['edges']
        print("Grafo AeropuertosRutasGraph (Dirigido)"+" |Aeropuertos: " +str(vertices)+ " - total de rutas aéreas: "+ str(arcos))
    
    except:
        print("Error al obtener los vértices y/o arcos del grafo: AeropuertosRutasGraph ")

    
    try:
        #print(catalog["AeropuertosRutasDoblesGraph"].keys())
        vertices1=catalog["AeropuertosRutasDoblesGraph"]['vertices']["size"]
        arcos1=catalog["AeropuertosRutasDoblesGraph"]['edges']
        print("Grafo AeropuertosRutasDoblesGraph (No dirigido)"+" |Aeropuertos: " +str(vertices1)+ " - total de rutas aéreas: "+ str(arcos1))
    
    except:
        print("Error al obtener los vértices y/o arcos del grafo: AeropuertosRutasDoblesGraph")
    
    #print(catalog["AeropuertosRutasDoblesGraph"])
    
    print("-"*40)
    print("\n"+"*"*10+"FIN Información mapas y grafos"+"*"*10)
    print("*"*50)

"""
Menu principal
"""
while True:
    printMenu()
    inputs = input('Seleccione una opción para continuar\n')
    
    if inputs!="0" and inputs!="8":
        printInput(inputs,"Input")

    print("\n")
    tiempoInicial=process_time()
    if int(inputs[0]) == 0:
        catalog=controller.initCatalog()

        info=controller.loadServices(catalog)
        infoCargaCatalogo()
        primerosAeropuertosGrafos="FALTA HACER PRETTY TABLE"#info[1]
        ultimaCiudadCargada=info[2]
        aeropuerto=info[1]
        #el primer aeropuerto es cargado a ambos grafos debido a la implementación que hicimos del model
        print("Primer aeropuerto cargado en ambos grafos: \n",primerosAeropuertosGrafos)
        printAeropuertos(aeropuerto)
        print("\nÚltima ciudad cargada a la tabla de simbolos: \n")
        printTablaCiudades(ultimaCiudadCargada)

    elif int(inputs[0]) == 1:
        resultado=controller.puntosInterconexion(catalog)
        printConexiones(resultado)
        display(controller.bonoRequerimiento1(resultado))
        pass

    elif int(inputs[0]) == 2:
        aeropuerto1="LED"#input("Ingrese el código IATA del aeropuerto1: ")
        aeropuerto2="RTP"#input("Ingrese el código IATA del aeropuerto2: ")
        resultado=controller.clustersTrafico(catalog,aeropuerto1,aeropuerto2)
        printCluster(resultado,aeropuerto1,aeropuerto2)
        display(controller.bonoRequerimiento2(catalog,resultado))

    elif int(inputs[0]) == 3:
        infoOrigen=printEscogerCiudad("Origen")
        #print(infoOrigen)
        if infoOrigen[0]:
            infoSalida=printEscogerCiudad("Destino")
            #print(infoSalida)
            aeropuerto1=infoOrigen[1]
            aeropuerto2=infoSalida[1]
            #print(aeropuerto1,aeropuerto2)
            resultado=controller.caminoCorto(catalog,aeropuerto1,aeropuerto2)
        else:
            print("Error en el nombre")
            pass #SE SIGUE IMPLEMENTANDO EL REQ3, Con info origen y infosalida se saben con precisión la info de ambas ciudades

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
