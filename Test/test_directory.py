import Ice
import sys
import os
import json
import time

Ice.loadSlice('../icedrive_directory/icedrive.ice')
import IceDrive

ruta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_DirectoryService = os.path.join(ruta_actual, "..", "icedrive_directory")
sys.path.append(ruta_DirectoryService)
from directory import DirectoryService, Directory

def test_persistence(proxy):
    with Ice.initialize(sys.argv) as communicator:
        proxy_service = communicator.stringToProxy(proxy)
        directory_service = IceDrive.DirectoryServicePrx.checkedCast(proxy_service)

        users = ["usuario1", "usuario2", "usuario3"]

        for user in users:
            root_directory_proxy = directory_service.getRoot(user)
            print(f"Directorio raíz para {user}: {str(root_directory_proxy)}")

def test_get_parent(proxy):
    with Ice.initialize(sys.argv) as communicator:
        proxy_service = communicator.stringToProxy(proxy)
        directory_service = IceDrive.DirectoryServicePrx.checkedCast(proxy_service)

        user = "usuario3"
        root_directory_proxy = directory_service.getRoot(user)
        print(f"Directorio raíz para {user}: {str(root_directory_proxy)}")

        try:
            parent_directory_proxy = root_directory_proxy.getParent()
            print(f"Directorio superior: {str(parent_directory_proxy)}")
        except IceDrive.RootHasNoParent:
            print("El directorio raíz no tiene un directorio superior (nodo raíz).")

def test_get_childs(proxy):
    with Ice.initialize(sys.argv) as communicator:
        proxy_service = communicator.stringToProxy(proxy)
        directory_service = IceDrive.DirectoryServicePrx.checkedCast(proxy_service)

        user = "usuario"
        root_directory_proxy = directory_service.getRoot(user)
        print(f"Directorio raíz para {user}: {str(root_directory_proxy)}")

        try:
            # Crear un subdirectorio
            subdirectory_proxy = root_directory_proxy.createChild("subdirectorio")
            print(f"Subdirectorio creado: {str(subdirectory_proxy)}")

            subdirectory_proxy = root_directory_proxy.createChild("subdirectorio1")
            print(f"Subdirectorio creado: {str(subdirectory_proxy)}")
 
            state_path = "../state_data/service_state.json"
            add_subdirectory_to_state(state_path, user, "subdirectorio", str(subdirectory_proxy))
            add_subdirectory_to_state(state_path, user, "subdirectorio1", str(subdirectory_proxy))

            # Obtener la lista de directorios hijos del directorio raíz
            child_directories = root_directory_proxy.getChilds()
            print(f"Directorios hijos del raíz: {child_directories}")

        except Exception as e:
            print(f"Error: {e}")

def add_subdirectory_to_state(state_path, user, subdirectory_name, subdirectory_proxy):
    try:
        # Cargar el estado actual
        with open(state_path, "r") as json_file:
            state = json.load(json_file)

        # Verificar si el usuario ya existe en el estado
        if user in state["directory_info"]:
            # Verificar si el subdirectorio ya existe
            if subdirectory_name in state["directory_info"][user]["subdirectories"]:
                raise IceDrive.ChildAlreadyExists(childName=subdirectory_name, path=f"root_{user}")

            # Almacenar directamente el identificador del subdirectorio en el estado como cadena
            subdirectory_id = str(subdirectory_proxy)
            state["directory_info"][user]["subdirectories"][subdirectory_name] = subdirectory_id

            # Guardar el estado actualizado
            with open(state_path, "w") as json_file:
                json.dump(state, json_file, indent=2)  # indent para una presentación más legible

        else:
            raise IceDrive.UserNotExist(username=user)

    except Exception as e:
        print(f"Error al agregar subdirectorio para el usuario {user}: {e}")
        raise  # Re-raise the exception after printing the error message


def test_get_child(proxy):
    with Ice.initialize(sys.argv) as communicator:
        proxy_service = communicator.stringToProxy(proxy)
        directory_service = IceDrive.DirectoryServicePrx.checkedCast(proxy_service)

        user = "usuario1"
        root_directory_proxy = directory_service.getRoot(user)
        print(f"Directorio raíz para {user}: {str(root_directory_proxy)}")

        try:
            # Crear un subdirectorio
            subdirectory_proxy = root_directory_proxy.createChild("subdirectorio")
            print(f"Subdirectorio creado: {str(subdirectory_proxy)}")

            state_path = "../state_data/service_state.json"
            add_subdirectory_to_state(state_path, user, "subdirectorio", str(subdirectory_proxy))

            # Obtener un hijo específico por nombre
            retrieved_child = root_directory_proxy.getChild(user)
            print(f"Directorio hijo recuperado: {str(retrieved_child)}")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("Uso: test_directory.py <proxy del servicio>")
        sys.exit(1)
    
    proxy = sys.argv[1]
    #test_persistence(proxy) --> Bien
    #test_get_parent(proxy)  --> Bien
    #test_get_childs(proxy)  --> Bien
    test_get_child(proxy)