"""Module for servants implementations."""

from typing import List

import Ice

import IceDrive

class Directory(IceDrive.Directory):
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.childs = {}
        self.files = {}

    def getParent(self, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
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


# Puedes inicializar aquí alguna estructura de datos para mapear usuarios a directorios raíz.
# Por ejemplo, un diccionario donde las claves son usuarios y los valores son instancias de Directorio.
class DirectoryService(IceDrive.DirectoryService):
    def __init__(self):
        self.user_roots = {}

    def getRoot(self, user: str, current=None) -> IceDrive.DirectoryPrx:
        # Verifica si ya existe un directorio raíz para el usuario.
        if user in self.user_roots:
            return self.user_roots[user]
        else:
            # Si no existe, crea uno nuevo y lo asocia al usuario.
            root_directory = Directory(name=f"root_{user}")
            self.user_roots[user] = root_directory
            return root_directory
