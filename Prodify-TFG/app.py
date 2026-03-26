<<<<<<< HEAD:Prodify-TFG/Prodify-TFG/app.py
﻿from datetime import datetime
import os
from urllib.parse import quote_plus

from flask import Flask, redirect, render_template, request, session, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

=======
﻿from datetime import datetime
import os
from urllib.parse import quote_plus

from flask import Flask, redirect, render_template, request, session, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from markupsafe import Markup, escape
from werkzeug.security import generate_password_hash, check_password_hash

>>>>>>> c672314 (Update project structure, templates and styles):app.py
# Creamos la aplicacion Flask y le indicamos donde estan las vistas y los estilos.
app = Flask(__name__, template_folder='html', static_folder='estilos', static_url_path='/estilos')

# Esta clave permite a Flask mantener la sesion iniciada del usuario.
app.secret_key = os.getenv('SECRET_KEY', 'prodify_super_secret_key')

# Configuracion de MySQL. Por defecto esta pensada para XAMPP en local.
db_user = os.getenv('DB_USER', 'root')
<<<<<<< HEAD:Prodify-TFG/Prodify-TFG/app.py
db_password = quote_plus(os.getenv('DB_PASSWORD', ''))
db_host = os.getenv('DB_HOST', 'localhost')
db_name = os.getenv('DB_NAME', 'prodify_db')

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}?charset=utf8mb4"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

=======
db_password = quote_plus(os.getenv('DB_PASSWORD', ''))
db_host = os.getenv('DB_HOST', 'localhost')
db_name = os.getenv('DB_NAME', 'prodify_db')

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}?charset=utf8mb4"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

>>>>>>> c672314 (Update project structure, templates and styles):app.py
# SQLAlchemy es el puente entre Python y la base de datos.
db = SQLAlchemy(app)

# Lista de plantillas listas para crear tableros de ejemplo.
BOARD_TEMPLATES = [
<<<<<<< HEAD:Prodify-TFG/Prodify-TFG/app.py
    {
        "id": "product",
        "name": "Lanzamiento de producto",
        "summary": "Coordina idea, validacion y salida al mercado.",
        "accent": "template-accent-blue",
        "category": "Producto",
        "tags": ["Roadmap", "Sprint", "Go-to-market"],
        "columns": ["Idea", "En progreso", "Validacion", "Listo"],
    },
    {
        "id": "marketing",
        "name": "Campana de marketing",
        "summary": "Gestiona creatividades, anuncios y calendario.",
        "accent": "template-accent-violet",
        "category": "Marketing",
        "tags": ["Contenido", "Ads", "Social"],
        "columns": ["Brief", "Produccion", "Revision", "Publicado"],
    },
    {
        "id": "ventas",
        "name": "Pipeline de ventas",
        "summary": "Controla leads, propuestas y cierres.",
        "accent": "template-accent-amber",
        "category": "Ventas",
        "tags": ["CRM", "Negociacion", "Seguimiento"],
        "columns": ["Lead", "Contacto", "Propuesta", "Cerrado"],
    },
    {
        "id": "ops",
        "name": "Operaciones internas",
        "summary": "Mantiene procesos, tareas recurrentes y calidad.",
        "accent": "template-accent-mint",
        "category": "Operaciones",
        "tags": ["Procesos", "Checklist", "Equipo"],
        "columns": ["Pendiente", "En curso", "Bloqueado", "Listo"],
    },
    {
        "id": "support",
        "name": "Soporte y tickets",
        "summary": "Prioriza solicitudes y mejora la experiencia.",
        "accent": "template-accent-rose",
        "category": "Soporte",
        "tags": ["Customer", "Feedback", "SLA"],
        "columns": ["Nuevo", "Asignado", "Investigando", "Resuelto"],
    },
    {
        "id": "personal",
        "name": "Plan semanal personal",
        "summary": "Organiza prioridades y rutinas diarias.",
        "accent": "template-accent-slate",
        "category": "Personal",
        "tags": ["Focus", "Rutina", "Productividad"],
        "columns": ["Pendiente", "En foco", "En pausa", "Hecho"],
    },
    {
        "id": "content",
        "name": "Calendario editorial",
        "summary": "Planifica contenidos desde la idea hasta la publicacion.",
        "accent": "template-accent-blue",
        "category": "Marketing",
        "tags": ["Contenido", "SEO", "Blog"],
        "columns": ["Ideas", "Brief", "Redaccion", "Edicion", "Publicado"],
    },
    {
        "id": "design",
        "name": "Sprint de diseno",
        "summary": "Controla research, wireframes y entregables.",
        "accent": "template-accent-violet",
        "category": "Diseno",
        "tags": ["UX", "UI", "Research"],
        "columns": ["Descubrimiento", "Wireframes", "UI", "Revision", "Listo"],
    },
    {
        "id": "recruit",
        "name": "Pipeline de talento",
        "summary": "Gestiona candidatos desde el primer contacto.",
        "accent": "template-accent-amber",
        "category": "Recursos Humanos",
        "tags": ["HR", "Talento", "Entrevistas"],
        "columns": ["Sourcing", "Screening", "Entrevista", "Oferta", "Contratado"],
    },
    {
        "id": "event",
        "name": "Evento y produccion",
        "summary": "Coordina proveedores, agenda y materiales.",
        "accent": "template-accent-rose",
        "category": "Eventos",
        "tags": ["Eventos", "Logistica", "Equipo"],
        "columns": ["Brief", "Proveedores", "Produccion", "Montaje", "Post-evento"],
    },
    {
        "id": "content_ads",
        "name": "Campanas Ads 360",
        "summary": "Planifica anuncios, creatividades y optimizacion.",
        "accent": "template-accent-mint",
        "category": "Marketing",
        "tags": ["Ads", "Performance", "Creativo"],
        "columns": ["Estrategia", "Creatividades", "Lanzamiento", "Optimizacion", "Reporte"],
    },
    {
        "id": "sprint",
        "name": "Sprint agile",
        "summary": "Backlog, trabajo en curso y cierre.",
        "accent": "template-accent-slate",
        "category": "Producto",
        "tags": ["Agile", "Scrum", "Equipo"],
        "columns": ["Backlog", "En progreso", "QA", "Done"],
    },
    {
        "id": "roadmap",
        "name": "Roadmap trimestral",
        "summary": "Visualiza iniciativas por trimestre.",
        "accent": "template-accent-blue",
        "category": "Producto",
        "tags": ["Estrategia", "Producto", "Visibilidad"],
        "columns": ["Q1", "Q2", "Q3", "Q4"],
    },
    {
        "id": "crm",
        "name": "CRM ligero",
        "summary": "Seguimiento simple de clientes y oportunidades.",
        "accent": "template-accent-amber",
        "category": "Ventas",
        "tags": ["CRM", "Clientes", "Ventas"],
        "columns": ["Nuevo lead", "Contacto", "Demo", "Propuesta", "Cerrado"],
    },
    {
        "id": "support_plus",
        "name": "Soporte avanzado",
        "summary": "Gestiona incidencias con prioridades y SLA.",
        "accent": "template-accent-rose",
        "category": "Soporte",
        "tags": ["Support", "SLA", "Prioridades"],
        "columns": ["Nuevo", "Triaged", "En curso", "Esperando", "Resuelto"],
    },
    {
        "id": "qa",
        "name": "QA y pruebas",
        "summary": "Flujo de testing y control de calidad.",
        "accent": "template-accent-violet",
        "category": "Calidad",
        "tags": ["QA", "Testing", "Bugs"],
        "columns": ["Pendiente", "En test", "Bug", "Re-test", "Aprobado"],
    },
    {
        "id": "ops_weekly",
        "name": "Operaciones semanal",
        "summary": "Rutinas y tareas repetitivas del equipo.",
        "accent": "template-accent-mint",
        "category": "Operaciones",
        "tags": ["Ops", "Checklist", "Rutinas"],
        "columns": ["Por hacer", "En curso", "Bloqueado", "Completado"],
    },
    {
        "id": "study",
        "name": "Plan de estudio DAW",
        "summary": "Modulos, practicas y entregas por semana.",
        "accent": "template-accent-slate",
        "category": "Educacion",
        "tags": ["DAW", "Estudio", "Calendario"],
        "columns": ["Semana actual", "En progreso", "Por entregar", "Hecho"],
    },
    {
        "id": "launch_checklist",
        "name": "Checklist de lanzamiento",
        "summary": "Control final antes de publicar una version.",
        "accent": "template-accent-blue",
        "category": "Producto",
        "tags": ["Release", "Checklist", "QA"],
        "columns": ["Preparacion", "Validacion", "Go/No-Go", "Lanzado"],
    },
    {
        "id": "social",
        "name": "Contenido social",
        "summary": "Planifica posts, disenos y publicaciones.",
        "accent": "template-accent-rose",
        "category": "Marketing",
        "tags": ["Social", "Creativo", "Calendario"],
        "columns": ["Ideas", "Produccion", "Revision", "Programado", "Publicado"],
    },
    {
        "id": "client",
        "name": "Onboarding clientes",
        "summary": "Pasos claros desde kick-off hasta entrega.",
        "accent": "template-accent-amber",
        "category": "Negocio",
        "tags": ["Clientes", "Onboarding", "Servicios"],
        "columns": ["Kick-off", "Recursos", "Implementacion", "Revision", "Entrega"],
    },
    {
        "id": "finance",
        "name": "Finanzas mensuales",
        "summary": "Controla presupuestos, pagos y cierres.",
        "accent": "template-accent-mint",
        "category": "Finanzas",
        "tags": ["Finanzas", "Budget", "Control"],
        "columns": ["Ingresos", "Gastos", "Pendiente", "Cerrado"],
    },
    {
        "id": "product_feedback",
        "name": "Feedback de producto",
        "summary": "Recoge ideas y prioriza mejoras.",
        "accent": "template-accent-violet",
        "category": "Producto",
        "tags": ["Feedback", "Producto", "Ideas"],
        "columns": ["Nuevo", "Analisis", "Priorizado", "En desarrollo", "Hecho"],
    },
    {
        "id": "agency",
        "name": "Agencia creativa",
        "summary": "Gestiona clientes, briefs y entregas.",
        "accent": "template-accent-blue",
        "category": "Agencia",
        "tags": ["Agencia", "Creativo", "Clientes"],
        "columns": ["Brief", "Concepto", "Produccion", "Revision", "Entrega"],
    },
    {
        "id": "personal_goals",
        "name": "Objetivos personales",
        "summary": "Objetivos mensuales con seguimiento visual.",
        "accent": "template-accent-slate",
        "category": "Personal",
        "tags": ["Goals", "Habitos", "Progreso"],
        "columns": ["Objetivo", "Plan", "En progreso", "Logrado"],
    },
]

