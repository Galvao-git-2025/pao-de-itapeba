from decimal import Decimal, InvalidOperation

from sqlalchemy import select

from app.models import ItemEstoque


class ErroCadastroItem(ValueError):
    """Erro relacionado às regras de cadastro de itens."""
    pass


def converter_decimal(valor, campo, casas_decimais):
    try:
        numero = Decimal(str(valor))
    except (InvalidOperation, ValueError, TypeError):
        raise ErroCadastroItem(f"{campo} inválido.")

    if not numero.is_finite() or numero < 0:
        raise ErroCadastroItem(
            f"{campo} não pode ser negativo."
        )

    unidade = Decimal("1").scaleb(-casas_decimais)

    if numero != numero.quantize(unidade):
        raise ErroCadastroItem(
            f"{campo} aceita no máximo "
            f"{casas_decimais} casas decimais."
        )

    return numero


def cadastrar_item(
    fabrica_sessoes,
    *,
    nome,
    tipo_item,
    unidade_medida,
    estoque_minimo,
    preco_venda=None
):
    nome = (nome or "").strip()
    tipo_item = (tipo_item or "").strip().lower()
    unidade_medida = (unidade_medida or "").strip()

    if not nome:
        raise ErroCadastroItem("Informe o nome do item.")

    if len(nome) > 100:
        raise ErroCadastroItem(
            "O nome deve ter no máximo 100 caracteres."
        )

    if tipo_item not in {"produto", "ingrediente"}:
        raise ErroCadastroItem("Tipo de item inválido.")

    if not unidade_medida:
        raise ErroCadastroItem(
            "Informe a unidade de medida."
        )

    if len(unidade_medida) > 15:
        raise ErroCadastroItem(
            "A unidade de medida deve ter no máximo 15 caracteres."
        )

    estoque_minimo = converter_decimal(
        estoque_minimo,
        "Estoque mínimo",
        3
    )

    preco = None

    if tipo_item == "produto":
        if preco_venda is None or str(preco_venda).strip() == "":
            raise ErroCadastroItem(
                "Informe o preço de venda do produto."
            )

        preco = converter_decimal(
            preco_venda,
            "Preço de venda",
            2
        )

        if preco <= 0:
            raise ErroCadastroItem(
                "O preço de venda deve ser maior que zero."
            )

    elif preco_venda is not None and str(preco_venda).strip():
        raise ErroCadastroItem(
            "Ingredientes não possuem preço de venda neste cadastro."
        )

    with fabrica_sessoes.begin() as sessao:
        existente = sessao.scalar(
            select(ItemEstoque).where(
                ItemEstoque.nome == nome,
                ItemEstoque.tipo_item == tipo_item
            )
        )

        if existente:
            raise ErroCadastroItem(
                "Já existe um item com esse nome e tipo."
            )

        item = ItemEstoque(
            nome=nome,
            tipo_item=tipo_item,
            unidade_medida=unidade_medida,
            quantidade_atual=Decimal("0.000"),
            estoque_minimo=estoque_minimo,
            preco_venda=preco,
            ativo=True
        )

        sessao.add(item)
        sessao.flush()

        resultado = {
            "id_item": item.id_item,
            "nome": item.nome,
            "tipo_item": item.tipo_item,
            "quantidade_atual": item.quantidade_atual
        }

    return resultado