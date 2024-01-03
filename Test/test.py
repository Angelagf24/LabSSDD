import Ice

import os
import sys
import unittest

ruta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_iceDrive = os.path.abspath(os.path.join(ruta_actual, "..", "icedrive_directory"))
sys.path.append(ruta_iceDrive)
import IceDrive

from icedrive_directory.directory import DirectoryService, Directory
from icedrive_directory.persistence import DirectoryPersistence

def test_getRoot_new_user(proxy_str):
    with Ice.initialize(sys.argv) as communicator:
        proxy_service = communicator.stringToProxy(proxy_str)
        directory_service = IceDrive.DirectoryServicePrx.checkedCast(proxy_service)
        new_user = "Angela"
        root_directory_proxy = directory_service.getRoot(new_user)
        print(f"Directorio raíz para {new_user}: {str(root_directory_proxy)}")

def test_createChild(proxy_str):
    with Ice.initialize(sys.argv) as communicator:
        proxy_service = communicator.stringToProxy(proxy_str)
        directory_service = IceDrive.DirectoryServicePrx.checkedCast(proxy_service)
        directory_proxy = directory_service.getRoot("angela")
        new_child_proxy = directory_proxy.createChild("subdirectorio1_angela")
        print(f"Subdirectorio hijo: {str(new_child_proxy)}")

def test_getParent(proxy_str):
    with Ice.initialize(sys.argv) as communicator:
        proxy_service = communicator.stringToProxy(proxy_str)
        directory_service = IceDrive.DirectoryServicePrx.checkedCast(proxy_service)
        user="angela"
        directory_proxy = directory_service.getRoot(user)
        try:
            parent_directory_root_proxy = directory_proxy.getParent()
            print(f"Directorio padre de raíz: {str(parent_directory_root_proxy)}")
        except IceDrive.RootHasNoParent:
            print("El directorio raíz no tiene padre.")

        subdirectory= "subdirectorio_angela"
        subdirectory_proxy = directory_proxy.createChild(subdirectory)
        print(f"Subdirectorio creado: {str(subdirectory_proxy)}")

        parent_subdirectory_proxy = subdirectory_proxy.getParent()
        print(f"Directorio padre de {subdirectory}: {str(parent_subdirectory_proxy)}")

def test_getChilds(proxy_str):
    with Ice.initialize(sys.argv) as communicator:
        proxy_service = communicator.stringToProxy(proxy_str)
        directory_service = IceDrive.DirectoryServicePrx.checkedCast(proxy_service)
        user="angela"
        directory_proxy = directory_service.getRoot(user)
        childs = directory_proxy.getChilds()
        print(f"Subdirectorios de {user}: {childs}")

def test_getChilds_empty(proxy_str):
    with Ice.initialize(sys.argv) as communicator:
        proxy_service = communicator.stringToProxy(proxy_str)
        directory_service = IceDrive.DirectoryServicePrx.checkedCast(proxy_service)
        user="new_user"
        directory_proxy = directory_service.getRoot(user)
        childs = directory_proxy.getChilds()
        print(f"Subdirectorios de {user}: {childs}")

def test_getChild(proxy_str):
    with Ice.initialize(sys.argv) as communicator:
        proxy_service = communicator.stringToProxy(proxy_str)
        directory_service = IceDrive.DirectoryServicePrx.checkedCast(proxy_service)
        user="Angela"
        directory_proxy = directory_service.getRoot(user)
        subdirectory = "subdirectorio1_angela"
        subdirectory_proxy = directory_proxy.getChild(subdirectory)
        print(f"Subdirectorio recuperado {subdirectory}: {str(subdirectory_proxy)}")

def test_removeChild(proxy_str):
    with Ice.initialize(sys.argv) as communicator:
        proxy_service = communicator.stringToProxy(proxy_str)
        directory_service = IceDrive.DirectoryServicePrx.checkedCast(proxy_service)
        user="angela"
        directory_proxy = directory_service.getRoot(user)
        subdirectory = "subdirectorio1_angela"
        directory_proxy.removeChild(subdirectory)
        print(f"Subdirectorio '{subdirectory}' eliminado con éxito")

def test_linkFile(proxy_str):
    with Ice.initialize(sys.argv) as communicator:
        proxy_service = communicator.stringToProxy(proxy_str)
        directory_service = IceDrive.DirectoryServicePrx.checkedCast(proxy_service)
        user="Angela"
        directory_proxy = directory_service.getRoot(user)
        subdirectory = "subdirectorio_Angela"
        subdirectory_proxy = directory_proxy.createChild(subdirectory)
        print(f"Subdirectorio creado: {str(subdirectory_proxy)}")
        subdirectory_proxy.linkFile("archivo1.txt", "12378404388338fehj89jdj02")

def test_unlinkFile_and_getFiles_and_getBlobId(proxy_str):
    with Ice.initialize(sys.argv) as communicator:
        proxy_service = communicator.stringToProxy(proxy_str)
        directory_service = IceDrive.DirectoryServicePrx.checkedCast(proxy_service)
        user="angela"
        directory_proxy = directory_service.getRoot(user)
        subdirectory = "subdirectorio1_angela"
        subdirectory_proxy = directory_proxy.createChild(subdirectory)
        print(f"Subdirectorio creado: {str(subdirectory_proxy)}")
        subsubdirectory_proxy = subdirectory_proxy.createChild("subsubdirectorio1_angela")
        print(f"Subdirectorio creado: {str(subsubdirectory_proxy)}")
        parent_subdirectory_proxy = subdirectory_proxy.getParent()
        print(f"Directorio padre de {subdirectory}: {str(parent_subdirectory_proxy)}")
        subdirectory_proxy.linkFile("archivo1.txt", "blob1")
        subdirectory_proxy.linkFile("archivo2.txt", "blob2")
        files = subdirectory_proxy.getFiles()
        print(f"Archivos en {subdirectory} antes de desvincular: {files}")
        subdirectory_proxy.unlinkFile("archivo2.txt")
        files_borrado = subdirectory_proxy.getFiles()
        print(f"Archivos en {subdirectory} después de desvincular: {files_borrado}")
        archivo = "archivo1.txt"
        blobID = subdirectory_proxy.getBlobId(archivo)
        print(f"El '{archivo}' tiene el BlobID: {blobID}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: script_name.py <proxy>")
        sys.exit(1)
    
    proxy = sys.argv[1]
    
    #test_getRoot_new_user(proxy)
    test_createChild(proxy)
    #test_getParent(proxy)
    #test_getChilds(proxy)
    #test_getChilds_empty(proxy)
    #test_getChild(proxy)
    #test_removeChild(proxy)
    #test_linkFile(proxy)
    #test_unlinkFile_and_getFiles_and_getBlobId(proxy)