# Modelo de usuario: guarda los datos de acceso.
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# Perfil basico del usuario para mostrar su nombre en la interfaz.
class UserProfile(db.Model):
    __tablename__ = 'user_profiles'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    display_name = db.Column(db.String(80), nullable=False)

# Espacio de trabajo que agrupa varios tableros.
class Workspace(db.Model):
    __tablename__ = 'workspaces'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# Tablero individual dentro de un espacio.
class Board(db.Model):
    __tablename__ = 'boards'

    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# Columna dentro de un tablero.
class BoardColumn(db.Model):
    __tablename__ = 'board_columns'

    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id'), nullable=False, index=True)
    title = db.Column(db.String(120), nullable=False)
    position = db.Column(db.Integer, nullable=False, default=0)

# Tarjeta o tarea dentro de una columna.
class Card(db.Model):
    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True)
    column_id = db.Column(db.Integer, db.ForeignKey('board_columns.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

=======
    {
        "id": "product",
        "name": "Lanzamiento de producto",
        "summary": "Coordina idea, validacion y salida al mercado.",
        "accent": "template-accent-blue",
        "category": "Producto",
        "tags": ["Roadmap", "Sprint", "Go-to-market"],
        "columns": ["Idea", "En progreso", "Validacion", "Listo"],
    },
    {
        "id": "marketing",
        "name": "Campana de marketing",
        "summary": "Gestiona creatividades, anuncios y calendario.",
        "accent": "template-accent-violet",
        "category": "Marketing",
        "tags": ["Contenido", "Ads", "Social"],
        "columns": ["Brief", "Produccion", "Revision", "Publicado"],
    },
    {
        "id": "ventas",
        "name": "Pipeline de ventas",
        "summary": "Controla leads, propuestas y cierres.",
        "accent": "template-accent-amber",
        "category": "Ventas",
        "tags": ["CRM", "Negociacion", "Seguimiento"],
        "columns": ["Lead", "Contacto", "Propuesta", "Cerrado"],
    },
    {
        "id": "ops",
        "name": "Operaciones internas",
        "summary": "Mantiene procesos, tareas recurrentes y calidad.",
        "accent": "template-accent-mint",
        "category": "Operaciones",
        "tags": ["Procesos", "Checklist", "Equipo"],
        "columns": ["Pendiente", "En curso", "Bloqueado", "Listo"],
    },
    {
        "id": "support",
        "name": "Soporte y tickets",
        "summary": "Prioriza solicitudes y mejora la experiencia.",
        "accent": "template-accent-rose",
        "category": "Soporte",
        "tags": ["Customer", "Feedback", "SLA"],
        "columns": ["Nuevo", "Asignado", "Investigando", "Resuelto"],
    },
    {
        "id": "personal",
        "name": "Plan semanal personal",
        "summary": "Organiza prioridades y rutinas diarias.",
        "accent": "template-accent-slate",
        "category": "Personal",
        "tags": ["Focus", "Rutina", "Productividad"],
        "columns": ["Pendiente", "En foco", "En pausa", "Hecho"],
    },
    {
        "id": "content",
        "name": "Calendario editorial",
        "summary": "Planifica contenidos desde la idea hasta la publicacion.",
        "accent": "template-accent-blue",
        "category": "Marketing",
        "tags": ["Contenido", "SEO", "Blog"],
        "columns": ["Ideas", "Brief", "Redaccion", "Edicion", "Publicado"],
    },
    {
        "id": "design",
        "name": "Sprint de diseno",
        "summary": "Controla research, wireframes y entregables.",
        "accent": "template-accent-violet",
        "category": "Diseno",
        "tags": ["UX", "UI", "Research"],
        "columns": ["Descubrimiento", "Wireframes", "UI", "Revision", "Listo"],
    },
    {
        "id": "recruit",
        "name": "Pipeline de talento",
        "summary": "Gestiona candidatos desde el primer contacto.",
        "accent": "template-accent-amber",
        "category": "Recursos Humanos",
        "tags": ["HR", "Talento", "Entrevistas"],
        "columns": ["Sourcing", "Screening", "Entrevista", "Oferta", "Contratado"],
    },
    {
        "id": "event",
        "name": "Evento y produccion",
        "summary": "Coordina proveedores, agenda y materiales.",
        "accent": "template-accent-rose",
        "category": "Eventos",
        "tags": ["Eventos", "Logistica", "Equipo"],
        "columns": ["Brief", "Proveedores", "Produccion", "Montaje", "Post-evento"],
    },
    {
        "id": "content_ads",
        "name": "Campanas Ads 360",
        "summary": "Planifica anuncios, creatividades y optimizacion.",
        "accent": "template-accent-mint",
        "category": "Marketing",
        "tags": ["Ads", "Performance", "Creativo"],
        "columns": ["Estrategia", "Creatividades", "Lanzamiento", "Optimizacion", "Reporte"],
    },
    {
        "id": "sprint",
        "name": "Sprint agile",
        "summary": "Backlog, trabajo en curso y cierre.",
        "accent": "template-accent-slate",
        "category": "Producto",
        "tags": ["Agile", "Scrum", "Equipo"],
        "columns": ["Backlog", "En progreso", "QA", "Done"],
    },
    {
        "id": "roadmap",
        "name": "Roadmap trimestral",
        "summary": "Visualiza iniciativas por trimestre.",
        "accent": "template-accent-blue",
        "category": "Producto",
        "tags": ["Estrategia", "Producto", "Visibilidad"],
        "columns": ["Q1", "Q2", "Q3", "Q4"],
    },
    {
        "id": "crm",
        "name": "CRM ligero",
        "summary": "Seguimiento simple de clientes y oportunidades.",
        "accent": "template-accent-amber",
        "category": "Ventas",
        "tags": ["CRM", "Clientes", "Ventas"],
        "columns": ["Nuevo lead", "Contacto", "Demo", "Propuesta", "Cerrado"],
    },
    {
        "id": "support_plus",
        "name": "Soporte avanzado",
        "summary": "Gestiona incidencias con prioridades y SLA.",
        "accent": "template-accent-rose",
        "category": "Soporte",
        "tags": ["Support", "SLA", "Prioridades"],
        "columns": ["Nuevo", "Triaged", "En curso", "Esperando", "Resuelto"],
    },
    {
        "id": "qa",
        "name": "QA y pruebas",
        "summary": "Flujo de testing y control de calidad.",
        "accent": "template-accent-violet",
        "category": "Calidad",
        "tags": ["QA", "Testing", "Bugs"],
        "columns": ["Pendiente", "En test", "Bug", "Re-test", "Aprobado"],
    },
    {
        "id": "ops_weekly",
        "name": "Operaciones semanal",
        "summary": "Rutinas y tareas repetitivas del equipo.",
        "accent": "template-accent-mint",
        "category": "Operaciones",
        "tags": ["Ops", "Checklist", "Rutinas"],
        "columns": ["Por hacer", "En curso", "Bloqueado", "Completado"],
    },
    {
        "id": "study",
        "name": "Plan de estudio DAW",
        "summary": "Modulos, practicas y entregas por semana.",
        "accent": "template-accent-slate",
        "category": "Educacion",
        "tags": ["DAW", "Estudio", "Calendario"],
        "columns": ["Semana actual", "En progreso", "Por entregar", "Hecho"],
    },
    {
        "id": "launch_checklist",
        "name": "Checklist de lanzamiento",
        "summary": "Control final antes de publicar una version.",
        "accent": "template-accent-blue",
        "category": "Producto",
        "tags": ["Release", "Checklist", "QA"],
        "columns": ["Preparacion", "Validacion", "Go/No-Go", "Lanzado"],
    },
    {
        "id": "social",
        "name": "Contenido social",
        "summary": "Planifica posts, disenos y publicaciones.",
        "accent": "template-accent-rose",
        "category": "Marketing",
        "tags": ["Social", "Creativo", "Calendario"],
        "columns": ["Ideas", "Produccion", "Revision", "Programado", "Publicado"],
    },
    {
        "id": "client",
        "name": "Onboarding clientes",
        "summary": "Pasos claros desde kick-off hasta entrega.",
        "accent": "template-accent-amber",
        "category": "Negocio",
        "tags": ["Clientes", "Onboarding", "Servicios"],
        "columns": ["Kick-off", "Recursos", "Implementacion", "Revision", "Entrega"],
    },
    {
        "id": "finance",
        "name": "Finanzas mensuales",
        "summary": "Controla presupuestos, pagos y cierres.",
        "accent": "template-accent-mint",
        "category": "Finanzas",
        "tags": ["Finanzas", "Budget", "Control"],
        "columns": ["Ingresos", "Gastos", "Pendiente", "Cerrado"],
    },
    {
        "id": "product_feedback",
        "name": "Feedback de producto",
        "summary": "Recoge ideas y prioriza mejoras.",
        "accent": "template-accent-violet",
        "category": "Producto",
        "tags": ["Feedback", "Producto", "Ideas"],
        "columns": ["Nuevo", "Analisis", "Priorizado", "En desarrollo", "Hecho"],
    },
    {
        "id": "agency",
        "name": "Agencia creativa",
        "summary": "Gestiona clientes, briefs y entregas.",
        "accent": "template-accent-blue",
        "category": "Agencia",
        "tags": ["Agencia", "Creativo", "Clientes"],
        "columns": ["Brief", "Concepto", "Produccion", "Revision", "Entrega"],
    },
    {
        "id": "personal_goals",
        "name": "Objetivos personales",
        "summary": "Objetivos mensuales con seguimiento visual.",
        "accent": "template-accent-slate",
        "category": "Personal",
        "tags": ["Goals", "Habitos", "Progreso"],
        "columns": ["Objetivo", "Plan", "En progreso", "Logrado"],
    },
]

# Modelo de usuario: guarda los datos de acceso.
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# Perfil basico del usuario para mostrar su nombre en la interfaz.
class UserProfile(db.Model):
    __tablename__ = 'user_profiles'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    display_name = db.Column(db.String(80), nullable=False)

# Espacio de trabajo que agrupa varios tableros.
class Workspace(db.Model):
    __tablename__ = 'workspaces'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# Tablero individual dentro de un espacio.
class Board(db.Model):
    __tablename__ = 'boards'

    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# Columna dentro de un tablero.
class BoardColumn(db.Model):
    __tablename__ = 'board_columns'

    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id'), nullable=False, index=True)
    title = db.Column(db.String(120), nullable=False)
    position = db.Column(db.Integer, nullable=False, default=0)

# Tarjeta o tarea dentro de una columna.
class Card(db.Model):
    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True)
    column_id = db.Column(db.Integer, db.ForeignKey('board_columns.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

>>>>>>> c672314 (Update project structure, templates and styles):app.py
# Historial de acciones del usuario.
class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    action = db.Column(db.String(120), nullable=False)
    detail = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


def get_user_or_redirect():
    """Devuelve el usuario actual; si no hay sesion, manda al login."""
<<<<<<< HEAD:Prodify-TFG/Prodify-TFG/app.py
    user_id = session.get('user_id')
    if not user_id:
        return None, redirect(url_for('login'))
    user = db.session.get(User, user_id)
    if not user:
        return None, redirect(url_for('login'))
    return user, None


def get_profile(user):
    """Busca el perfil y, si no existe, crea uno usando el email del usuario."""
    profile = db.session.get(UserProfile, user.id)
    if profile:
        return profile
    name = user.email.split('@')[0].replace('.', ' ').strip().title()
    if not name:
        name = 'Usuario'
    profile = UserProfile(user_id=user.id, display_name=name)
    db.session.add(profile)
    db.session.commit()
    return profile


def is_password_hashed(value):
    """Detecta si una contrasena ya esta guardada como hash seguro."""
    if not value:
        return False
    return value.startswith('pbkdf2:') or value.startswith('scrypt:') or value.startswith('argon2:')


def log_activity(user_id, action, detail):
    """Guarda una accion para mostrarla despues en la pagina de actividad."""
    if not user_id:
        return
    db.session.add(ActivityLog(user_id=user_id, action=action[:120], detail=detail[:255]))
    db.session.commit()


@app.route('/')
def home():
    """Vista principal con espacios y tableros recientes del usuario."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    profile = get_profile(user)
    # Cargamos todos los espacios que pertenecen al usuario logueado.
    workspaces = Workspace.query.filter_by(user_id=user.id).order_by(Workspace.created_at.asc()).all()

    workspace_ids = []
    for w in workspaces:
        workspace_ids.append(w.id)

    boards = []
    if len(workspace_ids) > 0:
        # Si hay espacios, cargamos tambien sus tableros.
        boards = Board.query.filter(Board.workspace_id.in_(workspace_ids)).order_by(Board.created_at.desc()).all()

    boards_by_workspace = {}
    for board in boards:
        # Agrupamos los tableros por espacio para la plantilla HTML.
        if board.workspace_id not in boards_by_workspace:
            boards_by_workspace[board.workspace_id] = []
        boards_by_workspace[board.workspace_id].append(board)

    recent_boards = boards[:4]

    return render_template(
        'index.html',
        user=user,
        profile=profile,
        workspaces=workspaces,
        boards_by_workspace=boards_by_workspace,
        recent_boards=recent_boards,
        active_workspace_id=None,
        active_page='boards',
    )


@app.route('/workspaces/<int:workspace_id>')
def workspace_view(workspace_id):
    """Muestra un espacio concreto y los tableros que contiene."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    profile = get_profile(user)
    workspaces = Workspace.query.filter_by(user_id=user.id).order_by(Workspace.created_at.asc()).all()
    workspace = Workspace.query.filter_by(id=workspace_id, user_id=user.id).first()
    if not workspace:
        return redirect(url_for('home'))

    boards = Board.query.filter_by(workspace_id=workspace.id).order_by(Board.created_at.desc()).all()
    boards_by_workspace = {workspace.id: boards}
    recent_boards = boards[:4]

    return render_template(
        'index.html',
        user=user,
        profile=profile,
        workspaces=workspaces,
        boards_by_workspace=boards_by_workspace,
        recent_boards=recent_boards,
        active_workspace_id=workspace.id,
        active_page='boards',
    )


@app.route('/workspaces/<int:workspace_id>/open')
def open_workspace(workspace_id):
    """Abre el tablero mas reciente del espacio para entrar mas rapido."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    workspace = Workspace.query.filter_by(id=workspace_id, user_id=user.id).first()
    if not workspace:
        return redirect(url_for('home'))

    board = Board.query.filter_by(workspace_id=workspace.id).order_by(Board.created_at.desc()).first()
    if board:
        return redirect(url_for('board_view', board_id=board.id))
    return redirect(url_for('workspace_view', workspace_id=workspace.id))

@app.route('/plantillas')
def templates_page():
    """Muestra las plantillas disponibles para crear tableros."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    profile = get_profile(user)
    workspaces = Workspace.query.filter_by(user_id=user.id).order_by(Workspace.created_at.asc()).all()
    # Ordenamos las plantillas por categoria para presentarlas mejor.
    grouped_templates = {}
    for template in BOARD_TEMPLATES:
        category = template.get('category', 'Otros')
        if category not in grouped_templates:
            grouped_templates[category] = []
        grouped_templates[category].append(template)
    template_categories = list(grouped_templates.keys())

    return render_template(
        'plantillas.html',
        user=user,
        profile=profile,
        workspaces=workspaces,
        templates=BOARD_TEMPLATES,
        grouped_templates=grouped_templates,
        template_categories=template_categories,
        active_page='templates',
    )


def render_account_page(title, description):
    """Funcion auxiliar para reutilizar la misma vista en varias paginas de cuenta."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    profile = get_profile(user)
    workspaces = Workspace.query.filter_by(user_id=user.id).order_by(Workspace.created_at.asc()).all()

    activities = []
    # Solo se cargan actividades cuando estamos en la pagina correspondiente.
    if title == 'Actividad':
        activities = (
            ActivityLog.query.filter_by(user_id=user.id)
            .order_by(ActivityLog.created_at.desc())
            .limit(10)
            .all()
        )

    return render_template(
        'account_page.html',
        user=user,
        profile=profile,
        workspaces=workspaces,
        page_title=title,
        page_description=description,
        activities=activities,
        active_page='account',
    )


=======
    user_id = session.get('user_id')
    if not user_id:
        return None, redirect(url_for('login'))
    user = db.session.get(User, user_id)
    if not user:
        return None, redirect(url_for('login'))
    return user, None


def get_profile(user):
    """Busca el perfil y, si no existe, crea uno usando el email del usuario."""
    profile = db.session.get(UserProfile, user.id)
    if profile:
        return profile
    name = user.email.split('@')[0].replace('.', ' ').strip().title()
    if not name:
        name = 'Usuario'
    profile = UserProfile(user_id=user.id, display_name=name)
    db.session.add(profile)
    db.session.commit()
    return profile


def is_password_hashed(value):
    """Detecta si una contrasena ya esta guardada como hash seguro."""
    if not value:
        return False
    return value.startswith('pbkdf2:') or value.startswith('scrypt:') or value.startswith('argon2:')


def log_activity(user_id, action, detail):
    """Guarda una accion para mostrarla despues en la pagina de actividad."""
    if not user_id:
        return
    db.session.add(ActivityLog(user_id=user_id, action=action[:120], detail=detail[:255]))
    db.session.commit()


def get_user_display_data(user, profile):
    """Prepara el nombre y la inicial para mostrarlos en las plantillas."""
    if profile and profile.display_name:
        return {
            "user_name": profile.display_name,
            "user_initial": profile.display_name[0].upper(),
        }

    email_name = user.email.split('@')[0]
    return {
        "user_name": email_name,
        "user_initial": user.email[0].upper(),
    }


def get_text_initial(text):
    """Devuelve la inicial en mayuscula de un texto."""
    if not text:
        return ''
    return text[0].upper()


def build_side_nav_html(active_page):
    """Genera el menu lateral principal."""
    links = [
        ('boards', 'Tableros', url_for('home')),
        ('templates', 'Plantillas', url_for('templates_page')),
        ('home', 'Inicio', url_for('landing')),
    ]

    html = ['<nav class="side-nav d-flex flex-column">']
    for key, label, href in links:
        active_class = ' active' if active_page == key else ''
        html.append(f'<a class="side-link{active_class}" href="{escape(href)}">{escape(label)}</a>')
    html.append('</nav>')
    return Markup(''.join(html))


def build_workspace_list_html(workspaces, active_workspace_id=None):
    """Genera la lista de espacios del sidebar."""
    if not workspaces:
        return Markup('<div class="workspace-item empty-note">Aun no tienes espacios de trabajo.</div>')

    html = []
    for workspace in workspaces:
        active_class = ' active' if active_workspace_id == workspace.id else ''
        href = url_for('open_workspace', workspace_id=workspace.id)
        html.append(
            f'<a class="workspace-item{active_class}" href="{escape(href)}">'
            f'<span class="workspace-avatar">{escape(get_text_initial(workspace.name))}</span>'
            f'<span>{escape(workspace.name)}</span>'
            '</a>'
        )
    return Markup(''.join(html))


def build_account_menu_html(user_name, user_initial, user_email):
    """Genera el menu desplegable de la cuenta."""
    html = [
        '<div class="account-menu" id="accountMenu" hidden>',
        '<div class="account-section-title">Cuenta</div>',
        '<div class="account-hero">',
        f'<div class="account-avatar">{escape(user_initial)}</div>',
        '<div class="account-meta">',
        f'<strong>{escape(user_name)}</strong>',
        f'<span>{escape(user_email)}</span>',
        '<small>Cuenta activa</small>',
        '</div>',
        '</div>',
        '<div class="account-links">',
        f'<a class="account-link" href="{escape(url_for("login"))}">Cambiar cuentas</a>',
        f'<a class="account-link account-link-ext" href="{escape(url_for("account_page"))}">Gestionar cuenta</a>',
        '</div>',
        '<div class="account-divider"></div>',
        '<div class="account-section-title">Prodify</div>',
        '<div class="account-links">',
        f'<a class="account-link" href="{escape(url_for("profile_page"))}">Perfil y visibilidad</a>',
        f'<a class="account-link" href="{escape(url_for("activity_page"))}">Actividad</a>',
        f'<a class="account-link" href="{escape(url_for("cards_page"))}">Tarjetas</a>',
        f'<a class="account-link" href="{escape(url_for("settings_page"))}">Ajustes</a>',
        '</div>',
        '<div class="account-divider"></div>',
        '<div class="account-links">',
        f'<a class="account-link" href="{escape(url_for("help_page"))}">Ayuda</a>',
        '</div>',
        '<div class="account-divider"></div>',
        f'<form action="{escape(url_for("logout"))}" method="POST" class="account-logout">',
        '<button type="submit" class="logout-btn">Cerrar sesion</button>',
        '</form>',
        '</div>',
    ]
    return Markup(''.join(html))


def build_recent_boards_html(recent_boards):
    """Genera el bloque de tableros recientes."""
    if not recent_boards:
        return Markup(
            '<div class="col-12 col-md-6 col-xl-6">'
            '<article class="board-card board-create h-100">'
            '<div class="board-create-text">Crea tu primer tablero</div>'
            '</article>'
            '</div>'
        )

    html = []
    for index, board in enumerate(recent_boards, start=1):
        preview_class = ' board-preview-b' if index % 2 == 0 else ''
        delete_url = url_for('delete_board', board_id=board.id)
        board_url = url_for('board_view', board_id=board.id)
        html.append(
            '<div class="col-12 col-md-6 col-xl-6">'
            '<article class="board-card h-100">'
            f'<form action="{escape(delete_url)}" method="POST" class="board-delete-form">'
            '<button type="submit" class="board-delete-btn js-delete-board" title="Borrar tablero">×</button>'
            '</form>'
            f'<a class="board-link" href="{escape(board_url)}">'
            f'<div class="board-preview{preview_class}"></div>'
            f'<div class="board-name">{escape(board.name)}</div>'
            '</a>'
            '</article>'
            '</div>'
        )
    return Markup(''.join(html))


def build_workspace_blocks_html(workspaces, boards_by_workspace, active_workspace_id):
    """Genera los bloques principales de espacios y tableros."""
    html = []
    for workspace in workspaces:
        if active_workspace_id and active_workspace_id != workspace.id:
            continue

        workspace_boards = boards_by_workspace.get(workspace.id, [])
        html.append('<div class="workspace-block">')
        html.append('<div class="workspace-header">')
        html.append('<div class="workspace-label">')
        html.append(f'<span class="workspace-avatar">{escape(get_text_initial(workspace.name))}</span>')
        html.append(f'<strong>{escape(workspace.name)}</strong>')
        html.append('</div>')
        html.append('<div class="workspace-actions">')
        html.append('<button type="button" class="btn btn-sm">Tableros</button>')
        html.append('<button type="button" class="btn btn-sm">Miembros</button>')
        html.append('<button type="button" class="btn btn-sm">Configuracion</button>')
        html.append(
            f'<form action="{escape(url_for("delete_workspace", workspace_id=workspace.id))}" method="POST" class="inline-form">'
            '<button type="submit" class="workspace-delete-btn js-delete-workspace btn btn-sm">Eliminar</button>'
            '</form>'
        )
        html.append('</div></div>')
        html.append('<div class="boards-row row g-3">')

        for index, board in enumerate(workspace_boards, start=1):
            preview_class = ' board-preview-b' if index % 2 == 0 else ''
            html.append('<div class="col-12 col-md-6 col-xl-6">')
            html.append('<article class="board-card h-100">')
            html.append(
                f'<form action="{escape(url_for("delete_board", board_id=board.id))}" method="POST" class="board-delete-form">'
                '<button type="submit" class="board-delete-btn js-delete-board" title="Borrar tablero">×</button>'
                '</form>'
            )
            html.append(f'<a class="board-link" href="{escape(url_for("board_view", board_id=board.id))}">')
            html.append(f'<div class="board-preview{preview_class}"></div>')
            html.append(f'<div class="board-name">{escape(board.name)}</div>')
            html.append('</a></article></div>')

        html.append(
            f'<div class="col-12 col-md-6 col-xl-6">'
            f'<article class="board-card board-create js-create-board h-100" data-workspace-id="{workspace.id}">'
            '<div class="board-create-text">Crear un tablero nuevo</div>'
            '</article>'
            '</div>'
        )
        html.append('</div></div>')
    return Markup(''.join(html))


def build_templates_sidebar_html(template_categories, grouped_templates):
    """Genera el indice lateral de plantillas."""
    html = []
    for category in template_categories:
        html.append('<details class="template-group" open>')
        html.append(f'<summary>{escape(category)}</summary>')
        html.append('<div class="template-group-links">')
        for template in grouped_templates.get(category, []):
            html.append(f'<a href="#template-{escape(template["id"])}">{escape(template["name"])}</a>')
        html.append('</div></details>')
    return Markup(''.join(html))


def build_templates_grid_html(templates):
    """Genera las tarjetas del catalogo de plantillas."""
    html = []
    for template in templates:
        html.append(
            f'<article class="template-card {escape(template["accent"])}" id="template-{escape(template["id"])}">'
            '<div class="template-head"><div>'
            f'<h3>{escape(template["name"])}</h3>'
            f'<p>{escape(template["summary"])}</p>'
            '</div>'
            f'<button type="button" class="template-action js-use-template" data-template-name="{escape(template["name"])}" data-template-id="{escape(template["id"])}">'
            'Usar plantilla</button></div>'
            '<div class="template-tags">'
        )
        for tag in template["tags"]:
            html.append(f'<span>#{escape(tag)}</span>')
        html.append('</div><div class="template-preview">')
        for column in template["columns"]:
            html.append(
                '<div class="preview-col">'
                f'<div class="preview-title">{escape(column)}</div>'
                '<div class="preview-card"></div>'
                '<div class="preview-card small"></div>'
                '</div>'
            )
        html.append('</div></article>')
    return Markup(''.join(html))


def build_board_columns_html(columns, cards_by_column):
    """Genera las columnas del kanban con sus tarjetas."""
    html = []
    for column in columns:
        html.append(f'<div class="kanban-column" data-column-id="{column.id}">')
        html.append('<div class="kanban-title">')
        html.append(f'<h3>{escape(column.title)}</h3>')
        html.append('<div class="kanban-actions">')
        html.append(f'<button type="button" class="add-card-btn js-add-card" data-column-id="{column.id}">+ Tarea</button>')
        html.append(
            f'<form action="{escape(url_for("delete_column", column_id=column.id))}" method="POST" class="inline-form">'
            '<button type="submit" class="delete-col-btn js-delete-column" title="Eliminar columna">Eliminar</button>'
            '</form>'
        )
        html.append('</div></div>')
        html.append(f'<div class="kanban-cards" data-column-id="{column.id}">')
        column_cards = cards_by_column.get(column.id, [])
        if column_cards:
            for card in column_cards:
                html.append(
                    f'<div class="kanban-card" draggable="true" data-card-id="{card.id}">'
                    f'<span class="card-title">{escape(card.title)}</span>'
                    f'<form action="{escape(url_for("delete_card", card_id=card.id))}" method="POST" class="card-delete-form">'
                    '<button type="submit" class="card-delete-btn js-delete-card" title="Eliminar tarea" draggable="false">×</button>'
                    '</form>'
                    '</div>'
                )
        else:
            html.append('<div class="kanban-card ghost">Sin tareas aun</div>')
        html.append('</div></div>')
    return Markup(''.join(html))


def build_login_error_html(error):
    """Genera el bloque de error del login si existe."""
    if not error:
        return Markup('')
    return Markup(f'<div class="login-error">{escape(error)}</div>')


def build_account_content_html(page_title, page_description, user_name, user_initial, user_email, activities):
    """Genera el contenido principal de la pagina de cuenta."""
    hero = [
        '<div class="account-page">',
        '<div class="account-page-hero">',
        '<div class="account-hero-left">',
        '<span class="eyebrow">Cuenta</span>',
        f'<h1>{escape(page_title)}</h1>',
        f'<p>{escape(page_description)}</p>',
        '<div class="hero-chips"><span class="chip">Equipo</span><span class="chip">Flujos activos</span><span class="chip">Productividad</span></div>',
        '</div>',
        '<div class="account-hero-stack">',
        '<div class="account-hero-card"><div class="account-hero-tag">Estado</div><strong>Activo</strong><span>Ultimo acceso: hoy</span></div>',
        '<div class="account-hero-card alt"><div class="account-hero-tag">Ritmo</div><strong>+12%</strong><span>Semana vs semana</span></div>',
        '</div></div>',
    ]

    if page_title == 'Gestionar cuenta':
        hero.append(
            '<div class="account-grid">'
            '<div class="account-page-card"><h3>Informacion de la cuenta</h3>'
            '<div class="account-page-row"><span>Nombre</span>'
            f'<strong>{escape(user_name)}</strong></div>'
            '<div class="account-page-row"><span>Email</span>'
            f'<strong>{escape(user_email)}</strong></div>'
            '<div class="account-page-row"><span>Plan</span><strong>Demo local</strong></div></div>'
            '<div class="account-page-card"><h3>Seguridad</h3><p>Buenas practicas activas para proteger la cuenta.</p>'
            '<div class="pill-row"><span class="pill">Sesion segura</span><span class="pill">Hash de contrasenas</span><span class="pill">Validacion basica</span></div></div>'
            '<div class="account-page-card"><h3>Acciones rapidas</h3><div class="action-list"><button type="button" class="action-btn">Cambiar contrasena</button><button type="button" class="action-btn">Actualizar email</button><button type="button" class="action-btn">Cerrar sesiones</button></div></div>'
            '<div class="account-page-card wide-card"><div class="split-head"><div><h3>Resumen del entorno</h3><p>Vista rapida de espacios, tableros y tareas.</p></div><span class="badge-soft">Actualizado</span></div>'
            '<div class="stat-grid expanded"><div class="stat-card"><strong>6</strong><span>Espacios activos</span></div><div class="stat-card"><strong>18</strong><span>Tableros en uso</span></div><div class="stat-card"><strong>42</strong><span>Tarjetas vivas</span></div><div class="stat-card"><strong>9</strong><span>En progreso</span></div></div></div>'
            '</div>'
        )
    elif page_title == 'Perfil y visibilidad':
        hero.append(
            '<div class="account-grid">'
            '<div class="account-page-card"><h3>Tu identidad en Prodify</h3><p>Asi se vera tu perfil dentro de los tableros.</p><div class="profile-preview">'
            f'<div class="profile-avatar">{escape(user_initial)}</div><div><strong>{escape(user_name)}</strong><span>{escape(user_email)}</span></div></div></div>'
            '<div class="account-page-card"><h3>Visibilidad</h3><div class="toggle-list"><div class="toggle-item"><div><strong>Mostrar email</strong><span>Visible solo en tu perfil.</span></div><div class="toggle-pill">Activo</div></div><div class="toggle-item"><div><strong>Estado en linea</strong><span>Indica actividad reciente.</span></div><div class="toggle-pill">Activo</div></div></div></div>'
            '<div class="account-page-card"><h3>Imagen de perfil</h3><p>Sube una foto para personalizar tu cuenta.</p><button type="button" class="action-btn wide">Subir imagen</button></div>'
            '<div class="account-page-card"><h3>Badges profesionales</h3><div class="pill-row"><span class="pill neon">Manager</span><span class="pill neon">UX Focus</span><span class="pill neon">Agile</span></div></div>'
            '<div class="account-page-card wide-card"><h3>Vista de firma</h3><div class="signature-card">'
            f'<div class="signature-avatar">{escape(user_initial)}</div><div><strong>{escape(user_name)}</strong><span>{escape(user_email)}</span><span class="muted">Equipo Prodify · Madrid</span></div>'
            '<div class="signature-badges"><span>Roadmap</span><span>Ops</span></div></div></div>'
            '</div>'
        )
    elif page_title == 'Actividad':
        activity_html = []
        if activities:
            for item in activities:
                activity_html.append(
                    '<div class="activity-item"><span class="activity-dot"></span><div>'
                    f'<strong>{escape(item.action)}</strong><span>{escape(item.detail)}</span></div>'
                    f'<small>{escape(item.created_at.strftime("%d/%m %H:%M"))}</small></div>'
                )
        else:
            activity_html.append(
                '<div class="activity-item"><span class="activity-dot"></span><div><strong>Aun no hay actividad</strong><span>Realiza acciones en tus tableros para verlas aqui.</span></div><small>Ahora</small></div>'
            )
        hero.append(
            '<div class="account-grid">'
            '<div class="account-page-card"><h3>Actividad reciente</h3><div class="activity-list">'
            + ''.join(activity_html) +
            '</div></div>'
            '<div class="account-page-card"><h3>Resumen semanal</h3><div class="stat-grid"><div class="stat-card"><strong>12</strong><span>Tarjetas movidas</span></div><div class="stat-card"><strong>4</strong><span>Tableros activos</span></div><div class="stat-card"><strong>2</strong><span>Espacios nuevos</span></div></div></div>'
            '<div class="account-page-card wide-card"><h3>Linea de tiempo</h3><div class="timeline"><div class="timeline-item"><span class="timeline-dot"></span><div><strong>Checklist actualizado</strong><span>Tablero Operaciones · 09:40</span></div></div><div class="timeline-item"><span class="timeline-dot"></span><div><strong>Nueva tarjeta creada</strong><span>Marketing · 08:15</span></div></div><div class="timeline-item"><span class="timeline-dot"></span><div><strong>Columna reordenada</strong><span>Ventas · Ayer</span></div></div></div></div>'
            '</div>'
        )
    elif page_title == 'Tarjetas':
        hero.append(
            '<div class="account-grid"><div class="account-page-card"><h3>Tarjetas destacadas</h3><div class="kanban-mini"><div class="kanban-mini-col"><div class="kanban-mini-title">Pendiente</div><div class="kanban-mini-card">Revisar landing</div><div class="kanban-mini-card">Checklist sprint</div></div><div class="kanban-mini-col"><div class="kanban-mini-title">En progreso</div><div class="kanban-mini-card">Campana marzo</div></div><div class="kanban-mini-col"><div class="kanban-mini-title">Listo</div><div class="kanban-mini-card">Actualizar roadmap</div></div></div></div><div class="account-page-card"><h3>Filtros rapidos</h3><div class="pill-row"><span class="pill">Mis tareas</span><span class="pill">Prioridad alta</span><span class="pill">Vencen hoy</span></div></div><div class="account-page-card wide-card"><h3>Backlog prioritario</h3><div class="backlog-list"><div class="backlog-item"><span class="priority high">Alta</span><div><strong>Revisar onboarding</strong><span>UX Team · 2 dias</span></div></div><div class="backlog-item"><span class="priority med">Media</span><div><strong>Optimizar reports</strong><span>Ops · 5 dias</span></div></div><div class="backlog-item"><span class="priority low">Baja</span><div><strong>Actualizar etiquetas</strong><span>General · 1 semana</span></div></div></div></div></div>'
        )
    elif page_title == 'Ajustes':
        hero.append(
            '<div class="account-grid"><div class="account-page-card"><h3>Preferencias generales</h3><div class="toggle-list"><div class="toggle-item"><div><strong>Notificaciones por email</strong><span>Resumen diario de actividad.</span></div><div class="toggle-pill">Activo</div></div><div class="toggle-item"><div><strong>Modo enfoque</strong><span>Reduce distracciones.</span></div><div class="toggle-pill">Activo</div></div></div></div><div class="account-page-card"><h3>Integraciones</h3><div class="action-list"><button type="button" class="action-btn">Conectar Google</button><button type="button" class="action-btn">Conectar Slack</button></div></div><div class="account-page-card"><h3>Notificaciones in-app</h3><div class="toggle-list"><div class="toggle-item"><div><strong>Alertas de tablero</strong><span>Se muestran en la campana.</span></div><div class="toggle-pill">Activo</div></div><div class="toggle-item"><div><strong>Recordatorios</strong><span>Antes de vencimientos.</span></div><div class="toggle-pill">Activo</div></div></div></div></div>'
        )
    elif page_title == 'Ayuda':
        hero.append(
            '<div class="account-grid"><div class="account-page-card"><h3>Centro de ayuda</h3><div class="help-grid"><div class="help-card"><strong>Guias rapidas</strong><span>Empieza a usar tableros en minutos.</span></div><div class="help-card"><strong>Preguntas frecuentes</strong><span>Resuelve dudas comunes.</span></div><div class="help-card"><strong>Contacto</strong><span>Escribenos para soporte.</span></div></div></div><div class="account-page-card"><h3>Recursos pro</h3><div class="resource-list"><div class="resource-item">Guia Kanban avanzada</div><div class="resource-item">Plantillas de equipos</div><div class="resource-item">Buenas practicas de productividad</div></div></div></div>'
        )

    hero.append('</div>')
    return Markup(''.join(hero))


@app.route('/')
def home():
    """Vista principal con espacios y tableros recientes del usuario."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    profile = get_profile(user)
    user_display = get_user_display_data(user, profile)
    # Cargamos todos los espacios que pertenecen al usuario logueado.
    workspaces = Workspace.query.filter_by(user_id=user.id).order_by(Workspace.created_at.asc()).all()

    workspace_ids = []
    for w in workspaces:
        workspace_ids.append(w.id)

    boards = []
    if len(workspace_ids) > 0:
        # Si hay espacios, cargamos tambien sus tableros.
        boards = Board.query.filter(Board.workspace_id.in_(workspace_ids)).order_by(Board.created_at.desc()).all()

    boards_by_workspace = {}
    for board in boards:
        # Agrupamos los tableros por espacio para la plantilla HTML.
        if board.workspace_id not in boards_by_workspace:
            boards_by_workspace[board.workspace_id] = []
        boards_by_workspace[board.workspace_id].append(board)

    recent_boards = boards[:4]

    return render_template(
        'index.html',
        user=user,
        profile=profile,
        user_name=user_display['user_name'],
        user_initial=user_display['user_initial'],
        account_menu_html=build_account_menu_html(user_display['user_name'], user_display['user_initial'], user.email),
        side_nav_html=build_side_nav_html('boards'),
        workspace_list_html=build_workspace_list_html(workspaces),
        recent_boards_html=build_recent_boards_html(recent_boards),
        workspace_blocks_html=build_workspace_blocks_html(workspaces, boards_by_workspace, None),
    )


@app.route('/workspaces/<int:workspace_id>')
def workspace_view(workspace_id):
    """Muestra un espacio concreto y los tableros que contiene."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    profile = get_profile(user)
    user_display = get_user_display_data(user, profile)
    workspaces = Workspace.query.filter_by(user_id=user.id).order_by(Workspace.created_at.asc()).all()
    workspace = Workspace.query.filter_by(id=workspace_id, user_id=user.id).first()
    if not workspace:
        return redirect(url_for('home'))

    boards = Board.query.filter_by(workspace_id=workspace.id).order_by(Board.created_at.desc()).all()
    boards_by_workspace = {workspace.id: boards}
    recent_boards = boards[:4]

    return render_template(
        'index.html',
        user=user,
        profile=profile,
        user_name=user_display['user_name'],
        user_initial=user_display['user_initial'],
        account_menu_html=build_account_menu_html(user_display['user_name'], user_display['user_initial'], user.email),
        side_nav_html=build_side_nav_html('boards'),
        workspace_list_html=build_workspace_list_html(workspaces, workspace.id),
        recent_boards_html=build_recent_boards_html(recent_boards),
        workspace_blocks_html=build_workspace_blocks_html(workspaces, boards_by_workspace, workspace.id),
    )


@app.route('/workspaces/<int:workspace_id>/open')
def open_workspace(workspace_id):
    """Abre el tablero mas reciente del espacio para entrar mas rapido."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    workspace = Workspace.query.filter_by(id=workspace_id, user_id=user.id).first()
    if not workspace:
        return redirect(url_for('home'))

    board = Board.query.filter_by(workspace_id=workspace.id).order_by(Board.created_at.desc()).first()
    if board:
        return redirect(url_for('board_view', board_id=board.id))
    return redirect(url_for('workspace_view', workspace_id=workspace.id))

@app.route('/plantillas')
def templates_page():
    """Muestra las plantillas disponibles para crear tableros."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    profile = get_profile(user)
    user_display = get_user_display_data(user, profile)
    workspaces = Workspace.query.filter_by(user_id=user.id).order_by(Workspace.created_at.asc()).all()
    # Ordenamos las plantillas por categoria para presentarlas mejor.
    grouped_templates = {}
    for template in BOARD_TEMPLATES:
        category = template.get('category', 'Otros')
        if category not in grouped_templates:
            grouped_templates[category] = []
        grouped_templates[category].append(template)
    template_categories = list(grouped_templates.keys())

    return render_template(
        'plantillas.html',
        user=user,
        profile=profile,
        user_name=user_display['user_name'],
        user_initial=user_display['user_initial'],
        account_menu_html=build_account_menu_html(user_display['user_name'], user_display['user_initial'], user.email),
        side_nav_html=build_side_nav_html('templates'),
        workspace_list_html=build_workspace_list_html(workspaces),
        templates_sidebar_html=build_templates_sidebar_html(template_categories, grouped_templates),
        templates_count=len(BOARD_TEMPLATES),
        templates_grid_html=build_templates_grid_html(BOARD_TEMPLATES),
    )


def render_account_page(title, description):
    """Funcion auxiliar para reutilizar la misma vista en varias paginas de cuenta."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    profile = get_profile(user)
    user_display = get_user_display_data(user, profile)
    workspaces = Workspace.query.filter_by(user_id=user.id).order_by(Workspace.created_at.asc()).all()

    activities = []
    # Solo se cargan actividades cuando estamos en la pagina correspondiente.
    if title == 'Actividad':
        activities = (
            ActivityLog.query.filter_by(user_id=user.id)
            .order_by(ActivityLog.created_at.desc())
            .limit(10)
            .all()
        )

    return render_template(
        'account_page.html',
        user=user,
        profile=profile,
        user_name=user_display['user_name'],
        user_initial=user_display['user_initial'],
        account_menu_html=build_account_menu_html(user_display['user_name'], user_display['user_initial'], user.email),
        side_nav_html=build_side_nav_html('account'),
        workspace_list_html=build_workspace_list_html(workspaces),
        page_title=title,
        account_content_html=build_account_content_html(
            title,
            description,
            user_display['user_name'],
            user_display['user_initial'],
            user.email,
            activities,
        ),
    )


>>>>>>> c672314 (Update project structure, templates and styles):app.py
@app.route('/cuenta')
def account_page():
    """Abre la pagina general de la cuenta."""
    return render_account_page(
        'Gestionar cuenta',
        'Aqui puedes revisar los datos basicos de tu cuenta y su estado.',
    )


@app.route('/perfil')
def profile_page():
    """Abre la pagina del perfil visible del usuario."""
    return render_account_page(
        'Perfil y visibilidad',
        'Configuracion basica del perfil y como se muestra tu nombre en la app.',
    )


@app.route('/actividad')
def activity_page():
    """Abre la pagina con el historial reciente."""
    return render_account_page(
        'Actividad',
        'Resumen de acciones recientes dentro de tus tableros y espacios.',
    )


@app.route('/tarjetas')
def cards_page():
    """Abre una vista informativa general sobre tarjetas."""
    return render_account_page(
        'Tarjetas',
        'Listado general de tareas (en esta version se muestra como vista informativa).',
    )


@app.route('/ajustes')
def settings_page():
    """Abre la pagina de ajustes generales."""
    return render_account_page(
        'Ajustes',
        'Preferencias generales de la aplicacion.',
    )


@app.route('/ayuda')
def help_page():
    """Abre la pagina de ayuda basica."""
    return render_account_page(
        'Ayuda',
        'Recursos rapidos para resolver dudas y usar la plataforma.',
    )


@app.route('/inicio')
def landing():
    """Pagina de bienvenida interna tras iniciar sesion."""
<<<<<<< HEAD:Prodify-TFG/Prodify-TFG/app.py
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    profile = get_profile(user)
    workspaces = Workspace.query.filter_by(user_id=user.id).order_by(Workspace.created_at.asc()).all()

    return render_template(
        'inicio.html',
        user=user,
        profile=profile,
        workspaces=workspaces,
        active_page='home',
    )


@app.route('/js/<path:filename>')
def js_static(filename):
    """Sirve archivos JavaScript desde la carpeta /js."""
    return send_from_directory('js', filename)


@app.route('/plantillas/usar', methods=['POST'])
def use_template():
    """Crea un espacio y un tablero nuevos usando una plantilla elegida."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    template_id = (request.form.get('template_id') or '').strip()
    workspace_name = (request.form.get('workspace_name') or '').strip() or 'Nuevo espacio'
    board_name = (request.form.get('board_name') or '').strip() or 'Nuevo tablero'

    # Buscamos la plantilla seleccionada por su id.
    template = None
    for t in BOARD_TEMPLATES:
        if t["id"] == template_id:
            template = t
            break

    if template:
        columns = template["columns"]
    else:
        columns = ["Pendiente", "En progreso", "Listo"]

    # Primero se crea el espacio y despues el tablero dentro de ese espacio.
    workspace = Workspace(user_id=user.id, name=workspace_name[:120])
    db.session.add(workspace)
    db.session.flush()

    board = Board(workspace_id=workspace.id, name=board_name[:120])
    db.session.add(board)
    db.session.flush()

    # Creamos las columnas iniciales definidas por la plantilla.
    pos = 0
    for title in columns:
        db.session.add(BoardColumn(board_id=board.id, title=title[:120], position=pos))
        pos += 1

    db.session.commit()
    log_activity(user.id, 'Plantilla aplicada', f'Tablero "{board.name}" creado en "{workspace.name}"')
    return redirect(url_for('board_view', board_id=board.id))


@app.route('/boards/<int:board_id>')
def board_view(board_id):
    """Muestra un tablero concreto con sus columnas y tarjetas."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    board = (
        db.session.query(Board)
        .join(Workspace, Board.workspace_id == Workspace.id)
        .filter(Board.id == board_id, Workspace.user_id == user.id)
        .first()
    )
    if not board:
        return redirect(url_for('home'))

    # Cargamos las columnas en su orden natural.
    columns = BoardColumn.query.filter_by(board_id=board.id).order_by(BoardColumn.position.asc()).all()
    board_name = board.name
    board_name = board.name
    board_name = board.name
    board_name = board.name
    board_name = board.name
    column_ids = []
    for c in columns:
        column_ids.append(c.id)
    cards = []
    if column_ids:
        # Cargamos todas las tarjetas de ese tablero.
        cards = Card.query.filter(Card.column_id.in_(column_ids)).order_by(Card.created_at.asc()).all()

    cards_by_column = {}
    for card in cards:
        # Agrupamos tarjetas por columna para que el HTML las pinte bien.
        if card.column_id not in cards_by_column:
            cards_by_column[card.column_id] = []
        cards_by_column[card.column_id].append(card)

    return render_template(
        'board.html',
        board=board,
        columns=columns,
        cards_by_column=cards_by_column,
        active_page='boards',
    )


@app.route('/boards/<int:board_id>/columns/create', methods=['POST'])
def create_column(board_id):
    """Crea una nueva columna al final del tablero."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    board = (
        db.session.query(Board)
        .join(Workspace, Board.workspace_id == Workspace.id)
        .filter(Board.id == board_id, Workspace.user_id == user.id)
        .first()
    )
    if not board:
        return redirect(url_for('home'))

    title = (request.form.get('column_title') or '').strip()
    if not title:
        return redirect(url_for('board_view', board_id=board.id))

=======
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    profile = get_profile(user)
    user_display = get_user_display_data(user, profile)
    workspaces = Workspace.query.filter_by(user_id=user.id).order_by(Workspace.created_at.asc()).all()

    return render_template(
        'inicio.html',
        user=user,
        profile=profile,
        user_name=user_display['user_name'],
        user_initial=user_display['user_initial'],
        account_menu_html=build_account_menu_html(user_display['user_name'], user_display['user_initial'], user.email),
        side_nav_html=build_side_nav_html('home'),
        workspace_list_html=build_workspace_list_html(workspaces),
    )


@app.route('/js/<path:filename>')
def js_static(filename):
    """Sirve archivos JavaScript desde la carpeta /js."""
    return send_from_directory('js', filename)


@app.route('/plantillas/usar', methods=['POST'])
def use_template():
    """Crea un espacio y un tablero nuevos usando una plantilla elegida."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    template_id = (request.form.get('template_id') or '').strip()
    workspace_name = (request.form.get('workspace_name') or '').strip() or 'Nuevo espacio'
    board_name = (request.form.get('board_name') or '').strip() or 'Nuevo tablero'

    # Buscamos la plantilla seleccionada por su id.
    template = None
    for t in BOARD_TEMPLATES:
        if t["id"] == template_id:
            template = t
            break

    if template:
        columns = template["columns"]
    else:
        columns = ["Pendiente", "En progreso", "Listo"]

    # Primero se crea el espacio y despues el tablero dentro de ese espacio.
    workspace = Workspace(user_id=user.id, name=workspace_name[:120])
    db.session.add(workspace)
    db.session.flush()

    board = Board(workspace_id=workspace.id, name=board_name[:120])
    db.session.add(board)
    db.session.flush()

    # Creamos las columnas iniciales definidas por la plantilla.
    pos = 0
    for title in columns:
        db.session.add(BoardColumn(board_id=board.id, title=title[:120], position=pos))
        pos += 1

    db.session.commit()
    log_activity(user.id, 'Plantilla aplicada', f'Tablero "{board.name}" creado en "{workspace.name}"')
    return redirect(url_for('board_view', board_id=board.id))


@app.route('/boards/<int:board_id>')
def board_view(board_id):
    """Muestra un tablero concreto con sus columnas y tarjetas."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    board = (
        db.session.query(Board)
        .join(Workspace, Board.workspace_id == Workspace.id)
        .filter(Board.id == board_id, Workspace.user_id == user.id)
        .first()
    )
    if not board:
        return redirect(url_for('home'))

    # Cargamos las columnas en su orden natural.
    columns = BoardColumn.query.filter_by(board_id=board.id).order_by(BoardColumn.position.asc()).all()
    board_name = board.name
    board_name = board.name
    board_name = board.name
    board_name = board.name
    board_name = board.name
    column_ids = []
    for c in columns:
        column_ids.append(c.id)
    cards = []
    if column_ids:
        # Cargamos todas las tarjetas de ese tablero.
        cards = Card.query.filter(Card.column_id.in_(column_ids)).order_by(Card.created_at.asc()).all()

    cards_by_column = {}
    for card in cards:
        # Agrupamos tarjetas por columna para que el HTML las pinte bien.
        if card.column_id not in cards_by_column:
            cards_by_column[card.column_id] = []
        cards_by_column[card.column_id].append(card)

    return render_template(
        'board.html',
        board=board,
        side_nav_html=build_side_nav_html('boards'),
        board_columns_html=build_board_columns_html(columns, cards_by_column),
    )


@app.route('/boards/<int:board_id>/columns/create', methods=['POST'])
def create_column(board_id):
    """Crea una nueva columna al final del tablero."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    board = (
        db.session.query(Board)
        .join(Workspace, Board.workspace_id == Workspace.id)
        .filter(Board.id == board_id, Workspace.user_id == user.id)
        .first()
    )
    if not board:
        return redirect(url_for('home'))

    title = (request.form.get('column_title') or '').strip()
    if not title:
        return redirect(url_for('board_view', board_id=board.id))

