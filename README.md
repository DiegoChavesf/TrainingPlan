# Documentación del Proyecto TrainingPlan

## Introducción
Este es un proyecto web de gestión de actividades desarrollado con Flask, Flask-Login y Sirope. La aplicación permite a los usuarios registrarse, iniciar sesión, añadir actividades, dar "me gusta" a las actividades y gestionar sus actividades. La base de datos se maneja a través de Sirope, un sistema de almacenamiento y recuperación de objetos.

## Requisitos
- Python 3.7 o superior
- Flask
- Flask-Login
- Sirope
- JSON para configuración

## Instalación
1. Clonar el repositorio:
   git clone https://github.com/DiegoChavesf/TrainingPlan.git
   cd TrainingPlan

2. Crear un entorno virtual y activar:
    python3 -m venv venv
    source venv/bin/activate 

3. Instalar las dependencias:
    pip install -r requirements.txt

## Configuración
1. Crear un archivo de configuración config.json en la raíz del proyecto con el siguiente formato:
    {
        "SECRET_KEY": "tu_clave_secreta",
    }
    
## Estructura del Proyecto
1. app.py: Archivo principal de la aplicación.
2. models.py: Define los modelos de datos.
3. templates/: Contiene las plantillas HTML.
4. static/: Contiene archivos estáticos (CSS, JS, imágenes).

## Modelos de Datos
1. UserDto: Representa a un usuario registrado.
2. ActivityDto: Representa una actividad creada por un usuario.
3. PostDto: Representa un comentario en una actividad.
4. KudosDto: Representa un me gusta a una activdad

## Funcionalidades Principales
1. Registro de Usuario
Permite a los usuarios registrarse en la aplicación proporcionando un nombre de usuario, correo electrónico y contraseña.

2. Inicio de Sesión
Permite a los usuarios registrados iniciar sesión en la aplicación.

3. Añadir Actividad
Permite a los usuarios añadir nuevas actividades proporcionando detalles como título, descripción y fecha.

4. Dar Me Gusta a una Actividad
Permite a los usuarios dar "me gusta" a las actividades de otros usuarios.

5. Borrar Actividad
Permite a los usuarios eliminar sus propias actividades y los comentarios asociados.

6. Añadir Comentarios
Permite a los usuarios añadir un comentario asociado a una actividad
