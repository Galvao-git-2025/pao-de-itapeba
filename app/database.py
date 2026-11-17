from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    """
    Classe-base dos modelos do banco de dados.
    Os modelos ItemEstoque e MovimentacaoEstoque herdam dela.
    """
    pass


def criar_engine(database_url: str) -> Engine:
    """
    Cria a conexão com o banco de dados.

    Aceita URLs do SQLite e PostgreSQL.
    """
    if not database_url:
        raise ValueError("A URL do banco de dados não foi configurada.")

    # Utiliza o driver Psycopg 3, já instalado no projeto.
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1
        )

    connect_args = {}

    # Configuração necessária para o SQLite em aplicações Flask.
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        connect_args=connect_args
    )

    return engine


def criar_fabrica_sessoes(engine: Engine):
    """
    Cria uma fábrica para abrir sessões de acesso ao banco.
    """
    return sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False
    )