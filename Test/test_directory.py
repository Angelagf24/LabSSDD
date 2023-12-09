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

def test_persistence1(proxy):
    with Ice.initialize(sys.argv) as communicator:
        proxy_service = communicator.stringToProxy(proxy)
        directory_service = IceDrive.DirectoryServicePrx.checkedCast(proxy_service)

        users = ["usuario1", "usuario2", "usuario3"]

        for user in users:
            root_directory_proxy = directory_service.getRoot(user)
            print(f"Directorio raíz para {user}: {str(root_directory_proxy)}")

def test_persistence(proxy):
    with Ice.initialize(sys.argv) as communicator:
        proxy_service = communicator.stringToProxy(proxy)
        directory_service = IceDrive.DirectoryServicePrx.checkedCast(proxy_service)

        users = ["usuario1", "usuario2", "usuario3"]

        for user in users:
            root_directory_proxy = directory_service.getRoot(user)

            # Crear subdirectorio y archivos enlazados
            subdirectory_proxy = root_directory_proxy.createChild("subdirectorio")
            """root_directory_proxy.linkFile("archivo1.txt", "blob1")
            subdirectory_proxy.linkFile("archivo2.txt", "blob2")

            # Recuperar el directorio después de la persistencia
            recovered_root_directory_proxy = directory_service.getRoot(user)

            # Verificar la persistencia de subdirectorios
            subdirectories = recovered_root_directory_proxy.getChilds()
            assert "subdirectorio" in subdirectories
            print(f"Persistencia exitosa de subdirectorios para el usuario {user}")

            # Verificar la persistencia de archivos enlazados
            files = recovered_root_directory_proxy.getFiles()
            assert "archivo1.txt" in files
            print(f"Persistencia exitosa de subdirectorios para el usuario {user}")

            # Recuperar el subdirectorio después de la persistencia
            recovered_subdirectory_proxy = recovered_root_directory_proxy.getChild("subdirectorio")

            # Verificar la persistencia de archivos en subdirectorios
            subdirectory_files = recovered_subdirectory_proxy.getFiles()
            assert "archivo2.txt" in subdirectory_files
            print(f"Persistencia exitosa de subdirectorios para el usuario {user}")

            print(f"Prueba de persistencia exitosa para el usuario {user}")"""

def test_persistence2(proxy):
    with Ice.initialize(sys.argv) as communicator:
        proxy_service = communicator.stringToProxy(proxy)
        directory_service = IceDrive.DirectoryServicePrx.checkedCast(proxy_service)

        user = "usuario1"
        root_directory_proxy = directory_service.getRoot(user)

        # Crear subdirectorio y archivos enlazados
        subdirectory = "subdirectorio1_usuario1"
        subdirectory_proxy = root_directory_proxy.createChild(subdirectory)
        print(f"Subdirectorio creado: {str(subdirectory_proxy)}")
        subdirectory_proxy.linkFile("archivo1.txt", "blob1")
        subdirectory_proxy.linkFile("archivo2.txt", "blob2")
        files = subdirectory_proxy.getFiles()
        print(f"Archivos del {user} : {files}")

        subdirectorio = subdirectory_proxy.getChild(subdirectory)
        print(f"Subdirectorio de {user}: {subdirectorio}")

        # Recuperar el directorio después de la persistencia
        recovered_root_directory_proxy = directory_service.getRoot(user)

        # Verificar la persistencia de subdirectorios
        subdirectories = recovered_root_directory_proxy.getChilds()
        print(f"Directorios hijos del raíz: {subdirectories}")


if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("Uso: test_directory.py <proxy del servicio>")
        sys.exit(1)
    
    proxy = sys.argv[1]
    test_persistence2(proxy)
