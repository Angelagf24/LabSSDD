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


if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("Uso: test_directory.py <proxy del servicio>")
        sys.exit(1)
    
    proxy = sys.argv[1]
    test_persistence(proxy)
