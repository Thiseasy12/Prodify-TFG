## Requisitos

- Python 3.x instalado
- XAMPP instalado (para MySQL)

## Instalacion

### 1. Enciende MySQL desde XAMPP

Abre el panel de XAMPP y pulsa **Start** en MySQL.

### 2. Instala las dependencias

bash
# bash / cmd
python -m pip install -r requirements.txt

# PowerShell
py -m pip install -r requirements.txt


### 3. Importa la base de datos

Abre phpMyAdmin en http://localhost/phpmyadmin e importa el archivo prodify database.sql

### 4. Crea el archivo .env

Copia `.env.example`, renombralo a `.env` y rellena tus datos:

```env
SECRET_KEY=pon_aqui_cualquier_texto_largo
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_NAME=prodify_db
PUBLIC_BASE_URL=http://127.0.0.1:5000
```

Si necesitas envio de correos (verificacion de cuenta, recuperar contrasena) rellena tambien la seccion SMTP del `.env`. Si se deja vacio la app funciona igual pero sin correos.

### 5. Arranca la app

bash
# bash / cmd
python app.py

# PowerShell
py app.py


Abre http://127.0.0.1:5000/login en el navegador.

## Solucion de problemas

- Error de conexion a la BD** — comprueba que MySQL esta encendido en XAMPP
- Tablas no encontradas** — importa `prodify database.sql` desde phpMyAdmin
- Error de variables de entorno** — asegurate de que el archivo `.env` existe y tiene `DB_NAME=prodify_db`
- Modulos no encontrados** — ejecuta `py -m pip install -r requirements.txt`
