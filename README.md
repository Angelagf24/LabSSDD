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

### Realización
Trabajo realizado por: Ángela Gijón Flores, Clase: 3ºB, correo: Angela.Gijon@alu.uclm.es

## Parte 1

### Introducción

Para mi proyecto he decidido ir haciendo las pruebas con un archivo json. 

Lo primero es que si se crea un usuario, se le asignará un directorio raíz y todos los directorios raices estan almacenados en un archivos json: directory_service.json, de tal forma que si se intenta crear un usuario por segunda vez, no habra redudancia y se le devolverá por pantalla que el usuario ya existe. Esto sería en relación con la persistencia a nivel de servicio. 

En cuanto a la persistencia a nivel de subdirectorio, cada vez que se crea un nuevo subdirectorio se crea un archivo json con la siguiente forma: nombresubdirectorio_info.json y dentro de él tendremos la información (el proxy) del subdirectorio y si se crean archivos, pues el nombre del archivo y el enlace. Se han controlado excepciones generales, como que un directorio raíz no tiene padre, es decir, no tiene un directorio raíz ya que es él el raíz o que no se puede crear un subdirectorio si ya existe, en otras (las del enunciado). 

Y por ultimo, tambien se permite saber el "blobId" asociado a un archivo, eliminar archivos y eliminar subdirectorios. La lógica está implementado para que sea fiel a la realidad, por ejemplo, si eliminas el subdirectorio x, se va a eliminar de la carpeta "Subdirectorios" que es donde están contenidos. O si eliminas un archivo, se eliminará del json de su subdirectorio correspondiente. 


### Características

- Creación de directorios en un entorno distribuido.
- Gestión de archivos vinculados a directorios.
- Persistencia de la estructura del directorio y metadatos de archivos a través de JSON.
- Manipulación segura de directorios utilizando el control de acceso y políticas de Ice.

### Requisitos Previos

Antes de instalar y ejecutar IceDrive, asegúrate de tener lo siguiente:

- Python 3.6 o superior.
- Ice para Python, que puedes instalar con pip install zeroc-ice.
- Cualquier otra dependencia específica de tu sistema.

### Instalación

Clona el repositorio de IceDrive en tu máquina local utilizando:
git clone https://github.com/Angelagf24/LabSSDD

He decidido que la Tarea 1 del laboratorio esté hecho en una rama y la Tarea 2 en otra rama. 
La tarea 1 está en la rama "directorio", he pasado mis cambios locales a la rama origin/directorio y ya he hecho un merge con la rama main.   

Ahora hay que ejecutar lo siguiente para lanzar el servidor:

pip3 install .

Y luego lanzas el servicio:

icedrive-directory --Ice.Config=config/directory.config

### Testing
He implementado testing para cada función tanto de la clase Directory como para la clase DirectoryService. 
Está contenido en la carpeta Test y en el archivo: test_directory.py

Para ejecutarlo:

cd Test

python3 test_directory.py "proxy_servidor"

En el main hay diferentes funciones para diferentes operaciones, por ejemplo crear varios usuarios, crear todo lo relacionado a subdirectorios y ver como se maneja, eliminar un subdirectorio, eliminar un enlace de un archivo o conocer el padre. 

Actualmente están comentados, si se quiere ir probando el funcionamiento uno a uno, ir descomentando y si se quiere probar el funcionamiento de todo a la vez, descomentar todos. 

### Estructura del Proyecto
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

## Parte 2

### Introducción
Este proyecto implementa un servicio de directorio para la gestión de usuarios y directorios en un entorno distribuido. El servicio de directorio tiene la capacidad de descubrir y comunicarse con los servicios de "Authentication" y "BlobService" para colaborar en diversas tareas. Además, es capaz de funcionar en un entorno con múltiples instancias del servicio "DirectoryService" y cooperar con ellas. También se implementa resolución en diferido.

### Características

1. **Descubrimiento de Servicios:**
   - Implementa un mecanismo de descubrimiento de servicios para ubicar y comunicarse con los servicios de "Authentication" y "BlobService".

2. **Interfaz de Usuario:**
   - Utiliza un proxy de tipo User para la interfaz, asegurándose de que el objeto User pertenezca a un servicio de autenticación válido. La verificación se realiza al recibir el objeto por primera vez. Por ello en getRoot() lo modificamos para que en vez de recibir el nombre del usuario como lo hacíamos en la parte 1, ahora es un objeto User.
     
3. **Manejo de Proxies de Usuario:**
   - Gestiona proxies de usuarios de manera que cada operación realizada por los directorios asociados a un usuario requiere una comprobación "isAlive" en el objeto User.

