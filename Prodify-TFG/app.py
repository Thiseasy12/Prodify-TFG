from datetime import datetime, timedelta
from html import escape as html_escape
import json
import os
import re
import secrets
import smtplib
import ssl
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from urllib.parse import quote_plus
from email.message import EmailMessage

from flask import Flask, redirect, render_template, request, session, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from markupsafe import Markup, escape
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename


def load_dotenv_file():
    """Carga variables desde un archivo .env local si existe."""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if not os.path.exists(env_path):
        return

    with open(env_path, 'r', encoding='utf-8') as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue

            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()

            if not key:
                continue

            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]

            os.environ.setdefault(key, value)


load_dotenv_file()

# Creamos la aplicacion Flask y le indicamos donde estan las vistas y los estilos.
app = Flask(__name__, template_folder='html', static_folder='estilos', static_url_path='/estilos')

# Esta clave permite a Flask mantener la sesion iniciada del usuario.
app.secret_key = os.getenv('SECRET_KEY', 'prodify_super_secret_key')

# Configuracion de MySQL. Por defecto esta pensada para XAMPP en local.
db_user = os.getenv('DB_USER', 'root')
db_password = quote_plus(os.getenv('DB_PASSWORD', ''))
db_host = os.getenv('DB_HOST', 'localhost')
db_name = os.getenv('DB_NAME', 'prodify_db')
public_base_url = os.getenv('PUBLIC_BASE_URL', 'http://127.0.0.1:5000').strip().rstrip('/')

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}?charset=utf8mb4"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = public_base_url.startswith('https://')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=12)

# SQLAlchemy es el puente entre Python y la base de datos.
db = SQLAlchemy(app)

resend_api_key = os.getenv('RESEND_API_KEY', '').strip()
resend_from = os.getenv('RESEND_FROM', 'Prodify <onboarding@resend.dev>').strip()
password_reset_max_age = int(os.getenv('PASSWORD_RESET_MAX_AGE', '3600'))
smtp_host = os.getenv('SMTP_HOST', '').strip()
smtp_port = int(os.getenv('SMTP_PORT', '587'))
smtp_user = os.getenv('SMTP_USER', '').strip()
smtp_password = os.getenv('SMTP_PASSWORD', '').strip()
smtp_from = os.getenv('SMTP_FROM', smtp_user or 'no-reply@prodify.local').strip()
smtp_use_tls = os.getenv('SMTP_USE_TLS', '1').strip().lower() not in ('0', 'false', 'no')
rate_limit_store = {}
email_regex = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
ALLOWED_AVATAR_EXTENSIONS = {'jpg', 'jpeg', 'png', 'svg', 'webp'}
avatar_upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images', 'avatars')
ALLOWED_BOARD_COVER_EXTENSIONS = {'jpg', 'jpeg', 'png', 'svg', 'webp'}
board_cover_upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images', 'board_covers')


def load_board_templates():
    """Carga el catalogo de plantillas desde un JSON local."""
    templates_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'board_templates.json')
    try:
        with open(templates_path, 'r', encoding='utf-8') as templates_file:
            data = json.load(templates_file)
    except (OSError, json.JSONDecodeError) as exc:
        print(f'[Prodify] No se pudo cargar board_templates.json: {exc}', flush=True)
        return []

    if not isinstance(data, list):
        print('[Prodify] board_templates.json no tiene una lista valida de plantillas.', flush=True)
        return []

    normalized_templates = []
    for item in data:
        if not isinstance(item, dict):
            continue
        template_id = sanitize_text(str(item.get('id') or ''), 80)
        name = sanitize_text(str(item.get('name') or ''), 120)
        summary = sanitize_text(str(item.get('summary') or ''), 200)
        accent = sanitize_text(str(item.get('accent') or 'template-accent-blue'), 40) or 'template-accent-blue'
        category = sanitize_text(str(item.get('category') or 'Otros'), 60) or 'Otros'
        tags = [sanitize_text(str(tag), 30) for tag in (item.get('tags') or []) if sanitize_text(str(tag), 30)]
        columns = [sanitize_text(str(column), 80) for column in (item.get('columns') or []) if sanitize_text(str(column), 80)]

        if not template_id or not name or not summary or len(columns) < 2:
            continue

        normalized_templates.append({
            'id': template_id,
            'name': name,
            'summary': summary,
            'accent': accent,
            'category': category,
            'tags': tags,
            'columns': columns,
        })

    return normalized_templates


def load_language_catalog():
    """Carga el catalogo de idiomas disponible para el selector."""
    catalog_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'languages.json')
    fallback = [{'code': 'es', 'label': 'Espanol'}]
    try:
        with open(catalog_path, 'r', encoding='utf-8') as catalog_file:
            data = json.load(catalog_file)
    except (OSError, json.JSONDecodeError) as exc:
        print(f'[Prodify] No se pudo cargar languages.json: {exc}', flush=True)
        return fallback

    if not isinstance(data, list):
        return fallback

    languages = []
    for item in data:
        if not isinstance(item, dict):
            continue
        code = sanitize_text(str(item.get('code') or ''), 10)
        label = sanitize_text(str(item.get('label') or ''), 80)
        if not code or not label:
            continue
        languages.append({'code': code, 'label': label})
    return languages or fallback


def load_translations_catalog():
    """Carga los textos traducidos de la interfaz."""
    translations_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'translations.json')
    fallback = {'es': {}, 'en': {}}
    try:
        with open(translations_path, 'r', encoding='utf-8') as translations_file:
            data = json.load(translations_file)
    except (OSError, json.JSONDecodeError) as exc:
        print(f'[Prodify] No se pudo cargar translations.json: {exc}', flush=True)
        return fallback

    if not isinstance(data, dict):
        return fallback
    return data


def load_countries_catalog():
    """Carga el catalogo de paises admitiendo comas finales en el JSON."""
    countries_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'banderas del mundo', 'countries.json')
    try:
        with open(countries_path, 'r', encoding='utf-8') as countries_file:
            raw_text = countries_file.read()
    except OSError as exc:
        print(f'[Prodify] No se pudo cargar countries.json: {exc}', flush=True)
        return []

    sanitized_text = re.sub(r',(\s*[}\]])', r'\1', raw_text)
    sanitized_text = re.sub(r'\]\s*;\s*$', ']', sanitized_text)
    try:
        data = json.loads(sanitized_text)
    except json.JSONDecodeError as exc:
        print(f'[Prodify] No se pudo interpretar countries.json: {exc}', flush=True)
        return []

    if not isinstance(data, list):
        return []
    return data


# Modelo de usuario: guarda los datos de acceso.
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email_verified = db.Column(db.Boolean, nullable=False, default=False, server_default=db.text('0'))
    verified_at = db.Column(db.DateTime, nullable=True)
    has_seen_inicio = db.Column(db.Boolean, nullable=False, default=False, server_default=db.text('0'))
    preferred_language = db.Column(db.String(10), nullable=False, default='es', server_default='es')

# Perfil basico del usuario para mostrar su nombre en la interfaz.
class UserProfile(db.Model):
    __tablename__ = 'user_profiles'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    display_name = db.Column(db.String(80), nullable=False)
    avatar_url = db.Column(db.String(300), nullable=True)

# Espacio de trabajo que agrupa varios tableros.
class Workspace(db.Model):
    __tablename__ = 'workspaces'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# Miembros que participan en un espacio con un rol concreto.
class WorkspaceMember(db.Model):
    __tablename__ = 'workspace_members'

    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    role = db.Column(db.String(20), nullable=False, default='lector')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('workspace_id', 'user_id', name='uq_workspace_member_user'),
    )

# Tablero individual dentro de un espacio.
class Board(db.Model):
    __tablename__ = 'boards'

    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    background_color = db.Column(db.String(20), nullable=True)
    cover_url = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class BoardMember(db.Model):
    __tablename__ = 'board_members'

    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    role = db.Column(db.String(20), nullable=False, default='lector')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('board_id', 'user_id', name='uq_board_member_user'),
    )


class BoardInvitation(db.Model):
    __tablename__ = 'board_invitations'

    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id', ondelete='CASCADE'), nullable=False, index=True)
    email = db.Column(db.String(100), nullable=False, index=True)
    role = db.Column(db.String(20), nullable=False, default='lector')
    token = db.Column(db.String(120), nullable=False, unique=True, index=True)
    invited_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    accepted_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# Columna dentro de un tablero.
class BoardColumn(db.Model):
    __tablename__ = 'board_columns'

    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(120), nullable=False)
    position = db.Column(db.Integer, nullable=False, default=0)

