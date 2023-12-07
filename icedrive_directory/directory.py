"""Module for servants implementations."""

from typing import List
import os
import json
import sys
import atexit

import Ice

import IceDrive

class Directory(IceDrive.Directory):
    def __init__(self, name, parent=None, adapter=None):
        self.name = name
        self.parent = parent
        self.childs = {}
        self.files = {}
        self.adapter = adapter

    def getParent(self, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        if not self.parent:
            raise IceDrive.RootHasNoParent()
        return self.parent

    def getChilds(self, current: Ice.Current = None) -> List[str]:
        return list(self.childs.keys())

    def getChild(self, name: str, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        if name in self.childs:
            proxy = IceDrive.DirectoryPrx.checkedCast(self.childs[name])
            return proxy
        else:
            raise IceDrive.ChildNotExists(childName=name)

    def createChild(self, name: str, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        if name not in self.childs:
            child = Directory(name, parent=self)
            self.childs[name] = child
            return IceDrive.DirectoryPrx.checkedCast(self.adapter.addWithUUID(child))
        else:
            raise IceDrive.ChildAlreadyExists(childName=name, path=self.getPath())

    def removeChild(self, name: str, current: Ice.Current = None) -> None:
        if name in self.childs:
            del self.childs[name]
        else:
            raise IceDrive.ChildNotExists(childName=name, path=self.getPath())

    def getFiles(self, current: Ice.Current = None) -> List[str]:
        return list(self.files.keys())

    def getBlobId(self, filename: str, current: Ice.Current = None) -> str:
        if filename in self.files:
            return self.files[filename]
        else:
            raise IceDrive.FileNotFound(filename=filename)

    def linkFile(self, filename: str, blob_id: str, current: Ice.Current = None) -> None:
        if filename not in self.files:
            self.files[filename] = blob_id
        else:
            raise IceDrive.FileAlreadyExists(filename=filename)

    def unlinkFile(self, filename: str, current: Ice.Current = None) -> None:
        if filename in self.files:
            del self.files[filename]
        else:
            raise IceDrive.FileNotFound(filename=filename)

    def getPath(self, current: Ice.Current = None) -> str:
        path = []
        current_dir = self
        while current_dir:
            path.insert(0, current_dir.name)
            current_dir = current_dir.parent
        return "/".join(path)

#Persistencia con JSON
class DirectoryService(IceDrive.DirectoryService):
    def __init__(self, adapter, communicator):
        self.directory_info = {}
        self.adapter = adapter
        self.communicator = communicator

        # Directorio para almacenar el estado
        self.state_directory = "state_data"

        # Crear el directorio si no existe
        os.makedirs(self.state_directory, exist_ok=True)

        self.load_state()

    def save_state(self):
        state_file_path = os.path.join(self.state_directory, "service_state.json")
        print(f"Intentando guardar el estado en: {state_file_path}")

        try:
            state = {"directory_info": self.directory_info}

            with open(state_file_path, "w") as json_file:
                json.dump(state, json_file)

            print("Estado guardado exitosamente.")
        except Exception as e:
            print(f"Error al guardar el estado: {e}")
        finally:
            print("Fin del intento de guardar el estado.")

    def load_state(self):
        state_file_path = os.path.join(self.state_directory, "service_state.json")
        try:
            with open(state_file_path, "r") as json_file:
                state = json.load(json_file)

                # Limpiar directory_info antes de cargar
                self.directory_info.clear()

                # Actualizar directory_info con los nuevos datos
                self.directory_info.update(state.get("directory_info", {}))
        except FileNotFoundError:
            pass
        except Exception as e:
            pass

    def getRoot(self, user: str, current=None) -> IceDrive.DirectoryPrx:
        print(f"Intentando obtener el directorio raíz para el usuario: {user}")
        try:
            # Verificar si la dirección del proxy ya existe
            if user in self.directory_info:
                root_proxy = self.directory_info[user]["root"]
                try:
                    # Utilizar ice_invokeAsync para limitar el tiempo de espera
                    async_result = self.communicator.stringToProxyAsync(root_proxy)
                    proxy = async_result.waitForResult(2000)  # Esperar máximo 2 segundos

                    if proxy and proxy.ice_isA("::IceDrive::DirectoryPrx"):
                        print(f"El usuario {user} ya existe. Estado actual de self.directory_info: {self.directory_info}")
                        return proxy
                    else:
                        print(f"Proxy no válido para el usuario: {user}")
                except Exception as e:
                    del self.directory_info[user]
                    pass

            # Crear un nuevo proxy si no existe
            new_proxy = IceDrive.DirectoryPrx.uncheckedCast(
                self.adapter.addWithUUID(Directory(name=f"root_{user}", adapter=self.adapter))
            )

            # Almacenar la dirección del proxy y la información del subdirectorio
            self.directory_info[user] = {"root": str(new_proxy), "subdirectories": {}}

            # Guardar el estado actualizado
            self.save_state()

            print(f"Nuevo proxy creado para el usuario {user}. Estado actual de self.directory_info: {self.directory_info}")

            return new_proxy

        except Exception as e:
            print(f"Error al obtener el directorio raíz para el usuario {user}: {e}")
