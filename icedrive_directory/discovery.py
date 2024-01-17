"""Servant implementations for service discovery."""

import Ice

import random

import IceDrive

class Discovery(IceDrive.Discovery):
    def __init__(self, id):
        self.id = id
        self.directory_service = []
        self.authentication_service = []
        self.blob_service = []
        self.servicios_registrado = {}

    def announceAuthentication(self, prx: IceDrive.AuthenticationPrx, current: Ice.Current = None) -> None:
        if prx not in self.authentication_service:
            self.authentication_service.append(prx)
            print(f"Authentication service announced and added: {prx}")

    def announceDirectoryService(self, prx: IceDrive.DirectoryServicePrx, current: Ice.Current = None) -> None:
        id= self.servicios_registrado.get(prx)
        if id is None:
            if prx not in self.directory_service:
                self.directory_service.append(prx)
                print(f"Directory service announced and added: {prx}")

    def announceBlobService(self, prx: IceDrive.BlobServicePrx, current: Ice.Current = None) -> None:
        if prx not in self.blob_service:
            self.blob_service.append(prx)
            print(f"Blob service announced and added: {prx}")

    def getAuthenticationService(self):
        if not self.authentication_service:
            return None
        return random.choice(self.authentication_service)

    def getDirectoryService(self):
        if not self.directory_service:
            return None
        return random.choice(self.directory_service)

    def getBlobService(self):
        if not self.blob_service:
            return None
        return random.choice(self.blob_service)