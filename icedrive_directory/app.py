"""Authentication service application."""

import logging
import sys
from typing import List

import Ice

from .directory import Directory


class DirectoryApp(Ice.Application):
    """Implementation of the Ice.Application for the Authentication service."""

    def run(self, args: List[str]) -> int:
        """Execute the code for the AuthentacionApp class."""
        adapter = self.communicator().createObjectAdapter("DirectoryAdapter")
        adapter.activate()

        #Creamos una instancia de la clase Directory para representar el directorio raíz.
        servant = Directory(name="root_directory")
        servant_proxy = adapter.addWithUUID(servant)

        logging.info("Proxy: %s", servant_proxy)

        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()

        return 0


def main():
    """Handle the icedrive-authentication program."""
    app = DirectoryApp()
    return app.main(sys.argv)