>>>>>>> c672314 (Update project structure, templates and styles):app.py
    # Buscamos la ultima posicion ocupada para poner la nueva al final.
    last_position = db.session.query(db.func.max(BoardColumn.position)).filter_by(board_id=board.id).scalar()
    position = (last_position + 1) if last_position is not None else 0
    new_column = BoardColumn(board_id=board.id, title=title[:120], position=position)
    db.session.add(new_column)
    db.session.commit()
    log_activity(user.id, 'Columna creada', f'Columna "{new_column.title}" en "{board.name}"')
    return redirect(url_for('board_view', board_id=board.id))


@app.route('/columns/<int:column_id>/cards/create', methods=['POST'])
def create_card(column_id):
    """Crea una tarjeta nueva dentro de una columna concreta."""
<<<<<<< HEAD:Prodify-TFG/Prodify-TFG/app.py
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    column = (
        db.session.query(BoardColumn)
        .join(Board, BoardColumn.board_id == Board.id)
        .join(Workspace, Board.workspace_id == Workspace.id)
        .filter(BoardColumn.id == column_id, Workspace.user_id == user.id)
        .first()
    )
    if not column:
        return redirect(url_for('home'))

    title = (request.form.get('card_title') or '').strip()
    if not title:
        return redirect(url_for('board_view', board_id=column.board_id))

    new_card = Card(column_id=column.id, title=title[:200])
    db.session.add(new_card)
    db.session.commit()
    board = db.session.get(Board, column.board_id)
    if board:
        log_activity(user.id, 'Tarjeta creada', f'"{new_card.title}" en "{board.name}"')
    return redirect(url_for('board_view', board_id=column.board_id))