# Tarjeta o tarea dentro de una columna.
class Card(db.Model):
    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True)
    column_id = db.Column(db.Integer, db.ForeignKey('board_columns.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# Historial de acciones del usuario.
class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    action = db.Column(db.String(120), nullable=False)
    detail = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


WORKSPACE_ROLE_LABELS = {
    'owner': 'Propietario',
    'admin': 'Admin',
    'editor': 'Editor',
    'lector': 'Lector',
}

MEMBER_ROLES = ('admin', 'editor', 'lector')
WORKSPACE_MEMBER_ROLES = MEMBER_ROLES
BOARD_MEMBER_ROLES = MEMBER_ROLES
ROLE_PRIORITY = {
    'owner': 4,
    'admin': 3,
    'editor': 2,
    'lector': 1,
}


def get_user_or_redirect():
    """Devuelve el usuario actual; si no hay sesion, manda al login."""
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


def validate_password_strength(password):
    """Comprueba que la contraseña cumpla unas reglas mínimas de seguridad."""
    if len(password) < 8:
        return 'La contraseña debe tener al menos 8 caracteres.'
    if not re.search(r'[A-Z]', password):
        return 'La contraseña debe incluir al menos una letra mayúscula.'
    if not re.search(r'[a-z]', password):
        return 'La contraseña debe incluir al menos una letra minúscula.'
    if not re.search(r'\d', password):
        return 'La contraseña debe incluir al menos un número.'
    if not re.search(r'[^A-Za-z0-9]', password):
        return 'La contraseña debe incluir al menos un carácter especial.'
    return None


def build_rate_limit_message(retry_after):
    """Devuelve un mensaje amigable cuando se supera un limite de peticiones."""
    minutes = max(1, (retry_after + 59) // 60)
    if minutes <= 1:
        return 'Has hecho demasiados intentos. Espera un minuto y vuelve a probar.'
    return f'Has hecho demasiados intentos. Espera unos {minutes} minutos y vuelve a probar.'


def get_reset_serializer():
    """Crea el serializador para firmar enlaces de recuperacion."""
    return URLSafeTimedSerializer(app.secret_key)


def generate_password_reset_token(user):
    """Firma un token temporal con el email del usuario."""
    serializer = get_reset_serializer()
    return serializer.dumps(user.email, salt='password-reset')


def generate_email_verification_token(user):
    """Firma un token temporal para confirmar el correo del usuario."""
    serializer = get_reset_serializer()
    return serializer.dumps(user.email, salt='email-verification')


def verify_password_reset_token(token):
    """Valida el token de recuperacion y devuelve el usuario si sigue vigente."""
    serializer = get_reset_serializer()
    try:
        email = serializer.loads(token, salt='password-reset', max_age=password_reset_max_age)
    except SignatureExpired:
        return None, 'El enlace de recuperacion ha caducado.'
    except BadSignature:
        return None, 'El enlace de recuperacion no es valido.'

    user = User.query.filter_by(email=email).first()
    if not user:
        return None, 'La cuenta asociada ya no existe.'
    return user, None


def get_client_ip():
    """Obtiene la IP del cliente teniendo en cuenta proxys simples."""
    forwarded_for = (request.headers.get('X-Forwarded-For') or '').split(',')[0].strip()
    return forwarded_for or (request.remote_addr or 'unknown')


def sanitize_text(value, max_length):
    """Limpia textos cortos eliminando espacios repetidos y limitando longitud."""
    if not value:
        return ''
    cleaned = re.sub(r'\s+', ' ', value).strip()
    return cleaned[:max_length]


def is_allowed_avatar_filename(filename):
    """Valida las extensiones de avatar permitidas."""
    if not filename or '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in ALLOWED_AVATAR_EXTENSIONS


def is_allowed_board_cover_filename(filename):
    """Valida las extensiones permitidas para fondos de tablero."""
    if not filename or '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in ALLOWED_BOARD_COVER_EXTENSIONS


BOARD_TEMPLATES = load_board_templates() or []
LANGUAGE_CATALOG = load_language_catalog()
TRANSLATIONS_CATALOG = load_translations_catalog()
COUNTRIES_CATALOG = load_countries_catalog()
DEFAULT_LANGUAGE = 'es'
LANGUAGE_LABELS = {item['code']: item['label'] for item in LANGUAGE_CATALOG}
COUNTRY_FLAG_URLS = {
    str(item.get('code') or '').upper(): str(item.get('flag') or '').strip()
    for item in COUNTRIES_CATALOG
    if isinstance(item, dict) and str(item.get('code') or '').strip() and str(item.get('flag') or '').strip()
}


LANGUAGE_ALIASES = {
    'es-es': 'es',
    'en-us': 'en',
    'en-gb': 'en',
    'fr-fr': 'fr',
    'it-it': 'it',
    'de-de': 'de',
}

def normalize_language_code(value):
    """Normaliza el codigo de idioma y aplica alias comunes."""
    raw_value = sanitize_text(str(value or ''), 20)
    if not raw_value:
        return DEFAULT_LANGUAGE

    if raw_value in LANGUAGE_LABELS:
        return raw_value

    lowered = raw_value.lower()
    if lowered in LANGUAGE_ALIASES:
        aliased = LANGUAGE_ALIASES[lowered]
        if aliased in LANGUAGE_LABELS:
            return aliased

    base_language = lowered.split('-', 1)[0]
    if base_language in LANGUAGE_LABELS:
        return base_language

    return DEFAULT_LANGUAGE


def get_language_label(language_code, display_language=None):
    """Devuelve el nombre visible del idioma leido desde translations.json."""
    normalized_code = normalize_language_code(language_code)
    normalized_display = normalize_language_code(display_language or normalized_code)
    translation_key = f'lang.name.{normalized_code}'
    translated = translate_text(translation_key, normalized_display)
    if translated and translated != translation_key:
        return translated
    return LANGUAGE_LABELS.get(normalized_code) or LANGUAGE_LABELS.get(DEFAULT_LANGUAGE, 'Espanol')


def get_language_flag(language_code):
    """Devuelve una bandera o icono corto asociado al idioma."""
    normalized_code = normalize_language_code(language_code)
    flag_map = {
        'es': '🇪🇸',
        'en': '🇺🇸',
        'fr': '🇫🇷',
        'de': '🇩🇪',
        'it': '🇮🇹',
        'pt': '🇵🇹',
        'nl': '🇳🇱',
        'pl': '🇵🇱',
        'ro': '🇷🇴',
        'tr': '🇹🇷',
        'ru': '🇷🇺',
        'uk': '🇺🇦',
        'ar': '🇸🇦',
        'hi': '🇮🇳',
        'bn': '🇧🇩',
        'ur': '🇵🇰',
        'zh-CN': '🇨🇳',
        'zh-TW': '🇹🇼',
        'ja': '🇯🇵',
        'ko': '🇰🇷',
        'id': '🇮🇩',
        'vi': '🇻🇳',
        'th': '🇹🇭',
        'ms': '🇲🇾',
    }
    return flag_map.get(normalized_code, '🌐')


def get_language_country_code(language_code):
    """Relaciona un idioma con el pais de bandera que queremos mostrar."""
    normalized_code = normalize_language_code(language_code)
    country_map = {
        'es': 'ES',
        'en': 'US',
        'fr': 'FR',
        'de': 'DE',
        'it': 'IT',
        'pt': 'PT',
        'nl': 'NL',
        'pl': 'PL',
        'ro': 'RO',
        'tr': 'TR',
        'ru': 'RU',
        'uk': 'UA',
        'ar': 'SA',
        'hi': 'IN',
        'bn': 'BD',
        'ur': 'PK',
        'zh-CN': 'CN',
        'zh-TW': 'TW',
        'ja': 'JP',
        'ko': 'KR',
        'id': 'ID',
        'vi': 'VN',
        'th': 'TH',
        'ms': 'MY',
    }
    return country_map.get(normalized_code, '')


def get_language_flag_url(language_code):
    """Obtiene la URL de bandera a partir del catalogo de paises del usuario."""
    country_code = get_language_country_code(language_code)
    if not country_code:
        return ''
    return COUNTRY_FLAG_URLS.get(country_code.upper(), '')


def get_language_flag_svg(language_code):
    """Devuelve una bandera SVG simple y estable para el idioma seleccionado."""
    normalized_code = normalize_language_code(language_code)
    flag_specs = {
        'es': ('horizontal', ['#c60b1e', '#ffc400', '#c60b1e']),
        'en': ('horizontal', ['#b22234', '#ffffff', '#3c3b6e']),
        'fr': ('vertical', ['#0055a4', '#ffffff', '#ef4135']),
        'de': ('horizontal', ['#000000', '#dd0000', '#ffce00']),
        'it': ('vertical', ['#009246', '#ffffff', '#ce2b37']),
        'pt': ('vertical-40', ['#046a38', '#da291c']),
        'nl': ('horizontal', ['#ae1c28', '#ffffff', '#21468b']),
        'pl': ('horizontal-50', ['#ffffff', '#dc143c']),
        'ro': ('vertical', ['#002b7f', '#fcd116', '#ce1126']),
        'tr': ('solid', ['#e30a17']),
        'ru': ('horizontal', ['#ffffff', '#0039a6', '#d52b1e']),
        'uk': ('horizontal', ['#0057b7', '#ffd700']),
        'ar': ('horizontal', ['#006c35', '#ffffff', '#000000']),
        'hi': ('horizontal', ['#ff9933', '#ffffff', '#138808']),
        'bn': ('solid', ['#006a4e']),
        'ur': ('vertical-25', ['#ffffff', '#01411c']),
        'zh-CN': ('solid', ['#de2910']),
        'zh-TW': ('solid', ['#fe0000']),
        'ja': ('horizontal-50', ['#ffffff', '#ffffff']),
        'ko': ('horizontal-50', ['#ffffff', '#ffffff']),
        'id': ('horizontal-50', ['#ce1126', '#ffffff']),
        'vi': ('solid', ['#da251d']),
        'th': ('horizontal-5', ['#a51931', '#f4f5f8', '#2d2a4a', '#f4f5f8', '#a51931']),
        'ms': ('horizontal', ['#cc0001', '#ffffff', '#010066']),
    }
    kind, colors = flag_specs.get(normalized_code, ('solid', ['#2563eb']))

    if kind == 'vertical':
        background = (
            f'<rect width="9" height="18" x="0" y="0" fill="{colors[0]}"/>'
            f'<rect width="9" height="18" x="9" y="0" fill="{colors[1]}"/>'
            f'<rect width="9" height="18" x="18" y="0" fill="{colors[2]}"/>'
        )
    elif kind == 'vertical-40':
        background = (
            f'<rect width="11" height="18" x="0" y="0" fill="{colors[0]}"/>'
            f'<rect width="16" height="18" x="11" y="0" fill="{colors[1]}"/>'
        )
    elif kind == 'vertical-25':
        background = (
            f'<rect width="7" height="18" x="0" y="0" fill="{colors[0]}"/>'
            f'<rect width="20" height="18" x="7" y="0" fill="{colors[1]}"/>'
        )
    elif kind == 'horizontal':
        background = (
            f'<rect width="27" height="6" x="0" y="0" fill="{colors[0]}"/>'
            f'<rect width="27" height="6" x="0" y="6" fill="{colors[1]}"/>'
            f'<rect width="27" height="6" x="0" y="12" fill="{colors[2]}"/>'
        )
    elif kind == 'horizontal-50':
        background = (
            f'<rect width="27" height="9" x="0" y="0" fill="{colors[0]}"/>'
            f'<rect width="27" height="9" x="0" y="9" fill="{colors[1]}"/>'
        )
    elif kind == 'horizontal-5':
        background = (
            f'<rect width="27" height="3.6" x="0" y="0" fill="{colors[0]}"/>'
            f'<rect width="27" height="3.6" x="0" y="3.6" fill="{colors[1]}"/>'
            f'<rect width="27" height="7.2" x="0" y="7.2" fill="{colors[2]}"/>'
            f'<rect width="27" height="3.6" x="0" y="14.4" fill="{colors[3]}"/>'
            f'<rect width="27" height="3.6" x="0" y="18" fill="{colors[4]}"/>'
        )
    else:
        background = f'<rect width="27" height="18" x="0" y="0" fill="{colors[0]}"/>'

    overlay = ''
    if normalized_code == 'tr':
        overlay = '<circle cx="11" cy="9" r="4.2" fill="#ffffff"/><circle cx="12.5" cy="9" r="3.4" fill="#e30a17"/>'
    elif normalized_code == 'hi':
        overlay = '<circle cx="13.5" cy="9" r="2.2" fill="none" stroke="#000080" stroke-width="1"/>'
    elif normalized_code == 'bn':
        overlay = '<circle cx="14" cy="9" r="4.2" fill="#f42a41"/>'
    elif normalized_code == 'ur':
        overlay = '<circle cx="17" cy="9" r="3.5" fill="#ffffff"/><circle cx="18.2" cy="9" r="2.8" fill="#01411c"/>'
    elif normalized_code == 'zh-CN':
        overlay = '<polygon points="6,3 7.2,6.1 10.5,6.1 7.8,8 8.9,11 6,9.2 3.1,11 4.2,8 1.5,6.1 4.8,6.1" fill="#ffde00"/>'
    elif normalized_code == 'zh-TW':
        overlay = '<rect x="0" y="0" width="11" height="8" fill="#000095"/><circle cx="5.5" cy="4" r="2" fill="#ffffff"/>'
    elif normalized_code == 'ja':
        overlay = '<circle cx="13.5" cy="9" r="4.4" fill="#bc002d"/>'
    elif normalized_code == 'ko':
        overlay = '<path d="M13.5 5a4 4 0 1 1-4 4c0-2.2 1.8-4 4-4z" fill="#cd2e3a"/><path d="M13.5 13a4 4 0 1 1 4-4c0 2.2-1.8 4-4 4z" fill="#0047a0"/>'
    elif normalized_code == 'vi':
        overlay = '<polygon points="13.5,4 15,8 19.2,8 15.8,10.4 17.2,14.2 13.5,11.7 9.8,14.2 11.2,10.4 7.8,8 12,8" fill="#ffde00"/>'
    elif normalized_code == 'ms':
        overlay = '<rect x="0" y="0" width="12" height="10" fill="#010066"/><circle cx="6.2" cy="5" r="2.5" fill="#ffcc00"/><circle cx="7" cy="5" r="2" fill="#010066"/>'

    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="27" height="18" viewBox="0 0 27 18" role="img" aria-hidden="true">'
        '<rect width="27" height="18" rx="3" fill="#ffffff"/>'
        f'{background}{overlay}'
        '<rect width="26" height="17" x=".5" y=".5" rx="2.5" fill="none" stroke="rgba(15,23,42,.18)"/>'
        '</svg>'
    )
    return Markup(svg)


def translate_text(key, language_code=None, **kwargs):
    """Obtiene un texto traducido con fallback seguro."""
    normalized_code = normalize_language_code(language_code)
    message = (
        TRANSLATIONS_CATALOG.get(normalized_code, {}).get(key)
        or TRANSLATIONS_CATALOG.get('en', {}).get(key)
        or TRANSLATIONS_CATALOG.get(DEFAULT_LANGUAGE, {}).get(key)
        or key
    )
    if kwargs:
        try:
            return message.format(**kwargs)
        except Exception:
            return message
    return message


def get_current_language(user=None):
    """Resuelve el idioma actual a partir de la sesion o del usuario."""
    session_language = normalize_language_code(session.get('preferred_language'))
    if user and getattr(user, 'preferred_language', None):
        resolved_language = normalize_language_code(user.preferred_language)
    elif session.get('user_id'):
        current_user = db.session.get(User, session.get('user_id'))
        resolved_language = normalize_language_code(
            current_user.preferred_language if current_user and current_user.preferred_language else session_language
        )
    else:
        resolved_language = session_language

    session['preferred_language'] = resolved_language
    return resolved_language


def build_language_options_html(selected_language, display_language=None):
    """Genera las opciones HTML del selector personalizado de idiomas."""
    normalized_selected = normalize_language_code(selected_language)
    normalized_display = normalize_language_code(display_language or normalized_selected)
    options = []
    for item in LANGUAGE_CATALOG:
        code = item['code']
        selected_attr = 'true' if code == normalized_selected else 'false'
        current_flag_url = get_language_flag_url(code)
        current_flag_markup = (
            Markup(f'<img src="{escape(current_flag_url)}" alt="" loading="lazy" decoding="async">')
            if current_flag_url
            else get_language_flag_svg(code)
        )
        label = get_language_label(code, normalized_display)
        options.append(
            '<button type="button" class="topbar-language-option js-language-option" '
            f'data-language-value="{escape(code)}" aria-pressed="{selected_attr}">'
            f'<span class="topbar-language-option-flag" aria-hidden="true">{current_flag_markup}</span>'
            f'<span class="topbar-language-option-label">{escape(label)}</span>'
            '</button>'
        )
    return Markup(''.join(options))


def build_topbar_language_html(selected_language):
    """Genera el selector de idioma compacto para la barra superior."""
    normalized_selected = normalize_language_code(selected_language)
    current_label = get_language_label(normalized_selected, normalized_selected)
    current_flag_url = get_language_flag_url(normalized_selected)
    current_flag_markup = (
        Markup(f'<img src="{escape(current_flag_url)}" alt="" loading="lazy" decoding="async">')
        if current_flag_url
        else get_language_flag_svg(normalized_selected)
    )
    next_url = request.full_path if request.query_string else request.path
    return Markup(
        f'<form class="topbar-language-form js-language-form" action="{escape(url_for("update_account_language"))}" method="POST">'
        f'<input type="hidden" name="next" value="{escape(next_url)}">'
        f'<input type="hidden" name="preferred_language" value="{escape(normalized_selected)}">'
        '<div class="topbar-language-field js-language-dropdown">'
        f'<button type="button" class="topbar-language-trigger js-language-trigger" aria-haspopup="listbox" aria-expanded="false" aria-label="{escape(current_label)}">'
        f'<span class="topbar-language-flag" aria-hidden="true">{current_flag_markup}</span>'
        f'<span class="topbar-language-current-label" aria-hidden="true">{escape(current_label)}</span>'
        '<span class="topbar-language-caret" aria-hidden="true"></span>'
        '</button>'
        '<div class="topbar-language-menu" hidden>'
        f'<div class="topbar-language-options" role="listbox" aria-label="{escape(current_label)}">'
        f'{build_language_options_html(normalized_selected, normalized_selected)}'
        '</div>'
        '</div>'
        '</div>'
        '</form>'
    )


def build_register_language_selector(selected_language):
    """Genera el selector de idioma para el formulario de registro."""
    normalized_selected = normalize_language_code(selected_language)
    current_label = get_language_label(normalized_selected, normalized_selected)
    current_flag_url = get_language_flag_url(normalized_selected)
    current_flag_markup = (
        Markup(f'<img src="{escape(current_flag_url)}" alt="" loading="lazy" decoding="async">')
        if current_flag_url
        else get_language_flag_svg(normalized_selected)
    )
    options = []
    for item in LANGUAGE_CATALOG:
        code = item['code']
        selected_attr = 'true' if code == normalized_selected else 'false'
        flag_url = get_language_flag_url(code)
        flag_markup = (
            Markup(f'<img src="{escape(flag_url)}" alt="" loading="lazy" decoding="async">')
            if flag_url
            else get_language_flag_svg(code)
        )
        label = get_language_label(code, normalized_selected)
        options.append(
            '<button type="button" class="topbar-language-option js-reg-lang-option" '
            f'data-language-value="{escape(code)}" aria-pressed="{selected_attr}">'
            f'<span class="topbar-language-option-flag" aria-hidden="true">{flag_markup}</span>'
            f'<span class="topbar-language-option-label">{escape(label)}</span>'
            '</button>'
        )
    options_html = Markup(''.join(options))
    return Markup(
        '<div class="register-language-selector js-reg-lang-dropdown">'
        f'<input type="hidden" name="preferred_language" value="{escape(normalized_selected)}">'
        f'<button type="button" class="topbar-language-trigger js-reg-lang-trigger" aria-haspopup="listbox" aria-expanded="false" aria-label="{escape(current_label)}">'
        f'<span class="topbar-language-flag js-reg-lang-flag" aria-hidden="true">{current_flag_markup}</span>'
        f'<span class="topbar-language-current-label js-reg-lang-label" aria-hidden="true">{escape(current_label)}</span>'
        '<span class="topbar-language-caret" aria-hidden="true"></span>'
        '</button>'
        '<div class="topbar-language-menu" hidden>'
        '<div class="topbar-language-options" role="listbox">'
        f'{options_html}'
        '</div>'
        '</div>'
        '</div>'
    )


def build_client_translations(language_code=None):
    """Expone los textos del frontend que necesita JavaScript."""
    keys = [
        'js.no_file_selected', 'js.select_workspace', 'js.create_new_workspace', 'js.no_templates',
        'js.col_pending', 'js.col_in_progress', 'js.col_done',
        'js.empty_board_summary', 'js.create_board_with_template', 'js.create_board', 'js.cancel',
        'js.create_normal', 'js.use_template', 'js.preview', 'js.board_background',
        'js.upload_image', 'js.board_title', 'js.board_title_placeholder', 'js.workspace',
        'js.new_workspace_name', 'js.new_workspace_placeholder', 'js.template',
        'js.create_board_failed_title', 'js.create_board_failed_text', 'js.workspace_settings_title',
        'js.workspace_name', 'js.workspace_name_placeholder', 'js.save_changes',
        'js.field_required', 'js.workspace_updated', 'js.default_board_name',
        'js.update_email_title', 'js.update_email_label', 'js.update_email_placeholder',
        'js.save_email', 'js.email_required', 'js.email_invalid', 'js.new_column_title',
        'js.column_name', 'js.column_placeholder', 'js.create', 'js.new_task_title',
        'js.task_name', 'js.task_placeholder', 'js.delete_column_title', 'js.delete_column_text',
        'js.confirm_delete', 'js.column_deleted', 'js.delete_task_title', 'js.delete_task_text',
        'js.task_deleted', 'js.delete_board_title', 'js.confirm_delete_board',
        'js.board_deleted', 'js.delete_workspace_title', 'js.delete_workspace_text',
        'js.confirm_delete_workspace', 'js.workspace_deleted',
        'js.board_title_required', 'js.workspace_required', 'js.new_workspace_required',
        'js.template_required', 'js.board_created_from_template', 'js.board_created',
        'js.workspace_and_board_created', 'js.empty_column',
        'js.edit_column_title', 'js.edit_column_label', 'js.edit_column_save', 'js.column_updated',
        'js.board_settings_saved', 'js.move_left', 'js.move_right',
    ]
    return {key: translate_text(key, language_code) for key in keys}


def is_valid_email_address(value):
    """Valida un email con un patron sencillo y limite de longitud."""
    if not value or len(value) > 100:
        return False
    return bool(email_regex.fullmatch(value))


def get_csrf_token():
    """Devuelve el token CSRF de la sesion o crea uno nuevo."""
    token = session.get('csrf_token')
    if not token:
        token = secrets.token_urlsafe(32)
        session['csrf_token'] = token
    return token


def is_csrf_valid():
    """Comprueba que el token CSRF de la peticion coincida con la sesion."""
    expected_token = session.get('csrf_token')
    provided_token = (
        request.form.get('csrf_token')
        or request.headers.get('X-CSRF-Token')
        or request.headers.get('X-Csrf-Token')
    )
    if not expected_token or not provided_token:
        return False
    return secrets.compare_digest(expected_token, provided_token)


def check_rate_limit(action, limit, window_seconds, extra_scope=''):
    """Aplica un rate limit simple en memoria por IP y ambito adicional."""
    now = time.time()
    key = f'{action}:{get_client_ip()}:{extra_scope}'
    entries = rate_limit_store.get(key, [])
    entries = [stamp for stamp in entries if now - stamp < window_seconds]
    if len(entries) >= limit:
        retry_after = max(1, int(window_seconds - (now - entries[0])))
        rate_limit_store[key] = entries
        return False, retry_after
    entries.append(now)
    rate_limit_store[key] = entries
    return True, 0


@app.context_processor
def inject_security_helpers():
    """Hace disponible el token CSRF en todas las plantillas."""
    current_language = get_current_language()
    return {
        'csrf_token': get_csrf_token,
        'current_language': current_language,
        'language_catalog': LANGUAGE_CATALOG,
        'language_switcher_html': build_topbar_language_html(current_language),
        'js_translations': build_client_translations(current_language),
        't': lambda key, **kwargs: translate_text(key, current_language, **kwargs),
    }


@app.before_request
def apply_basic_request_protection():
    """Aplica medidas basicas de sesion y CSRF antes de atender la peticion."""
    session.permanent = True

    if request.method == 'POST' and request.endpoint not in ('static', 'js_static'):
        if not is_csrf_valid():
            return 'Solicitud no valida.', 400


@app.after_request
def add_security_headers(response):
    """Endurece las respuestas con cabeceras de seguridad razonables."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    return response


def verify_email_verification_token(token):
    """Valida el token del correo de verificacion."""
    serializer = get_reset_serializer()
    try:
        email = serializer.loads(token, salt='email-verification', max_age=86400)
    except SignatureExpired:
        return None, 'El enlace de verificacion ha caducado.'
    except BadSignature:
        return None, 'El enlace de verificacion no es valido.'

    user = User.query.filter_by(email=email).first()
    if not user:
        return None, 'La cuenta asociada ya no existe.'
    return user, None


def log_activity(user_id, action, detail):
    """Guarda una accion para mostrarla despues en la pagina de actividad."""
    if not user_id:
        return
    db.session.add(ActivityLog(user_id=user_id, action=action[:120], detail=detail[:255]))
    db.session.commit()


def build_email_shell(
    title,
    intro,
    cta_label=None,
    cta_url=None,
    detail_lines=None,
    outro=None,
    show_cta=False,
    show_cta_fallback=False,
    buttons=None,
    intro_html=None,
):
    """Construye una plantilla HTML sencilla y cuidada para los emails de Prodify."""
    safe_title = html_escape(title)
    safe_intro = intro_html if intro_html is not None else html_escape(intro).replace('\n', '<br>')
    safe_cta_label = html_escape(cta_label or '')
    safe_cta_url = html_escape(cta_url or '')
    safe_outro = html_escape(outro or '').replace('\n', '<br>')
    safe_detail_lines = [html_escape(line) for line in (detail_lines or []) if line]
    year = datetime.utcnow().year
    login_url = f'{public_base_url}/login'

    details_html = ''
    if safe_detail_lines:
        detail_items = ''.join(
            f'<li style="margin:0 0 8px;color:#94a3b8;font-size:14px;line-height:1.6;">{line}</li>'
            for line in safe_detail_lines
        )
        details_html = (
            '<div style="margin:24px 0;padding:20px 22px;border-radius:18px;'
            'background:#0b1324;border:1px solid #1e335c;">'
            '<div style="color:#e2e8f0;font-size:14px;font-weight:700;margin-bottom:10px;">'
            'Detalles importantes</div>'
            f'<ul style="padding-left:18px;margin:0;">{detail_items}</ul>'
            '</div>'
        )

    buttons_html = ''
    if buttons:
        parts = []
        for btn in buttons:
            btn_url = html_escape(btn.get('url', ''))
            btn_label = html_escape(btn.get('label', ''))
            if btn.get('primary'):
                parts.append(
                    f'<a href="{btn_url}" style="display:inline-block;padding:13px 26px;border-radius:999px;'
                    f'background:linear-gradient(135deg,#2f63ff,#1ea7ff);color:#ffffff !important;'
                    f'-webkit-text-fill-color:#ffffff !important;font-size:15px;font-weight:700;'
                    f'text-decoration:none;box-shadow:0 12px 28px rgba(47,99,255,.3);">{btn_label}</a>'
                )
            else:
                parts.append(
                    f'<a href="{btn_url}" style="display:inline-block;padding:12px 24px;border-radius:999px;'
                    f'background:transparent;color:#93c5fd !important;-webkit-text-fill-color:#93c5fd !important;'
                    f'font-size:15px;font-weight:700;text-decoration:none;border:1.5px solid #2f63ff;">{btn_label}</a>'
                )
        fallback_url = html_escape(buttons[0].get('url', '')) if buttons else ''
        buttons_html = (
            '<div style="margin:28px 0 16px;display:flex;gap:12px;flex-wrap:wrap;">' +
            ''.join(parts) +
            '</div>'
            f'<div style="color:#64748b;font-size:12px;margin-bottom:8px;">'
            f'Si los botones no se abren, copia este enlace: '
            f'<span style="color:#93c5fd;word-break:break-all;">{fallback_url}</span></div>'
        )

    cta_html = ''
    if show_cta and safe_cta_label and safe_cta_url:
        cta_html = (
            '<div style="margin:28px 0 24px;">'
            f'<a href="{safe_cta_url}" '
            'style="display:inline-block;padding:14px 24px;border-radius:999px;'
            'background:linear-gradient(135deg,#2f63ff,#1ea7ff);color:#ffffff !important;'
            '-webkit-text-fill-color:#ffffff !important;font-size:15px;font-weight:700;'
            'text-decoration:none;box-shadow:0 16px 30px rgba(47,99,255,.35);">'
            f'{safe_cta_label}</a>'
            '</div>'
        )

    cta_fallback_html = ''
    if show_cta_fallback and safe_cta_url:
        cta_fallback_html = (
            '<div style="margin:18px 0 0;color:#94a3b8 !important;-webkit-text-fill-color:#94a3b8 !important;'
            'font-size:12px;line-height:1.7;">'
            'Si no se abre el boton, copia este enlace en tu navegador:<br>'
            f'<span style="color:#93c5fd !important;-webkit-text-fill-color:#93c5fd !important;word-break:break-all;">{safe_cta_url}</span>'
            '</div>'
        )

    return (
        '<!DOCTYPE html>'
        '<html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">'
        f'<title>{safe_title}</title></head>'
        '<body style="margin:0;padding:0;background:#05070d;font-family:Arial,Helvetica,sans-serif;color:#e2e8f0;">'
        '<div style="padding:32px 16px;background:radial-gradient(circle at top,#16346d 0%,#05070d 54%);">'
        '<div style="max-width:640px;margin:0 auto;">'
        '<div style="padding:28px;border-radius:28px;background:linear-gradient(180deg,#0b1324,#09101d);'
        'border:1px solid #1f3156;box-shadow:0 24px 60px rgba(0,0,0,.45);">'
        '<div style="margin-bottom:28px;">'
        '<div style="display:inline-flex;align-items:center;gap:18px;">'
        '<div style="width:50px;height:50px;border-radius:16px;background:linear-gradient(135deg,#2f63ff,#1ea7ff);'
        'color:#fff;font-size:26px;font-weight:800;line-height:50px;text-align:center;box-shadow:0 16px 30px rgba(47,99,255,.35);">P</div>'
        '<div style="padding-left:2px;">'
        '<div style="color:#e5efff !important;-webkit-text-fill-color:#e5efff !important;font-size:22px;font-weight:800;letter-spacing:.02em;line-height:1.1;">Prodify</div>'
        '<div style="color:#93c5fd !important;-webkit-text-fill-color:#93c5fd !important;font-size:12px;letter-spacing:.18em;text-transform:uppercase;">Workspace Flow</div>'
        '</div></div></div>'
        '<div style="padding:28px;border-radius:24px;background:linear-gradient(180deg,#101a2d,#0c1629);border:1px solid #28406d;">'
        f'<div style="display:inline-block;margin-bottom:14px;padding:6px 10px;border-radius:999px;background:rgba(47,99,255,.18);color:#bfdbfe !important;-webkit-text-fill-color:#bfdbfe !important;font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;">Notificacion de cuenta</div>'
        f'<h1 style="margin:0 0 14px;color:#ffffff !important;-webkit-text-fill-color:#ffffff !important;font-size:30px;font-weight:800;line-height:1.15;">{safe_title}</h1>'
        f'<p style="margin:0;color:#cbd5e1 !important;-webkit-text-fill-color:#cbd5e1 !important;font-size:16px;line-height:1.75;">{safe_intro}</p>'
        f'{buttons_html}'
        f'{cta_html}'
        f'{details_html}'
        f'{cta_fallback_html}'
        f'<p style="margin:22px 0 0;color:#94a3b8 !important;-webkit-text-fill-color:#94a3b8 !important;font-size:14px;line-height:1.7;">{safe_outro}</p>'
        '</div>'
        '<div style="padding-top:24px;color:#64748b !important;-webkit-text-fill-color:#64748b !important;font-size:12px;line-height:1.7;">'
        f'Has recibido este correo porque tienes una cuenta en Prodify o has iniciado una accion relacionada con tu acceso.<br>'
        f'Prodify &middot; {year}'
        '</div>'
        '</div></div></div></body></html>'
    )


def send_email_message(to_email, subject, text_content, html_content=None):
    """Envia un email por Resend o SMTP si alguno de los dos esta configurado."""
    if resend_api_key:
        print(f'[Prodify] Intentando enviar email por Resend a {to_email} con asunto "{subject}"', flush=True)
        payload = {
            'from': resend_from,
            'to': [to_email],
            'subject': subject,
            'text': text_content,
        }
        if html_content:
            payload['html'] = html_content
        request = Request(
            'https://api.resend.com/emails',
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'Authorization': f'Bearer {resend_api_key}',
                'Content-Type': 'application/json',
                'User-Agent': 'Prodify/1.0',
            },
            method='POST',
        )
        try:
            with urlopen(request, timeout=15) as response:
                response.read()
            print(f'[Prodify] Email enviado por Resend a {to_email}', flush=True)
            return True, None
        except HTTPError as exc:
            error_body = exc.read().decode('utf-8', errors='replace')
            print(f'[Prodify] Fallo Resend para {to_email}: HTTP {exc.code}: {error_body}', flush=True)
            return False, f'Resend HTTP {exc.code}: {error_body}'
        except URLError as exc:
            print(f'[Prodify] Fallo Resend para {to_email}: {exc.reason}', flush=True)
            return False, f'Resend error de red: {exc.reason}'
        except Exception as exc:
            print(f'[Prodify] Fallo Resend para {to_email}: {exc}', flush=True)
            return False, f'Resend error inesperado: {exc}'

    if smtp_host and smtp_user and smtp_password:
        print(
            f'[Prodify] Intentando enviar email por SMTP a {to_email} usando {smtp_host}:{smtp_port} '
            f'con remitente {smtp_from}',
            flush=True
        )
        message = EmailMessage()
        message['Subject'] = subject
        message['From'] = smtp_from
        message['To'] = to_email
        message.set_content(text_content)
        if html_content:
            message.add_alternative(html_content, subtype='html')

        try:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
                server.ehlo()
                if smtp_use_tls:
                    server.starttls(context=ssl.create_default_context())
                    server.ehlo()
                server.login(smtp_user, smtp_password)
                server.send_message(message)
            print(f'[Prodify] Email enviado por SMTP a {to_email}', flush=True)
            return True, None
        except Exception as exc:
            print(f'[Prodify] Fallo SMTP para {to_email}: {exc}', flush=True)
            return False, f'SMTP error: {exc}'

    print('[Prodify] No hay proveedor de correo configurado para enviar emails.', flush=True)
    return False, 'No hay servicio de correo configurado. Configura RESEND_API_KEY o SMTP_HOST/SMTP_USER/SMTP_PASSWORD.'


def send_password_reset_email(user):
    """Envia el correo de recuperacion o deja el enlace en consola si no hay servicio."""
    token = generate_password_reset_token(user)
    reset_url = f'{public_base_url}/reset-password/{token}'
    print(f'[Prodify] Preparando recuperacion para {user.email}', flush=True)

    if not (resend_api_key or (smtp_host and smtp_user and smtp_password)):
        print(f'[Prodify] Enlace de recuperacion para {user.email}: {reset_url}')
        return False, reset_url

    sent, error_detail = send_email_message(
        user.email,
        'Recupera tu acceso a Prodify',
        'Hemos recibido una solicitud para restablecer tu contraseña en Prodify.\n\n'
        f'Abre este enlace para crear una nueva contraseña:\n{reset_url}\n\n'
        f'El enlace caduca en {max(1, password_reset_max_age // 60)} minutos.\n'
        'Si no has pedido este cambio, puedes ignorar este correo.',
        build_email_shell(
            'Recupera tu acceso',
            'Hemos recibido una solicitud para restablecer la contraseña de tu cuenta en Prodify.',
            'Restablecer contraseña',
            reset_url,
            [
                f'El enlace caduca en {max(1, password_reset_max_age // 60)} minutos.',
                'Si no has pedido este cambio, puedes ignorar este mensaje.',
            ],
            'Si necesitas volver a entrar, podrás hacerlo en cuanto cambies la contraseña.',
            show_cta=True,
            show_cta_fallback=True,
        )
    )
    if not sent:
        print(f'[Prodify] Error enviando recuperacion a {user.email}: {error_detail}')
        print(f'[Prodify] Enlace de recuperacion para {user.email}: {reset_url}')
        return False, reset_url
    return True, reset_url


def send_verification_email(user):
    """Envia el correo de verificacion o deja el enlace en consola si no hay servicio."""
    token = generate_email_verification_token(user)
    verify_url = url_for('verify_email', token=token, _external=True)
    print(f'[Prodify] Preparando verificacion para {user.email}', flush=True)

    if not (resend_api_key or (smtp_host and smtp_user and smtp_password)):
        print(f'[Prodify] Enlace de verificacion para {user.email}: {verify_url}')
        return False, verify_url

    sent, error_detail = send_email_message(
        user.email,
        'Confirma tu cuenta de Prodify',
        'Gracias por registrarte en Prodify.\n\n'
        f'Confirma tu correo con este enlace:\n{verify_url}\n\n'
        'Hasta que no verifiques la cuenta no podrás iniciar sesión.\n'
        'Si no has creado esta cuenta, puedes ignorar este mensaje.',
        build_email_shell(
            'Confirma tu cuenta',
            'Ya casi esta todo listo. Confirma tu correo para activar tu cuenta y empezar a organizar tus tableros en Prodify.',
            'Verificar correo',
            verify_url,
            [
                'Necesitas verificar la cuenta antes de iniciar sesión.',
                'Si no has creado esta cuenta, puedes ignorar este mensaje.',
            ],
            'Tu espacio de trabajo te estara esperando en cuanto completes la verificacion.'
        )
    )
    if not sent:
        print(f'[Prodify] Error enviando verificacion a {user.email}: {error_detail}')
        print(f'[Prodify] Enlace de verificacion para {user.email}: {verify_url}')
        return False, verify_url
    print(f'[Prodify] Verificacion enviada correctamente a {user.email}', flush=True)
    return True, verify_url


def send_verified_confirmation_email(user):
    """Envia un correo confirmando que la cuenta ya ha quedado activada."""
    print(f'[Prodify] Preparando confirmacion de cuenta verificada para {user.email}', flush=True)

    if not (resend_api_key or (smtp_host and smtp_user and smtp_password)):
        print(f'[Prodify] No hay proveedor configurado para confirmar la verificacion de {user.email}', flush=True)
        return False

    sent, error_detail = send_email_message(
        user.email,
        'Tu cuenta de Prodify ya esta verificada',
        'Tu correo se ha verificado correctamente.\n\n'
        'Ya puedes iniciar sesión y empezar a usar Prodify con normalidad.\n\n'
        'Si no has realizado esta accion, revisa la seguridad de tu cuenta.',
        build_email_shell(
            'Cuenta verificada con exito',
            'Tu correo ya ha sido confirmado y tu cuenta de Prodify esta activa.',
            'Entrar en Prodify',
            f'{public_base_url}/login',
            [
                'Ya puedes iniciar sesión con normalidad.',
                'Si no has sido tú, revisa tu cuenta y cambia la contraseña cuanto antes.',
            ],
            'Gracias por confiar en Prodify para organizar tu trabajo.'
        )
    )
    if not sent:
        print(f'[Prodify] Error enviando confirmacion de verificacion a {user.email}: {error_detail}', flush=True)
        return False

    print(f'[Prodify] Confirmacion de verificacion enviada a {user.email}', flush=True)
    return True


def send_registration_welcome_email(user):
    """Envia un correo bonito confirmando que el registro en Prodify se ha completado."""
    print(f'[Prodify] Preparando correo de bienvenida para {user.email}', flush=True)

    if not (resend_api_key or (smtp_host and smtp_user and smtp_password)):
        print(f'[Prodify] No hay proveedor configurado para enviar bienvenida a {user.email}', flush=True)
        return False

    sent, error_detail = send_email_message(
        user.email,
        'Te has registrado en Prodify',
        'Tu cuenta en Prodify se ha creado correctamente.\n\n'
        'Ya puedes iniciar sesión y empezar a organizar tus tableros, tareas y espacios de trabajo.\n\n'
        'Si no has sido tú, ignora este correo o cambia tu contraseña cuanto antes.',
        build_email_shell(
            'Bienvenido a Prodify',
            'Tu cuenta ya esta lista. Hemos completado el registro correctamente y ya puedes entrar a tu espacio de trabajo.',
            None,
            None,
            [
                'Tu registro se ha completado correctamente.',
                'Ya puedes iniciar sesión con tu correo y tu contraseña.',
                'Si no has sido tu, revisa la seguridad de tu cuenta cuanto antes.',
            ],
            'Gracias por unirte a Prodify. Esperamos ayudarte a organizar mejor tu trabajo.'
        )
    )
    if not sent:
        print(f'[Prodify] Error enviando bienvenida a {user.email}: {error_detail}', flush=True)
        return False

    print(f'[Prodify] Correo de bienvenida enviado a {user.email}', flush=True)
    return True


def send_board_invitation_email(invitation, board, workspace, invited_by_user):
    """Envia una invitacion por email para acceder a un tablero concreto."""
    accept_url = f'{public_base_url}{url_for("accept_board_invitation", token=invitation.token)}'
    board_url = f'{public_base_url}{url_for("board_view", board_id=board.id)}'
    inviter_name = invited_by_user.email if invited_by_user else 'Prodify'
    role_label = get_role_label(invitation.role)
    subject = f'Te han invitado al tablero "{board.name}" en Prodify'
    text_content = (
        f'{inviter_name} te ha invitado al tablero "{board.name}"'
        f' del espacio "{workspace.name}" como {role_label}.\n\n'
        f'Acepta la invitacion:\n{accept_url}\n\n'
        f'Ver tablero:\n{board_url}\n\n'
        'Si no tenias cuenta, podras registrarte con ese mismo correo y entrar directamente.'
    )
    html_content = build_email_shell(
        'Invitacion a tablero',
        '',
        intro_html=(
            f'{html_escape(inviter_name)} quiere que te unas al tablero '
            f'<strong style="color:#ffffff">{html_escape(board.name)}</strong> dentro de Prodify.'
        ),
        detail_lines=[
            f'Espacio: {html_escape(workspace.name)}',
            f'Rol asignado: {html_escape(role_label)}',
            'Si todavia no tienes cuenta, podras crearla con este correo y entrar despues.',
        ],
        outro='Haz clic en Aceptar invitacion para unirte. Iniciara sesion automaticamente y te llevara al tablero.',
        buttons=[
            {'label': 'Aceptar invitacion', 'url': accept_url, 'primary': True},
        ],
    )
    return send_email_message(invitation.email, subject, text_content, html_content)


def get_user_display_data(user, profile):
    """Prepara el nombre y la inicial para mostrarlos en las plantillas."""
    if profile and profile.display_name:
        return {
            "user_name": profile.display_name,
            "user_initial": profile.display_name[0].upper(),
            "avatar_url": profile.avatar_url or '',
        }

    email_name = user.email.split('@')[0]
    return {
        "user_name": email_name,
        "user_initial": user.email[0].upper(),
        "avatar_url": (profile.avatar_url if profile and profile.avatar_url else ''),
    }


def get_accessible_workspaces(user_id):
    """Devuelve los espacios accesibles por el usuario y el rol que tiene en cada uno."""
    owned_workspaces = Workspace.query.filter_by(user_id=user_id).order_by(Workspace.created_at.asc()).all()
    memberships = WorkspaceMember.query.filter_by(user_id=user_id).all()

    roles_by_workspace = {}
    workspaces_by_id = {}

    for workspace in owned_workspaces:
        roles_by_workspace[workspace.id] = 'owner'
        workspaces_by_id[workspace.id] = workspace

    shared_workspace_ids = []
    for membership in memberships:
        if membership.role not in WORKSPACE_MEMBER_ROLES:
            continue
        if membership.workspace_id not in workspaces_by_id:
            shared_workspace_ids.append(membership.workspace_id)
            roles_by_workspace[membership.workspace_id] = membership.role

    if shared_workspace_ids:
        shared_workspaces = Workspace.query.filter(Workspace.id.in_(shared_workspace_ids)).all()
        for workspace in shared_workspaces:
            workspaces_by_id[workspace.id] = workspace

    workspaces = list(workspaces_by_id.values())
    workspaces.sort(key=lambda item: item.created_at or datetime.utcnow())
    return workspaces, roles_by_workspace


def get_workspace_role(workspace, user_id):
    """Devuelve el rol del usuario dentro de un espacio o None si no tiene acceso."""
    if not workspace:
        return None
    if workspace.user_id == user_id:
        return 'owner'

    membership = WorkspaceMember.query.filter_by(workspace_id=workspace.id, user_id=user_id).first()
    if membership and membership.role in WORKSPACE_MEMBER_ROLES:
        return membership.role
    return None


def can_view_workspace(role):
    return role in ('owner', 'admin', 'editor', 'lector')


def can_manage_workspace(role):
    return role in ('owner', 'admin')


def can_manage_board(role):
    return role in ('owner', 'admin')


def can_edit_board_content(role):
    """Permite editar contenido del tablero si tienes rol suficiente. True por defecto para debug."""
    if role is None:
        return True  # Debug: Si no hay rol, permite editar
    return role in ('owner', 'admin', 'editor')


def can_view_board(role):
    return role in ('owner', 'admin', 'editor', 'lector')


def resolve_stronger_role(primary_role, secondary_role):
    """Devuelve el rol con mayor nivel de permisos."""
    primary_priority = ROLE_PRIORITY.get((primary_role or '').strip().lower(), 0)
    secondary_priority = ROLE_PRIORITY.get((secondary_role or '').strip().lower(), 0)
    return primary_role if primary_priority >= secondary_priority else secondary_role


def get_board_member_role(board, user_id):
    """Devuelve el rol directo del usuario dentro de un tablero."""
    if not board:
        return None
    membership = BoardMember.query.filter_by(board_id=board.id, user_id=user_id).first()
    if membership and membership.role in BOARD_MEMBER_ROLES:
        return membership.role
    return None


def get_board_role(board, user_id):
    """Combina el rol del espacio y el rol directo del tablero."""
    if not board:
        return None
    workspace = db.session.get(Workspace, board.workspace_id)
    workspace_role = get_workspace_role(workspace, user_id) if workspace else None
    board_role = get_board_member_role(board, user_id)
    return resolve_stronger_role(workspace_role, board_role)


def get_workspace_for_user(workspace_id, user_id):
    """Busca un espacio accesible por el usuario y devuelve tambien su rol."""
    workspace = db.session.get(Workspace, workspace_id)
    if not workspace:
        return None, None

    role = get_workspace_role(workspace, user_id)
    if not can_view_workspace(role):
        return None, None
    return workspace, role


def build_manageable_workspaces_data(workspaces, roles_by_workspace=None):
    """Devuelve los espacios donde el usuario puede crear tableros."""
    manageable = []
    roles_by_workspace = roles_by_workspace or {}
    for workspace in workspaces:
        role = roles_by_workspace.get(workspace.id, 'owner')
        if can_manage_board(role):
            manageable.append({
                'id': workspace.id,
                'name': workspace.name,
            })
    return manageable


def get_board_preview_style(board, index=0):
    """Construye el estilo inline de la portada de un tablero."""
    fallback_gradients = [
        'linear-gradient(140deg, #1d4ed8, #2f63ff 45%, #1ea7ff)',
        'linear-gradient(140deg, #0e2a66, #1b459f 45%, #2f63ff)',
    ]
    if getattr(board, 'cover_url', ''):
        safe_url = escape(board.cover_url)
        return f'background-image: linear-gradient(rgba(6, 10, 18, .18), rgba(6, 10, 18, .28)), url("{safe_url}"); background-size: cover; background-position: center;'
    if getattr(board, 'background_color', ''):
        safe_color = escape(board.background_color)
        return f'background: {safe_color};'
    return f'background: {fallback_gradients[index % len(fallback_gradients)]};'


def get_board_for_user(board_id, user_id):
    """Busca un tablero accesible por el usuario junto a su espacio y rol."""
    board = db.session.get(Board, board_id)
    if not board:
        return None, None, None

    workspace = db.session.get(Workspace, board.workspace_id)
    role = get_board_role(board, user_id)
    if not workspace or not can_view_board(role):
        return None, None, None
    return board, workspace, role


def get_column_for_user(column_id, user_id):
    """Busca una columna accesible por el usuario junto al tablero, espacio y rol."""
    column = db.session.get(BoardColumn, column_id)
    if not column:
        return None, None, None, None

    board, workspace, role = get_board_for_user(column.board_id, user_id)
    if not board:
        return None, None, None, None
    return column, board, workspace, role


def get_card_for_user(card_id, user_id):
    """Busca una tarjeta accesible por el usuario junto a su contexto completo."""
    card = db.session.get(Card, card_id)
    if not card:
        return None, None, None, None, None

    column, board, workspace, role = get_column_for_user(card.column_id, user_id)
    if not column:
        return None, None, None, None, None
    return card, column, board, workspace, role


def get_role_label(role):
    """Transforma el rol interno en una etiqueta legible."""
    role_key = (role or '').strip().lower()
    role_translation_keys = {
        'owner': 'role.owner',
        'admin': 'role.admin',
        'editor': 'role.editor',
        'lector': 'role.reader',
    }
    translation_key = role_translation_keys.get(role_key)
    if translation_key:
        return translate_text(translation_key, get_current_language())
    return translate_text('role.no_access', get_current_language())


def build_avatar_html(initial, avatar_url='', class_name='member-avatar', alt_text='Avatar'):
    """Devuelve un avatar con foto si existe o una inicial como fallback."""
    safe_class = escape(class_name)
    safe_alt = escape(alt_text)
    if avatar_url:
        return Markup(
            f'<img src="{escape(avatar_url)}" alt="{safe_alt}" class="{safe_class} avatar-image">'
        )
    return Markup(
        f'<span class="{safe_class} avatar-fallback" aria-label="{safe_alt}">'
        f'<span class="avatar-letter">{escape(initial)}</span>'
        '</span>'
    )


def get_text_initial(text):
    """Devuelve la inicial en mayuscula de un texto."""
    if not text:
        return ''
    return text[0].upper()


def build_side_nav_html(active_page, language_code=None):
    """Genera el menu lateral principal."""
    tr = lambda key, **kwargs: translate_text(key, language_code or get_current_language(), **kwargs)
    links = [
        ('boards', tr('nav.boards'), url_for('home')),
        ('templates', tr('nav.templates'), url_for('templates_page')),
        ('home', tr('nav.home'), url_for('landing')),
    ]

    html = ['<nav class="side-nav d-flex flex-column">']
    for key, label, href in links:
        active_class = ' active' if active_page == key else ''
        html.append(f'<a class="side-link{active_class}" href="{escape(href)}">{escape(label)}</a>')
    html.append('</nav>')
    return Markup(''.join(html))


def build_workspace_list_html(workspaces, active_workspace_id=None, roles_by_workspace=None, language_code=None):
    """Genera la lista de espacios del sidebar."""
    tr = lambda key, **kwargs: translate_text(key, language_code or get_current_language(), **kwargs)
    if not workspaces:
        return Markup(f'<div class="workspace-item empty-note">{escape(tr("workspace.empty"))}</div>')

    html = []
    for workspace in workspaces:
        active_class = ' active' if active_workspace_id == workspace.id else ''
        href = url_for('open_workspace', workspace_id=workspace.id)
        role = (roles_by_workspace or {}).get(workspace.id, 'owner')
        html.append(
            f'<a class="workspace-item{active_class}" href="{escape(href)}">'
            f'<span class="workspace-avatar">{escape(get_text_initial(workspace.name))}</span>'
            f'<span>{escape(workspace.name)}</span>'
            f'<small class="workspace-role-badge">{escape(get_role_label(role))}</small>'
            '</a>'
        )
    return Markup(''.join(html))


def build_account_toggle_html(user_name, user_initial, avatar_url='', language_code=None):
    """Genera el boton del avatar de la cabecera usando foto o inicial."""
    tr = lambda key, **kwargs: translate_text(key, language_code or get_current_language(), **kwargs)
    avatar_html = build_avatar_html(user_initial, avatar_url, 'user-badge-avatar', tr('account.avatar_of', name=user_name))
    return Markup(
        f'<button class="user-badge" id="accountToggle" type="button" aria-label="{escape(tr("account.open_menu"))}">'
        f'{avatar_html}'
        '</button>'
    )


def build_account_menu_html(user_name, user_initial, user_email, avatar_url='', language_code=None):
    """Genera el menu desplegable de la cuenta."""
    tr = lambda key, **kwargs: translate_text(key, language_code or get_current_language(), **kwargs)
    account_avatar_html = build_avatar_html(user_initial, avatar_url, 'account-avatar', tr('account.avatar_of', name=user_name))
    html = [
        '<div class="account-menu" id="accountMenu" hidden>',
        f'<div class="account-section-title">{escape(tr("account.section"))}</div>',
        '<div class="account-hero">',
        str(account_avatar_html),
        '<div class="account-meta">',
        f'<strong>{escape(user_name)}</strong>',
        f'<span>{escape(user_email)}</span>',
        f'<small>{escape(tr("account.active"))}</small>',
        '</div>',
        '</div>',
        '<div class="account-links">',
        f'<a class="account-link" href="{escape(url_for("login"))}">{escape(tr("account.change_accounts"))}</a>',
        f'<a class="account-link account-link-ext" href="{escape(url_for("account_page"))}">{escape(tr("account.manage"))}</a>',
        '</div>',
        '<div class="account-divider"></div>',
        '<div class="account-section-title">Prodify</div>',
        '<div class="account-links">',
        f'<a class="account-link" href="{escape(url_for("profile_page"))}">{escape(tr("account.profile"))}</a>',
        f'<a class="account-link" href="{escape(url_for("activity_page"))}">{escape(tr("account.activity"))}</a>',
        f'<a class="account-link" href="{escape(url_for("cards_page"))}">{escape(tr("account.cards"))}</a>',
        f'<a class="account-link" href="{escape(url_for("settings_page"))}">{escape(tr("account.settings"))}</a>',
        '</div>',
        '<div class="account-divider"></div>',
        '<div class="account-links">',
        f'<a class="account-link" href="{escape(url_for("help_page"))}">{escape(tr("account.help"))}</a>',
        '</div>',
        '<div class="account-divider"></div>',
        f'<form action="{escape(url_for("logout"))}" method="POST" class="account-logout">',
        f'<button type="submit" class="logout-btn">{escape(tr("account.logout"))}</button>',
        '</form>',
        '</div>',
    ]
    return Markup(''.join(html))


def build_recent_boards_html(recent_boards, manageable_workspace_ids=None, language_code=None):
    """Genera el bloque de tableros recientes."""
    tr = lambda key, **kwargs: translate_text(key, language_code or get_current_language(), **kwargs)
    if not recent_boards:
        return Markup(
            '<div class="col-12 col-md-6 col-xl-6">'
            '<article class="board-card board-create js-create-board h-100">'
            f'<div class="board-create-text">{escape(tr("board.create_first"))}</div>'
            '</article>'
            '</div>'
        )

    html = []
    for index, board in enumerate(recent_boards, start=1):
        delete_url = url_for('delete_board', board_id=board.id)
        board_url = url_for('board_view', board_id=board.id)
        preview_style = get_board_preview_style(board, index - 1)
        html.append('<div class="col-12 col-md-6 col-xl-6"><article class="board-card h-100">')
        if board.workspace_id in (manageable_workspace_ids or set()):
            html.append(
                f'<form action="{escape(delete_url)}" method="POST" class="board-delete-form">'
                f'<button type="submit" class="board-delete-btn js-delete-board" title="{escape(tr("board.delete"))}">&times;</button>'
                '</form>'
            )
        html.append(
            f'<a class="board-link" href="{escape(board_url)}">'
            f'<div class="board-preview" style="{preview_style}"></div>'
            f'<div class="board-name">{escape(board.name)}</div>'
            '</a>'
            '</article></div>'
        )
    return Markup(''.join(html))


def build_workspace_blocks_html(workspaces, boards_by_workspace, active_workspace_id, roles_by_workspace=None, language_code=None):
    """Genera los bloques principales de espacios y tableros."""
    tr = lambda key, **kwargs: translate_text(key, language_code or get_current_language(), **kwargs)
    html = []
    for workspace in workspaces:
        if active_workspace_id and active_workspace_id != workspace.id:
            continue

        workspace_boards = boards_by_workspace.get(workspace.id, [])
        role = (roles_by_workspace or {}).get(workspace.id, 'owner')
        can_manage = can_manage_workspace(role)
        can_manage_boards = can_manage_board(role)
        html.append('<div class="workspace-block">')
        html.append('<div class="workspace-header">')
        html.append('<div class="workspace-label">')
        html.append(f'<span class="workspace-avatar">{escape(get_text_initial(workspace.name))}</span>')
        html.append(f'<strong>{escape(workspace.name)}</strong>')
        html.append(f'<small class="workspace-role-label">{escape(get_role_label(role))}</small>')
        html.append('</div>')
        html.append('<div class="workspace-actions">')
        html.append(
            f'<a href="{escape(url_for("workspace_view", workspace_id=workspace.id))}" class="btn btn-sm">{escape(tr("nav.boards"))}</a>'
        )
        html.append(
            f'<a href="{escape(url_for("workspace_members_page", workspace_id=workspace.id))}" class="btn btn-sm">{escape(tr("workspace.members"))}</a>'
        )
        if can_manage:
            html.append(
                f'<button type="button" class="btn btn-sm js-workspace-settings" '
                f'data-workspace-id="{workspace.id}" '
                f'data-workspace-name="{escape(workspace.name)}">{escape(tr("workspace.settings"))}</button>'
            )
        if role == 'owner':
            html.append(
                f'<form action="{escape(url_for("delete_workspace", workspace_id=workspace.id))}" method="POST" class="inline-form">'
                f'<button type="submit" class="workspace-delete-btn js-delete-workspace btn btn-sm">{escape(tr("common.delete"))}</button>'
                '</form>'
            )
        html.append('</div></div>')
        html.append('<div class="boards-row row g-3">')

        for index, board in enumerate(workspace_boards, start=1):
            preview_style = get_board_preview_style(board, index - 1)
            html.append('<div class="col-12 col-md-6 col-xl-6">')
            html.append('<article class="board-card h-100">')
            if can_manage_boards:
                html.append(
                    f'<form action="{escape(url_for("delete_board", board_id=board.id))}" method="POST" class="board-delete-form">'
                    f'<button type="submit" class="board-delete-btn js-delete-board" title="{escape(tr("board.delete"))}">&times;</button>'
                    '</form>'
                )
            html.append(f'<a class="board-link" href="{escape(url_for("board_view", board_id=board.id))}">')
            html.append(f'<div class="board-preview" style="{preview_style}"></div>')
            html.append(f'<div class="board-name">{escape(board.name)}</div>')
            html.append('</a></article></div>')

        if can_manage_boards:
            html.append(
                f'<div class="col-12 col-md-6 col-xl-6">'
                f'<article class="board-card board-create js-create-board h-100" data-workspace-id="{workspace.id}" data-workspace-name="{escape(workspace.name)}">'
                f'<div class="board-create-text">{escape(tr("board.create_new"))}</div>'
                '</article>'
                '</div>'
            )
        html.append('</div></div>')
    return Markup(''.join(html))


def get_translated_board_templates(language_code=None):
    lang = language_code or get_current_language()
    tr = lambda key: translate_text(key, lang)
    result = []
    for tpl in BOARD_TEMPLATES:
        raw_id = tpl['id']
        cat_key = 'template.cat.' + tpl['category'].lower().replace(' ', '_')
        translated = dict(tpl)
        translated['name']     = tr(f'template.{raw_id}.name') or tpl['name']
        translated['summary']  = tr(f'template.{raw_id}.summary') or tpl['summary']
        translated['category'] = tr(cat_key) or tpl['category']
        translated['columns']  = [tr(f'template.{raw_id}.col.{i}') or c for i, c in enumerate(tpl['columns'])]
        translated['tags']     = [tr(f'template.{raw_id}.tag.{i}') or tag for i, tag in enumerate(tpl['tags'])]
        result.append(translated)
    return result


def build_templates_sidebar_html(template_categories, grouped_templates, language_code=None):
    """Genera el indice lateral de plantillas."""
    tr = lambda key, **kwargs: translate_text(key, language_code or get_current_language(), **kwargs)
    html = []
    for category in template_categories:
        cat_key = 'template.cat.' + category.lower().replace(' ', '_')
        cat_label = tr(cat_key) or category
        html.append('<details class="template-group" open>')
        html.append(f'<summary>{escape(cat_label)}</summary>')
        html.append('<div class="template-group-links">')
        for template in grouped_templates.get(category, []):
            t_id = template["id"]
            t_name = tr(f'template.{t_id}.name') or template["name"]
            html.append(f'<a href="#template-{escape(t_id)}">{escape(t_name)}</a>')
        html.append('</div></details>')
    return Markup(''.join(html))


def build_templates_grid_html(templates, language_code=None):
    """Genera las tarjetas del catalogo de plantillas con diseno mejorado."""
    tr = lambda key, **kwargs: translate_text(key, language_code or get_current_language(), **kwargs)
    html = []
    for template in templates:
        raw_id  = template["id"]
        t_id    = escape(raw_id)
        t_acc   = escape(template["accent"])
        cat_key = 'template.cat.' + template["category"].lower().replace(' ', '_')
        t_cat   = escape(tr(cat_key) or template["category"])
        t_name  = escape(tr(f'template.{raw_id}.name') or template["name"])
        t_sum   = escape(tr(f'template.{raw_id}.summary') or template["summary"])
        raw_cols = [tr(f'template.{raw_id}.col.{i}') or c for i, c in enumerate(template["columns"])]
        column_count = len(raw_cols)

        html.append(
            f'<article class="template-card {t_acc}" id="template-{t_id}">'
            '<div class="template-poster">'
            '<div class="template-orb"></div>'
            '<div class="template-poster-top">'
            f'<span class="template-category">{t_cat}</span>'
            f'<span class="template-columns-count">{column_count} col.</span>'
            '</div>'
            '<div class="template-board-shell">'
            '<div class="template-board-chrome"><span></span><span></span><span></span></div>'
            '<div class="template-preview">'
        )
        for col in raw_cols:
            html.append(
                '<div class="preview-col">'
                f'<div class="preview-title">{escape(col)}</div>'
                '<div class="preview-card"></div>'
                '<div class="preview-card small"></div>'
                '<div class="preview-card micro"></div>'
                '</div>'
            )
        html.append(
            '</div>'
            '<div class="template-board-footer">'
            '<span class="board-pill"></span>'
            '<span class="board-pill short"></span>'
            '<span class="board-avatar-stack"><i></i><i></i><i></i></span>'
            '</div>'
            '</div>'
            '</div>'
            '<div class="template-head"><div>'
            f'<h3>{t_name}</h3>'
            f'<p>{t_sum}</p>'
            '</div>'
            f'<button type="button" class="template-action js-use-template" '
            f'data-template-name="{t_name}" data-template-id="{t_id}">'
            f'{escape(tr("common.start_with_template"))}</button></div>'
            '<div class="template-tags">'
        )
        raw_tags = [tr(f'template.{raw_id}.tag.{i}') or tag for i, tag in enumerate(template["tags"])]
        for tag in raw_tags:
            html.append(f'<span>#{escape(tag)}</span>')
        html.append('</div></article>')
    return Markup(''.join(html))


_BOARD_ACCENTS = ['blue', 'violet', 'rose', 'mint', 'amber', 'slate']


def build_board_settings_panel_html(board, columns, cards_by_column, workspace_role):
    """Genera un panel lateral de ajustes del tablero inspirado en el menu de Trello."""
    tr = lambda key, **kwargs: translate_text(key, get_current_language(), **kwargs)
    can_manage = can_manage_board(workspace_role)
    total_cards = sum(len(cards_by_column.get(column.id, [])) for column in columns)
    selected_color = board.background_color or '#1d4ed8'
    color_options = ['#1d4ed8', '#0f766e', '#be185d', '#7c3aed', '#ea580c', '#334155']
    board_members = BoardMember.query.filter_by(board_id=board.id).order_by(BoardMember.created_at.asc()).all()
    pending_invitations = BoardInvitation.query.filter_by(board_id=board.id, accepted_at=None).order_by(BoardInvitation.created_at.desc()).all()
    workspace = db.session.get(Workspace, board.workspace_id)
    owner = db.session.get(User, workspace.user_id) if workspace else None
    owner_profile = get_profile(owner) if owner else None
    owner_display = get_user_display_data(owner, owner_profile) if owner else {"user_name": "Usuario"}

    html = [
        '<aside class="board-settings-panel" aria-hidden="true">',
        '<div class="board-settings-shell">',
        '<div class="board-settings-head">',
        '<div class="board-settings-head-main">',
        f'<span class="eyebrow">{escape(tr("board.settings"))}</span>',
        f'<h2>{escape(tr("board.settings"))}</h2>',
        f'<p>{escape(tr("board.settings_subtitle"))}</p>',
        '</div>',
        f'<button type="button" class="board-settings-close js-board-settings-close" aria-label="{escape(tr("board.settings_close"))}" title="{escape(tr("board.settings_close"))}">&times;</button>',
        '</div>',
        '<div class="board-settings-metrics">',
        f'<div class="board-settings-metric"><span>{escape(tr("board.columns_count", count=len(columns)))}</span><strong>{len(columns)}</strong></div>',
        f'<div class="board-settings-metric"><span>{escape(tr("board.cards_count", count=total_cards))}</span><strong>{total_cards}</strong></div>',
        f'<div class="board-settings-metric"><span>{escape(tr("board.access_current"))}</span><strong>{escape(get_role_label(workspace_role))}</strong></div>',
        '</div>',
        '<section class="board-settings-section">',
        f'<div class="board-settings-section-head"><div><strong>{escape(tr("board.settings_background"))}</strong><span>{escape(tr("board.settings_background_help"))}</span></div></div>',
        f'<form class="board-settings-form" action="{escape(url_for("update_board", board_id=board.id))}" method="POST" enctype="multipart/form-data">',
        f'<input type="hidden" name="board_name" value="{escape(board.name)}">',
        f'<input type="hidden" name="board_background" value="{escape(selected_color)}" id="boardBackgroundInput">',
        '<div class="board-color-grid board-settings-colors">',
    ]
    for color in color_options:
        active = ' is-active' if color.lower() == selected_color.lower() else ''
        disabled = ' disabled' if not can_manage else ''
        html.append(f'<button type="button" class="board-color-option js-board-color-option{active}" data-color-value="{escape(color)}" style="background:{escape(color)}"{disabled}></button>')
    html.extend([
        '</div>',
        f'<label class="board-settings-label" for="boardSettingsCover">{escape(tr("board.background_cover_label"))}</label>',
        '<div class="board-cover-upload board-settings-upload">',
        f'<label for="boardSettingsCover" class="board-cover-upload-btn">{escape(translate_text("js.upload_image", get_current_language()))}</label>',
        f'<input id="boardSettingsCover" class="js-board-cover-input" type="file" name="board_cover_file" accept=".jpg,.jpeg,.png,.svg,.webp,image/jpeg,image/png,image/svg+xml,image/webp" {"disabled" if not can_manage else ""}>',
        f'<span class="board-cover-upload-name js-board-cover-name">{escape(board.cover_url or tr("js.no_file_selected"))}</span>',
        '</div>',
        f'<p class="board-settings-help">{escape(tr("board.background_cover_help"))}</p>',
        f'<button type="submit" class="btn-primary board-settings-save" {"disabled" if not can_manage else ""}>{escape(tr("board.save_changes"))}</button>',
        '</form>',
        '</section>',
        '<section class="board-settings-section">',
        f'<div class="board-settings-section-head"><div><strong>{escape(tr("board.settings_permissions"))}</strong><span>{escape(tr("board.settings_permissions_help"))}</span></div></div>',
        '<div class="board-permissions-list">',
        '<div class="board-member-row board-owner-row">',
        f'<div class="board-member-copy"><strong>{escape(owner_display["user_name"])}</strong><span>{escape(owner.email if owner else "")}</span></div>',
        f'<span class="workspace-role-label member-role-owner">{escape(get_role_label("owner"))}</span>',
        '</div>',
    ])
    for membership in board_members:
        member_user = db.session.get(User, membership.user_id)
        if not member_user:
            continue
        html.append('<div class="board-member-row">')
        html.append(f'<div class="board-member-copy"><strong>{escape(member_user.email.split("@")[0])}</strong><span>{escape(member_user.email)}</span></div>')
        html.append('<div class="board-member-actions">')
        if can_manage:
            html.append(f'<form action="{escape(url_for("update_board_member_role", board_id=board.id, member_id=membership.id))}" method="POST" class="board-member-role-form"><select name="role" class="board-settings-select">')
            for role in BOARD_MEMBER_ROLES:
                selected = ' selected' if role == membership.role else ''
                html.append(f'<option value="{escape(role)}"{selected}>{escape(get_role_label(role))}</option>')
            html.append(f'</select><button type="submit" class="settings-action-btn compact">{escape(tr("workspace.save"))}</button></form>')
            html.append(f'<form action="{escape(url_for("remove_board_member", board_id=board.id, member_id=membership.id))}" method="POST" class="inline-form"><button type="submit" class="workspace-delete-btn btn btn-sm">{escape(tr("common.delete"))}</button></form>')
        else:
            html.append(f'<span class="workspace-role-label">{escape(get_role_label(membership.role))}</span>')
        html.append('</div></div>')
    html.extend([
        '</div>',
        f'<form class="board-settings-form board-invite-form" action="{escape(url_for("invite_board_member", board_id=board.id))}" method="POST">',
        '<div class="board-invite-grid">',
        f'<input type="email" name="member_email" class="board-settings-input" placeholder="{escape(tr("board.invite_email_placeholder"))}" required>',
        '<select name="role" class="board-settings-select">',
    ])
    for role in BOARD_MEMBER_ROLES:
        html.append(f'<option value="{escape(role)}">{escape(get_role_label(role))}</option>')
    html.extend([
        '</select>',
        f'<button type="submit" class="btn-primary" {"disabled" if not can_manage else ""}>{escape(tr("board.invite_btn"))}</button>',
        '</div>',
        '</form>',
    ])
    if pending_invitations:
        html.extend([
            f'<div class="board-settings-section-head"><div><strong>{escape(tr("board.pending_invitations"))}</strong><span>{escape(tr("board.pending_invitations_help"))}</span></div></div>',
            '<div class="board-pending-list">',
        ])
        for invitation in pending_invitations:
            html.append('<div class="board-member-row">')
            html.append(f'<div class="board-member-copy"><strong>{escape(invitation.email)}</strong><span>{escape(get_role_label(invitation.role))}</span></div>')
            html.append('<div class="board-member-actions">')
            if can_manage:
                html.append(f'<form action="{escape(url_for("delete_board_invitation", board_id=board.id, invitation_id=invitation.id))}" method="POST" class="inline-form"><button type="submit" class="workspace-delete-btn btn btn-sm">{escape(tr("common.delete"))}</button></form>')
            html.append('</div></div>')
        html.append('</div>')
    html.extend([
        '</section>',
        '<section class="board-settings-section board-settings-danger">',
        f'<div class="board-settings-section-head"><div><strong>{escape(tr("board.settings_danger"))}</strong><span>{escape(tr("board.settings_danger_help"))}</span></div></div>',
        f'<form action="{escape(url_for("delete_board", board_id=board.id))}" method="POST" class="inline-form"><button type="submit" class="workspace-delete-btn js-delete-board btn btn-sm" {"disabled" if not can_manage else ""}>{escape(tr("board.delete"))}</button></form>',
        '</section>',
        '</div>',
        '</aside>',
    ])
    return Markup(''.join(html))


def build_board_columns_html(columns, cards_by_column, board_id=0, can_edit=False):
    """Genera las columnas del kanban con titulo editable y soporte para reordenar."""
    accent = _BOARD_ACCENTS[board_id % len(_BOARD_ACCENTS)]
    tr = lambda key, **kwargs: translate_text(key, get_current_language(), **kwargs)
    html = []
    for column in columns:
        column_cards = cards_by_column.get(column.id, [])
        html.append(
            f'<div class="kanban-column" data-column-id="{column.id}" data-accent="{accent}">'
        )
        if can_edit:
            html.append(
                f'<div class="kanban-title js-column-drag-handle" draggable="true" data-column-id="{column.id}">'
                '<div class="kanban-title-copy">'
                f'<button type="button" class="kanban-column-name js-edit-column" data-column-id="{column.id}" data-column-title="{escape(column.title)}" title="{escape(tr("board.column_rename"))}">{escape(column.title)}</button>'
                f'<span>{len(column_cards)} {escape(tr("board.task"))}</span>'
                '</div>'
                '<div class="kanban-col-delete">'
                f'<form action="{escape(url_for("delete_column", column_id=column.id))}" method="POST" class="inline-form">'
                f'<button type="submit" class="delete-col-btn js-delete-column" title="{escape(tr("board.delete_column"))}" draggable="false">🗑</button>'
                '</form>'
                '</div>'
                '</div>'
            )
        else:
            html.append(
                '<div class="kanban-title">'
                '<div class="kanban-title-copy">'
                f'<h3>{escape(column.title)}</h3>'
                f'<span>{len(column_cards)} {escape(tr("board.task"))}</span>'
                '</div>'
                '</div>'
            )
        html.append(f'<div class="kanban-cards" data-column-id="{column.id}">')
        if column_cards:
            for card in column_cards:
                draggable = 'true' if can_edit else 'false'
                html.append(
                    f'<div class="kanban-card" draggable="{draggable}" data-card-id="{card.id}">'
                    f'<span class="card-title">{escape(card.title)}</span>'
                )
                if can_edit:
                    html.append(
                        f'<form action="{escape(url_for("delete_card", card_id=card.id))}" method="POST" class="card-delete-form">'
                        f'<button type="submit" class="card-delete-btn js-delete-card" title="{escape(tr("board.delete_task"))}" draggable="false">&times;</button>'
                        '</form>'
                    )
                html.append('</div>')
        else:
            html.append(f'<div class="kanban-card ghost">{escape(tr("board.no_tasks"))}</div>')
        
        html.append('</div>')
        
        if can_edit:
            html.append('<div class="kanban-footer">')
            html.append(
                f'<button type="button" class="add-card-btn js-add-card" data-column-id="{column.id}" title="Agregar nueva tarea">'
                '+ Tarea'
                '</button>'
            )
            html.append('</div>')
        
        html.append('</div>')
    return Markup(''.join(html))


def build_auth_message_html(message, tone='error'):
    """Genera mensajes visuales para login, registro y recuperacion."""
    if not message:
        return Markup('')
    class_name = 'login-error'
    if tone == 'success':
        class_name = 'login-success'
    elif tone == 'info':
        class_name = 'login-info'
    return Markup(f'<div class="{class_name}">{escape(message)}</div>')



def ensure_auth_schema():
    """Asegura que la tabla de usuarios tenga las columnas nuevas de verificacion."""
    inspector = db.inspect(db.engine)
    columns = {column['name'] for column in inspector.get_columns('users')}

    if 'email_verified' not in columns:
        db.session.execute(db.text('ALTER TABLE users ADD COLUMN email_verified TINYINT(1) NOT NULL DEFAULT 1'))
        db.session.commit()

    if 'verified_at' not in columns:
        db.session.execute(db.text('ALTER TABLE users ADD COLUMN verified_at DATETIME NULL'))
        db.session.commit()

    if 'has_seen_inicio' not in columns:
        db.session.execute(db.text('ALTER TABLE users ADD COLUMN has_seen_inicio TINYINT(1) NOT NULL DEFAULT 0'))
        db.session.commit()
        db.session.execute(db.text('UPDATE users SET has_seen_inicio = 1'))
        db.session.commit()

    if 'preferred_language' not in columns:
        db.session.execute(db.text("ALTER TABLE users ADD COLUMN preferred_language VARCHAR(10) NOT NULL DEFAULT 'es'"))
        db.session.commit()

    db.session.execute(
        db.text(
            "UPDATE users SET verified_at = COALESCE(verified_at, NOW()) "
            "WHERE email_verified = 1 AND verified_at IS NULL"
        )
    )
    db.session.commit()
    db.session.execute(
        db.text("UPDATE users SET preferred_language = COALESCE(NULLIF(preferred_language, ''), 'es')")
    )
    db.session.commit()

    profile_columns = {column['name'] for column in inspector.get_columns('user_profiles')}
    if 'avatar_url' not in profile_columns:
        db.session.execute(db.text('ALTER TABLE user_profiles ADD COLUMN avatar_url VARCHAR(300) NULL'))
        db.session.commit()

    board_columns = {column['name'] for column in inspector.get_columns('boards')}
    if 'background_color' not in board_columns:
        db.session.execute(db.text('ALTER TABLE boards ADD COLUMN background_color VARCHAR(20) NULL'))
        db.session.commit()
    if 'cover_url' not in board_columns:
        db.session.execute(db.text('ALTER TABLE boards ADD COLUMN cover_url VARCHAR(300) NULL'))
        db.session.commit()


def ensure_cascade_delete(table_name, constrained_column, referred_table, constraint_name):
    """Fuerza una foreign key con borrado en cascada para evitar bloqueos al eliminar."""
    inspector = db.inspect(db.engine)
    foreign_keys = inspector.get_foreign_keys(table_name)

    for foreign_key in foreign_keys:
        columns = foreign_key.get('constrained_columns') or []
        if columns != [constrained_column]:
            continue
        if foreign_key.get('referred_table') != referred_table:
            continue

        options = foreign_key.get('options') or {}
        delete_rule = str(options.get('ondelete', '')).upper()
        if delete_rule == 'CASCADE':
            return

        existing_name = foreign_key.get('name')
        if existing_name:
            db.session.execute(db.text(f'ALTER TABLE {table_name} DROP FOREIGN KEY {existing_name}'))
            db.session.commit()

        db.session.execute(
            db.text(
                f'ALTER TABLE {table_name} '
                f'ADD CONSTRAINT {constraint_name} FOREIGN KEY ({constrained_column}) '
                f'REFERENCES {referred_table}(id) ON DELETE CASCADE'
            )
        )
        db.session.commit()
        return


_schema_ready = False


def ensure_runtime_schema():
    """Prepara el esquema al cargar la app, tambien fuera de __main__."""
    global _schema_ready
    if _schema_ready:
        return

    with app.app_context():
        os.makedirs(avatar_upload_dir, exist_ok=True)
        db.create_all()
        ensure_auth_schema()
        ensure_cascade_delete('user_profiles', 'user_id', 'users', 'fk_user_profiles_user_id')
        ensure_cascade_delete('workspaces', 'user_id', 'users', 'fk_workspaces_user_id')
        ensure_cascade_delete('workspace_members', 'workspace_id', 'workspaces', 'fk_workspace_members_workspace_id')
        ensure_cascade_delete('workspace_members', 'user_id', 'users', 'fk_workspace_members_user_id')
        ensure_cascade_delete('boards', 'workspace_id', 'workspaces', 'fk_boards_workspace_id')
        ensure_cascade_delete('board_columns', 'board_id', 'boards', 'fk_board_columns_board_id')
        ensure_cascade_delete('cards', 'column_id', 'board_columns', 'fk_cards_column_id')
        ensure_cascade_delete('activity_logs', 'user_id', 'users', 'fk_activity_logs_user_id')
        _schema_ready = True


ensure_runtime_schema()


def build_account_content_html(page_key, page_title, page_description, user_name, user_initial, user_email, avatar_url, activities, activity_pagination=None, language_code=None):
    """Genera el contenido principal de la pagina de cuenta."""
    tr = lambda key, **kwargs: translate_text(key, language_code or get_current_language(), **kwargs)
    profile_avatar_html = build_avatar_html(user_initial, avatar_url, 'profile-avatar', tr('account.avatar_of', name=user_name))
    current_language = normalize_language_code(language_code or get_current_language())
    hero = [
        '<div class="account-page">',
        '<div class="account-page-hero">',
        '<div class="account-hero-left">',
        f'<span class="eyebrow">{escape(tr("account.section"))}</span>',
        f'<h1>{escape(page_title)}</h1>',
        f'<p>{escape(page_description)}</p>',
        f'<div class="hero-chips"><span class="chip">{escape(tr("hero.team"))}</span><span class="chip">{escape(tr("hero.active_flows"))}</span><span class="chip">{escape(tr("hero.productivity"))}</span></div>',
        '</div>',
        '<div class="account-hero-stack">',
        f'<div class="account-hero-card"><div class="account-hero-tag">{escape(tr("hero.status"))}</div><strong>{escape(tr("hero.active"))}</strong><span>{escape(tr("hero.last_access_today"))}</span></div>',
        f'<div class="account-hero-card alt"><div class="account-hero-tag">{escape(tr("hero.pace"))}</div><strong>+12%</strong><span>{escape(tr("hero.week_vs_week"))}</span></div>',
        '</div></div>',
    ]

    if page_key == 'account':
        hero.append(
            '<div class="account-grid">'
            f'<div class="account-page-card"><h3>{escape(tr("account.info_title"))}</h3>'
            f'<div class="account-page-row"><span>{escape(tr("account.label_name"))}</span>'
            f'<strong>{escape(user_name)}</strong></div>'
            f'<div class="account-page-row"><span>{escape(tr("account.label_email"))}</span>'
            f'<strong>{escape(user_email)}</strong></div>'
            f'<div class="account-page-row"><span>{escape(tr("account.label_plan"))}</span><strong>{escape(tr("account.plan_active"))}</strong></div></div>'
            f'<div class="account-page-card"><h3>{escape(tr("account.security_title"))}</h3><p>{escape(tr("account.security_help"))}</p>'
            f'<div class="pill-row"><span class="pill">{escape(tr("account.pill_session"))}</span><span class="pill">{escape(tr("account.pill_passwords"))}</span><span class="pill">{escape(tr("account.pill_validation"))}</span></div></div>'
            f'<div class="account-page-card"><h3>{escape(tr("account.quick_actions"))}</h3><div class="action-list">'
            f'<form action="{escape(url_for("account_password_reset"))}" method="POST"><button type="submit" class="action-btn wide">{escape(tr("account.change_password"))}</button></form>'
            f'<button type="button" class="action-btn wide js-account-update-email" data-current-email="{escape(user_email)}">{escape(tr("account.update_email"))}</button>'
            f'<form action="{escape(url_for("logout"))}" method="POST"><button type="submit" class="action-btn wide">{escape(tr("account.close_sessions"))}</button></form>'
            '</div></div>'
            f'<div class="account-page-card wide-card"><div class="split-head"><div><h3>{escape(tr("account.summary_title"))}</h3><p>{escape(tr("account.summary_help"))}</p></div><span class="badge-soft">{escape(tr("account.badge_updated"))}</span></div>'
            f'<div class="stat-grid expanded"><div class="stat-card"><strong>6</strong><span>{escape(tr("account.stat_spaces"))}</span></div><div class="stat-card"><strong>18</strong><span>{escape(tr("account.stat_boards"))}</span></div><div class="stat-card"><strong>42</strong><span>{escape(tr("account.stat_cards"))}</span></div><div class="stat-card"><strong>9</strong><span>{escape(tr("account.stat_in_progress"))}</span></div></div></div>'
            '</div>'
        )
    elif page_key == 'profile':
        hero.append(
            '<div class="account-grid">'
            f'<div class="account-page-card"><h3>{escape(tr("account.identity_title"))}</h3><p>{escape(tr("account.identity_help"))}</p><div class="profile-preview">'
            f'{profile_avatar_html}<div><strong>{escape(user_name)}</strong><span>{escape(user_email)}</span></div></div></div>'
            f'<div class="account-page-card"><h3>{escape(tr("account.visibility_title"))}</h3><div class="toggle-list"><div class="toggle-item"><div><strong>{escape(tr("account.show_email"))}</strong><span>{escape(tr("account.show_email_help"))}</span></div><div class="toggle-pill">{escape(tr("account.status_active"))}</div></div><div class="toggle-item"><div><strong>{escape(tr("account.online_status"))}</strong><span>{escape(tr("account.online_status_help"))}</span></div><div class="toggle-pill">{escape(tr("account.status_active"))}</div></div></div></div>'
            f'<div class="account-page-card wide-card profile-upload-card"><h3>{escape(tr("account.profile_image_title"))}</h3><p>{escape(tr("account.profile_image_help"))}</p>'
            f'<form class="account-form" action="{escape(url_for("update_account"))}" method="POST" enctype="multipart/form-data">'
            f'<label class="account-field"><span class="account-field-label">{escape(tr("account.display_name_label"))}</span><input type="text" name="display_name" value="{escape(user_name)}" maxlength="80" placeholder="{escape(tr("account.display_name_placeholder"))}"></label>'
            f'<label class="account-file-field">{escape(tr("account.upload_photo"))}'
            '<div class="account-file-picker">'
            '<input id="avatarFileInput" type="file" name="avatar_file" accept=".jpg,.jpeg,.png,.svg,.webp,image/jpeg,image/png,image/svg+xml,image/webp">'
            f'<button type="button" class="account-file-btn js-avatar-picker">{escape(tr("account.select_file"))}</button>'
            f'<span class="account-file-name" id="avatarFileName">{escape(tr("js.no_file_selected"))}</span>'
            '</div></label>'
            f'<label class="account-check"><input type="checkbox" name="remove_avatar" value="1"> {escape(tr("account.remove_photo"))}</label>'
            f'<button type="submit">{escape(tr("account.save_profile"))}</button></form></div>'
            '</div>'
        )
    elif page_key == 'activity':
        activity_html = []
        timeline_html = []
        activity_pagination = activity_pagination or {}
        recent_total = len(activities)
        week_cutoff = datetime.utcnow() - timedelta(days=7)
        weekly_total = 0
        board_flow_total = 0
        account_total = 0
        active_days = set()
        total_items = activity_pagination.get('total_items', recent_total)
        page = activity_pagination.get('page', 1)
        per_page = activity_pagination.get('per_page', 10)
        total_pages = activity_pagination.get('total_pages', 1)
        has_prev = activity_pagination.get('has_prev', False)
        has_next = activity_pagination.get('has_next', False)
        prev_url = activity_pagination.get('prev_url', '')
        next_url = activity_pagination.get('next_url', '')
        start_index = activity_pagination.get('start_index', 0)
        end_index = activity_pagination.get('end_index', 0)

        if activities:
            for item in activities:
                created_at = item.created_at or datetime.utcnow()
                created_label = created_at.strftime("%d/%m %H:%M")
                active_days.add(created_at.date())
                if created_at >= week_cutoff:
                    weekly_total += 1

                normalized_action = (item.action or '').lower()
                normalized_detail = (item.detail or '').lower()
                if any(keyword in normalized_action for keyword in ('tarjeta', 'tablero', 'columna', 'plantilla')):
                    board_flow_total += 1
                elif any(keyword in normalized_action for keyword in ('inicio de sesion', 'correo', 'email', 'contrasena', 'registro', 'recuperacion')):
                    account_total += 1
                elif any(keyword in normalized_detail for keyword in ('tablero', 'columna', 'tarjeta', 'espacio')):
                    board_flow_total += 1
                else:
                    account_total += 1

                action_label = tr(item.action) if item.action else ''
                activity_html.append(
                    '<article class="activity-entry">'
                    '<span class="activity-entry-dot"></span>'
                    '<div class="activity-entry-body">'
                    f'<strong>{escape(action_label)}</strong>'
                    f'<span>{escape(item.detail)}</span>'
                    '</div>'
                    f'<small>{escape(created_label)}</small>'
                    '</article>'
                )
                timeline_html.append(
                    '<article class="timeline-row">'
                    '<span class="timeline-row-dot"></span>'
                    '<div class="timeline-row-body">'
                    f'<strong>{escape(action_label)}</strong>'
                    f'<span>{escape(item.detail)}</span>'
                    '</div>'
                    f'<time>{escape(created_label)}</time>'
                    '</article>'
                )
        else:
            activity_html.append(
                '<article class="activity-entry is-empty">'
                '<span class="activity-entry-dot"></span>'
                f'<div class="activity-entry-body"><strong>{escape(tr("account.no_activity"))}</strong><span>{escape(tr("account.no_activity_help"))}</span></div>'
                f'<small>{escape(tr("account.now"))}</small>'
                '</article>'
            )
            timeline_html.append(
                '<article class="timeline-row is-empty">'
                '<span class="timeline-row-dot"></span>'
                f'<div class="timeline-row-body"><strong>{escape(tr("account.no_events"))}</strong><span>{escape(tr("account.no_events_help"))}</span></div>'
                f'<time>{escape(tr("account.now"))}</time>'
                '</article>'
            )

        latest_activity_label = activities[0].created_at.strftime("%d/%m %H:%M") if activities and activities[0].created_at else tr('account.no_records')
        active_days_total = len(active_days)
        pagination_html = [
            '<div class="activity-pagination">'
            f'<div class="activity-pagination-summary">{escape(tr("account.showing"))} <strong>{start_index}-{end_index}</strong> {escape(tr("account.of"))} <strong>{total_items}</strong> {escape(tr("account.records"))}</div>'
            '<div class="activity-pagination-actions">'
        ]
        if has_prev and prev_url:
            pagination_html.append(f'<a class="activity-page-btn" href="{escape(prev_url)}">{escape(tr("account.prev"))}</a>')
        else:
            pagination_html.append(f'<span class="activity-page-btn disabled" aria-disabled="true">{escape(tr("account.prev"))}</span>')
        pagination_html.append(f'<span class="activity-page-indicator">{escape(tr("account.page"))} {page} {escape(tr("account.page_of"))} {total_pages}</span>')
        if has_next and next_url:
            pagination_html.append(f'<a class="activity-page-btn" href="{escape(next_url)}">{escape(tr("account.next"))}</a>')
        else:
            pagination_html.append(f'<span class="activity-page-btn disabled" aria-disabled="true">{escape(tr("account.next"))}</span>')
        pagination_html.append('</div></div>')
        hero.append(
            '<div class="account-grid activity-grid">'
            '<div class="account-page-card wide-card activity-overview-card">'
            f'<div class="split-head"><div><h3>{escape(tr("account.activity_overview"))}</h3><p>{escape(tr("account.activity_overview_help"))}</p></div>'
            f'<span class="badge-soft">{escape(tr("account.last_record"))} {escape(latest_activity_label)}</span></div>'
            '<div class="activity-overview-metrics">'
            f'<div class="overview-metric"><span>{escape(tr("account.visible_events"))}</span><strong>{recent_total}</strong><small>{escape(tr("account.events_block").format(per_page=per_page))}</small></div>'
            f'<div class="overview-metric"><span>{escape(tr("account.last_7_days"))}</span><strong>{weekly_total}</strong><small>{escape(tr("account.week_activity"))}</small></div>'
            f'<div class="overview-metric"><span>{escape(tr("account.active_days"))}</span><strong>{active_days_total}</strong><small>{escape(tr("account.active_days_help"))}</small></div>'
            '</div></div>'
            f'<div class="account-page-card wide-card activity-timeline-card"><div class="split-head"><div><h3>{escape(tr("account.timeline"))}</h3><p>{escape(tr("account.timeline_help"))}</p></div>'
            f'<span class="badge-soft">{escape(tr("account.page"))} {page}</span></div><div class="timeline timeline-detailed">'
            + ''.join(timeline_html) +
            '</div>' + ''.join(pagination_html) + '</div>'
            '</div>'
        )
    elif page_key == 'cards':
        ph = escape(tr('account.priority_high'))
        pm = escape(tr('account.priority_med'))
        pl = escape(tr('account.priority_low'))
        def task_row(priority_cls, title, team, board, badge):
            return (
                f'<div class="ctask-row ctask-row--{priority_cls}">'
                f'<div class="ctask-accent"></div>'
                f'<div class="ctask-dot ctask-dot--{priority_cls}"></div>'
                '<div class="ctask-body">'
                f'<strong>{title}</strong>'
                f'<span>{team} <span class="ctask-board">{board}</span></span>'
                '</div>'
                f'<span class="ctask-badge ctask-badge--{priority_cls}">{badge}</span>'
                '</div>'
            )
        hero.append(
            '<div class="cards-page-wrap">'

            '<div class="cards-stats-strip">'
            f'<div class="cstat"><div class="cstat-inner"><span class="cstat-num">12</span><span class="cstat-label">{escape(tr("account.cards_total"))}</span></div><div class="cstat-icon cstat-icon--total">◈</div></div>'
            f'<div class="cstat cstat--done"><div class="cstat-inner"><span class="cstat-num">8</span><span class="cstat-label">{escape(tr("account.cards_completed"))}</span></div><div class="cstat-icon cstat-icon--done">✓</div></div>'
            f'<div class="cstat cstat--open"><div class="cstat-inner"><span class="cstat-num">4</span><span class="cstat-label">{escape(tr("account.cards_open"))}</span></div><div class="cstat-icon cstat-icon--open">◎</div></div>'
            '</div>'

            '<div class="cards-main-grid">'

            '<div class="cards-col-main">'
            '<div class="cards-section-head">'
            f'<strong>{escape(tr("account.cards_recent"))}</strong>'
            f'<span class="csection-pill">{escape(tr("account.cards_sorted"))}</span>'
            '</div>'
            '<div class="ctask-list">'
            + task_row('high', 'Revisar onboarding',   'UX Team',   '· 2d',      ph)
            + task_row('high', 'Documentar API',        'Dev',       '· 3d',      ph)
            + task_row('med',  'Optimizar reports',     'Ops',       '· 5d',      pm)
            + task_row('med',  'Revisar landing page',  'Marketing', '· 1w',      pm)
            + task_row('low',  'Actualizar etiquetas',  'General',   '· 1w',      pl) +
            '</div>'
            '</div>'

            '<div class="cards-col-side">'
            '<div class="cards-section-head">'
            f'<strong>{escape(tr("account.cards_filters"))}</strong>'
            '</div>'
            '<div class="cfilter-list">'
            f'<button class="cfilter-btn cfilter-btn--active"><span class="cfilter-dot"></span>{escape(tr("account.my_tasks"))}</button>'
            f'<button class="cfilter-btn cfilter-btn--high"><span class="cfilter-dot cfilter-dot--high"></span>{escape(tr("account.high_priority"))}</button>'
            f'<button class="cfilter-btn"><span class="cfilter-dot cfilter-dot--time"></span>{escape(tr("account.due_today"))}</button>'
            '</div>'

            '</div>'

            '</div>'
            '</div>'
        )
    elif page_key == 'settings':
        def stg_row(icon, label_key, help_key, value_key, badge_type):
            return (
                '<div class="stg-row">'
                f'<div class="stg-icon">{icon}</div>'
                '<div class="stg-copy">'
                f'<strong>{escape(tr(label_key))}</strong>'
                f'<span>{escape(tr(help_key))}</span>'
                '</div>'
                f'<span class="stg-badge stg-badge--{badge_type}">{escape(tr(value_key))}</span>'
                '</div>'
            )
        hero.append(
            '<div class="stg-wrap">'
            f'<p class="stg-desc">{escape(tr("settings.description"))}</p>'
            f'<div class="stg-section-label">{escape(tr("settings.section_appearance"))}</div>'
            '<div class="stg-list">'
            + stg_row('🎨', 'settings.theme', 'settings.theme_help', 'settings.theme_value', 'neutral') +
            '</div>'
            f'<div class="stg-section-label">{escape(tr("settings.section_notifications"))}</div>'
            '<div class="stg-list">'
            + stg_row('✉', 'settings.email_notifications', 'settings.email_notifications_help', 'settings.email_notifications_value', 'on')
            + stg_row('🔔', 'settings.reminders', 'settings.reminders_help', 'settings.reminders_value', 'on')
            + stg_row('🔊', 'settings.sounds', 'settings.sounds_help', 'settings.sounds_value', 'off') +
            '</div>'
            f'<div class="stg-section-label">{escape(tr("settings.section_interface"))}</div>'
            '<div class="stg-list">'
            + stg_row('⌨', 'settings.shortcuts', 'settings.shortcuts_help', 'settings.shortcuts_value', 'on') +
            '</div>'
            '</div>'
        )
    elif page_key == 'help':
        hero.append(
            f'<div class="account-grid"><div class="account-page-card"><h3>{escape(tr("account.help_center"))}</h3><div class="help-grid"><div class="help-card"><strong>{escape(tr("account.quick_guides"))}</strong><span>{escape(tr("account.quick_guides_help"))}</span></div><div class="help-card"><strong>{escape(tr("account.faq"))}</strong><span>{escape(tr("account.faq_help"))}</span></div><div class="help-card"><strong>{escape(tr("account.contact"))}</strong><span>{escape(tr("account.contact_help"))}</span></div></div></div><div class="account-page-card"><h3>{escape(tr("account.pro_resources"))}</h3><div class="resource-list"><div class="resource-item">{escape(tr("account.kanban_guide"))}</div><div class="resource-item">{escape(tr("account.team_templates"))}</div><div class="resource-item">{escape(tr("account.productivity_tips"))}</div></div></div></div>'
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
    current_language = get_current_language(user)
    user_display = get_user_display_data(user, profile)
    # Cargamos todos los espacios accesibles por el usuario, propios y compartidos.
    workspaces, roles_by_workspace = get_accessible_workspaces(user.id)

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
    manageable_workspace_ids = {workspace_id for workspace_id, role in roles_by_workspace.items() if can_manage_board(role)}
    manageable_workspaces = build_manageable_workspaces_data(workspaces, roles_by_workspace)
    role_labels = {role: get_role_label(role) for role in WORKSPACE_MEMBER_ROLES}

    return render_template(
        'index.html',
        user=user,
        profile=profile,
        user_name=user_display['user_name'],
        user_initial=user_display['user_initial'],
        current_language=current_language,
        account_toggle_html=build_account_toggle_html(user_display['user_name'], user_display['user_initial'], user_display['avatar_url'], current_language),
        account_menu_html=build_account_menu_html(user_display['user_name'], user_display['user_initial'], user.email, user_display['avatar_url'], current_language),
        side_nav_html=build_side_nav_html('boards', current_language),
        workspace_list_html=build_workspace_list_html(workspaces, None, roles_by_workspace, current_language),
        recent_boards_html=build_recent_boards_html(recent_boards, manageable_workspace_ids, current_language),
        workspace_blocks_html=build_workspace_blocks_html(workspaces, boards_by_workspace, None, roles_by_workspace, current_language),
        manageable_workspaces=manageable_workspaces,
        board_templates=get_translated_board_templates(current_language),
    )


@app.route('/workspaces/<int:workspace_id>')
def workspace_view(workspace_id):
    """Muestra un espacio concreto y los tableros que contiene."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    profile = get_profile(user)
    current_language = get_current_language(user)
    user_display = get_user_display_data(user, profile)
    workspaces, roles_by_workspace = get_accessible_workspaces(user.id)
    workspace, workspace_role = get_workspace_for_user(workspace_id, user.id)
    if not workspace:
        return redirect(url_for('home'))

    boards = Board.query.filter_by(workspace_id=workspace.id).order_by(Board.created_at.desc()).all()
    boards_by_workspace = {workspace.id: boards}
    recent_boards = boards[:4]
    manageable_workspace_ids = {workspace_id for workspace_id, role in roles_by_workspace.items() if can_manage_board(role)}
    manageable_workspaces = build_manageable_workspaces_data(workspaces, roles_by_workspace)

    return render_template(
        'index.html',
        user=user,
        profile=profile,
        user_name=user_display['user_name'],
        user_initial=user_display['user_initial'],
        current_language=current_language,
        account_toggle_html=build_account_toggle_html(user_display['user_name'], user_display['user_initial'], user_display['avatar_url'], current_language),
        account_menu_html=build_account_menu_html(user_display['user_name'], user_display['user_initial'], user.email, user_display['avatar_url'], current_language),
        side_nav_html=build_side_nav_html('boards', current_language),
        workspace_list_html=build_workspace_list_html(workspaces, workspace.id, roles_by_workspace, current_language),
        recent_boards_html=build_recent_boards_html(recent_boards, manageable_workspace_ids, current_language),
        workspace_blocks_html=build_workspace_blocks_html(workspaces, boards_by_workspace, workspace.id, roles_by_workspace, current_language),
        manageable_workspaces=manageable_workspaces,
        board_templates=get_translated_board_templates(current_language),
    )


@app.route('/workspaces/<int:workspace_id>/open')
def open_workspace(workspace_id):
    """Abre el tablero mas reciente del espacio para entrar mas rapido."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    workspace, _workspace_role = get_workspace_for_user(workspace_id, user.id)
    if not workspace:
        return redirect(url_for('home'))

    board = Board.query.filter_by(workspace_id=workspace.id).order_by(Board.created_at.desc()).first()
    if board:
        return redirect(url_for('board_view', board_id=board.id))
    return redirect(url_for('workspace_view', workspace_id=workspace.id))


@app.route('/workspaces/<int:workspace_id>/members')
def workspace_members_page(workspace_id):
    """Muestra la gestion de miembros de un espacio de trabajo."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    profile = get_profile(user)
    current_language = get_current_language(user)
    user_display = get_user_display_data(user, profile)
    workspaces, roles_by_workspace = get_accessible_workspaces(user.id)
    manageable_workspaces = build_manageable_workspaces_data(workspaces, roles_by_workspace)
    workspace, workspace_role = get_workspace_for_user(workspace_id, user.id)
    if not workspace:
        return redirect(url_for('home'))

    owner = db.session.get(User, workspace.user_id)
    owner_profile = get_profile(owner) if owner else None
    owner_display = get_user_display_data(owner, owner_profile) if owner else {"user_name": "Usuario", "user_initial": "U", "avatar_url": ""}

    memberships = (
        WorkspaceMember.query.filter_by(workspace_id=workspace.id)
        .order_by(WorkspaceMember.created_at.asc())
        .all()
    )

    member_rows = []
    for membership in memberships:
        member_user = db.session.get(User, membership.user_id)
        if not member_user:
            continue
        member_profile = get_profile(member_user)
        member_display = get_user_display_data(member_user, member_profile)
        member_rows.append({
            'id': membership.id,
            'name': member_display['user_name'],
            'initial': member_display['user_initial'],
            'avatar_url': member_display['avatar_url'],
            'email': member_user.email,
            'role': membership.role,
            'role_label': get_role_label(membership.role),
            'is_current_user': membership.user_id == user.id,
        })

    notice = sanitize_text(request.args.get('notice') or '', 160)
    notice_tone = sanitize_text(request.args.get('tone') or 'info', 20)
    manageable_workspaces = build_manageable_workspaces_data(workspaces, roles_by_workspace)

    return render_template(
        'workspace_members.html',
        user=user,
        profile=profile,
        user_name=user_display['user_name'],
        user_initial=user_display['user_initial'],
        current_language=current_language,
        account_toggle_html=build_account_toggle_html(user_display['user_name'], user_display['user_initial'], user_display['avatar_url'], current_language),
        account_menu_html=build_account_menu_html(user_display['user_name'], user_display['user_initial'], user.email, user_display['avatar_url'], current_language),
        side_nav_html=build_side_nav_html('boards', current_language),
        workspace_list_html=build_workspace_list_html(workspaces, workspace.id, roles_by_workspace, current_language),
        workspace=workspace,
        workspace_role=workspace_role,
        workspace_role_label=get_role_label(workspace_role),
        can_manage_members=can_manage_workspace(workspace_role),
        owner_name=owner_display['user_name'],
        owner_initial=owner_display['user_initial'],
        owner_avatar_url=owner_display.get('avatar_url', ''),
        owner_email=owner.email if owner else '',
        member_rows=member_rows,
        role_options=WORKSPACE_MEMBER_ROLES,
        role_labels=WORKSPACE_ROLE_LABELS,
        notice=notice,
        notice_tone=notice_tone,
        manageable_workspaces=manageable_workspaces,
        board_templates=get_translated_board_templates(current_language),
    )


@app.route('/workspaces/<int:workspace_id>/members/add', methods=['POST'])
def add_workspace_member(workspace_id):
    """Agrega un miembro a un espacio o actualiza su rol si ya existe."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    workspace, workspace_role = get_workspace_for_user(workspace_id, user.id)
    if not workspace:
        return redirect(url_for('home'))
    if not can_manage_workspace(workspace_role):
        return redirect(url_for('workspace_members_page', workspace_id=workspace.id, tone='error', notice='No tienes permisos para gestionar miembros.'))

    email = sanitize_text((request.form.get('member_email') or '').lower(), 100)
    role = sanitize_text((request.form.get('role') or 'lector').lower(), 20)
    if role not in WORKSPACE_MEMBER_ROLES:
        role = 'lector'

    if not is_valid_email_address(email):
        return redirect(url_for('workspace_members_page', workspace_id=workspace.id, tone='error', notice='Introduce un correo valido.'))

    target_user = User.query.filter(db.func.lower(User.email) == email).first()
    if not target_user:
        return redirect(url_for('workspace_members_page', workspace_id=workspace.id, tone='error', notice='Ese usuario todavía no está registrado.'))

    if target_user.id == workspace.user_id:
        return redirect(url_for('workspace_members_page', workspace_id=workspace.id, tone='info', notice='El propietario ya forma parte del espacio.'))

    membership = WorkspaceMember.query.filter_by(workspace_id=workspace.id, user_id=target_user.id).first()
    if membership:
        membership.role = role
        db.session.commit()
        log_activity(user.id, 'activity.member_updated', f'Rol actualizado en "{workspace.name}" para {target_user.email}')
        return redirect(url_for('workspace_members_page', workspace_id=workspace.id, tone='success', notice='Miembro actualizado correctamente.'))

    db.session.add(WorkspaceMember(workspace_id=workspace.id, user_id=target_user.id, role=role))
    db.session.commit()
    log_activity(user.id, 'activity.member_added', f'{target_user.email} unido a "{workspace.name}" como {get_role_label(role)}')
    return redirect(url_for('workspace_members_page', workspace_id=workspace.id, tone='success', notice='Miembro agregado correctamente.'))


@app.route('/workspaces/<int:workspace_id>/members/<int:member_id>/role', methods=['POST'])
def update_workspace_member_role(workspace_id, member_id):
    """Cambia el rol de un miembro existente."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    workspace, workspace_role = get_workspace_for_user(workspace_id, user.id)
    if not workspace:
        return redirect(url_for('home'))
    if not can_manage_workspace(workspace_role):
        return redirect(url_for('workspace_members_page', workspace_id=workspace.id, tone='error', notice='No tienes permisos para cambiar roles.'))

    membership = WorkspaceMember.query.filter_by(id=member_id, workspace_id=workspace.id).first()
    if not membership:
        return redirect(url_for('workspace_members_page', workspace_id=workspace.id, tone='error', notice='Miembro no encontrado.'))

    role = sanitize_text((request.form.get('role') or 'lector').lower(), 20)
    if role not in WORKSPACE_MEMBER_ROLES:
        role = 'lector'

    membership.role = role
    db.session.commit()
    member_user = db.session.get(User, membership.user_id)
    if member_user:
        log_activity(user.id, 'activity.role_updated', f'{member_user.email} ahora es {get_role_label(role)} en "{workspace.name}"')
    return redirect(url_for('workspace_members_page', workspace_id=workspace.id, tone='success', notice='Rol actualizado correctamente.'))


@app.route('/workspaces/<int:workspace_id>/members/<int:member_id>/remove', methods=['POST'])
def remove_workspace_member(workspace_id, member_id):
    """Quita a un miembro del espacio o permite salir del espacio compartido."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    workspace, workspace_role = get_workspace_for_user(workspace_id, user.id)
    if not workspace:
        return redirect(url_for('home'))

    membership = WorkspaceMember.query.filter_by(id=member_id, workspace_id=workspace.id).first()
    if not membership:
        return redirect(url_for('workspace_members_page', workspace_id=workspace.id, tone='error', notice='Miembro no encontrado.'))

    can_remove = can_manage_workspace(workspace_role) or membership.user_id == user.id
    if not can_remove:
        return redirect(url_for('workspace_members_page', workspace_id=workspace.id, tone='error', notice='No tienes permisos para quitar miembros.'))

    removed_self = membership.user_id == user.id
    member_user = db.session.get(User, membership.user_id)
    db.session.delete(membership)
    db.session.commit()

    if member_user:
        log_activity(user.id, 'activity.member_removed', f'{member_user.email} salio de "{workspace.name}"')

    if removed_self:
        return redirect(url_for('home'))
    return redirect(url_for('workspace_members_page', workspace_id=workspace.id, tone='success', notice='Miembro eliminado correctamente.'))

@app.route('/plantillas')
def templates_page():
    """Muestra las plantillas disponibles para crear tableros."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    profile = get_profile(user)
    current_language = get_current_language(user)
    user_display = get_user_display_data(user, profile)
    workspaces, roles_by_workspace = get_accessible_workspaces(user.id)
    # Ordenamos las plantillas por categoria para presentarlas mejor.
    grouped_templates = {}
    for template in BOARD_TEMPLATES:
        category = template.get('category', 'Otros')
        if category not in grouped_templates:
            grouped_templates[category] = []
        grouped_templates[category].append(template)
    template_categories = list(grouped_templates.keys())
    manageable_workspaces = build_manageable_workspaces_data(workspaces, roles_by_workspace)

    return render_template(
        'plantillas.html',
        user=user,
        profile=profile,
        user_name=user_display['user_name'],
        user_initial=user_display['user_initial'],
        current_language=current_language,
        account_toggle_html=build_account_toggle_html(user_display['user_name'], user_display['user_initial'], user_display['avatar_url'], current_language),
        account_menu_html=build_account_menu_html(user_display['user_name'], user_display['user_initial'], user.email, user_display['avatar_url'], current_language),
        side_nav_html=build_side_nav_html('templates', current_language),
        workspace_list_html=build_workspace_list_html(workspaces, None, roles_by_workspace, current_language),
        templates_sidebar_html=build_templates_sidebar_html(template_categories, grouped_templates, current_language),
        templates_count=len(BOARD_TEMPLATES),
        templates_grid_html=build_templates_grid_html(BOARD_TEMPLATES, current_language),
        manageable_workspaces=manageable_workspaces,
        board_templates=get_translated_board_templates(current_language),
    )


ACCOUNT_PAGE_META = {
    'account': ('page.account.title', 'page.account.description'),
    'profile': ('page.profile.title', 'page.profile.description'),
    'activity': ('page.activity.title', 'page.activity.description'),
    'cards': ('page.cards.title', 'page.cards.description'),
    'settings': ('page.settings.title', 'page.settings.description'),
    'help': ('page.help.title', 'page.help.description'),
}


def render_account_page(page_key):
    """Funcion auxiliar para reutilizar la misma vista en varias paginas de cuenta."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    current_language = get_current_language(user)
    title_key, description_key = ACCOUNT_PAGE_META.get(page_key, ACCOUNT_PAGE_META['account'])
    title = translate_text(title_key, current_language)
    description = translate_text(description_key, current_language)
    profile = get_profile(user)
    current_language = get_current_language(user)
    user_display = get_user_display_data(user, profile)
    workspaces, roles_by_workspace = get_accessible_workspaces(user.id)

    activities = []
    activity_pagination = {}
    notice = sanitize_text(request.args.get('notice') or '', 160)
    notice_tone = sanitize_text(request.args.get('tone') or 'info', 20)
    # Solo se cargan actividades cuando estamos en la pagina correspondiente.
    if page_key == 'activity':
        per_page = 10
        page = request.args.get('page', 1, type=int) or 1
        page = max(page, 1)
        base_query = ActivityLog.query.filter_by(user_id=user.id)
        total_items = base_query.count()
        total_pages = max((total_items + per_page - 1) // per_page, 1)
        page = min(page, total_pages)
        offset = (page - 1) * per_page
        activities = (
            base_query
            .order_by(ActivityLog.created_at.desc())
            .offset(offset)
            .limit(per_page)
            .all()
        )
        start_index = offset + 1 if total_items else 0
        end_index = min(offset + len(activities), total_items) if total_items else 0
        activity_pagination = {
            'page': page,
            'per_page': per_page,
            'total_items': total_items,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages,
            'prev_url': url_for('activity_page', page=page - 1) if page > 1 else '',
            'next_url': url_for('activity_page', page=page + 1) if page < total_pages else '',
            'start_index': start_index,
            'end_index': end_index,
        }

    return render_template(
        'account_page.html',
        user=user,
        profile=profile,
        user_name=user_display['user_name'],
        user_initial=user_display['user_initial'],
        current_language=current_language,
        account_toggle_html=build_account_toggle_html(user_display['user_name'], user_display['user_initial'], user_display['avatar_url'], current_language),
        account_menu_html=build_account_menu_html(user_display['user_name'], user_display['user_initial'], user.email, user_display['avatar_url'], current_language),
        side_nav_html=build_side_nav_html('account', current_language),
        workspace_list_html=build_workspace_list_html(workspaces, None, roles_by_workspace, current_language),
        page_title=title,
        notice=notice,
        notice_tone=notice_tone,
        account_content_html=build_account_content_html(
            page_key,
            title,
            description,
            user_display['user_name'],
            user_display['user_initial'],
            user.email,
            user_display['avatar_url'],
            activities,
            activity_pagination,
            current_language,
        ),
    )


@app.route('/cuenta')
def account_page():
    """Abre la pagina general de la cuenta."""
    return render_account_page('account')


@app.route('/perfil')
def profile_page():
    """Abre la pagina del perfil visible del usuario."""
    return render_account_page('profile')


@app.route('/actividad')
def activity_page():
    """Abre la pagina con el historial reciente."""
    return render_account_page('activity')


@app.route('/tarjetas')
def cards_page():
    """Abre una vista informativa general sobre tarjetas."""
    return render_account_page('cards')


@app.route('/ajustes')
def settings_page():
    """Abre la pagina de ajustes generales."""
    return render_account_page('settings')


@app.route('/ayuda')
def help_page():
    """Abre la pagina de ayuda basica."""
    return render_account_page('help')


@app.route('/cuenta/language', methods=['POST'])
def update_account_language():
    """Guarda el idioma preferido para el usuario actual."""
    user, redirect_response = get_user_or_redirect()

    preferred_language = normalize_language_code(request.form.get('preferred_language'))
    next_url = (request.form.get('next') or '').strip()
    session['preferred_language'] = preferred_language
    if user and not redirect_response:
        user.preferred_language = preferred_language
        db.session.commit()
        log_activity(user.id, 'activity.language_updated', f'Idioma cambiado a {get_language_label(preferred_language)}')
    if next_url.startswith('/') and not next_url.startswith('//'):
        return redirect(next_url)
    if redirect_response:
        return redirect(url_for('register'))
    return redirect(url_for('settings_page'))


@app.route('/cuenta/password-reset', methods=['POST'])
def account_password_reset():
    """Envia un correo de recuperacion a la cuenta activa."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    sent, _ = send_password_reset_email(user)
    log_activity(user.id, 'activity.recovery_requested', 'Se ha pedido un enlace para cambiar la contrasena desde la cuenta')
    notice = 'Te hemos enviado un enlace para cambiar la contraseña.'
    if not sent:
        notice += ' Modo local: revisa la terminal del servidor para copiarlo.'
    return redirect(url_for('account_page', tone='success', notice=notice))


@app.route('/cuenta/email', methods=['POST'])
def update_account_email():
    """Actualiza el correo principal del usuario."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    new_email = sanitize_text((request.form.get('email') or '').lower(), 100)
    if not is_valid_email_address(new_email):
        return redirect(url_for('account_page', tone='error', notice='Introduce un correo electronico valido.'))
    if new_email == user.email.lower():
        return redirect(url_for('account_page', tone='info', notice='Ese ya es tu correo actual.'))

    existing_user = User.query.filter(db.func.lower(User.email) == new_email).first()
    if existing_user and existing_user.id != user.id:
        return redirect(url_for('account_page', tone='error', notice='Ese correo ya esta en uso.'))

    previous_email = user.email
    user.email = new_email
    db.session.commit()
    log_activity(user.id, 'activity.email_updated', f'Correo cambiado de "{previous_email}" a "{new_email}"')
    return redirect(url_for('account_page', tone='success', notice='Correo actualizado correctamente.'))


@app.route('/inicio')
def landing():
    """Pagina de bienvenida interna tras iniciar sesion."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    if not user.has_seen_inicio:
        user.has_seen_inicio = True
        db.session.commit()

    current_language = get_current_language(user)
    profile = get_profile(user)
    user_display = get_user_display_data(user, profile)
    workspaces, roles_by_workspace = get_accessible_workspaces(user.id)
    manageable_workspaces = build_manageable_workspaces_data(workspaces, roles_by_workspace)

    return render_template(
        'inicio.html',
        user=user,
        profile=profile,
        user_name=user_display['user_name'],
        user_initial=user_display['user_initial'],
        current_language=current_language,
        account_toggle_html=build_account_toggle_html(user_display['user_name'], user_display['user_initial'], user_display['avatar_url'], current_language),
        account_menu_html=build_account_menu_html(user_display['user_name'], user_display['user_initial'], user.email, user_display['avatar_url'], current_language),
        side_nav_html=build_side_nav_html('home', current_language),
        workspace_list_html=build_workspace_list_html(workspaces, None, roles_by_workspace, current_language),
        manageable_workspaces=manageable_workspaces,
        board_templates=get_translated_board_templates(current_language),
    )


@app.route('/js/<path:filename>')
def js_static(filename):
    """Sirve archivos JavaScript desde la carpeta /js."""
    return send_from_directory('js', filename)


@app.route('/uploads/avatars/<path:filename>')
def uploaded_avatar(filename):
    """Sirve los avatares subidos por los usuarios."""
    return send_from_directory(avatar_upload_dir, filename)


@app.route('/favicon.ico')
def send_favicon():
    """Sirve el favicon principal de la aplicacion."""
    return send_from_directory('favicon', 'favicon-prodify.ico', mimetype='image/x-icon')


@app.route('/favicon.svg')
def send_favicon_svg():
    """Sirve la version SVG del favicon para navegadores modernos."""
    return send_from_directory('favicon', 'favicon-prodify.svg', mimetype='image/svg+xml')


@app.route('/plantillas/usar', methods=['POST'])
def use_template():
    """Crea un tablero usando una plantilla en un espacio existente o nuevo."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    template_id = (request.form.get('template_id') or '').strip()
    workspace_name = sanitize_text(request.form.get('workspace_name') or '', 120) or 'Nuevo espacio'
    workspace_id = request.form.get('workspace_id')
    board_name = sanitize_text(request.form.get('board_name') or '', 120) or 'Nuevo tablero'

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

    workspace = None
    if workspace_id:
        try:
            workspace_id = int(workspace_id)
        except (TypeError, ValueError):
            workspace_id = None
    if workspace_id:
        workspace, workspace_role = get_workspace_for_user(workspace_id, user.id)
        if not workspace or not can_manage_board(workspace_role):
            return redirect(url_for('home'))
    else:
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
    log_activity(user.id, 'activity.template_applied', f'Tablero "{board.name}" creado en "{workspace.name}"')
    return redirect(url_for('board_view', board_id=board.id))


@app.route('/uploads/board-covers/<path:filename>')
def uploaded_board_cover(filename):
    """Sirve las imagenes subidas como fondo de tablero."""
    return send_from_directory(board_cover_upload_dir, filename)


def resolve_board_cover_inputs():
    """Recoge el color y la imagen opcional enviados al crear un tablero."""
    background_color = sanitize_text(request.form.get('board_background') or '', 20)
    if not re.fullmatch(r'#[0-9A-Fa-f]{6}', background_color or ''):
        background_color = ''

    cover_url = None
    board_cover_file = request.files.get('board_cover_file')
    if board_cover_file and board_cover_file.filename:
        if is_allowed_board_cover_filename(board_cover_file.filename):
            safe_name = secure_filename(board_cover_file.filename)
            extension = safe_name.rsplit('.', 1)[1].lower()
            stored_name = f'board_{secrets.token_hex(8)}.{extension}'
            os.makedirs(board_cover_upload_dir, exist_ok=True)
            board_cover_file.save(os.path.join(board_cover_upload_dir, stored_name))
            cover_url = url_for('uploaded_board_cover', filename=stored_name)
        else:
            board_cover_file = None
    return background_color or None, cover_url


@app.route('/boards/<int:board_id>')
def board_view(board_id):
    """Muestra un tablero concreto con sus columnas y tarjetas."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    board, workspace, workspace_role = get_board_for_user(board_id, user.id)
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

    current_language = get_current_language(user)
    return render_template(
        'board.html',
        board=board,
        workspace=workspace,
        workspace_role=workspace_role,
        workspace_role_label=get_role_label(workspace_role),
        can_edit_board=can_edit_board_content(workspace_role),
        current_language=current_language,
        side_nav_html=build_side_nav_html('boards', current_language),
        board_columns_html=build_board_columns_html(columns, cards_by_column, board.id, can_edit_board_content(workspace_role)),
        board_settings_html=build_board_settings_panel_html(board, columns, cards_by_column, workspace_role),
        can_open_workspace=can_view_workspace(get_workspace_role(workspace, user.id)),
    )


@app.route('/boards/<int:board_id>/update', methods=['POST'])
def update_board(board_id):
    """Actualiza nombre y fondo de un tablero existente."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    board, workspace, workspace_role = get_board_for_user(board_id, user.id)
    if not board:
        return redirect(url_for('home'))
    if not can_manage_board(workspace_role):
        return redirect(url_for('board_view', board_id=board.id))

    board_name = sanitize_text(request.form.get('board_name') or '', 120)
    if board_name:
        board.name = board_name[:120]

    background_color, cover_url = resolve_board_cover_inputs()
    board.background_color = background_color or board.background_color
    if cover_url:
        board.cover_url = cover_url
    elif background_color:
        board.cover_url = None

    db.session.commit()
    log_activity(user.id, 'activity.board_updated', f'"{board.name}" en "{workspace.name}"')
    return redirect(url_for('board_view', board_id=board.id))


@app.route('/boards/<int:board_id>/cover/delete', methods=['POST'])
def delete_board_cover(board_id):
    """Elimina la imagen de portada de un tablero."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    board, workspace, workspace_role = get_board_for_user(board_id, user.id)
    if not board:
        return redirect(url_for('home'))
    if not can_manage_board(workspace_role):
        return redirect(url_for('board_view', board_id=board.id))

    if board.cover_url:
        try:
            filename = board.cover_url.split('/')[-1]
            file_path = os.path.join(board_cover_upload_dir, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f'Error eliminando portada del tablero: {e}')

        board.cover_url = None
        db.session.commit()
        log_activity(user.id, 'activity.cover_deleted', f'Portada eliminada de "{board.name}"')

    return redirect(url_for('board_view', board_id=board.id))


@app.route('/boards/<int:board_id>/members/invite', methods=['POST'])
def invite_board_member(board_id):
    """Invita por correo a una persona para un tablero concreto."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    board, workspace, workspace_role = get_board_for_user(board_id, user.id)
    if not board:
        return redirect(url_for('home'))
    if not can_manage_board(workspace_role):
        return redirect(url_for('board_view', board_id=board.id))

    email = sanitize_text((request.form.get('member_email') or '').lower(), 100)
    role = sanitize_text((request.form.get('role') or 'lector').lower(), 20)
    if role not in BOARD_MEMBER_ROLES:
        role = 'lector'
    if not is_valid_email_address(email):
        return redirect(url_for('board_view', board_id=board.id))

    existing_user = User.query.filter(db.func.lower(User.email) == email).first()
    if existing_user:
        membership = BoardMember.query.filter_by(board_id=board.id, user_id=existing_user.id).first()
        if membership:
            membership.role = role
        else:
            db.session.add(BoardMember(board_id=board.id, user_id=existing_user.id, role=role))

    invitation = BoardInvitation.query.filter_by(board_id=board.id, email=email, accepted_at=None).first()
    if not invitation:
        invitation = BoardInvitation(
            board_id=board.id,
            email=email,
            role=role,
            token=secrets.token_urlsafe(32),
            invited_by_user_id=user.id,
        )
        db.session.add(invitation)
    else:
        invitation.role = role
        invitation.token = secrets.token_urlsafe(32)
        invitation.invited_by_user_id = user.id
    db.session.commit()

    send_board_invitation_email(invitation, board, workspace, user)
    log_activity(user.id, 'activity.invitation_sent', f'{email} invitado a "{board.name}" como {get_role_label(role)}')
    return redirect(url_for('board_view', board_id=board.id))


@app.route('/board-invitations/<token>/accept')
def accept_board_invitation(token):
    """Acepta una invitacion pendiente a un tablero."""
    invitation = BoardInvitation.query.filter_by(token=token, accepted_at=None).first()
    if not invitation:
        return redirect(url_for('home'))

    target_url = url_for('accept_board_invitation', token=token)
    logged_user = db.session.get(User, session.get('user_id')) if session.get('user_id') else None
    if not logged_user:
        target_user = User.query.filter(db.func.lower(User.email) == invitation.email.lower()).first()
        if target_user:
            return redirect(url_for('login', next=target_url, email=invitation.email))
        return redirect(url_for('register', next=target_url, email=invitation.email))

    if logged_user.email.lower() != invitation.email.lower():
        return redirect(url_for('login', next=target_url, email=invitation.email))

    membership = BoardMember.query.filter_by(board_id=invitation.board_id, user_id=logged_user.id).first()
    if membership:
        membership.role = invitation.role
    else:
        db.session.add(BoardMember(board_id=invitation.board_id, user_id=logged_user.id, role=invitation.role))
    invitation.accepted_at = datetime.utcnow()
    db.session.commit()
    return redirect(url_for('board_view', board_id=invitation.board_id))


@app.route('/boards/<int:board_id>/members/<int:member_id>/role', methods=['POST'])
def update_board_member_role(board_id, member_id):
    """Actualiza el rol de un miembro del tablero."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    board, _workspace, workspace_role = get_board_for_user(board_id, user.id)
    if not board or not can_manage_board(workspace_role):
        return redirect(url_for('home'))

    membership = BoardMember.query.filter_by(id=member_id, board_id=board.id).first()
    if not membership:
        return redirect(url_for('board_view', board_id=board.id))

    role = sanitize_text((request.form.get('role') or 'lector').lower(), 20)
    if role not in BOARD_MEMBER_ROLES:
        role = 'lector'
    membership.role = role
    db.session.commit()
    return redirect(url_for('board_view', board_id=board.id))


@app.route('/boards/<int:board_id>/members/<int:member_id>/remove', methods=['POST'])
def remove_board_member(board_id, member_id):
    """Elimina a un miembro directo del tablero."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    board, _workspace, workspace_role = get_board_for_user(board_id, user.id)
    if not board or not can_manage_board(workspace_role):
        return redirect(url_for('home'))

    membership = BoardMember.query.filter_by(id=member_id, board_id=board.id).first()
    if membership:
        db.session.delete(membership)
        db.session.commit()
    return redirect(url_for('board_view', board_id=board.id))


@app.route('/boards/<int:board_id>/invitations/<int:invitation_id>/delete', methods=['POST'])
def delete_board_invitation(board_id, invitation_id):
    """Cancela una invitacion pendiente de tablero."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    board, _workspace, workspace_role = get_board_for_user(board_id, user.id)
    if not board or not can_manage_board(workspace_role):
        return redirect(url_for('home'))

    invitation = BoardInvitation.query.filter_by(id=invitation_id, board_id=board.id, accepted_at=None).first()
    if invitation:
        db.session.delete(invitation)
        db.session.commit()
    return redirect(url_for('board_view', board_id=board.id))


@app.route('/boards/<int:board_id>/columns/create', methods=['POST'])
def create_column(board_id):
    """Crea una nueva columna al final del tablero."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    board, _workspace, workspace_role = get_board_for_user(board_id, user.id)
    if not board:
        return redirect(url_for('home'))
    if not can_edit_board_content(workspace_role):
        return redirect(url_for('board_view', board_id=board.id))

    title = sanitize_text(request.form.get('column_title') or '', 120)
    if not title:
        return redirect(url_for('board_view', board_id=board.id))

    # Buscamos la ultima posicion ocupada para poner la nueva al final.
    last_position = db.session.query(db.func.max(BoardColumn.position)).filter_by(board_id=board.id).scalar()
    position = (last_position + 1) if last_position is not None else 0
    new_column = BoardColumn(board_id=board.id, title=title[:120], position=position)
    db.session.add(new_column)
    db.session.commit()
    log_activity(user.id, 'activity.column_created', f'Columna "{new_column.title}" en "{board.name}"')
    return redirect(url_for('board_view', board_id=board.id))


@app.route('/columns/<int:column_id>/update', methods=['POST'])
def update_column(column_id):
    """Actualiza el nombre de una columna existente."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    column, board, _workspace, workspace_role = get_column_for_user(column_id, user.id)
    if not column:
        return redirect(url_for('home'))
    if not can_edit_board_content(workspace_role):
        return redirect(url_for('board_view', board_id=column.board_id))

    title = sanitize_text(request.form.get('column_title') or '', 120)
    if not title:
        return redirect(url_for('board_view', board_id=column.board_id))

    old_title = column.title
    column.title = title[:120]
    db.session.commit()
    if board:
        log_activity(user.id, 'activity.column_updated', f'"{old_title}" paso a "{column.title}" en "{board.name}"')
    return redirect(url_for('board_view', board_id=column.board_id))


@app.route('/columns/<int:column_id>/move', methods=['POST'])
def move_column(column_id):
    """Mueve una columna a izquierda o derecha dentro del tablero."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    column, board, _workspace, workspace_role = get_column_for_user(column_id, user.id)
    if not column:
        return redirect(url_for('home'))
    if not can_edit_board_content(workspace_role):
        return redirect(url_for('board_view', board_id=column.board_id))

    direction = sanitize_text(request.form.get('direction') or '', 10).lower()
    columns = BoardColumn.query.filter_by(board_id=column.board_id).order_by(BoardColumn.position.asc(), BoardColumn.id.asc()).all()
    current_index = next((index for index, item in enumerate(columns) if item.id == column.id), None)
    if current_index is None:
        return redirect(url_for('board_view', board_id=column.board_id))

    target_index = current_index - 1 if direction == 'left' else current_index + 1 if direction == 'right' else current_index
    if target_index < 0 or target_index >= len(columns) or target_index == current_index:
        return redirect(url_for('board_view', board_id=column.board_id))

    columns[current_index], columns[target_index] = columns[target_index], columns[current_index]
    for position, item in enumerate(columns):
        item.position = position
    db.session.commit()
    if board:
        log_activity(user.id, 'activity.column_moved', f'Columna "{column.title}" reorganizada en "{board.name}"')
    return redirect(url_for('board_view', board_id=column.board_id))


@app.route('/boards/<int:board_id>/columns/reorder', methods=['POST'])
def reorder_columns(board_id):
    """Reordena las columnas de un tablero segun el orden recibido por el frontend."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    board, _workspace, workspace_role = get_board_for_user(board_id, user.id)
    if not board:
        return ('', 404)
    if not can_edit_board_content(workspace_role):
        return ('', 403)

    raw_order = request.form.get('column_order') or ''
    ordered_ids = []
    for value in raw_order.split(','):
        value = value.strip()
        if not value.isdigit():
            continue
        ordered_ids.append(int(value))

    columns = BoardColumn.query.filter_by(board_id=board.id).order_by(BoardColumn.position.asc(), BoardColumn.id.asc()).all()
    current_ids = [column.id for column in columns]
    if not ordered_ids or sorted(ordered_ids) != sorted(current_ids):
        return ('', 400)

    for position, column_id in enumerate(ordered_ids):
        for column in columns:
            if column.id == column_id:
                column.position = position
                break

    db.session.commit()
    log_activity(user.id, 'activity.columns_reordered', f'Se reorganizaron las columnas en "{board.name}"')
    return ('', 204)


@app.route('/columns/<int:column_id>/cards/create', methods=['POST'])
def create_card(column_id):
    """Crea una tarjeta nueva dentro de una columna concreta."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    column, board, _workspace, workspace_role = get_column_for_user(column_id, user.id)
    if not column:
        return redirect(url_for('home'))
    if not can_edit_board_content(workspace_role):
        return redirect(url_for('board_view', board_id=column.board_id))

    title = sanitize_text(request.form.get('card_title') or '', 200)
    if not title:
        return redirect(url_for('board_view', board_id=column.board_id))

    new_card = Card(column_id=column.id, title=title[:200])
    db.session.add(new_card)
    db.session.commit()
    if board:
        log_activity(user.id, 'activity.card_created', f'"{new_card.title}" en "{board.name}"')
    return redirect(url_for('board_view', board_id=column.board_id))


@app.route('/columns/<int:column_id>/delete', methods=['POST'])
def delete_column(column_id):
    """Elimina una columna y tambien todas sus tarjetas."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    column, board, _workspace, workspace_role = get_column_for_user(column_id, user.id)
    if not column:
        return redirect(url_for('home'))
    if not can_edit_board_content(workspace_role):
        return redirect(url_for('board_view', board_id=column.board_id))

    column_title = column.title
    board_id = column.board_id
    Card.query.filter_by(column_id=column.id).delete(synchronize_session=False)
    db.session.delete(column)
    db.session.commit()
    if board:
        log_activity(user.id, 'activity.column_deleted', f'Columna "{column_title}" en "{board.name}"')
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
    card, current_column, _board, _workspace, workspace_role = get_card_for_user(card_id, user.id)
    if not card:
        return redirect(url_for('home'))
    if not can_edit_board_content(workspace_role):
        return ('', 403)

    # La columna destino debe pertenecer al mismo tablero.
    target_column, target_board, _target_workspace, target_role = get_column_for_user(target_column_id, user.id)
    if not target_column or target_column.board_id != current_column.board_id:
        return redirect(url_for('board_view', board_id=current_column.board_id))
    if not can_edit_board_content(target_role):
        return ('', 403)

    card_title = card.title
    card.column_id = target_column_id
    db.session.commit()
    if target_board:
        log_activity(user.id, 'activity.card_moved', f'"{card_title}" a "{target_column.title}" en "{target_board.name}"')
    return ('', 204)


@app.route('/cards/<int:card_id>/delete', methods=['POST'])
def delete_card(card_id):
    """Elimina una tarjeta concreta del tablero."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    card, _column, board, _workspace, workspace_role = get_card_for_user(card_id, user.id)
    if not card:
        return redirect(url_for('home'))
    if not can_edit_board_content(workspace_role):
        return redirect(url_for('board_view', board_id=board.id if board else 0))

    card_title = card.title
    board_id = board.id if board else None

    db.session.delete(card)
    db.session.commit()
    if board_id:
        board = db.session.get(Board, board_id)
        if board:
            log_activity(user.id, 'activity.card_deleted', f'"{card_title}" en "{board.name}"')
    if board_id:
        return redirect(url_for('board_view', board_id=board_id))
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Muestra el login y valida las credenciales enviadas por el formulario."""
    next_url = sanitize_text(request.values.get('next') or '', 240)
    prefilled_email = sanitize_text((request.values.get('email') or '').lower(), 100)
    if request.method == 'POST':
        email = sanitize_text((request.form.get('email') or '').lower(), 100)
        password = request.form.get('password') or ''
        allowed, retry_after = check_rate_limit('login', 8, 600, email)
        if not allowed:
            return render_template(
                'login.html',
                error='Demasiados intentos',
                message_html=build_auth_message_html(build_rate_limit_message(retry_after)),
                next_url=next_url,
                prefilled_email=email or prefilled_email,
            )

        if not is_valid_email_address(email) or not password:
            return render_template(
                'login.html',
                error='Credenciales invalidas',
                message_html=build_auth_message_html('Credenciales invalidas'),
                next_url=next_url,
                prefilled_email=email or prefilled_email,
            )

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
                session['preferred_language'] = normalize_language_code(user.preferred_language)
                log_activity(user.id, 'activity.login', 'Acceso correcto a la plataforma')
                if next_url.startswith('/'):
                    return redirect(next_url)
                return redirect(url_for('landing' if not user.has_seen_inicio else 'home'))

        return render_template(
            'login.html',
            error='Credenciales invalidas',
            message_html=build_auth_message_html('Credenciales invalidas'),
            next_url=next_url,
            prefilled_email=email or prefilled_email,
        )

    message = None
    tone = 'error'
    if request.args.get('registered') == '1':
        message = 'Cuenta creada correctamente. Ya puedes iniciar sesión.'
        tone = 'success'
    elif request.args.get('reset') == '1':
        message = 'Contraseña actualizada. Inicia sesión con la nueva clave.'
        tone = 'success'

    return render_template(
        'login.html',
        error=None,
        message_html=build_auth_message_html(message, tone),
        next_url=next_url,
        prefilled_email=prefilled_email,
    )


@app.route('/registro', methods=['GET', 'POST'])
def register():
    """Permite crear una cuenta real y guardarla en la base de datos."""
    next_url = sanitize_text(request.values.get('next') or '', 240)
    prefilled_email = sanitize_text((request.values.get('email') or '').lower(), 100)

    def render_register_error(message, email_val='', lang='es'):
        return render_template(
            'register.html',
            message_html=build_auth_message_html(message),
            next_url=next_url,
            prefilled_email=email_val or prefilled_email,
            register_language_selector=build_register_language_selector(lang),
        )

    if request.method == 'POST':
        email = sanitize_text((request.form.get('email') or '').lower(), 100)
        password = request.form.get('password') or ''
        confirm_password = request.form.get('confirm_password') or ''
        display_name = sanitize_text(request.form.get('display_name') or '', 80)
        preferred_language = normalize_language_code(request.form.get('preferred_language') or 'es')
        allowed, retry_after = check_rate_limit('register', 5, 3600, email)
        if not allowed:
            return render_register_error(build_rate_limit_message(retry_after), email, preferred_language)
        if not email or not password or not confirm_password:
            return render_register_error('Completa todos los campos obligatorios.', email, preferred_language)
        if not is_valid_email_address(email):
            return render_register_error('Introduce un correo electronico valido.', email, preferred_language)
        if password != confirm_password:
            return render_register_error('Las contraseñas no coinciden.', email, preferred_language)
        password_error = validate_password_strength(password)
        if password_error:
            return render_register_error(password_error, email, preferred_language)
        if User.query.filter_by(email=email).first():
            return render_register_error('Ese correo ya esta registrado.', email, preferred_language)

        user = User(
            email=email,
            password=generate_password_hash(password),
            email_verified=True,
            verified_at=datetime.utcnow(),
            has_seen_inicio=False,
            preferred_language=preferred_language,
        )
        db.session.add(user)
        db.session.flush()

        final_name = display_name[:80] if display_name else email.split('@')[0].replace('.', ' ').strip().title()
        if not final_name:
            final_name = 'Usuario'
        db.session.add(UserProfile(user_id=user.id, display_name=final_name))
        db.session.commit()
        sent = send_registration_welcome_email(user)
        log_activity(user.id, 'activity.registered', 'Cuenta creada correctamente')
        if not sent:
            print(f'[Prodify] No se pudo enviar el correo de bienvenida a {user.email}')
        if next_url.startswith('/'):
            session['user_id'] = user.id
            session['preferred_language'] = normalize_language_code(user.preferred_language)
            return redirect(next_url)
        return redirect(url_for('login', registered=1))

    return render_template(
        'register.html',
        message_html=build_auth_message_html(None),
        next_url=next_url,
        prefilled_email=prefilled_email,
        register_language_selector=build_register_language_selector(get_current_language()),
    )


@app.route('/recuperar', methods=['GET', 'POST'])
def forgot_password():
    """Solicita un enlace de recuperacion para restablecer la contrasena."""
    if request.method == 'POST':
        email = sanitize_text((request.form.get('email') or '').lower(), 100)
        user = User.query.filter_by(email=email).first()
        local_hint = ''
        print(f'[Prodify] Solicitud de recuperacion recibida para {email}', flush=True)
        allowed, retry_after = check_rate_limit('forgot-password', 5, 1800, email)
        if not allowed:
            message = build_rate_limit_message(retry_after)
            return render_template(
                'forgot_password.html',
                message_html=build_auth_message_html(message),
            )

        if not is_valid_email_address(email):
            return render_template(
                'forgot_password.html',
                message_html=build_auth_message_html('Introduce un correo electronico valido.'),
            )

        if user:
            print(f'[Prodify] Cuenta encontrada para recuperacion: {email}', flush=True)
            sent, _ = send_password_reset_email(user)
            log_activity(user.id, 'activity.recovery_requested', 'Se ha pedido un enlace para cambiar la contrasena')
            if not sent:
                local_hint = ' Modo local: revisa la terminal del servidor para copiar el enlace.'
        else:
            print(f'[Prodify] No existe ninguna cuenta con el correo {email}', flush=True)

        message = 'Si existe una cuenta con ese correo, te hemos enviado instrucciones para recuperar el acceso.' + local_hint
        return render_template(
            'forgot_password.html',
            message_html=build_auth_message_html(message, 'success'),
        )

    return render_template('forgot_password.html', message_html=build_auth_message_html(None))


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Permite fijar una nueva contrasena a partir del correo de recuperacion."""
    user, token_error = verify_password_reset_token(token)
    if token_error:
        return render_template(
            'reset_password.html',
            token=token,
            token_error=token_error,
            message_html=build_auth_message_html(token_error),
        )

    if request.method == 'POST':
        password = request.form.get('password') or ''
        confirm_password = request.form.get('confirm_password') or ''
        allowed, retry_after = check_rate_limit('reset-password', 6, 1800, user.email)
        if not allowed:
            message = build_rate_limit_message(retry_after)
            return render_template(
                'reset_password.html',
                token=token,
                token_error=None,
                message_html=build_auth_message_html(message),
            )

        password_error = validate_password_strength(password)
        if password_error:
            message = password_error
            return render_template(
                'reset_password.html',
                token=token,
                token_error=None,
                message_html=build_auth_message_html(message),
            )

        if password != confirm_password:
            message = 'Las contraseñas no coinciden.'
            return render_template(
                'reset_password.html',
                token=token,
                token_error=None,
                message_html=build_auth_message_html(message),
            )

        user.password = generate_password_hash(password)
        db.session.commit()
        log_activity(user.id, 'activity.password_updated', 'La contrasena se ha cambiado desde recuperacion')
        return redirect(url_for('login', reset=1))

    return render_template(
        'reset_password.html',
        token=token,
        token_error=None,
        message_html=build_auth_message_html(None),
    )


@app.route('/verificar/<token>')
def verify_email(token):
    """Confirma el correo del usuario antes de permitir el acceso."""
    user, token_error = verify_email_verification_token(token)
    if token_error:
        return render_template(
            'verify_notice.html',
            message_html=build_auth_message_html(token_error),
            email='',
        )

    if not user.email_verified:
        user.email_verified = True
        user.verified_at = datetime.utcnow()
        db.session.commit()
        log_activity(user.id, 'activity.email_verified', 'La cuenta se ha activado correctamente')
        send_verified_confirmation_email(user)

    return redirect(url_for('login', verified=1))


@app.route('/reenviar-verificacion', methods=['GET', 'POST'])
def resend_verification():
    """Permite reenviar el correo de verificacion a una cuenta pendiente."""
    if request.method == 'POST':
        email = sanitize_text((request.form.get('email') or '').lower(), 100)
        user = User.query.filter_by(email=email).first()
        allowed, retry_after = check_rate_limit('resend-verification', 4, 1800, email)
        if not allowed:
            message = build_rate_limit_message(retry_after)
            return render_template(
                'verify_notice.html',
                message_html=build_auth_message_html(message),
                email=email,
            )

        if not is_valid_email_address(email):
            return render_template(
                'verify_notice.html',
                message_html=build_auth_message_html('Introduce un correo electronico valido.'),
                email=email,
            )

        if user and not user.email_verified:
            sent, _ = send_verification_email(user)
            message = 'Si la cuenta existe y sigue pendiente, te hemos enviado un nuevo correo de verificacion.'
            if not sent:
                message += ' Modo local: revisa la terminal del servidor para abrir el enlace.'
            return render_template(
                'verify_notice.html',
                message_html=build_auth_message_html(message, 'success'),
                email=email,
            )

        message = 'Si la cuenta existe y sigue pendiente, te hemos enviado un nuevo correo de verificacion.'
        return render_template(
            'verify_notice.html',
            message_html=build_auth_message_html(message, 'success'),
            email=email,
        )

    return render_template(
        'verify_notice.html',
        message_html=build_auth_message_html(None),
        email='',
    )


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    """Cierra la sesion actual del usuario."""
    session.pop('user_id', None)
    session.pop('preferred_language', None)
    return redirect(url_for('login'))


@app.route('/workspaces/create', methods=['POST'])
def create_workspace():
    """Crea un espacio nuevo y un tablero inicial."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    name = sanitize_text(request.form.get('workspace_name') or '', 120)
    board_name = sanitize_text(request.form.get('board_name') or '', 120) or 'Tablero principal'
    if not name:
        return redirect(url_for('home'))
    background_color, cover_url = resolve_board_cover_inputs()

    workspace = Workspace(user_id=user.id, name=name[:120])
    db.session.add(workspace)
    db.session.flush()

    board = Board(
        workspace_id=workspace.id,
        name=board_name[:120],
        background_color=background_color,
        cover_url=cover_url,
    )
    db.session.add(board)
    db.session.flush()

    # Estas son las columnas iniciales del tablero principal.
    titles = ["Pendiente", "En progreso", "Listo"]
    for i in range(len(titles)):
        db.session.add(BoardColumn(board_id=board.id, title=titles[i], position=i))

    db.session.commit()
    log_activity(user.id, 'activity.workspace_created', f'"{workspace.name}" con tablero principal')
    redirect_url = url_for('board_view', board_id=board.id)
    if request.headers.get('X-Requested-With') == 'fetch':
        return {'redirect_url': redirect_url}
    return redirect(redirect_url)


@app.route('/workspaces/<int:workspace_id>/boards/create', methods=['POST'])
def create_board(workspace_id):
    """Crea un tablero nuevo dentro de un espacio existente."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    workspace, workspace_role = get_workspace_for_user(workspace_id, user.id)
    if not workspace:
        return redirect(url_for('home'))
    if not can_manage_board(workspace_role):
        return redirect(url_for('workspace_view', workspace_id=workspace_id))

    name = sanitize_text(request.form.get('board_name') or '', 120)
    if not name:
        return redirect(url_for('home'))
    background_color, cover_url = resolve_board_cover_inputs()

    new_board = Board(
        workspace_id=workspace.id,
        name=name[:120],
        background_color=background_color,
        cover_url=cover_url,
    )
    db.session.add(new_board)
    db.session.commit()
    log_activity(user.id, 'activity.board_created', f'"{new_board.name}" en "{workspace.name}"')
    redirect_url = url_for('board_view', board_id=new_board.id)
    if request.headers.get('X-Requested-With') == 'fetch':
        return {'redirect_url': redirect_url}
    return redirect(redirect_url)


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
    log_activity(user.id, 'activity.workspace_deleted', f'"{workspace_name}" y su contenido')
    return redirect(url_for('home'))


@app.route('/workspaces/<int:workspace_id>/update', methods=['POST'])
def update_workspace(workspace_id):
    """Actualiza el nombre de un espacio existente."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    workspace, workspace_role = get_workspace_for_user(workspace_id, user.id)
    if not workspace:
        return redirect(url_for('home'))
    if not can_manage_workspace(workspace_role):
        return redirect(url_for('workspace_view', workspace_id=workspace_id))

    new_name = sanitize_text(request.form.get('workspace_name') or '', 120)
    if not new_name:
        return redirect(url_for('workspace_view', workspace_id=workspace.id))

    old_name = workspace.name
    workspace.name = new_name[:120]
    db.session.commit()
    log_activity(user.id, 'activity.workspace_updated', f'"{old_name}" paso a llamarse "{workspace.name}"')
    return redirect(url_for('workspace_view', workspace_id=workspace.id))


@app.route('/boards/<int:board_id>/delete', methods=['POST'])
def delete_board(board_id):
    """Elimina un tablero con sus columnas y sus tarjetas."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    board, _workspace, workspace_role = get_board_for_user(board_id, user.id)
    if not board:
        return redirect(url_for('home'))
    if not can_manage_board(workspace_role):
        return redirect(url_for('board_view', board_id=board_id))

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
    log_activity(user.id, 'activity.board_deleted', f'"{board_name}"')
    return redirect(url_for('home'))


@app.route('/account/update', methods=['POST'])
def update_account():
    """Actualiza el nombre visible del usuario en su perfil."""
    user, redirect_response = get_user_or_redirect()
    if redirect_response:
        return redirect_response

    profile = get_profile(user)
    new_name = sanitize_text(request.form.get('display_name') or '', 80)
    if new_name:
        profile.display_name = new_name

    if request.form.get('remove_avatar') == '1' and profile.avatar_url:
        existing_name = profile.avatar_url.rsplit('/', 1)[-1]
        existing_path = os.path.join(avatar_upload_dir, existing_name)
        if os.path.exists(existing_path):
            try:
                os.remove(existing_path)
            except OSError:
                pass
        profile.avatar_url = None

    avatar_file = request.files.get('avatar_file')
    if avatar_file and avatar_file.filename:
        if is_allowed_avatar_filename(avatar_file.filename):
            safe_name = secure_filename(avatar_file.filename)
            extension = safe_name.rsplit('.', 1)[1].lower()
            stored_name = f'user_{user.id}_{secrets.token_hex(8)}.{extension}'
            os.makedirs(avatar_upload_dir, exist_ok=True)
            avatar_file.save(os.path.join(avatar_upload_dir, stored_name))

            if profile.avatar_url:
                previous_name = profile.avatar_url.rsplit('/', 1)[-1]
                previous_path = os.path.join(avatar_upload_dir, previous_name)
                if os.path.exists(previous_path):
                    try:
                        os.remove(previous_path)
                    except OSError:
                        pass

            profile.avatar_url = url_for('uploaded_avatar', filename=stored_name)

    db.session.commit()

    return redirect(url_for('profile_page'))


if __name__ == '__main__':
    ensure_runtime_schema()
    # Arranca el servidor local de desarrollo.
    app.run(host='127.0.0.1', port=5000, debug=True)
