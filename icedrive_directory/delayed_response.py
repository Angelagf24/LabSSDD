"""Servant implementation for the delayed response mechanism."""

import Ice

import IceDrive

import logging

class DirectoryQueryResponse(IceDrive.DirectoryQueryResponse):
    def __init__(self):
        self.response = False
        self.root = None

    def rootDirectoryResponse(self, root: IceDrive.DirectoryPrx, current: Ice.Current = None) -> None:
        self.response = True
        self.root = root

class DirectoryQuery(IceDrive.DirectoryQuery):
    def __init__(self, service):
        self.service = service

    def rootDirectory(self, user: IceDrive.UserPrx, response: IceDrive.DirectoryQueryResponsePrx, current: Ice.Current = None) -> None:
        logging.info("rootDirectory")
        root = self.service.getRoot(user)
        if root is not None:
            response.rootDirectoryResponse(root)
        else:
            print("No se pudo obtener el root")
        