@app.route('/columns/<int:column_id>/delete', methods=['POST'])
def delete_column(column_id):
    """Elimina una columna y tambien todas sus tarjetas."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    column = (
        db.session.query(BoardColumn)
        .join(Board, BoardColumn.board_id == Board.id)
        .join(Workspace, Board.workspace_id == Workspace.id)
        .filter(BoardColumn.id == column_id, Workspace.user_id == user.id)
        .first()
    )
    if not column:
        return redirect(url_for('home'))

    column_title = column.title
    board_id = column.board_id
    board = db.session.get(Board, board_id)
    Card.query.filter_by(column_id=column.id).delete(synchronize_session=False)
    db.session.delete(column)
    db.session.commit()
    if board:
        log_activity(user.id, 'Columna eliminada', f'Columna "{column_title}" en "{board.name}"')
    return redirect(url_for('board_view', board_id=board_id))


@app.route('/cards/<int:card_id>/move', methods=['POST'])
def move_card(card_id):
    """Mueve una tarjeta a otra columna usando drag and drop."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    target_column_id = request.form.get('column_id', type=int)
    if not target_column_id:
        return redirect(url_for('home'))

    # Comprobamos que la tarjeta pertenece al usuario actual.
    card = (
        db.session.query(Card)
        .join(BoardColumn, Card.column_id == BoardColumn.id)
        .join(Board, BoardColumn.board_id == Board.id)
        .join(Workspace, Board.workspace_id == Workspace.id)
        .filter(Card.id == card_id, Workspace.user_id == user.id)
        .first()
    )
    if not card:
        return redirect(url_for('home'))

    current_column = db.session.get(BoardColumn, card.column_id)
    if not current_column:
        return redirect(url_for('home'))

    # La columna destino debe pertenecer al mismo tablero.
    target_column = (
        db.session.query(BoardColumn)
        .join(Board, BoardColumn.board_id == Board.id)
        .join(Workspace, Board.workspace_id == Workspace.id)
        .filter(BoardColumn.id == target_column_id, Workspace.user_id == user.id)
        .first()
    )
    if not target_column or target_column.board_id != current_column.board_id:
        return redirect(url_for('board_view', board_id=current_column.board_id))

    card_title = card.title
    card.column_id = target_column_id
    db.session.commit()
    board = db.session.get(Board, target_column.board_id)
    if board:
        log_activity(user.id, 'Tarjeta movida', f'"{card_title}" a "{target_column.title}" en "{board.name}"')
    return ('', 204)


