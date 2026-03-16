from datetime import datetime
import os
from urllib.parse import quote_plus

from flask import Flask, redirect, render_template, request, session, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='html', static_folder='estilos', static_url_path='/estilos')
# Clave para sesiones. En un entorno real se cambia por variable segura.
app.secret_key = os.getenv('SECRET_KEY', 'prodify_super_secret_key')

# Configuracion MySQL para XAMPP
db_user = os.getenv('DB_USER', 'root')
db_password = quote_plus(os.getenv('DB_PASSWORD', ''))
db_host = os.getenv('DB_HOST', 'localhost')
db_name = os.getenv('DB_NAME', 'prodify_db')

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}?charset=utf8mb4"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

BOARD_TEMPLATES = [
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


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)


class UserProfile(db.Model):
    __tablename__ = 'user_profiles'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    display_name = db.Column(db.String(80), nullable=False)


class Workspace(db.Model):
    __tablename__ = 'workspaces'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Board(db.Model):
    __tablename__ = 'boards'

    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class BoardColumn(db.Model):
    __tablename__ = 'board_columns'

    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id'), nullable=False, index=True)
    title = db.Column(db.String(120), nullable=False)
    position = db.Column(db.Integer, nullable=False, default=0)


class Card(db.Model):
    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True)
    column_id = db.Column(db.Integer, db.ForeignKey('board_columns.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    action = db.Column(db.String(120), nullable=False)
    detail = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


def get_user_or_redirect():
    """Devuelve el usuario logueado o redirige al login."""
    user_id = session.get('user_id')
    if not user_id:
        return None, redirect(url_for('login'))
    user = db.session.get(User, user_id)
    if not user:
        return None, redirect(url_for('login'))
    return user, None


def get_profile(user):
    """Asegura que exista un perfil con nombre visible."""
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
    """Comprueba si una contraseña parece estar hasheada por Werkzeug."""
    if not value:
        return False
    return value.startswith('pbkdf2:') or value.startswith('scrypt:') or value.startswith('argon2:')


def log_activity(user_id, action, detail):
    """Guarda una accion para mostrarla en la pagina de actividad."""
    if not user_id:
        return
    db.session.add(ActivityLog(user_id=user_id, action=action[:120], detail=detail[:255]))
    db.session.commit()


@app.route('/')
def home():
    """Vista principal: muestra espacios y tableros recientes."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    profile = get_profile(user)
    # Cargamos todos los espacios del usuario
    workspaces = Workspace.query.filter_by(user_id=user.id).order_by(Workspace.created_at.asc()).all()

    workspace_ids = []
    for w in workspaces:
        workspace_ids.append(w.id)

    boards = []
    if len(workspace_ids) > 0:
        # Si hay espacios, traemos sus tableros
        boards = Board.query.filter(Board.workspace_id.in_(workspace_ids)).order_by(Board.created_at.desc()).all()

    boards_by_workspace = {}
    for board in boards:
        # Agrupar tableros por espacio
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
    """Muestra solo el espacio seleccionado en la vista principal."""
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
    """Abre directamente el tablero mas reciente del espacio."""
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
    """Pagina de plantillas."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    profile = get_profile(user)
    workspaces = Workspace.query.filter_by(user_id=user.id).order_by(Workspace.created_at.asc()).all()
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
    """Render de paginas simples del menu de cuenta."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    profile = get_profile(user)
    workspaces = Workspace.query.filter_by(user_id=user.id).order_by(Workspace.created_at.asc()).all()

    activities = []
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


@app.route('/cuenta')
def account_page():
    return render_account_page(
        'Gestionar cuenta',
        'Aqui puedes revisar los datos basicos de tu cuenta y su estado.',
    )


@app.route('/perfil')
def profile_page():
    return render_account_page(
        'Perfil y visibilidad',
        'Configuracion basica del perfil y como se muestra tu nombre en la app.',
    )


@app.route('/actividad')
def activity_page():
    return render_account_page(
        'Actividad',
        'Resumen de acciones recientes dentro de tus tableros y espacios.',
    )


@app.route('/tarjetas')
def cards_page():
    return render_account_page(
        'Tarjetas',
        'Listado general de tareas (en esta version se muestra como vista informativa).',
    )


@app.route('/ajustes')
def settings_page():
    return render_account_page(
        'Ajustes',
        'Preferencias generales de la aplicacion.',
    )


@app.route('/ayuda')
def help_page():
    return render_account_page(
        'Ayuda',
        'Recursos rapidos para resolver dudas y usar la plataforma.',
    )


@app.route('/inicio')
def landing():
    """Pagina de inicio/landing interna."""
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
    """Servir archivos JS desde /js."""
    return send_from_directory('js', filename)


@app.route('/plantillas/usar', methods=['POST'])
def use_template():
    """Crea un espacio y tablero usando una plantilla."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    template_id = (request.form.get('template_id') or '').strip()
    workspace_name = (request.form.get('workspace_name') or '').strip() or 'Nuevo espacio'
    board_name = (request.form.get('board_name') or '').strip() or 'Nuevo tablero'

    template = None
    for t in BOARD_TEMPLATES:
        if t["id"] == template_id:
            template = t
            break

    if template:
        columns = template["columns"]
    else:
        columns = ["Pendiente", "En progreso", "Listo"]

    # Crear espacio y tablero en la base de datos
    workspace = Workspace(user_id=user.id, name=workspace_name[:120])
    db.session.add(workspace)
    db.session.flush()

    board = Board(workspace_id=workspace.id, name=board_name[:120])
    db.session.add(board)
    db.session.flush()

    # Crear columnas iniciales segun plantilla
    pos = 0
    for title in columns:
        db.session.add(BoardColumn(board_id=board.id, title=title[:120], position=pos))
        pos += 1

    db.session.commit()
    log_activity(user.id, 'Plantilla aplicada', f'Tablero "{board.name}" creado en "{workspace.name}"')
    return redirect(url_for('board_view', board_id=board.id))


@app.route('/boards/<int:board_id>')
def board_view(board_id):
    """Vista de un tablero con columnas y tarjetas."""
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

    # Columnas del tablero
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
        # Traer tarjetas de todas las columnas
        cards = Card.query.filter(Card.column_id.in_(column_ids)).order_by(Card.created_at.asc()).all()

    cards_by_column = {}
    for card in cards:
        # Agrupar tarjetas por columna para la vista
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
    """Crea una nueva columna en un tablero."""
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

    last_position = db.session.query(db.func.max(BoardColumn.position)).filter_by(board_id=board.id).scalar()
    position = (last_position + 1) if last_position is not None else 0
    new_column = BoardColumn(board_id=board.id, title=title[:120], position=position)
    db.session.add(new_column)
    db.session.commit()
    log_activity(user.id, 'Columna creada', f'Columna "{new_column.title}" en "{board.name}"')
    return redirect(url_for('board_view', board_id=board.id))


@app.route('/columns/<int:column_id>/cards/create', methods=['POST'])
def create_card(column_id):
    """Crea una tarjeta dentro de una columna."""
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
    """Elimina una columna y todas sus tarjetas."""
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
    """Mueve una tarjeta a otra columna (drag & drop)."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    target_column_id = request.form.get('column_id', type=int)
    if not target_column_id:
        return redirect(url_for('home'))

    # Comprobar que la tarjeta pertenezca al usuario logueado
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

    # Verificar que la columna destino es del mismo usuario/tablero
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
    """Elimina una tarjeta concreta."""
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
    """Login simple con email y password."""
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']

        user = User.query.filter_by(email=email, password=password).first()
        if not user:
            user = User.query.filter_by(email=email).first()

        if user:
            if is_password_hashed(user.password):
                is_ok = check_password_hash(user.password, password)
            else:
                is_ok = (user.password == password)
                if is_ok:
                    # Migracion suave: si estaba en texto plano, lo guardamos hasheado
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
    """Cerrar sesion."""
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/workspaces/create', methods=['POST'])
def create_workspace():
    """Crea un espacio de trabajo y un tablero principal."""
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

    titles = ["Pendiente", "En progreso", "Listo"]
    for i in range(len(titles)):
        db.session.add(BoardColumn(board_id=board.id, title=titles[i], position=i))

    db.session.commit()
    log_activity(user.id, 'Espacio creado', f'"{workspace.name}" con tablero principal')
    return redirect(url_for('board_view', board_id=board.id))


@app.route('/workspaces/<int:workspace_id>/boards/create', methods=['POST'])
def create_board(workspace_id):
    """Crea un tablero dentro de un espacio."""
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
    """Elimina un espacio y todo su contenido."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    workspace = Workspace.query.filter_by(id=workspace_id, user_id=user.id).first()
    if not workspace:
        return redirect(url_for('home'))

    # Borrado en cascada manual (tableros -> columnas -> tarjetas)
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
    """Elimina un tablero y su contenido."""
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
    """Actualiza el nombre visible del usuario."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    new_name = (request.form.get('display_name') or '').strip()
    if new_name:
        profile = get_profile(user)
        profile.display_name = new_name[:80]
        db.session.commit()

    return redirect(url_for('home'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Usuario de prueba para acceso rapido
        default_user = User.query.filter_by(email='test@prodify.com').first()
        if not default_user:
            default_user = User(email='test@prodify.com', password=generate_password_hash('1234'))
            db.session.add(default_user)
            db.session.commit()

    app.run(host='127.0.0.1', port=5000, debug=True)
