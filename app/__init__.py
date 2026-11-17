from flask import Flask
from flask_wtf.csrf import CSRFProtect

from config import Config
from app.database import criar_engine, criar_fabrica_sessoes


csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Proteção dos formulários contra ataques CSRF.
    csrf.init_app(app)

    # Configuração da conexão com o banco de dados.
    engine = criar_engine(app.config["DATABASE_URL"])

    # Disponibiliza a fábrica de sessões para as rotas.
    app.extensions["database_engine"] = engine
    app.extensions["session_factory"] = criar_fabrica_sessoes(engine)

    # Registro das rotas.
    from app.controllers.main_controller import main_bp
    app.register_blueprint(main_bp)

    return app