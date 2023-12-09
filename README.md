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

IceDrive es un sistema de directorios diseñado para permitir la manipulación y gestión de archivos y directorios a través de una red distribuida. Utilizando las capacidades de Ice, un middleware de comunicaciones orientado a objetos, IceDrive proporciona un entorno seguro y robusto para operaciones de archivos distribuidos.

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
Por lo que para la instalación hay que descargarse el contenido de la siguiente rama:
Rama: Entrega_Tarea1

Ahora hay que ejecutar lo siguiente para lanzar el servidor:
pip3 install .
Y luego lanzas el servicio:
icedrive-directory --Ice.Config=config/directory.config

Para el testing:
cd Test
python3 test_directory.py "proxy_servidor"

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