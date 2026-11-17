from sqlalchemy import (
    String, Integer, Numeric, Boolean,
    CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ItemEstoque(Base):
    __tablename__ = "item_estoque"

    __table_args__ = (
        UniqueConstraint(
            "nome", "tipo_item",
            name="uq_item_nome_tipo"
        ),
        CheckConstraint(
            "tipo_item IN ('produto', 'ingrediente')",
            name="ck_tipo_item"
        ),
        CheckConstraint(
            "quantidade_atual >= 0",
            name="ck_quantidade"
        ),
        CheckConstraint(
            "estoque_minimo >= 0",
            name="ck_estoque_minimo"
        ),
        CheckConstraint(
            "preco_venda IS NULL OR preco_venda > 0",
            name="ck_preco_positivo"
        ),
        CheckConstraint(
            "tipo_item != 'produto' OR preco_venda IS NOT NULL",
            name="ck_preco_produto"
        ),
    )

    id_item: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )

    nome: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    tipo_item: Mapped[str] = mapped_column(
        String(20), nullable=False
    )

    unidade_medida: Mapped[str] = mapped_column(
        String(15), nullable=False
    )

    quantidade_atual: Mapped[float] = mapped_column(
        Numeric(10, 3), nullable=False, default=0
    )

    estoque_minimo: Mapped[float] = mapped_column(
        Numeric(10, 3), nullable=False
    )

    preco_venda: Mapped[float | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )

    ativo: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )

    movimentacoes = relationship(
        "MovimentacaoEstoque",
        back_populates="item"
    )
