import os
import uuid
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
import bleach
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from PIL import Image
import secrets

# Import romantic AI module
try:
    from romantic_ai import generate_romantic_declaration, generate_preview_declaration
except ImportError:
    # Fallback functions if AI module fails
    def generate_romantic_declaration(nome_destinatario, tema="apaixonada e animada"):
        safe_name = bleach.clean(nome_destinatario)
        return f"""
        <h2>💕 {safe_name} 💕</h2>
        <p>🌹 Você é a pessoa mais especial da minha vida. Cada dia ao seu lado é uma nova oportunidade de me apaixonar ainda mais por quem você é. 🌹</p>
        <p>✨ Seus olhos iluminam meus dias mais escuros, seu sorriso aquece meu coração e sua presença faz de mim uma pessoa melhor. ✨</p>
        <p>💫 Prometo estar sempre ao seu lado, nos momentos de alegria e nos desafios da vida. Você é meu porto seguro, minha inspiração e meu grande amor. 💫</p>
        <p class="text-end"><strong>💖 Com todo meu amor eterno 💖</strong></p>
        """
    def generate_preview_declaration(nome_destinatario):
        safe_name = bleach.clean(nome_destinatario)
        return f"""
        <h4 class="text-romantic mb-3">{safe_name} 💕</h4>
        <p>Você ilumina minha vida como as estrelas iluminam a noite. 🌟</p>
        <p>Meu amor por você é infinito e verdadeiro. 💝</p>
        <p class="text-end"><strong>Com todo meu amor ❤️</strong></p>
        """

app = Flask(__name__)

# Configuração de segurança para produção
if not os.environ.get('SESSION_SECRET'):
    if os.environ.get('RENDER') or not __name__ == '__main__':
        # Em produção, exigir SESSION_SECRET
        raise ValueError("SESSION_SECRET environment variable is required for production")
    else:
        # Em desenvolvimento local, usar fallback
        app.config['SECRET_KEY'] = secrets.token_hex(16)
else:
    app.config['SECRET_KEY'] = os.environ['SESSION_SECRET']

# Configurações de cookie seguro em produção
if os.environ.get('RENDER') or not app.debug:
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configurar proteção CSRF
csrf = CSRFProtect(app)

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # type: ignore
login_manager.login_message = 'Por favor, faça login para acessar esta página.'

# Criar diretórios necessários
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Modelo de Usuário
class User(UserMixin):
    def __init__(self, user_id, email, nome):
        self.id = user_id
        self.email = email
        self.nome = nome

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM usuarios WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user:
        return User(user['id'], user['email'], user['nome'])
    return None

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    
    # Tabela de usuários
    conn.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de declarações
    conn.execute('''
        CREATE TABLE IF NOT EXISTS declaracoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            link_unico TEXT UNIQUE NOT NULL,
            nome_destinatario TEXT NOT NULL,
            foto_filename TEXT,
            data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
            visualizacoes INTEGER DEFAULT 0,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM usuarios WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['senha'], senha):
            user_obj = User(user['id'], user['email'], user['nome'])
            login_user(user_obj)
            return redirect(url_for('dashboard'))
        else:
            flash('Email ou senha incorretos.', 'error')
    
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        confirmar_senha = request.form['confirmar_senha']
        
        if senha != confirmar_senha:
            flash('As senhas não coincidem.', 'error')
            return render_template('registro.html')
        
        conn = get_db_connection()
        existing_user = conn.execute('SELECT id FROM usuarios WHERE email = ?', (email,)).fetchone()
        
        if existing_user:
            flash('Este email já está cadastrado.', 'error')
            conn.close()
            return render_template('registro.html')
        
        hashed_password = generate_password_hash(senha)
        conn.execute('INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)',
                    (nome, email, hashed_password))
        conn.commit()
        conn.close()
        
        flash('Conta criada com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('login'))
    
    return render_template('registro.html')

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    declaracoes = conn.execute('''
        SELECT * FROM declaracoes 
        WHERE usuario_id = ? 
        ORDER BY data_criacao DESC
    ''', (current_user.id,)).fetchall()
    conn.close()
    
    return render_template('dashboard.html', declaracoes=declaracoes)

@app.route('/criar-declaracao', methods=['GET', 'POST'])
@login_required
def criar_declaracao():
    if request.method == 'POST':
        nome_destinatario = request.form['nome_destinatario']
        foto = request.files.get('foto')
        
        if not nome_destinatario:
            flash('O nome do destinatário é obrigatório.', 'error')
            return render_template('criar_declaracao.html')
        
        # Gerar link único
        link_unico = str(uuid.uuid4())
        
        # Processar upload da foto
        foto_filename = None
        if foto and foto.filename:
            base_filename = secure_filename(foto.filename)
            if base_filename and base_filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                # Criar nome único para o arquivo
                unique_filename = f"{uuid.uuid4()}_{base_filename}"
                foto_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                
                # Redimensionar imagem com tratamento de erro
                try:
                    img = Image.open(foto.stream)
                    img.verify()  # Verificar se é uma imagem válida
                    foto.stream.seek(0)  # Reset stream após verify
                    img = Image.open(foto.stream)
                    img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                    img.save(foto_path, optimize=True, quality=85)
                except Exception as e:
                    flash('Erro ao processar a imagem. Por favor, use uma imagem válida.', 'error')
                    return render_template('criar_declaracao.html')
                
                foto_filename = unique_filename
        
        # Salvar no banco de dados
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO declaracoes (usuario_id, link_unico, nome_destinatario, foto_filename)
            VALUES (?, ?, ?, ?)
        ''', (current_user.id, link_unico, nome_destinatario, foto_filename))
        conn.commit()
        conn.close()
        
        flash('Declaração criada com sucesso!', 'success')
        return redirect(url_for('ver_declaracao', link=link_unico))
    
    return render_template('criar_declaracao.html')

