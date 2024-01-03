import Ice
import sys

import IceDrive

from icedrive_directory.persistence import DirectoryPersistence
from icedrive_directory.directory import Directory, DirectoryService

def test_persistence_get_Root(proxy):
    with Ice.initialize(sys.argv) as communicator:
        proxy_service = communicator.stringToProxy(proxy)
        directory_service = IceDrive.DirectoryServicePrx.checkedCast(proxy_service)

        users = ["usuario1", "usuario2", "usuario3"]

        for user in users:
            root_directory_proxy = directory_service.getRoot(user)
            print(f"Directorio raíz para {user}: {str(root_directory_proxy)}")

def test_persistence_subdirectorios(proxy):
    with Ice.initialize(sys.argv) as communicator:
        proxy_service = communicator.stringToProxy(proxy)
        directory_service = IceDrive.DirectoryServicePrx.checkedCast(proxy_service)

        user = "usuario1"
        root_directory_proxy = directory_service.getRoot(user)
        print(f"Directorio raíz para {user}: {str(root_directory_proxy)}")

        # Crear subdirectorio y archivos enlazados
        subdirectory = f"subdirectorio1_{user}"
        subdirectory_proxy = root_directory_proxy.createChild(subdirectory)
        print(f"Subdirectorio creado: {str(subdirectory_proxy)}")
        subdirectory_proxy.linkFile("archivo1.txt", "blob1")
        subdirectory_proxy.linkFile("archivo2.txt", "blob2")

        files = subdirectory_proxy.getFiles()
        print(f"Archivos en {subdirectory}: {files}")

        archivo = "archivo1.txt"
        blobID = subdirectory_proxy.getBlobId(archivo)
        print(f"El '{archivo}' tiene el BlobID: {blobID}")

        # Verificar la persistencia de subdirectorios
        subdirectories = root_directory_proxy.getChilds()
        print(f"Subdirectorios en raíz: {subdirectories}")

        subdirectorio = root_directory_proxy.getChild(subdirectory)
        print(f"Subdirectorio recuperado: {subdirectorio}")

def test_persistence_borrado(proxy):
    with Ice.initialize(sys.argv) as communicator:
        proxy_service = communicator.stringToProxy(proxy)
        directory_service = IceDrive.DirectoryServicePrx.checkedCast(proxy_service)

        user = "usuario1"
        root_directory_proxy = directory_service.getRoot(user)
        print(f"Directorio raíz para {user}: {str(root_directory_proxy)}")

        subdirectory = f"subdirectorio1_{user}"
        root_directory_proxy.removeChild(subdirectory)
        print(f"Subdirectorio '{subdirectory}' eliminado con éxito")


def test_persistence_unLink(proxy):
    with Ice.initialize(sys.argv) as communicator:
        proxy_service = communicator.stringToProxy(proxy)
        directory_service = IceDrive.DirectoryServicePrx.checkedCast(proxy_service)

        user = "usuario1"
        root_directory_proxy = directory_service.getRoot(user)
        print(f"Directorio raíz para {user}: {str(root_directory_proxy)}")

        subdirectory = f"subdirectorio1_{user}"
        subdirectory_proxy = root_directory_proxy.createChild(subdirectory)
        print(f"Subdirectorio creado: {str(subdirectory_proxy)}")
        subdirectory_proxy.linkFile("archivo1.txt", "blob1")
        subdirectory_proxy.linkFile("archivo2.txt", "blob2")

        subdirectory_proxy.unlinkFile("archivo1.txt")
        files = subdirectory_proxy.getFiles()
        print(f"Archivos en {subdirectory} después de desvincular: {files}")

def test_persistence_getParent(proxy):
    with Ice.initialize(sys.argv) as communicator:
        proxy_service = communicator.stringToProxy(proxy)
        directory_service = IceDrive.DirectoryServicePrx.checkedCast(proxy_service)

        user = "usuario1"
        root_directory_proxy = directory_service.getRoot(user)
        print(f"Directorio raíz para {user}: {str(root_directory_proxy)}")

        try:
            parent_directory_root_proxy = root_directory_proxy.getParent()
            print(f"Directorio padre de raíz: {str(parent_directory_root_proxy)}")
        except IceDrive.RootHasNoParent:
            print("El directorio raíz no tiene padre.")

        subdirectory = f"subdirectorio1_{user}"
        subdirectory_proxy = root_directory_proxy.createChild(subdirectory)
        print(f"Subdirectorio creado: {str(subdirectory_proxy)}")

        parent_subdirectory_proxy = subdirectory_proxy.getParent()
        print(f"Directorio padre de {subdirectory}: {str(parent_subdirectory_proxy)}")


#if __name__ == '__main__':
def main():

    if len(sys.argv) < 2:
        print("Uso: test_directory.py <proxy del servicio>")
        sys.exit(1)
    
    proxy = sys.argv[1]
    #test_persistence_get_Root(proxy)
    #test_persistence_subdirectorios(proxy)
    #test_persistence_borrado(proxy)
    #test_persistence_unLink(proxy)
    #test_persistence_getParent(proxy)

