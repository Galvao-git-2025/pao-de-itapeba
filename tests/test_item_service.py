from decimal import Decimal

import pytest
from sqlalchemy import select

from app.database import (
    Base,
    criar_engine,
    criar_fabrica_sessoes
)

from app.models import ItemEstoque

from app.services.item_service import (
    ErroCadastroItem,
    cadastrar_item
)


@pytest.fixture
def fabrica_sessoes():
    engine = criar_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    fabrica = criar_fabrica_sessoes(engine)

    yield fabrica

    engine.dispose()


def test_cadastrar_produto(fabrica_sessoes):
    resultado = cadastrar_item(
        fabrica_sessoes,
        nome="Esfirra de carne",
        tipo_item="produto",
        unidade_medida="unidade",
        estoque_minimo="10.000",
        preco_venda="7.50"
    )

    assert resultado["nome"] == "Esfirra de carne"
    assert resultado["tipo_item"] == "produto"
    assert resultado["quantidade_atual"] == Decimal("0.000")

    with fabrica_sessoes() as sessao:
        item = sessao.scalar(
            select(ItemEstoque).where(
                ItemEstoque.id_item == resultado["id_item"]
            )
        )

        assert item.preco_venda == Decimal("7.50")
        assert item.ativo is True


def test_cadastrar_ingrediente(fabrica_sessoes):
    resultado = cadastrar_item(
        fabrica_sessoes,
        nome="Farinha de trigo",
        tipo_item="ingrediente",
        unidade_medida="kg",
        estoque_minimo="5.000"
    )

    assert resultado["tipo_item"] == "ingrediente"

    with fabrica_sessoes() as sessao:
        item = sessao.get(ItemEstoque, resultado["id_item"])

        assert item.preco_venda is None
        assert item.quantidade_atual == Decimal("0.000")


def test_impedir_produto_sem_preco(fabrica_sessoes):
    with pytest.raises(ErroCadastroItem):
        cadastrar_item(
            fabrica_sessoes,
            nome="Kibe",
            tipo_item="produto",
            unidade_medida="unidade",
            estoque_minimo="5.000"
        )


def test_impedir_nome_vazio(fabrica_sessoes):
    with pytest.raises(ErroCadastroItem):
        cadastrar_item(
            fabrica_sessoes,
            nome=" ",
            tipo_item="ingrediente",
            unidade_medida="kg",
            estoque_minimo="2.000"
        )


def test_impedir_tipo_invalido(fabrica_sessoes):
    with pytest.raises(ErroCadastroItem):
        cadastrar_item(
            fabrica_sessoes,
            nome="Farinha",
            tipo_item="material",
            unidade_medida="kg",
            estoque_minimo="2.000"
        )


def test_impedir_estoque_minimo_negativo(fabrica_sessoes):
    with pytest.raises(ErroCadastroItem):
        cadastrar_item(
            fabrica_sessoes,
            nome="Açúcar",
            tipo_item="ingrediente",
            unidade_medida="kg",
            estoque_minimo="-1.000"
        )


def test_impedir_cadastro_duplicado(fabrica_sessoes):
    dados = {
        "nome": "Farinha de trigo",
        "tipo_item": "ingrediente",
        "unidade_medida": "kg",
        "estoque_minimo": "5.000"
    }

    cadastrar_item(fabrica_sessoes, **dados)

    with pytest.raises(ErroCadastroItem):
        cadastrar_item(fabrica_sessoes, **dados)


def test_impedir_preco_zero(fabrica_sessoes):
    with pytest.raises(ErroCadastroItem):
        cadastrar_item(
            fabrica_sessoes,
            nome="Esfirra de queijo",
            tipo_item="produto",
            unidade_medida="unidade",
            estoque_minimo="5.000",
            preco_venda="0.00"
        )