@app.route('/declaracao/<link>')
def ver_declaracao(link):
    conn = get_db_connection()
    declaracao = conn.execute('''
        SELECT d.*, u.nome as nome_criador 
        FROM declaracoes d 
        JOIN usuarios u ON d.usuario_id = u.id 
        WHERE d.link_unico = ?
    ''', (link,)).fetchone()
    
    if declaracao:
        # Incrementar visualizações
        conn.execute('UPDATE declaracoes SET visualizacoes = visualizacoes + 1 WHERE link_unico = ?', (link,))
        conn.commit()
    
    conn.close()
    
    if not declaracao:
        return render_template('404.html'), 404
    
    # Gerar declaração romântica com IA
    try:
        declaracao_ai = generate_romantic_declaration(declaracao['nome_destinatario'], "apaixonada e animada")
    except Exception as e:
        print(f"Erro ao gerar declaração com IA: {e}")
        # Usar declaração de fallback segura
        safe_name = bleach.clean(declaracao['nome_destinatario'])
        declaracao_ai = f"""
        <h2>💕 {safe_name} 💕</h2>
        
        <p>🌹 Você é a pessoa mais especial da minha vida. Cada dia ao seu lado é uma nova oportunidade de me apaixonar ainda mais por quem você é. 🌹</p>
        
        <p>✨ Seus olhos iluminam meus dias mais escuros, seu sorriso aquece meu coração e sua presença faz de mim uma pessoa melhor. ✨</p>
        
        <p>💫 Prometo estar sempre ao seu lado, nos momentos de alegria e nos desafios da vida. Você é meu porto seguro, minha inspiração e meu grande amor. 💫</p>
        
        <p class="text-end"><strong>💖 Com todo meu amor eterno 💖</strong></p>
        """
    
    return render_template('declaracao.html', declaracao=declaracao, declaracao_ai=declaracao_ai)

@app.route('/api/preview-declaracao', methods=['POST'])
@csrf.exempt  # Exempt from CSRF for API endpoint
def api_preview_declaracao():
    """API endpoint para gerar prévia da declaração"""
    nome_destinatario = (request.json and request.json.get('nome')) or request.form.get('nome')
    
    if not nome_destinatario:
        return jsonify({'error': 'Nome é obrigatório'}), 400
    
    try:
        preview = generate_preview_declaration(nome_destinatario)
        return jsonify({'preview': preview})
    except Exception as e:
        # Retornar prévia de fallback em caso de erro (sanitizada)
        safe_name = bleach.clean(nome_destinatario)
        fallback = f"""
        <h4 class="text-romantic mb-3">{safe_name} 💕</h4>
        <p>Você ilumina minha vida como as estrelas iluminam a noite. Cada momento ao seu lado é um presente que guardo no coração. 🌟</p>
        <p>Meu amor por você cresce a cada dia, como flores que desabrocham em um jardim eterno. 💝</p>
        <p class="text-end"><strong>Com todo meu amor ❤️</strong></p>
        """
        return jsonify({'preview': fallback})

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

# Inicializar banco de dados
with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)