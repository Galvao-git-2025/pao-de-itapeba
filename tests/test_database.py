from decimal import Decimal

from sqlalchemy import inspect

from app.database import criar_engine, criar_fabrica_sessoes, Base
from app.models import ItemEstoque, MovimentacaoEstoque


def test_criar_tabelas_e_registrar_movimentacao():
    # Cria um banco temporário em memória.
    engine = criar_engine("sqlite:///:memory:")

    # Cria as tabelas a partir dos modelos.
    Base.metadata.create_all(engine)

    # Verifica se as duas tabelas foram criadas.
    tabelas = inspect(engine).get_table_names()

    assert "item_estoque" in tabelas
    assert "movimentacao_estoque" in tabelas

    # Cria uma sessão para trabalhar com o banco.
    FabricaSessoes = criar_fabrica_sessoes(engine)

    with FabricaSessoes() as sessao:
        # Registra um ingrediente.
        item = ItemEstoque(
            nome="Farinha de trigo",
            tipo_item="ingrediente",
            unidade_medida="kg",
            quantidade_atual=Decimal("10.000"),
            estoque_minimo=Decimal("2.000"),
            preco_venda=None
        )

        sessao.add(item)
        sessao.flush()

        # Registra uma entrada de estoque.
        movimentacao = MovimentacaoEstoque(
            item=item,
            tipo_movimento="entrada",
            quantidade=Decimal("5.000")
        )

        sessao.add(movimentacao)
        sessao.commit()

        # Confirma o relacionamento entre as entidades.
        sessao.refresh(item)

        assert len(item.movimentacoes) == 1
        assert item.movimentacoes[0].tipo_movimento == "entrada"
        assert item.movimentacoes[0].quantidade == Decimal("5.000")

    engine.dispose()