@app.route('/cards/<int:card_id>/delete', methods=['POST'])
def delete_card(card_id):
    """Elimina una tarjeta concreta del tablero."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    card = (
        db.session.query(Card)
        .join(BoardColumn, Card.column_id == BoardColumn.id)
        .join(Board, BoardColumn.board_id == Board.id)
        .join(Workspace, Board.workspace_id == Workspace.id)
        .filter(Card.id == card_id, Workspace.user_id == user.id)
        .first()
    )
    if not card:
        return redirect(url_for('home'))

    card_title = card.title
    board_id = (
        db.session.query(Board.id)
        .join(BoardColumn, BoardColumn.board_id == Board.id)
        .filter(BoardColumn.id == card.column_id)
        .scalar()
    )

    db.session.delete(card)
    db.session.commit()
    if board_id:
        board = db.session.get(Board, board_id)
        if board:
            log_activity(user.id, 'Tarjeta eliminada', f'"{card_title}" en "{board.name}"')
    if board_id:
        return redirect(url_for('board_view', board_id=board_id))
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Muestra el login y valida las credenciales enviadas por el formulario."""
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']

        # Intento rapido para usuarios antiguos guardados en texto plano.
        user = User.query.filter_by(email=email, password=password).first()
        if not user:
            user = User.query.filter_by(email=email).first()

        if user:
            # Si la clave ya estaba protegida, la comprobamos con hash.
            if is_password_hashed(user.password):
                is_ok = check_password_hash(user.password, password)
            else:
                is_ok = (user.password == password)
                if is_ok:
                    # Si entra bien y la clave estaba en plano, la guardamos mas segura.
                    user.password = generate_password_hash(password)
                    db.session.commit()

            if is_ok:
                session['user_id'] = user.id
                log_activity(user.id, 'Inicio de sesion', 'Acceso correcto a la plataforma')
                return redirect(url_for('home'))

        return render_template('login.html', error='Credenciales invalidas')

    return render_template('login.html', error=None)


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    """Cierra la sesion actual del usuario."""
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/workspaces/create', methods=['POST'])
def create_workspace():
    """Crea un espacio nuevo y un tablero principal por defecto."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    name = (request.form.get('workspace_name') or '').strip()
    if not name:
        return redirect(url_for('home'))

    workspace = Workspace(user_id=user.id, name=name[:120])
    db.session.add(workspace)
    db.session.flush()

    board = Board(workspace_id=workspace.id, name='Tablero principal')
    db.session.add(board)
    db.session.flush()

=======
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    column = (
        db.session.query(BoardColumn)
        .join(Board, BoardColumn.board_id == Board.id)
        .join(Workspace, Board.workspace_id == Workspace.id)
        .filter(BoardColumn.id == column_id, Workspace.user_id == user.id)
        .first()
    )
    if not column:
        return redirect(url_for('home'))

    title = (request.form.get('card_title') or '').strip()
    if not title:
        return redirect(url_for('board_view', board_id=column.board_id))

    new_card = Card(column_id=column.id, title=title[:200])
    db.session.add(new_card)
    db.session.commit()
    board = db.session.get(Board, column.board_id)
    if board:
        log_activity(user.id, 'Tarjeta creada', f'"{new_card.title}" en "{board.name}"')
    return redirect(url_for('board_view', board_id=column.board_id))


@app.route('/columns/<int:column_id>/delete', methods=['POST'])
def delete_column(column_id):
    """Elimina una columna y tambien todas sus tarjetas."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    column = (
        db.session.query(BoardColumn)
        .join(Board, BoardColumn.board_id == Board.id)
        .join(Workspace, Board.workspace_id == Workspace.id)
        .filter(BoardColumn.id == column_id, Workspace.user_id == user.id)
        .first()
    )
    if not column:
        return redirect(url_for('home'))

    column_title = column.title
    board_id = column.board_id
    board = db.session.get(Board, board_id)
    Card.query.filter_by(column_id=column.id).delete(synchronize_session=False)
    db.session.delete(column)
    db.session.commit()
    if board:
        log_activity(user.id, 'Columna eliminada', f'Columna "{column_title}" en "{board.name}"')
    return redirect(url_for('board_view', board_id=board_id))


