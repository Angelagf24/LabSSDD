"""Module for servants implementations."""

from typing import List
import os
import json
from uuid import uuid4
import uuid
import configparser

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
    def __init__(self):
        self.user_roots = {}
        self.proxy_file_path = 'proxy.json'
        self.fixed_identity = str(uuid4())
        self.config_file_path = 'config.json'

        # Cargar la configuración al iniciar el servicio
        self.load_configuration()

        # Cargar el proxy al iniciar el servicio, si existe
        if os.path.exists(self.proxy_file_path):
            self.load_proxy()

    def load_configuration(self):
        self.config_file_path = 'config/config.json'
        if os.path.exists(self.config_file_path):
            with open(self.config_file_path, 'r') as file:
                self.configuration = json.load(file)
        else:
            # Configuración por defecto si el archivo no existe
            self.configuration = {
                'directory': {
                    'state.path': 'default_directory'
                }
            }

    def save_configuration(self):
        with open(self.config_file_path, 'w') as file:
            json.dump(self.configuration, file, indent=2)


    def get_configuration_value(self, section, key, fallback=None):
        return self.configuration.get(section, {}).get(key, fallback)

    def set_configuration_value(self, section, key, value):
        if section not in self.configuration:
            self.configuration[section] = {}
        self.configuration[section][key] = value
        self.save_configuration()

    def getRoot(self, user: str, current=None) -> IceDrive.DirectoryPrx:
        # Verifica si ya existe un directorio raíz para el usuario.
        if user in self.user_roots:
            return self.user_roots[user]
        else:
            # Si no existe, crea uno nuevo y lo asocia al usuario.
            root_directory = Directory(name=f"root_{user}")
            self.user_roots[user] = root_directory

            # Guardar el proxy en un archivo
            self.save_proxy(root_directory, self.fixed_identity)

            return root_directory

    def save_proxy(self, proxy, identity):
        identity_str = Ice.uncheckedCast(identity, Ice.Identity).ice_toString()
        endpoint = proxy.ice_getCommunicator().proxyToString(proxy)

        data = {"identity": identity_str, "endpoint": endpoint}

        with open(self.proxy_file_path, 'w') as file:
            json.dump(data, file)

    def load_proxy(self):
        try:
            with open(self.proxy_file_path, 'r') as file:
                loaded_data = json.load(file)
                identity_str = loaded_data["identity"]
                endpoint = loaded_data["endpoint"]
                identity = Ice.stringToIdentity(identity_str)
                proxy = self.communicator().stringToProxy(f"{identity}:tcp -h {endpoint}")
                # Utiliza el proxy cargado según sea necesario
        except (ValueError, KeyError) as e:
            print(f"Error al cargar el proxy: {e}")
        