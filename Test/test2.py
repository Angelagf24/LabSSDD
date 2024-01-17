import Ice
import os
import sys
import uuid
import logging
import datetime
import time

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

logging.basicConfig(level=logging.INFO)

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
        serviceId = str(uuid.uuid4())

        adapter_Directory = communicator.createObjectAdapter("DirectoryAdapter")
        adapter_Directory_1 = communicator.createObjectAdapterWithEndpoints("DirectoryAdapter1", "tcp -h localhost -p 10003")
        adapter_authentication = communicator.createObjectAdapterWithEndpoints("AuthAdapter", "tcp -h localhost -p 10004")

        adapter_Directory.activate()
        adapter_Directory_1.activate()
        adapter_authentication.activate()

        auth = Authentication()
        auth_proxy = IceDrive.AuthenticationPrx.checkedCast(adapter_authentication.addWithUUID(auth))

        discovery = Discovery(serviceId)
        discovery_proxy = IceDrive.DiscoveryPrx.checkedCast(adapter_Directory.addWithUUID(discovery))

        persistence = DirectoryPersistence('../test_persistence.json') 
        servant_directory = DirectoryService(persistence=persistence, discovery=discovery) 
        servant_proxy_directory = IceDrive.DirectoryServicePrx.checkedCast(adapter_Directory.addWithUUID(servant_directory))
  
        persistence_1 = DirectoryPersistence('./test_persistence.json')
        servant_directory_1 = DirectoryService(persistence=persistence_1, discovery=discovery)
        servant_proxy_directory_1 = IceDrive.DirectoryServicePrx.checkedCast(adapter_Directory.addWithUUID(servant_directory_1))

        query = DirectoryQuery(servant_proxy_directory)
        query_proxy = IceDrive.DirectoryQueryPrx.checkedCast(adapter_Directory.addWithUUID(query))

        topic_manager = communicator.propertyToProxy("IceStorm.TopicManager.Proxy")
        topic_manager = IceStorm.TopicManagerPrx.checkedCast(topic_manager)

        topic = topic_manager.retrieve("discovery")
        topicQuery = topic_manager.retrieve("directory")

        publisher_proxy = IceDrive.DirectoryQueryPrx.uncheckedCast(topicQuery.getPublisher().ice_oneway())

        servant_directory.directoryQuery = publisher_proxy
        servant_directory_1.directoryQuery = publisher_proxy

        topicQuery.subscribeAndGetPublisher({}, query_proxy)
        topic.subscribeAndGetPublisher({}, discovery_proxy)

        discovery_proxy.announceAuthentication(auth_proxy)

        user = auth_proxy.newUser("user", "pass")
        assert auth_proxy.verifyUser(user) == True

        directory = servant_proxy_directory.getRoot(user) 
        assert directory != None

        directory_1 = servant_proxy_directory_1.getRoot(user)
        logging.info(directory_1)
        assert directory_1 != None

        time.sleep(5)

        directory.linkFile("archivo1.txt", "blob1")
        directory.unlinkFile("archivo1.txt")

        communicator.waitForShutdown()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: test2.py --Ice.Config=../config/directory.config")
        sys.exit(1)

    iniciar_testing()