"""Module for servants implementations."""

from typing import List
import os
import json
import sys
import uuid

import Ice

import IceDrive

class Directory(IceDrive.Directory):
    def __init__(self, name, adapter=None, parent=None):
        self.name = name
        self.adapter = adapter
        self.child_directories = {}  # Directorios hijos
        self.linked_files = {}  # Archivos enlazados
        self.files = {}  # Agrega este atributo
        self.parent = parent  # Incluye el argumento parent

        # Cargar la información persistente
        self.load_persistence()

    def load_persistence(self):
        # Crear un archivo de persistencia para cada directorio
        directory_path = os.path.join('Subdirectorios', f"{self.name}_info.json")

        if os.path.exists(directory_path):
            with open(directory_path, 'r') as file:
                directory_info = json.load(file)
                self.child_directories = directory_info.get('child_directories', {})
                self.linked_files = directory_info.get('linked_files', {})

                # Cargar información de subdirectorios recursivamente
                for dir_name, dir_info in self.child_directories.items():
                    subdirectory = Directory(dir_name, parent=self)
                    subdirectory.load_persistence()
                    self.child_directories[dir_name] = subdirectory

    def persist(self):
        # Crear un archivo de persistencia para cada directorio
        directory_path = os.path.join('Subdirectorios', f"{self.name}_info.json")
        directory_info = {
            'child_directories': {},
            'linked_files': self.linked_files
        }

        # Guardar información de subdirectorios recursivamente
        for dir_name, subdirectory in self.child_directories.items():
            subdirectory.persist()
            directory_info['child_directories'][dir_name] = {
                'child_directories': {},
                'linked_files': subdirectory.linked_files
            }

        with open(directory_path, 'w') as file:
            json.dump(directory_info, file, indent=2)


    def persist_after_creation(self):
        # Llama al método persist después de crear un nuevo directorio raíz
        self.persist()
    
    def getChilds(self, current: Ice.Current = None) -> List[str]:
        return list(self.child_directories.keys())
    
    def getChild(self, name: str, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        if name in self.child_directories:
            proxy = IceDrive.DirectoryPrx.checkedCast(self.child_directories[name])
            return proxy
        else:
            raise IceDrive.ChildNotExists(childName=name)

    def createChild(self, name: str, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        if name not in self.child_directories:
            child = Directory(name, parent=self)

            # Crear la identidad del objeto manualmente
            child_identity = Ice.Identity(name, str(uuid.uuid4()))

            # Registrar el objeto en el adaptador con su identidad
            self.adapter.addWithUUID(child, child_identity)

            # Obtener un proxy con la identidad del objeto
            child_proxy = IceDrive.DirectoryPrx.uncheckedCast(self.adapter.createProxy(child_identity))

            # Almacenar el proxy en self.child_directories
            self.child_directories[name] = child_proxy

            child.persist_after_creation()
            print(f"Directorio: {str(child_proxy)}")
            return child_proxy
        else:
            raise IceDrive.ChildAlreadyExists(childName=name, path=self.getPath())

    def getFiles(self, current: Ice.Current = None) -> List[str]:
        return list(self.files.keys())

    def linkFile(self, filename: str, blob_id: str, current: Ice.Current = None) -> None:
        if filename not in self.files:
            self.files[filename] = blob_id
        else:
            raise IceDrive.FileAlreadyExists(filename=filename)


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

        user_directory_path = os.path.join(os.getcwd(), 'Subdirectorios', f'{user}_info.json')
        directory_info = {
            'directory_info': {
                user: {'root': str(new_proxy)}
            }
        }
        with open(user_directory_path, 'w') as file:
            json.dump(directory_info, file, indent=2)

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

    """def persist_directory_info(self, user, directory_proxy):
        # Cargar la información existente
        file_path = f'{user}_info.json'
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                directory_info = json.load(file)
        else:
            directory_info = {}

        # Actualizar la información con el nuevo directorio
        directory_info[user] = {'root': str(directory_proxy)}

        # Guardar la información actualizada en el archivo JSON
        with open(file_path, 'w') as file:
            json.dump(directory_info, file, indent=2)"""