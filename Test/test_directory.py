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
        """user1 = "usuario_nuevo"
        root_directory_proxy2 = directory_service.getRoot(user1)
        print(f"Directorio raíz para {user1}: {root_directory_proxy2}")"""

        existing_user = "usuario_existente"

        # Obtener el directorio raíz para el usuario existente
        root_directory_proxy = directory_service.getRoot(existing_user)
        if root_directory_proxy:
            print(f"Directorio raíz para {existing_user}: {str(root_directory_proxy)}")
        else:
            print(f"No se encontró el directorio raíz para {existing_user}")

        existing_user2 = "usuario_existente2"

        # Obtener el directorio raíz para el usuario existente
        root_directory_proxy1 = directory_service.getRoot(existing_user2)
        if root_directory_proxy:
            print(f"Directorio raíz para {existing_user2}: {str(root_directory_proxy1)}")
        else:
            print(f"No se encontró el directorio raíz para {existing_user2}")


if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("Uso: test_directory.py <proxy del servicio>")
        sys.exit(1)
    
    proxy = sys.argv[1]
    test_directory_service(proxy)