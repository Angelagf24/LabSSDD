# IceDrive Directory service template

This repository contains the project template for the Directory service proposed as laboratory work for the students
of Distributed Systems in the course 2023-2024.

## Updating `pyproject.toml`

One of the first things that you need to setup when you clone this branch is to take a look into
`pyproject.toml` file and update the needed values:

- Project authors
- Project dependencies
- Projects URL humepage

=======
# LabSSDD

## Realización
Trabajo realizado por: Ángela Gijón Flores, Clase: 3ºB, correo: Angela.Gijon@alu.uclm.es

## Introducción

Para mi proyecto he decidido ir haciendo las pruebas con un archivo json. 
Lo primero es que si se crea un usuario, se le asignará un directorio raíz y todos los directorios raices estan almacenados en un archivos json: directory_service.json, de tal forma que si se intenta crear un usuario por segunda vez, no habra redudancia y se le devolverá por pantalla que el usuario ya existe. Esto sería en relación con la persistencia a nivel de servicio. 
En cuanto a la persistencia a nivel de subdirectorio, cada vez que se crea un nuevo subdirectorio se crea un archivo json con la siguiente forma: nombresubdirectorio_info.json y dentro de él tendremos la información (el proxy) del subdirectorio y si se crean archivos, pues el nombre del archivo y el enlace. Se han controlado excepciones generales, como que un directorio raíz no tiene padre, es decir, no tiene un directorio raíz ya que es él el raíz o que no se puede crear un subdirectorio si ya existe, en otras (las del enunciado). 
Y por ultimo, tambien se permite saber el "blobId" asociado a un archivo, eliminar archivos y eliminar subdirectorios. La lógica está implementado para que sea fiel a la realidad, por ejemplo, si eliminas el subdirectorio x, se va a eliminar de la carpeta "Subdirectorios" que es donde están contenidos. O si eliminas un archivo, se eliminará del json de su subdirectorio correspondiente. 


## Características

- Creación de directorios en un entorno distribuido.
- Gestión de archivos vinculados a directorios.
- Persistencia de la estructura del directorio y metadatos de archivos a través de JSON.
- Manipulación segura de directorios utilizando el control de acceso y políticas de Ice.

## Requisitos Previos

Antes de instalar y ejecutar IceDrive, asegúrate de tener lo siguiente:

- Python 3.6 o superior.
- Ice para Python, que puedes instalar con pip install zeroc-ice.
- Cualquier otra dependencia específica de tu sistema.

## Instalación

Clona el repositorio de IceDrive en tu máquina local utilizando:
git clone https://github.com/Angelagf24/LabSSDD

He decidido que la Tarea 1 del laboratorio esté hecho en una rama y la Tarea 2 en otra rama. 
La tarea 1 está en la rama "directorio", he pasado mis cambios locales a la rama origin/directorio y ya he hecho un merge con la rama main.   

Ahora hay que ejecutar lo siguiente para lanzar el servidor:
pip3 install .
Y luego lanzas el servicio:
icedrive-directory --Ice.Config=config/directory.config

## Testing
He implementado testing para cada función tanto de la clase Directory como para la clase DirectoryService. 
Está contenido en la carpeta Test y en el archivo: test_directory.py

Para ejecutarlo:
cd Test
python3 test_directory.py "proxy_servidor"

En el main hay diferentes funciones para diferentes operaciones, por ejemplo crear varios usuarios, crear todo lo relacionado a subdirectorios y ver como se maneja, eliminar un subdirectorio, eliminar un enlace de un archivo o conocer el padre. 
Actualmente están comentados, si se quiere ir probando el funcionamiento uno a uno, ir descomentando y si se quiere probar el funcionamiento de todo a la vez, descomentar todos. 

## Estructura del Proyecto
├── .github
│   ├── workflows
│       ├── lintian.yml
├── config
│   ├── directory.config
├── icedrive_directory
│   ├── __init__.py
│   ├── app.py
│   ├── directory.py
│   ├── icedrive.ice
├── Subdirectorios (Cada vez que se crea un subdirectorio se almacena aquí)
├── Test
│   ├── test_directory.py
├── (directory_info.json): si no está creado, se creo al iniciar el programa
├── pyproject.toml
├── README

## Autores

- Ángela Gijón Flores - Tarea 1 Laboratorio SSDD - [Angelagf24](https://github.com/Angelagf24/LabSSDD)