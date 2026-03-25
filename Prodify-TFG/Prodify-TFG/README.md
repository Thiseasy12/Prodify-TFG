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

## Usuario de prueba

- Email: `test@prodify.com`
- Contrasena: `1234`

## Si algo no funciona

- Revisa que `MySQL` este encendido en XAMPP
- Revisa que la base de datos se llame `prodify_db`
- Revisa que has importado el archivo `prodify database.sql`
- Revisa que has instalado las dependencias con `requirements.txt`