4. **Resolución en Diferido:**
   - Implementa la resolución en diferido para obtener el directorio raíz de un usuario. Si en nuestra persistencia el directorio raíz de un usuario no existe, intenta una resolución en diferido y crea un nuevo directorio root si no se obtiene un resultado en un tiempo especificado.

5. **Integración con BlobService:**
   - Permite la comunicación con el servicio de almacenamiento de archivos ("BlobService") para realizar operaciones de enlazado y desenlazado de archivos. Lanza la excepción "TemporaryUnavailable" si no se ha descubierto ninguna instancia de "BlobService".

6. **Interfaz de Directorio:**
   - Se ha modificado la lógica de directorio con respecto a la tarea 1 para ofrecer una interfaz de directorio completa que incluye métodos para obtener la ruta, el directorio padre, listar los hijos, crear, eliminar y manipular archivos, y obtener identificadores de blobs.

7. **Manejo de Eventos:**
   - Utiliza eventos para la resolución en diferido del directorio raíz. Una instancia que tiene el root de un usuario responde a eventos con el método rootDirectoryResponse().

8. **Excepciones y Manejo de Errores:**
   - Lanza excepciones como "RootHasNoParent", "ChildNotExists", "ChildAlreadyExists", "FileNotFound", "FileAlreadyExists", y "TemporaryUnavailable" para manejar situaciones inesperadas y errores.
  
### Diferencias con respecto a la Tarea 1

Se han realizado varias modificaciones y mejoras en la implementación del servicio de directorio desde la Tarea 1. A continuación, se detallan las diferencias significativas:

#### Estructura de Archivos:

1. **División de la Persistencia:**
   - Se ha creado una clase adicional para manejar la persistencia, separando la lógica de persistencia del archivo "directory.py". Esto mejora la claridad y limpieza del código en "directory.py".

2. **Organización Mejorada del JSON:**
   - Se ha implementado una estructura más atractiva para la organización de la información en el archivo JSON. Esto contribuye a una mejor legibilidad y mantenimiento del archivo JSON.

3. **Centralización de la Información:**
   - En lugar de tener directorios en un JSON y subdirectorios en archivos JSON independientes, ahora toda la información se centraliza y almacena en un único archivo JSON. Esto simplifica la gestión y acceso a la información.

4. **Modificación de la Clase de Pruebas:**
   - La clase de pruebas ha sido renombrada a "test.py" para reflejar mejor su propósito. Se han realizado ajustes para adaptarse a los cambios en la estructura y organización de la información.

#### Cambios en Métodos Específicos:

5. **Modificación de getRoot():**
   - Ahora, en lugar de recibir un nombre de usuario como parámetro, getRoot() recibe un objeto de tipo User. La lógica de validación del usuario se ha actualizado en consecuencia.

   - Se ha implementado una lógica para verificar si el usuario existe en la persistencia. En caso contrario, se realiza una búsqueda en diferido en otros servicios de directorio. Si el usuario es encontrado, se añade a la persistencia local.

6. **Manejo Mejorado de linkFile y unlinkFile:**
   - En los métodos linkFile y unlinkFile, se ha agregado una comprobación para verificar si el servicio Blob al que se accede está activo. Se lanza la excepción TemporaryUnavailable("Blob service") en caso de que el servicio Blob no esté disponible, utilizando el mecanismo de descubrimiento.

Estos cambios proporcionan una estructura más ordenada, mejor legibilidad y manejo mejorado de la persistencia y los servicios relacionados.

### Testing
He implementado testing para comprobar el diferido. 
Está contenido en la carpeta Test y en el archivo: test2.py

Para ejecutarlo:

cd Test

python3 test2.py --Ice.Config=../config/directory.config

Este test prueba que nuestro servicio se anuncie y subscriba. También prueba la resolución por diferido y como se implementarían linkFile y unlinkFile con la nueva modificación. 

### Estructura actualizada del Proyecto

├── config

│   ├── directory.config

│   ├── icebox.config

│   ├── icestorm.config

├── icedrive_directory

│   ├── __init__.py

│   ├── app.py

│   ├── directory.py

│   ├── discovery.py

│   ├── delayed_response.py

│   ├── icedrive.ice //Se ha utilizado el archivo .ice de la máquina virtual según indicaron

│   ├── persistence.py

├── Test

│   ├── test.py //Test para la Tarea 1

│   ├── test2.py //Test para la Tarea 2

├── test_persistence.json //Almacena la persistencia

├── pyproject.toml

├── run_icestorm

├── README


## Autores

- Ángela Gijón Flores - Tarea 1 Laboratorio SSDD - [Angelagf24](https://github.com/Angelagf24/LabSSDD)
- Ángela Gijón Flores - Tarea 2 Laboratorio SSDD - [Angelagf24](https://github.com/Angelagf24/LabSSDD)