@app.route('/cards/<int:card_id>/move', methods=['POST'])
def move_card(card_id):
    """Mueve una tarjeta a otra columna usando drag and drop."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    target_column_id = request.form.get('column_id', type=int)
    if not target_column_id:
        return redirect(url_for('home'))

    # Comprobamos que la tarjeta pertenece al usuario actual.
    card = (
        db.session.query(Card)
        .join(BoardColumn, Card.column_id == BoardColumn.id)
        .join(Board, BoardColumn.board_id == Board.id)
        .join(Workspace, Board.workspace_id == Workspace.id)
        .filter(Card.id == card_id, Workspace.user_id == user.id)
        .first()
    )
    if not card:
        return redirect(url_for('home'))

    current_column = db.session.get(BoardColumn, card.column_id)
    if not current_column:
        return redirect(url_for('home'))

    # La columna destino debe pertenecer al mismo tablero.
    target_column = (
        db.session.query(BoardColumn)
        .join(Board, BoardColumn.board_id == Board.id)
        .join(Workspace, Board.workspace_id == Workspace.id)
        .filter(BoardColumn.id == target_column_id, Workspace.user_id == user.id)
        .first()
    )
    if not target_column or target_column.board_id != current_column.board_id:
        return redirect(url_for('board_view', board_id=current_column.board_id))

    card_title = card.title
    card.column_id = target_column_id
    db.session.commit()
    board = db.session.get(Board, target_column.board_id)
    if board:
        log_activity(user.id, 'Tarjeta movida', f'"{card_title}" a "{target_column.title}" en "{board.name}"')
    return ('', 204)


@app.route('/cards/<int:card_id>/delete', methods=['POST'])
def delete_card(card_id):
    """Elimina una tarjeta concreta del tablero."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    card = (
        db.session.query(Card)
        .join(BoardColumn, Card.column_id == BoardColumn.id)
        .join(Board, BoardColumn.board_id == Board.id)
        .join(Workspace, Board.workspace_id == Workspace.id)
        .filter(Card.id == card_id, Workspace.user_id == user.id)
        .first()
    )
    if not card:
        return redirect(url_for('home'))

    card_title = card.title
    board_id = (
        db.session.query(Board.id)
        .join(BoardColumn, BoardColumn.board_id == Board.id)
        .filter(BoardColumn.id == card.column_id)
        .scalar()
    )

    db.session.delete(card)
    db.session.commit()
    if board_id:
        board = db.session.get(Board, board_id)
        if board:
            log_activity(user.id, 'Tarjeta eliminada', f'"{card_title}" en "{board.name}"')
    if board_id:
        return redirect(url_for('board_view', board_id=board_id))
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Muestra el login y valida las credenciales enviadas por el formulario."""
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']

        # Intento rapido para usuarios antiguos guardados en texto plano.
        user = User.query.filter_by(email=email, password=password).first()
        if not user:
            user = User.query.filter_by(email=email).first()

        if user:
            # Si la clave ya estaba protegida, la comprobamos con hash.
            if is_password_hashed(user.password):
                is_ok = check_password_hash(user.password, password)
            else:
                is_ok = (user.password == password)
                if is_ok:
                    # Si entra bien y la clave estaba en plano, la guardamos mas segura.
                    user.password = generate_password_hash(password)
                    db.session.commit()

            if is_ok:
                session['user_id'] = user.id
                log_activity(user.id, 'Inicio de sesion', 'Acceso correcto a la plataforma')
                return redirect(url_for('home'))

        return render_template('login.html', error='Credenciales invalidas', error_html=build_login_error_html('Credenciales invalidas'))

    return render_template('login.html', error=None, error_html=build_login_error_html(None))


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    """Cierra la sesion actual del usuario."""
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/workspaces/create', methods=['POST'])
def create_workspace():
    """Crea un espacio nuevo y un tablero principal por defecto."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    name = (request.form.get('workspace_name') or '').strip()
    if not name:
        return redirect(url_for('home'))

    workspace = Workspace(user_id=user.id, name=name[:120])
    db.session.add(workspace)
    db.session.flush()

    board = Board(workspace_id=workspace.id, name='Tablero principal')
    db.session.add(board)
    db.session.flush()

