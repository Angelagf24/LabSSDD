import Ice

import os
import sys
import datetime
import uuid
import logging

ruta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_iceDrive = os.path.abspath(os.path.join(ruta_actual, "..", "icedrive_directory"))
sys.path.append(ruta_iceDrive)

Ice.loadSlice('../icedrive_directory/icedrive.ice')
import IceDrive

import IceStorm

from directory import DirectoryService, Directory
from persistence import DirectoryPersistence
from discovery import Discovery
from delayed_response import DirectoryQuery

class User(IceDrive.User):
    def __init__(self, name):
        self.name = name
        self.time = datetime.datetime.now() + datetime.timedelta(minutes=2)

    def getUsername(self, current: Ice.Current = None) -> str:
        return self.name
    
    def isAlive(self, current: Ice.Current = None) -> bool:
        return datetime.datetime.now() < self.time 
    
    def refresh(self, current: Ice.Current = None) -> None:
        pass

class Authentication(IceDrive.Authentication):
    def __init__(self):
        self.users = {}

    def login(self, name: str, password: str, current: Ice.Current = None) -> IceDrive.UserPrx:
        pass

    def newUser(self, name: str, password: str, current: Ice.Current = None) -> IceDrive.UserPrx:
        user = User(name)
        proxy = IceDrive.UserPrx.uncheckedCast(current.adapter.addWithUUID(user))
        self.users[proxy] = user
        return proxy
    
    def removeUser(self, name: str, current: Ice.Current = None) -> None:
        pass

    def verifyUser(self, user: IceDrive.UserPrx, current: Ice.Current = None) -> bool:
        return user in self.users

def iniciar_testing():
    with Ice.initialize(sys.argv) as communicator:
        adapter_auth = communicator.createObjectAdapterWithEndpoints("AuthenticationService", "tcp -h localhost -p 10004")
        adapter_auth.activate()

        auth = Authentication()
        servant_auth = adapter_auth.addWithUUID(auth)
        servant_proxy_auth = IceDrive.AuthenticationPrx.uncheckedCast(servant_auth)

        adapter_directory = communicator.createObjectAdapterWithEndpoints("DirectoryService", "tcp -h localhost -p 10005")
        adapter_directory.activate()
        persistence = DirectoryPersistence('../test_persistence.json')
        discovery = Discovery(str(uuid.uuid4()))
        discoveryprx = adapter_directory.addWithUUID(discovery)
        servant_directory = DirectoryService(persistence=persistence, discovery=discovery)
        servantprx_directory = adapter_directory.addWithUUID(servant_directory)
        servant_proxy_directory = IceDrive.DirectoryServicePrx.uncheckedCast(servantprx_directory)

        discovery.announceAuthentication(servant_proxy_auth)

        query = DirectoryQuery(servant_proxy_directory)
        queryprx = adapter_directory.addWithUUID(query)
        query_proxy = IceDrive.DirectoryQueryPrx.uncheckedCast(queryprx)
        topic_manager = communicator.propertyToProxy("IceStorm.TopicManager.Proxy")
        topic_manager = IceStorm.TopicManagerPrx.checkedCast(topic_manager)
        topic = topic_manager.retrieve("directory")
        publisher = topic.getPublisher()
        publisherprx = IceDrive.DirectoryQueryPrx.uncheckedCast(publisher)
        servant_directory.directoryQuery = publisherprx

        adapter_directory_1 = communicator.createObjectAdapterWithEndpoints("DirectoryService1", "tcp -h localhost -p 10006")
        adapter_directory_1.activate()
        persistence_1 = DirectoryPersistence('./test_persistence.json')
        servant_directory_1 = DirectoryService(persistence=persistence_1, discovery=discovery)
        servantprx_directory_1 = adapter_directory_1.addWithUUID(servant_directory_1)
        servant_proxy_directory_1 = IceDrive.DirectoryServicePrx.uncheckedCast(servantprx_directory_1)

        servant_directory_1.directoryQuery = publisherprx

        topic.subscribeAndGetPublisher({}, query_proxy)

        user = comprobar_VerifyUser(servant_proxy_auth)
        comprobar_GetRoot(servant_proxy_directory, user)
        comprobar_diferido(servant_proxy_directory_1, user)

        communicator.waitForShutdown()

def comprobar_VerifyUser(servant_proxy):
    user = servant_proxy.newUser("user", "pass")
    #print(servant_proxy.verifyUser(user))
    assert servant_proxy.verifyUser(user) == True
    return user 

#Test pasado con éxito: si pasamos un objeto usuario crea un directorio raíz para ese usuario
def comprobar_GetRoot(servant_proxy, user):
    #print(servant_proxy.getRoot(user))
    assert servant_proxy.getRoot(user) != None

def comprobar_diferido(servant_proxy, user):
    #print(servant_proxy.getRoot(user))
    assert servant_proxy.getRoot(user) != None

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: test_Parte2.py --Ice.Config=../config/directory.config")
        sys.exit(1)

    iniciar_testing()
