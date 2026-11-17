from decimal import Decimal

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SelectField,
    DecimalField,
    SubmitField
)
from wtforms.validators import (
    DataRequired,
    InputRequired,
    Length,
    NumberRange,
    Optional
)


class ItemForm(FlaskForm):

    nome = StringField(
        "Nome do item",
        validators=[
            DataRequired(message="Informe o nome do item."),
            Length(
                max=100,
                message="O nome deve ter no máximo 100 caracteres."
            )
        ]
    )

    tipo_item = SelectField(
        "Tipo de item",
        choices=[
            ("produto", "Produto"),
            ("ingrediente", "Ingrediente")
        ],
        validators=[
            DataRequired(message="Selecione o tipo do item.")
        ]
    )

    unidade_medida = StringField(
        "Unidade de medida",
        validators=[
            DataRequired(message="Informe a unidade de medida."),
            Length(
                max=15,
                message="A unidade deve ter no máximo 15 caracteres."
            )
        ]
    )

    estoque_minimo = DecimalField(
        "Estoque mínimo",
        places=3,
        validators=[
            InputRequired(message="Informe o estoque mínimo."),
            NumberRange(
                min=Decimal("0"),
                message="O estoque mínimo não pode ser negativo."
            )
        ]
    )

    preco_venda = DecimalField(
        "Preço de venda (R$)",
        places=2,
        validators=[
            Optional(),
            NumberRange(
                min=Decimal("0.01"),
                message="O preço deve ser maior que zero."
            )
        ]
    )

    submit = SubmitField("Cadastrar item")

    def validate(self, extra_validators=None):

        valido = super().validate(extra_validators)

        if self.tipo_item.data == "produto":
            if self.preco_venda.data is None:
                self.preco_venda.errors.append(
                    "O preço de venda é obrigatório para produtos."
                )
                valido = False

        elif self.tipo_item.data == "ingrediente":
            if self.preco_venda.data is not None:
                self.preco_venda.errors.append(
                    "Ingredientes não possuem preço de venda."
                )
                valido = False

        return valido