import Ice
import sys
import os

Ice.loadSlice('../icedrive_directory/icedrive.ice')
import IceDrive

sys.path.append('../icedrive_directory')
from directory import DirectoryService, Directory

def test_directory_service(proxy):
    with Ice.initialize(sys.argv) as communicator:
        proxy_service = communicator.stringToProxy(proxy)
        directory_service = IceDrive.DirectoryServicePrx.checkedCast(proxy_service)

        if directory_service:
            try:
                user_root = directory_service.getRoot("usuario_prueba")
                root = IceDrive.DirectoryPrx.checkedCast(user_root)

                # Imprimir la ruta del directorio raíz
                print(root.getPath())
            except Exception as e:
                print(f"Error durante las pruebas: {e}")
        else:
            print("Error: No se pudo obtener el servicio de directorio.")

def tearDown(self):
    # Limpia después de las pruebas
    self.communicator.destroy()

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("Uso: test_directory.py <proxy del servicio>")
        sys.exit(1)
    
    proxy = sys.argv[1]
    test_directory_service(proxy)