>>>>>>> c672314 (Update project structure, templates and styles):app.py
    # Estas son las columnas iniciales del tablero principal.
    titles = ["Pendiente", "En progreso", "Listo"]
    for i in range(len(titles)):
        db.session.add(BoardColumn(board_id=board.id, title=titles[i], position=i))

    db.session.commit()
    log_activity(user.id, 'Espacio creado', f'"{workspace.name}" con tablero principal')
    return redirect(url_for('board_view', board_id=board.id))


@app.route('/workspaces/<int:workspace_id>/boards/create', methods=['POST'])
def create_board(workspace_id):
    """Crea un tablero nuevo dentro de un espacio existente."""
<<<<<<< HEAD:Prodify-TFG/Prodify-TFG/app.py
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    workspace = Workspace.query.filter_by(id=workspace_id, user_id=user.id).first()
    if not workspace:
        return redirect(url_for('home'))

    name = (request.form.get('board_name') or '').strip()
    if not name:
        return redirect(url_for('home'))

    new_board = Board(workspace_id=workspace.id, name=name[:120])
    db.session.add(new_board)
    db.session.commit()
    log_activity(user.id, 'Tablero creado', f'"{new_board.name}" en "{workspace.name}"')
    return redirect(url_for('home'))


@app.route('/workspaces/<int:workspace_id>/delete', methods=['POST'])
def delete_workspace(workspace_id):
    """Elimina un espacio completo junto con todo su contenido."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    workspace = Workspace.query.filter_by(id=workspace_id, user_id=user.id).first()
    if not workspace:
        return redirect(url_for('home'))

    # Borrado manual en cascada: primero tarjetas, luego columnas y luego tableros.
    workspace_name = workspace.name
    board_ids = []
    boards = Board.query.filter_by(workspace_id=workspace.id).all()
    for b in boards:
        board_ids.append(b.id)
    if board_ids:
        column_ids = []
        cols = BoardColumn.query.filter(BoardColumn.board_id.in_(board_ids)).all()
        for c in cols:
            column_ids.append(c.id)
        if column_ids:
            Card.query.filter(Card.column_id.in_(column_ids)).delete(synchronize_session=False)
        BoardColumn.query.filter(BoardColumn.board_id.in_(board_ids)).delete(synchronize_session=False)
    Board.query.filter_by(workspace_id=workspace.id).delete()
    db.session.delete(workspace)
    db.session.commit()
    log_activity(user.id, 'Espacio eliminado', f'"{workspace_name}" y su contenido')
    return redirect(url_for('home'))


@app.route('/boards/<int:board_id>/delete', methods=['POST'])
def delete_board(board_id):
    """Elimina un tablero con sus columnas y sus tarjetas."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    board = (
        db.session.query(Board)
        .join(Workspace, Board.workspace_id == Workspace.id)
        .filter(Board.id == board_id, Workspace.user_id == user.id)
        .first()
    )
    if not board:
        return redirect(url_for('home'))

    board_name = board.name
    column_ids = []
    cols = BoardColumn.query.filter_by(board_id=board.id).all()
    for c in cols:
        column_ids.append(c.id)
    if column_ids:
        Card.query.filter(Card.column_id.in_(column_ids)).delete(synchronize_session=False)
    BoardColumn.query.filter_by(board_id=board.id).delete()
    db.session.delete(board)
    db.session.commit()
    log_activity(user.id, 'Tablero eliminado', f'"{board_name}"')
    return redirect(url_for('home'))


