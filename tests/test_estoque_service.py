from decimal import Decimal

import pytest
from sqlalchemy import func, select

from app.database import (
    Base,
    criar_engine,
    criar_fabrica_sessoes
)

from app.models import ItemEstoque, MovimentacaoEstoque

from app.services.estoque_service import (
    ErroMovimentacao,
    registrar_movimentacao
)


@pytest.fixture
def fabrica_sessoes():
    engine = criar_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    fabrica = criar_fabrica_sessoes(engine)

    yield fabrica

    engine.dispose()


def criar_item(
    fabrica_sessoes,
    tipo_item="ingrediente",
    quantidade="10.000",
    ativo=True
):
    with fabrica_sessoes.begin() as sessao:
        item = ItemEstoque(
            nome="Farinha de trigo",
            tipo_item=tipo_item,
            unidade_medida="kg",
            quantidade_atual=Decimal(quantidade),
            estoque_minimo=Decimal("2.000"),
            preco_venda=(
                Decimal("6.50")
                if tipo_item == "produto"
                else None
            ),
            ativo=ativo
        )

        sessao.add(item)
        sessao.flush()

        id_item = item.id_item

    return id_item


def consultar_saldo(fabrica_sessoes, id_item):
    with fabrica_sessoes() as sessao:
        item = sessao.get(ItemEstoque, id_item)
        return item.quantidade_atual


def contar_movimentacoes(fabrica_sessoes):
    with fabrica_sessoes() as sessao:
        return sessao.scalar(
            select(func.count()).select_from(MovimentacaoEstoque)
        )


def test_entrada_aumenta_saldo(fabrica_sessoes):
    id_item = criar_item(fabrica_sessoes)

    resultado = registrar_movimentacao(
        fabrica_sessoes,
        id_item=id_item,
        tipo_movimento="entrada",
        quantidade="5.000"
    )

    assert resultado["saldo_atual"] == Decimal("15.000")
    assert contar_movimentacoes(fabrica_sessoes) == 1


def test_saida_reduz_saldo(fabrica_sessoes):
    id_item = criar_item(fabrica_sessoes)

    resultado = registrar_movimentacao(
        fabrica_sessoes,
        id_item=id_item,
        tipo_movimento="saida",
        quantidade="3.000"
    )

    assert resultado["saldo_atual"] == Decimal("7.000")


def test_venda_reduz_saldo_e_registra_preco(fabrica_sessoes):
    id_item = criar_item(
        fabrica_sessoes,
        tipo_item="produto"
    )

    resultado = registrar_movimentacao(
        fabrica_sessoes,
        id_item=id_item,
        tipo_movimento="venda",
        quantidade="2.000",
        preco_unitario="6.50"
    )

    assert resultado["saldo_atual"] == Decimal("8.000")

    with fabrica_sessoes() as sessao:
        movimentacao = sessao.scalar(
            select(MovimentacaoEstoque)
        )

        assert movimentacao.preco_unitario == Decimal("6.50")


def test_perda_reduz_saldo_e_registra_motivo(fabrica_sessoes):
    id_item = criar_item(fabrica_sessoes)

    resultado = registrar_movimentacao(
        fabrica_sessoes,
        id_item=id_item,
        tipo_movimento="perda",
        quantidade="1.000",
        motivo="Produto vencido"
    )

    assert resultado["saldo_atual"] == Decimal("9.000")

    with fabrica_sessoes() as sessao:
        movimentacao = sessao.scalar(
            select(MovimentacaoEstoque)
        )

        assert movimentacao.motivo == "Produto vencido"


def test_saldo_insuficiente_cancela_operacao(fabrica_sessoes):
    id_item = criar_item(
        fabrica_sessoes,
        quantidade="2.000"
    )

    with pytest.raises(ErroMovimentacao):
        registrar_movimentacao(
            fabrica_sessoes,
            id_item=id_item,
            tipo_movimento="saida",
            quantidade="5.000"
        )

    assert consultar_saldo(fabrica_sessoes, id_item) == Decimal("2.000")
    assert contar_movimentacoes(fabrica_sessoes) == 0


def test_item_inativo_nao_permite_movimentacao(fabrica_sessoes):
    id_item = criar_item(
        fabrica_sessoes,
        ativo=False
    )

    with pytest.raises(ErroMovimentacao):
        registrar_movimentacao(
            fabrica_sessoes,
            id_item=id_item,
            tipo_movimento="entrada",
            quantidade="1.000"
        )

    assert contar_movimentacoes(fabrica_sessoes) == 0


def test_venda_nao_permitida_para_ingrediente(fabrica_sessoes):
    id_item = criar_item(fabrica_sessoes)

    with pytest.raises(ErroMovimentacao):
        registrar_movimentacao(
            fabrica_sessoes,
            id_item=id_item,
            tipo_movimento="venda",
            quantidade="1.000",
            preco_unitario="5.00"
        )

    assert contar_movimentacoes(fabrica_sessoes) == 0