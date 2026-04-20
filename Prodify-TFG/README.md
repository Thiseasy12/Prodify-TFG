# Prodify

Aplicacion web de gestion de proyectos con tableros Kanban. Hecha con Flask, MySQL y JavaScript vanilla.

## Lo que necesitas

- Python instalado
- XAMPP instalado (para la base de datos)

## Como instalarlo

**1. Enciende MySQL desde XAMPP**

**2. Instala las dependencias**

```bash
python -m pip install -r requirements.txt
```

**3. Importa la base de datos**

Abre phpMyAdmin en `http://localhost/phpmyadmin` e importa el archivo `prodify database.sql`

**4. Crea el archivo .env**

Copia `.env.example`, renombralo a `.env` y rellena tus datos:

```
SECRET_KEY=pon_aqui_cualquier_texto_largo
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_NAME=prodify_db
PUBLIC_BASE_URL=http://127.0.0.1:5000
```

Si quieres que funcione el envio de correos (verificacion, recuperar contraseña) rellena tambien la parte de SMTP. Si lo dejas vacio la app funciona igual pero sin correos.

**5. Arranca la app**

```bash
python app.py
```

Y abre `http://127.0.0.1:5000/login` en el navegador.

## Si algo falla

- Que MySQL este encendido en XAMPP
- Que hayas importado el archivo SQL
- Que el `.env` exista y tenga `DB_NAME=prodify_db`
- Que hayas instalado las dependencias
