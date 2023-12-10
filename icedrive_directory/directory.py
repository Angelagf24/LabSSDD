"""Module for servants implementations."""

from typing import List
import os
import json
import sys
import uuid

import Ice

import IceDrive

class Directory(IceDrive.Directory):
    def __init__(self, name, adapter=None, parent=None, proxy=None, parent_proxy=None):
        self.name = name
        self.adapter = adapter
        self.proxy = proxy
        self.child_directories = {}  
        self.linked_files = {}  
        self.files = {}  
        self.parent = parent 
        self.subdirectory_path = None
        self.child_uuids = {}
        self.parent_proxy = parent_proxy

    def getParent(self, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        try:
            if not self.parent:
                raise IceDrive.RootHasNoParent()
            return self.parent_proxy
        except IceDrive.RootHasNoParent:
            print("El directorio raíz no tiene un directorio superior (nodo raíz).")

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
            print(f"Ese directorio '{name}' ya existe.")
            raise IceDrive.ChildAlreadyExists(childName=name, path=self.getPath())
        
        print(f"Subdirectorio creado: {str(child_proxy)}")
        print(f"Detalles del subdirectorio: {subdirectory_uuid}")

        self.parent_proxy = child.proxy

        self.child_directories[name] = child_proxy
        self.child_uuids[name] = subdirectory_uuid

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
        child_names = list(self.child_directories.keys())
        print(f"Directorios hijos del raíz: {child_names}")
        return child_names
    
    def getChild(self, target_name: str, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        if target_name in self.child_directories:
            proxy = IceDrive.DirectoryPrx.checkedCast(self.child_directories[target_name])
            print(f"Subdirectorio del {target_name}: {proxy}")
            return proxy
        else:
            raise IceDrive.ChildNotExists(childName=target_name)

    def getFiles(self, current: Ice.Current = None) -> List[str]:
        files = list(self.files.keys())
        print(f"Archivos: {files}")
        return files
    
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

    def linkFile(self, filename: str, blob_id: str, current=None):
        if filename not in self.files:
            print(f"{filename} --> {blob_id}")
            self.files[filename] = blob_id
            self.persist(filename, blob_id)
        else:
            raise IceDrive.FileAlreadyExists(filename=filename)
        
    def unlinkFile(self, filename: str, current: Ice.Current = None) -> None:
        if filename in self.files:
            print(f"Archivo {filename} eliminado con éxito")
            del self.files[filename]
            self.persistUnLink(filename)
        else:
            raise IceDrive.FileNotFound(filename=filename)
        
    def persistUnLink(self, filename):
        if self.parent:
            # Llama a remove_directory_data con la ruta del subdirectorio
            self.parent.remove_directory_data(filename=filename, file_path=self.subdirectory_path)
        
    def remove_directory_data(self, filename, file_path=None):
        file_path = file_path or self.subdirectory_path

        # Verifica si el archivo JSON existe
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                data = json.load(file)

            # Elimina la entrada correspondiente al archivo en el archivo JSON
            if 'files' in data and filename in data['files']:
                del data['files'][filename]

                # Guarda la información actualizada en el archivo JSON
                with open(file_path, 'w') as file:
                    json.dump(data, file, indent=2)
        
    def getBlobId(self, filename: str, current: Ice.Current = None) -> str:
        if filename in self.files:
            return self.files[filename]
        else:
            raise IceDrive.FileNotFound(filename=filename)


    def getPath(self, current: Ice.Current = None) -> str:
        path = self.name
        current_directory = self.parent

        while current_directory:
            path = os.path.join(current_directory.name, path)
            current_directory = current_directory.parent

        return path
        
    def removeChild(self, name: str, current: Ice.Current = None) -> None:
        if name in self.child_directories:
            child_proxy = self.child_directories.pop(name)
            subdirectory_uuid = self.get_name_uuid(name)
            subdirectory_name = f"{subdirectory_uuid}"
            self.child_uuids.pop(subdirectory_name, None)  
            self.remove_subdirectory_info(name)
            print(f"Subdirectorio '{name}' eliminado con éxito.")
        else:
            raise IceDrive.ChildNotExists(childName=name, path=self.getPath())
    
    def remove_subdirectory_info(self, name):
        directory_path = os.path.join('Subdirectorios', f'{name}_info.json')
        if os.path.exists(directory_path):
            os.remove(directory_path)


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
            print(f"Su directorio es: {stored_proxy}")
            return stored_proxy

        # Si el usuario no tiene un directorio registrado, crear uno nuevo
        directory_name = f"root_{user_uuid}"
        new_proxy = IceDrive.DirectoryPrx.uncheckedCast(
            self.adapter.addWithUUID(Directory(name=directory_name, adapter=self.adapter))
        )

        print(f"El directorio raíz de {user} es: {new_proxy}")

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
