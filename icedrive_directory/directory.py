"""Module for servants implementations."""

from typing import List
import os
import json
import sys
import uuid

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


#Persistencia con JSON
class DirectoryService(IceDrive.DirectoryService):
    def __init__(self, adapter, communicator):
        self.directories = {}
        self.adapter = adapter
        self.communicator = communicator

        # Verificar si el archivo existe antes de cargar su contenido
        file_path = 'directory_info.json'
        if not os.path.exists(file_path):
            # Si el archivo no existe, crea un diccionario vacío y guarda el archivo
            directory_info = {'directory_info': {}}
            with open(file_path, 'w') as file:
                json.dump(directory_info, file, indent=2)

    def getRoot(self, user, current=None):
        user_uuid = self.get_user_uuid(user)

        # Verificar si el usuario ya tiene un directorio asignado
        if user in self.directories:
            print(f"El usuario '{user}' ya tiene un directorio asignado.")
            return self.directories[user]

        # Verificar si el usuario ya tiene un directorio registrado en el archivo JSON
        file_path = 'directory_info.json'
        with open(file_path, 'r') as file:
            directory_info = json.load(file)

        if user in directory_info['directory_info']:
            # Si el usuario ya tiene un directorio registrado, recuperar el proxy y almacenarlo en la caché
            stored_proxy_str = directory_info['directory_info'][user]['root']
            stored_proxy = IceDrive.DirectoryPrx.uncheckedCast(self.communicator.stringToProxy(stored_proxy_str))
            self.directories[user] = stored_proxy
            print(f"El usuario '{user}' ya tiene un directorio registrado en el archivo JSON.")
            return stored_proxy

        # Si el usuario no tiene un directorio registrado, crear uno nuevo
        directory_name = f"root_{user_uuid}"
        new_proxy = IceDrive.DirectoryPrx.uncheckedCast(
            self.adapter.addWithUUID(Directory(name=directory_name, adapter=self.adapter))
        )

        self.directories[user] = new_proxy
        self.persist_directory_info(user, new_proxy)

        return new_proxy

    def get_user_uuid(self, user):
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, user))

    def persist_directory_info(self, user, directory_proxy):
        # Cargar la información existente
        file_path = 'directory_info.json'
        with open(file_path, 'r') as file:
            directory_info = json.load(file)

        # Actualizar la información con el nuevo directorio
        directory_info.setdefault('directory_info', {})
        directory_info['directory_info'].setdefault(user, {})
        directory_info['directory_info'][user]['root'] = str(directory_proxy)

        # Guardar la información actualizada en el archivo JSON
        with open(file_path, 'w') as file:
            json.dump(directory_info, file, indent=2)