"""Authentication service application."""

import logging
import sys
import uuid
import time
import threading
from typing import List

import Ice
import IceDrive
import IceStorm

from .directory import DirectoryService
from .persistence import DirectoryPersistence
from .discovery import Discovery
from .delayed_response import DirectoryQuery

class DirectoryApp(Ice.Application):
    """Implementation of the Ice.Application for the Authentication service."""

    def run(self, args: List[str]) -> int:
        """Execute the code for the AuthentacionApp class."""
        adapter = self.communicator().createObjectAdapter("DirectoryAdapter")
        adapter.activate()

        unique_id = str(uuid.uuid4())
        discovery = Discovery(unique_id)
        discoveryprx = adapter.addWithUUID(discovery)
        discovery_proxy = IceDrive.DiscoveryPrx.uncheckedCast(discoveryprx)

        persistence = DirectoryPersistence('./test_persistence.json')

        servant = DirectoryService(persistence=persistence, discovery=discovery)
        servantprx = adapter.addWithUUID(servant)
        servant_proxy = IceDrive.DirectoryServicePrx.uncheckedCast(servantprx)

        query = DirectoryQuery(servantprx)
        queryprx = adapter.addWithUUID(query)
        servant_query = IceDrive.DirectoryQueryPrx.uncheckedCast(queryprx)

        topic_mgr = self.communicator().propertyToProxy("IceStorm.TopicManager.Proxy")
        topic_manager = IceStorm.TopicManagerPrx.checkedCast(topic_mgr)

        try:
            topicQuery = topic_manager.retrieve("directory")
            topic = topic_manager.retrieve("discovery")  
        except IceStorm.NoSuchTopic:
            topicQuery = topic_manager.create("directory")
            topic = topic_manager.create("discovery")

        publisher = topic.getPublisher()
        publisher_prx = IceDrive.DiscoveryPrx.uncheckedCast(publisher)
        publisherQuery = topicQuery.getPublisher()
        publisherQuery_prx = IceDrive.DirectoryQueryPrx.uncheckedCast(publisherQuery)

        servant.directoryQuery = publisherQuery_prx

        topic.subscribeAndGetPublisher({}, discovery_proxy)
        topicQuery.subscribeAndGetPublisher({}, servant_query)

        hilo = threading.Thread(target=self.start_announcing, 
                                args=(publisher_prx, servant_proxy, discovery, unique_id))
        hilo.daemon = True  
        hilo.start()

        logging.info("Proxy: %s", servant_proxy)

        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()

        return 0
    
    def start_announcing(self, publisher_prx, servant_proxy, discovery, unique_id):
        while True:
            discovery.servicios_registrado[servant_proxy] = unique_id
            publisher_prx.announceDirectoryService(servant_proxy)
            time.sleep(5)


def main():
    """Handle the icedrive-authentication program."""
    app = DirectoryApp()
    return app.main(sys.argv)