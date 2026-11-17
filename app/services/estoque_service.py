from decimal import Decimal, InvalidOperation

from sqlalchemy import select

from app.models import ItemEstoque, MovimentacaoEstoque


class ErroMovimentacao(ValueError):
    """Erro relacionado às regras de movimentação do estoque."""
    pass


def converter_decimal(valor, campo):
    try:
        numero = Decimal(str(valor))
    except (InvalidOperation, ValueError, TypeError):
        raise ErroMovimentacao(f"{campo} inválido.")

    if not numero.is_finite() or numero <= 0:
        raise ErroMovimentacao(f"{campo} deve ser maior que zero.")

    return numero


def registrar_movimentacao(
    fabrica_sessoes,
    *,
    id_item: int,
    tipo_movimento: str,
    quantidade,
    motivo: str | None = None,
    preco_unitario=None
):
    tipos_validos = {"entrada", "saida", "venda", "perda"}

    if tipo_movimento not in tipos_validos:
        raise ErroMovimentacao("Tipo de movimentação inválido.")

    quantidade = converter_decimal(quantidade, "Quantidade")

    if quantidade != quantidade.quantize(Decimal("0.001")):
        raise ErroMovimentacao(
            "A quantidade aceita no máximo três casas decimais."
        )

    if tipo_movimento == "perda" and not (motivo or "").strip():
        raise ErroMovimentacao("Informe o motivo da perda.")

    if preco_unitario is not None and tipo_movimento != "venda":
        raise ErroMovimentacao(
            "O preço unitário deve ser informado somente em vendas."
        )

    if tipo_movimento == "venda" and preco_unitario is None:
        raise ErroMovimentacao(
            "Informe o preço unitário da venda."
        )

    preco = None

    if preco_unitario is not None:
        preco = converter_decimal(preco_unitario, "Preço")

        if preco != preco.quantize(Decimal("0.01")):
            raise ErroMovimentacao(
                "O preço aceita no máximo duas casas decimais."
            )

    with fabrica_sessoes.begin() as sessao:

        item = sessao.scalar(
            select(ItemEstoque)
            .where(ItemEstoque.id_item == id_item)
            .with_for_update()
        )

        if item is None:
            raise ErroMovimentacao("Item não encontrado.")

        if not item.ativo:
            raise ErroMovimentacao("O item está inativo.")

        if tipo_movimento == "venda" and item.tipo_item != "produto":
            raise ErroMovimentacao(
                "Somente produtos podem receber movimentação de venda."
            )

        if tipo_movimento == "entrada":
            item.quantidade_atual += quantidade

        else:
            if item.quantidade_atual < quantidade:
                raise ErroMovimentacao(
                    "Saldo insuficiente para essa movimentação."
                )

            item.quantidade_atual -= quantidade

        movimentacao = MovimentacaoEstoque(
            item=item,
            tipo_movimento=tipo_movimento,
            quantidade=quantidade,
            motivo=(motivo or "").strip() or None,
            preco_unitario=preco
        )

        sessao.add(movimentacao)
        sessao.flush()

        resultado = {
            "id_movimentacao": movimentacao.id_movimentacao,
            "saldo_atual": item.quantidade_atual
        }

    return resultado