@app.route('/account/update', methods=['POST'])
def update_account():
    """Actualiza el nombre visible del usuario en su perfil."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    new_name = (request.form.get('display_name') or '').strip()
    if new_name:
        profile = get_profile(user)
        profile.display_name = new_name[:80]
        db.session.commit()

    return redirect(url_for('home'))


=======
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    workspace = Workspace.query.filter_by(id=workspace_id, user_id=user.id).first()
    if not workspace:
        return redirect(url_for('home'))

    name = (request.form.get('board_name') or '').strip()
    if not name:
        return redirect(url_for('home'))

    new_board = Board(workspace_id=workspace.id, name=name[:120])
    db.session.add(new_board)
    db.session.commit()
    log_activity(user.id, 'Tablero creado', f'"{new_board.name}" en "{workspace.name}"')
    return redirect(url_for('home'))


@app.route('/workspaces/<int:workspace_id>/delete', methods=['POST'])
def delete_workspace(workspace_id):
    """Elimina un espacio completo junto con todo su contenido."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    workspace = Workspace.query.filter_by(id=workspace_id, user_id=user.id).first()
    if not workspace:
        return redirect(url_for('home'))

    # Borrado manual en cascada: primero tarjetas, luego columnas y luego tableros.
    workspace_name = workspace.name
    board_ids = []
    boards = Board.query.filter_by(workspace_id=workspace.id).all()
    for b in boards:
        board_ids.append(b.id)
    if board_ids:
        column_ids = []
        cols = BoardColumn.query.filter(BoardColumn.board_id.in_(board_ids)).all()
        for c in cols:
            column_ids.append(c.id)
        if column_ids:
            Card.query.filter(Card.column_id.in_(column_ids)).delete(synchronize_session=False)
        BoardColumn.query.filter(BoardColumn.board_id.in_(board_ids)).delete(synchronize_session=False)
    Board.query.filter_by(workspace_id=workspace.id).delete()
    db.session.delete(workspace)
    db.session.commit()
    log_activity(user.id, 'Espacio eliminado', f'"{workspace_name}" y su contenido')
    return redirect(url_for('home'))


@app.route('/boards/<int:board_id>/delete', methods=['POST'])
def delete_board(board_id):
    """Elimina un tablero con sus columnas y sus tarjetas."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    board = (
        db.session.query(Board)
        .join(Workspace, Board.workspace_id == Workspace.id)
        .filter(Board.id == board_id, Workspace.user_id == user.id)
        .first()
    )
    if not board:
        return redirect(url_for('home'))

    board_name = board.name
    column_ids = []
    cols = BoardColumn.query.filter_by(board_id=board.id).all()
    for c in cols:
        column_ids.append(c.id)
    if column_ids:
        Card.query.filter(Card.column_id.in_(column_ids)).delete(synchronize_session=False)
    BoardColumn.query.filter_by(board_id=board.id).delete()
    db.session.delete(board)
    db.session.commit()
    log_activity(user.id, 'Tablero eliminado', f'"{board_name}"')
    return redirect(url_for('home'))


@app.route('/account/update', methods=['POST'])
def update_account():
    """Actualiza el nombre visible del usuario en su perfil."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    new_name = (request.form.get('display_name') or '').strip()
    if new_name:
        profile = get_profile(user)
        profile.display_name = new_name[:80]
        db.session.commit()

    return redirect(url_for('home'))


>>>>>>> c672314 (Update project structure, templates and styles):app.py
if __name__ == '__main__':
    with app.app_context():
        # Crea las tablas si todavia no existen en la base de datos.
        db.create_all()

        # Usuario de prueba para poder entrar rapido en local.
        default_user = User.query.filter_by(email='test@prodify.com').first()
<<<<<<< HEAD:Prodify-TFG/Prodify-TFG/app.py
        if not default_user:
            default_user = User(email='test@prodify.com', password=generate_password_hash('1234'))
            db.session.add(default_user)
            db.session.commit()

=======
        if not default_user:
            default_user = User(email='test@prodify.com', password=generate_password_hash('1234'))
            db.session.add(default_user)
            db.session.commit()

>>>>>>> c672314 (Update project structure, templates and styles):app.py
    # Arranca el servidor local de desarrollo.
    app.run(host='127.0.0.1', port=5000, debug=True)
