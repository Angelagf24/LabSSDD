"""Module for servants implementations."""

from typing import List
import time
import logging

from delayed_response import DirectoryQueryResponse

import Ice

import IceDrive

class Directory(IceDrive.Directory):
    def __init__(self, name, persistence):
        self.name = name
        self.persistence = persistence

    def getPath(self, current: Ice.Current = None) -> str:
        return self.persistence.get_path_for_dir(self.name)

    def getParent(self, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        parent_id = self.persistence.get_parent_for_dir(self.name)
        if not parent_id:
            raise IceDrive.RootHasNoParent()
        return IceDrive.DirectoryPrx.uncheckedCast(
            current.adapter.addWithUUID(Directory(parent_id, self.persistence)))

    def getChilds(self, current: Ice.Current = None) -> List[str]:
        return self.persistence.get_subdirs_for_dir(self.name)
    
    def getChild(self, child_name, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        subdirs = self.persistence.get_subdirs_for_dir(self.name)
        child_id = subdirs.get(child_name)
        if not child_id:
            raise IceDrive.ChildNotExists(childName=child_name, path=self.getPath()) 
        return IceDrive.DirectoryPrx.uncheckedCast(
            current.adapter.addWithUUID(Directory(child_id, self.persistence)))
    
    def createChild(self, name: str, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        child_uuid = self.persistence.create_subdir_for_dir(self.name, name)
        if child_uuid is None:
            raise IceDrive.ChildAlreadyExists(childName=name, path=self.getPath())
        return IceDrive.DirectoryPrx.uncheckedCast(
            current.adapter.addWithUUID(Directory(child_uuid, self.persistence)))

    def removeChild(self, name: str, current: Ice.Current = None) -> None:
        if not self.persistence.remove_subdir_for_dir(self.name, name):
            raise IceDrive.ChildNotExists(childName=name, path=self.getPath()) 
        
    def getFiles(self, current: Ice.Current = None) -> List[str]:
        file_names = self.persistence.get_files_for_dir(self.name)
        return file_names
    
    def getBlobId(self, filename: str, current: Ice.Current = None) -> str:
        blob_id = self.persistence.get_blob_id_for_file(self.name, filename)
        if blob_id is None:
            raise IceDrive.FileNotFound(filename=filename) 
        return blob_id
    
    def linkFile(self, filename: str, blob_id: str, current: Ice.Current = None) -> None:
        self.persistence.link_file_to_dir(self.name, filename, blob_id)

    def unlinkFile(self, filename: str, current: Ice.Current = None) -> None:
        if not self.persistence.unlink_file_from_dir(self.name, filename):
            raise IceDrive.FileNotFound(filename=filename)

class DirectoryService(IceDrive.DirectoryService):
    def __init__(self, persistence, discovery):
        self.persistence = persistence
        self.discovery = discovery
        self.directoryQuery = None
    
    def getRoot(self, user: IceDrive.User, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        # Verificar que el proxy User es válido
        prxAutenticacion = self.discovery.getAuthenticationService()
        if not prxAutenticacion:
            raise Exception("No hay servicio de autenticación")

        if not prxAutenticacion.verifyUser(user):
            raise IceDrive.Unauthorized("User is not valid")
        
        # Comprobar si el usuario está vivo
        if not user.isAlive():
            raise IceDrive.Unauthorized("User is not alive")

        # Obtener el UUID del directorio raíz del usuario
        user_id = user.getUsername() 
        
        #Comprobar si existe:
        if self.persistence.exist_user(user_id):
            directory_uuid = self.persistence.get_directory_for_user(user_id)

            # Crear la instancia de Directory y el proxy
            servant = Directory(directory_uuid, self.persistence)
            new_proxy = IceDrive.DirectoryPrx.uncheckedCast(
                current.adapter.addWithUUID(servant)
            )

            return new_proxy
        else:
            response = DirectoryQueryResponse()
            response_prx = IceDrive.DirectoryQueryResponsePrx.uncheckedCast(
                current.adapter.addWithUUID(response)
            )
            self.directoryQuery.rootDirectory(user, response_prx)
            starTime = time.time()
            while not response.response and time.time() - starTime < 5: # 5 segundos
                time.sleep(0.1)
            if response.response:
                new_proxy = response.root
                return new_proxy
            else: 
                logging.info("Se ha superado el tiempo de espera")
                directory_uuid = self.persistence.get_directory_for_user(user_id)

                # Crear la instancia de Directory y el proxy
                servant = Directory(directory_uuid, self.persistence)
                new_proxy = IceDrive.DirectoryPrx.uncheckedCast(
                    current.adapter.addWithUUID(servant)
                )

                return new_proxy