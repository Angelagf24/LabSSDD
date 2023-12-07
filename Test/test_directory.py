import Ice
import sys
import os

Ice.loadSlice('../icedrive_directory/icedrive.ice')
import IceDrive

ruta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_DirectoryService = os.path.join(ruta_actual, "..", "icedrive_directory")
sys.path.append(ruta_DirectoryService)
from directory import DirectoryService, Directory

def test_directory_service(proxy):
    with Ice.initialize(sys.argv) as communicator:
        proxy_service = communicator.stringToProxy(proxy)

        # Crear una instancia de DirectoryService
        directory_service = IceDrive.DirectoryServicePrx.checkedCast(proxy_service)

        # Caso 1: Obtener directorio raíz para un usuario que nunca lo ha solicitado anteriormente
        """user1 = "usuario1"
        root_directory_proxy1 = directory_service.getRoot(user1)
        print(f"Directorio raíz para {user1}: {root_directory_proxy1}")

        user2= "usuario2"
        root_directory_proxy2 = directory_service.getRoot(user2)
        print(f"Directorio raíz para {user2}: {str(root_directory_proxy2)}")"""

        user3 = "usuario3"
        root_directory_proxy3 = directory_service.getRoot(user3)
        print(f"Directorio raíz para {user3}: {str(root_directory_proxy3)}")


if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("Uso: test_directory.py <proxy del servicio>")
        sys.exit(1)
    
    proxy = sys.argv[1]
    test_directory_service(proxy)