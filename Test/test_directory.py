import unittest
from directory import Directory  # Asegúrate de importar correctamente la clase Directory
import IceDrive
import Ice

#from IceDrive import FileNotFound, FileAlreadyExists, ChildNotExists


class TestDirectory(unittest.TestCase):
    #Este método configura el entorno de prueba creando un directorio raíz y subdirectorios, 
    #además de agregar algunos archivos. Esto se utiliza como base para varias pruebas.
    def setUp(self):
        # Configuración inicial para las pruebas.
        self.root = Directory("root")
        self.subdir = self.root.createChild("subdir")
        self.root.linkFile("file1", "blobId1")
        self.subdir.linkFile("file2", "blobId2")

    def test_getFiles_empty(self):
        # Prueba obtener archivos de un directorio vacío
        empty_dir = self.root.createChild("empty")
        self.assertEqual(empty_dir.getFiles(), [])

    def test_getFiles_nonEmpty(self):
        # Prueba obtener archivos en un directorio no vacío
        self.assertEqual(set(self.root.getFiles()), {"file1"})

    def test_getBlobId(self):
        # Prueba obtener el blobId de un archivo existente
        self.assertEqual(self.root.getBlobId("file1"), "blobId1")

    def test_getBlobId_notFound(self):
        # Prueba la excepción cuando el archivo no existe
        with self.assertRaises(IceDrive.FileNotFound):
            self.root.getBlobId("nonExistingFile")

    def test_linkFile_existingFile(self):
        # Prueba la creación de un archivo que ya existe
        with self.assertRaises(IceDrive.FileAlreadyExists):
            self.root.linkFile("file1", "blobId1")

    def test_unlinkFile(self):
        # Prueba eliminar un archivo existente
        self.root.unlinkFile("file1")
        with self.assertRaises(IceDrive.FileNotFound):
            self.root.getBlobId("file1")

    def test_getChilds(self):
        # Prueba obtener subdirectorios
        self.assertEqual(set(self.root.getChilds()), {"subdir"})

    def test_getChild_notExists(self):
        # Prueba obtener un subdirectorio que no existe
        with self.assertRaises(IceDrive.ChildNotExists):
            self.root.getChild("nonExistingSubdir")

    def test_createChild_existingChild(self):
        # Prueba crear un subdirectorio que ya existe
        with self.assertRaises(IceDrive.ChildAlreadyExists):
            self.root.createChild("subdir")

    def test_removeChild_notExists(self):
        # Prueba eliminar un subdirectorio que no existe
        with self.assertRaises(IceDrive.ChildNotExists):
            self.root.removeChild("nonExistingSubdir")

    def test_getParent(self):
        # Prueba obtener el directorio padre
        self.assertEqual(self.subdir.getParent(), self.root)

    def test_getParent_root(self):
        # Prueba obtener el directorio padre de la raíz
        self.assertIsNone(self.root.getParent())

if __name__ == '__main__':
    unittest.main()