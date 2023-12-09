"""Module for servants implementations."""

from typing import List
import os
import json
import sys
import uuid

import Ice

import IceDrive

class Directory(IceDrive.Directory):
    def __init__(self, name, adapter=None, parent=None, proxy=None):
        self.name = name
        self.adapter = adapter
        self.proxy = proxy
        self.child_directories = {}  # Directorios hijos
        self.linked_files = {}  # Archivos enlazados
        self.files = {}  # Agrega este atributo
        self.parent = parent  # Incluye el argumento parent
        self.subdirectory_path = None

    def get_name_uuid(self, name):
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, name))
    
    def createChild(self, name: str, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        subdirectory_uuid = self.get_name_uuid(name)

        if name not in self.child_directories:
            subdirectory_name = f"{subdirectory_uuid}"
            child = Directory(name=subdirectory_name, parent=self)
            child_proxy = IceDrive.DirectoryPrx.uncheckedCast(
                self.adapter.addWithUUID(child)
            )
        else:
            print(f"Ese directorio '{name}' ya tiene existe.")
            raise IceDrive.ChildAlreadyExists(childName=name, path=self.getPath())

        self.child_directories[name] = child_proxy

        self.persist_subdirectory_info(child, child_proxy, name)

        self.subdirectory_path = os.path.join('Subdirectorios', f'{name}_info.json')

        return child_proxy
        
    def persist_subdirectory_info(self, child, child_proxy, name):
        directory_path = os.path.join('Subdirectorios', f'{name}_info.json')

        if not os.path.exists(directory_path):
            with open(directory_path, 'w') as file:
                json.dump({'subdirectory_info': {}}, file, indent=2)

        with open(directory_path, 'r') as file:
            subdirectory_info = json.load(file)

        # Actualizar la información con el nuevo directorio
        subdirectory_info.setdefault('subdirectory_info', {})
        subdirectory_info['subdirectory_info']['subdirectories'] = str(child_proxy)

        # Guardar la información actualizada en el archivo JSON
        with open(directory_path, 'w') as file:
            json.dump(subdirectory_info, file, indent=2)

    
    def getChilds(self, current: Ice.Current = None) -> List[str]:
        return list(self.child_directories.keys())
    
    def getChild(self, target_name: str, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        if target_name in self.child_directories:
            proxy = IceDrive.DirectoryPrx.checkedCast(self.child_directories[target_name])
            return proxy
        else:
            raise IceDrive.ChildNotExists(childName=target_name)

    def getFiles(self, current: Ice.Current = None) -> List[str]:
        return list(self.files.keys())

    def linkFile(self, filename: str, blob_id: str, current=None):
        if filename not in self.files:
            self.files[filename] = blob_id
            self.persist(filename, blob_id)
        else:
            raise IceDrive.FileAlreadyExists(filename=filename)

    def save_directory_data(self, file_path=None, filename=None, blob_id=None):
        # Utiliza la ruta proporcionada o la predeterminada si no se especifica
        file_path = file_path or self.subdirectory_path

        with open(file_path, 'r+') as file:
            data = json.load(file)
            data.setdefault('files', {})
            files_representation = f"{filename} -> {blob_id}"
            data['files'][filename] = files_representation
            file.seek(0)
            file.truncate()
            json.dump(data, file, indent=2)

    def persist(self, filename, blob_id):
        if self.parent:
            # Llama a save_directory_data con la ruta del subdirectorio
            self.parent.save_directory_data(file_path=self.subdirectory_path, filename=filename, blob_id=blob_id)


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
