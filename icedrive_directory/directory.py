"""Module for servants implementations."""

from typing import List
import os
import json
import sys
import atexit

import Ice

import IceDrive

class Directory(IceDrive.Directory):
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.childs = {}
        self.files = {}

    def getParent(self, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        if not self.parent:
            raise IceDrive.RootHasNoParent()
        return self.parent

    def getChilds(self, current: Ice.Current = None) -> List[str]:
        return list(self.childs.keys())

    def getChild(self, name: str, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        if name in self.childs:
            return self.childs[name]
        else:
            raise IceDrive.ChildNotExists(childName=name, path=self.getPath())

    def createChild(self, name: str, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        if name not in self.childs:
            child = Directory(name, parent=self)
            self.childs[name] = child
            return child
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
    def __init__(self, adapter):
        self.user_roots = {}
        self.adapter = adapter

        # Directorio para almacenar el estado
        self.state_directory = "state_data"

        # Crear el directorio si no existe
        os.makedirs(self.state_directory, exist_ok=True)

        # Cargar el estado desde un archivo JSON si existe
        self.load_state()

        atexit.register(self.save_state)
    
    def load_state(self):
        state_file_path = os.path.join(self.state_directory, "service_state.json")
        try:
            with open(state_file_path, "r") as json_file:
                state = json.load(json_file)

                # Deserializar los proxies utilizando el comunicador
                self.user_roots = {user: self.communicator.stringToProxy(proxy_str)
                                for user, proxy_str in state["user_roots"].items()}
        except FileNotFoundError:
            pass  # El archivo no existe aún
        except Exception as e:
           pass

    def save_state(self):
        state_file_path = os.path.join(self.state_directory, "service_state.json")
        print(f"Intentando guardar el estado en: {state_file_path}")

        try:
            state = {"user_roots": {user: str(proxy) for user, proxy in self.user_roots.items()}}

            # Cambio aquí: usar modo "w" para sobrescribir
            with open(state_file_path, "w") as json_file:
                json.dump(state, json_file)

            print("Estado guardado exitosamente.")
        except Exception as e:
            print(f"Error al guardar el estado: {e}")
        finally:
            print("Fin del intento de guardar el estado.")

    def getRoot(self, user: str, current=None) -> IceDrive.DirectoryPrx:
        print(f"Intentando obtener el directorio raíz para el usuario: {user}")
        try:
            # Verificar si el proxy ya existe y es válido
            if user in self.user_roots:
                proxy = self.user_roots[user]
                if proxy.ice_isA("::IceDrive::DirectoryPrx"):
                    print("El usuario ya esta creado.")
                    return proxy
                else:
                    print(f"Proxy no válido para el usuario: {user}")

            # Crear un nuevo proxy si no existe
            return self.user_roots.setdefault(
                user,
                IceDrive.DirectoryPrx.uncheckedCast(
                    self.adapter.addWithUUID(Directory(name=f"root_{user}"))
                ),
            )
        except Exception as e:
            print(f"Error al obtener el directorio raíz para el usuario {user}: {e}")