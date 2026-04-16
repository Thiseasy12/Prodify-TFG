# Prodify

Guia para poner la pagina web en otro pc

## Que se necesita

- Python instalado
- XAMPP instalado
- Este proyecto descargado en tu ordenador

## Antes de empezar

1. Abre XAMPP.
2. Enciende `MySQL`.

## Instalar lo necesario

Abre una terminal dentro de la carpeta del proyecto y ejecuta:

```powershell
python -m pip install -r requirements.txt
```

Si `python` no funciona, prueba con:

```powershell
py -m pip install -r requirements.txt
```

## Preparar la base de datos

1. Abre `http://localhost/phpmyadmin`
2. Importa el archivo `prodify database.sql`

## Iniciar la pagina

En la terminal, dentro de la carpeta del proyecto, ejecuta:

```powershell
python app.py
```

Si `python` no funciona:

```powershell
py app.py
```

## Abrir en el navegador

Cuando arranque, abre esta direccion:

`http://127.0.0.1:5000/login`

## Activar correos de verificacion

Prodify ya crea y envia el correo de verificacion al email que escribe el usuario al registrarse, pero necesitas configurar un proveedor de correo en `.env`.

Puedes usar una de estas opciones:

### Opcion 1: Resend

```env
RESEND_API_KEY=re_xxxxxxxxx
RESEND_FROM=Prodify <onboarding@resend.dev>
```

### Opcion 2: SMTP

Ejemplo con Gmail:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_correo@gmail.com
SMTP_PASSWORD=tu_app_password
SMTP_FROM=Prodify <tu_correo@gmail.com>
SMTP_USE_TLS=1
```

Notas:

- En Gmail normalmente necesitas una `App Password`, no tu contrasena normal.
- Cuando el usuario se registra, Prodify manda el enlace de verificacion al correo que ha escrito en el formulario.
- Si no configuras Resend ni SMTP, el enlace se imprime en la terminal del servidor en modo local.


## Si algo no funciona

- Revisa que `MySQL` este encendido en XAMPP
- Revisa que la base de datos se llame `prodify_db`
- Revisa que has importado el archivo `prodify database.sql`
- Revisa que has instalado las dependencias con `requirements.txt`
- Si borras usuarios manualmente desde phpMyAdmin, Prodify ya intenta dejar las relaciones en cascada al arrancar para que tambien se borren sus perfiles, espacios, tableros, tarjetas y actividad.
