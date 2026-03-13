from datetime import datetime
import os
from urllib.parse import quote_plus

from flask import Flask, redirect, render_template, request, session, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder='html', static_folder='estilos', static_url_path='/estilos')
app.secret_key = os.getenv('SECRET_KEY', 'prodify_super_secret_key')

# Configuracion MySQL para XAMPP (puedes sobrescribir con variables de entorno)
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
        "tags": ["Roadmap", "Sprint", "Go-to-market"],
        "columns": ["Idea", "En progreso", "Validacion", "Listo"],
    },
    {
        "id": "marketing",
        "name": "Campana de marketing",
        "summary": "Gestiona creatividades, anuncios y calendario.",
        "accent": "template-accent-violet",
        "tags": ["Contenido", "Ads", "Social"],
        "columns": ["Brief", "Produccion", "Revision", "Publicado"],
    },
    {
        "id": "ventas",
        "name": "Pipeline de ventas",
        "summary": "Controla leads, propuestas y cierres.",
        "accent": "template-accent-amber",
        "tags": ["CRM", "Negociacion", "Seguimiento"],
        "columns": ["Lead", "Contacto", "Propuesta", "Cerrado"],
    },
    {
        "id": "ops",
        "name": "Operaciones internas",
        "summary": "Mantiene procesos, tareas recurrentes y calidad.",
        "accent": "template-accent-mint",
        "tags": ["Procesos", "Checklist", "Equipo"],
        "columns": ["Pendiente", "En curso", "Bloqueado", "Listo"],
    },
    {
        "id": "support",
        "name": "Soporte y tickets",
        "summary": "Prioriza solicitudes y mejora la experiencia.",
        "accent": "template-accent-rose",
        "tags": ["Customer", "Feedback", "SLA"],
        "columns": ["Nuevo", "Asignado", "Investigando", "Resuelto"],
    },
    {
        "id": "personal",
        "name": "Plan semanal personal",
        "summary": "Organiza prioridades y rutinas diarias.",
        "accent": "template-accent-slate",
        "tags": ["Focus", "Rutina", "Productividad"],
        "columns": ["Pendiente", "En foco", "En pausa", "Hecho"],
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


def get_user_or_redirect():
    user_id = session.get('user_id')
    if not user_id:
        return None, redirect(url_for('login'))
    user = db.session.get(User, user_id)
    if not user:
        return None, redirect(url_for('login'))
    return user, None


def get_profile(user):
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


@app.route('/')
def home():
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    profile = get_profile(user)
    workspaces = Workspace.query.filter_by(user_id=user.id).order_by(Workspace.created_at.asc()).all()

    workspace_ids = []
    for w in workspaces:
        workspace_ids.append(w.id)

    boards = []
    if len(workspace_ids) > 0:
        boards = Board.query.filter(Board.workspace_id.in_(workspace_ids)).order_by(Board.created_at.desc()).all()

    boards_by_workspace = {}
    for board in boards:
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
        active_page='boards',
    )

@app.route('/plantillas')
def templates_page():
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    profile = get_profile(user)
    workspaces = Workspace.query.filter_by(user_id=user.id).order_by(Workspace.created_at.asc()).all()

    return render_template(
        'plantillas.html',
        user=user,
        profile=profile,
        workspaces=workspaces,
        templates=BOARD_TEMPLATES,
        active_page='templates',
    )


@app.route('/inicio')
def landing():
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
    return send_from_directory('js', filename)


@app.route('/plantillas/usar', methods=['POST'])
def use_template():
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

    workspace = Workspace(user_id=user.id, name=workspace_name[:120])
    db.session.add(workspace)
    db.session.flush()

    board = Board(workspace_id=workspace.id, name=board_name[:120])
    db.session.add(board)
    db.session.flush()

    pos = 0
    for title in columns:
        db.session.add(BoardColumn(board_id=board.id, title=title[:120], position=pos))
        pos += 1

    db.session.commit()
    return redirect(url_for('board_view', board_id=board.id))


@app.route('/boards/<int:board_id>')
def board_view(board_id):
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

    columns = BoardColumn.query.filter_by(board_id=board.id).order_by(BoardColumn.position.asc()).all()
    column_ids = []
    for c in columns:
        column_ids.append(c.id)
    cards = []
    if column_ids:
        cards = Card.query.filter(Card.column_id.in_(column_ids)).order_by(Card.created_at.asc()).all()

    cards_by_column = {}
    for card in cards:
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
    db.session.add(BoardColumn(board_id=board.id, title=title[:120], position=position))
    db.session.commit()
    return redirect(url_for('board_view', board_id=board.id))


@app.route('/columns/<int:column_id>/cards/create', methods=['POST'])
def create_card(column_id):
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

    db.session.add(Card(column_id=column.id, title=title[:200]))
    db.session.commit()
    return redirect(url_for('board_view', board_id=column.board_id))


@app.route('/columns/<int:column_id>/delete', methods=['POST'])
def delete_column(column_id):
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

    Card.query.filter_by(column_id=column.id).delete(synchronize_session=False)
    board_id = column.board_id
    db.session.delete(column)
    db.session.commit()
    return redirect(url_for('board_view', board_id=board_id))


@app.route('/cards/<int:card_id>/move', methods=['POST'])
def move_card(card_id):
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    target_column_id = request.form.get('column_id', type=int)
    if not target_column_id:
        return redirect(url_for('home'))

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

    target_column = (
        db.session.query(BoardColumn)
        .join(Board, BoardColumn.board_id == Board.id)
        .join(Workspace, Board.workspace_id == Workspace.id)
        .filter(BoardColumn.id == target_column_id, Workspace.user_id == user.id)
        .first()
    )
    if not target_column or target_column.board_id != current_column.board_id:
        return redirect(url_for('board_view', board_id=current_column.board_id))

    card.column_id = target_column_id
    db.session.commit()
    return ('', 204)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']

        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('home'))

        return render_template('login.html', error='Credenciales invalidas')

    return render_template('login.html', error=None)


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/workspaces/create', methods=['POST'])
def create_workspace():
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
    return redirect(url_for('board_view', board_id=board.id))


@app.route('/workspaces/<int:workspace_id>/boards/create', methods=['POST'])
def create_board(workspace_id):
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    workspace = Workspace.query.filter_by(id=workspace_id, user_id=user.id).first()
    if not workspace:
        return redirect(url_for('home'))

    name = (request.form.get('board_name') or '').strip()
    if not name:
        return redirect(url_for('home'))

    db.session.add(Board(workspace_id=workspace.id, name=name[:120]))
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/workspaces/<int:workspace_id>/delete', methods=['POST'])
def delete_workspace(workspace_id):
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    workspace = Workspace.query.filter_by(id=workspace_id, user_id=user.id).first()
    if not workspace:
        return redirect(url_for('home'))

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
    return redirect(url_for('home'))


@app.route('/boards/<int:board_id>/delete', methods=['POST'])
def delete_board(board_id):
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

    column_ids = []
    cols = BoardColumn.query.filter_by(board_id=board.id).all()
    for c in cols:
        column_ids.append(c.id)
    if column_ids:
        Card.query.filter(Card.column_id.in_(column_ids)).delete(synchronize_session=False)
    BoardColumn.query.filter_by(board_id=board.id).delete()
    db.session.delete(board)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/account/update', methods=['POST'])
def update_account():
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
            default_user = User(email='test@prodify.com', password='1234')
            db.session.add(default_user)
            db.session.commit()

    app.run(host='127.0.0.1', port=5000, debug=True)

