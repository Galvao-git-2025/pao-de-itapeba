from datetime import datetime, timezone

from sqlalchemy import (
    Integer, String, Numeric, DateTime,
    ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class MovimentacaoEstoque(Base):
    __tablename__ = "movimentacao_estoque"

    __table_args__ = (
        CheckConstraint(
            "tipo_movimento IN ('entrada', 'saida', 'venda', 'perda')",
            name="ck_tipo_movimento"
        ),
        CheckConstraint(
            "quantidade > 0",
            name="ck_quantidade_positiva"
        ),
        CheckConstraint(
            "preco_unitario IS NULL OR preco_unitario > 0",
            name="ck_preco_positivo"
        ),
        CheckConstraint(
            "tipo_movimento != 'venda' OR preco_unitario IS NOT NULL",
            name="ck_preco_venda"
        ),
        CheckConstraint(
            "tipo_movimento != 'perda' OR "
            "(motivo IS NOT NULL AND length(trim(motivo)) > 0)",
            name="ck_motivo_perda"
        ),
        Index("ix_movimentacao_item_data", "id_item", "data_hora"),
    )

    id_movimentacao: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )

    id_item: Mapped[int] = mapped_column(
        ForeignKey("item_estoque.id_item", ondelete="RESTRICT"),
        nullable=False
    )

    tipo_movimento: Mapped[str] = mapped_column(
        String(20), nullable=False
    )

    quantidade: Mapped[float] = mapped_column(
        Numeric(10, 3), nullable=False
    )

    data_hora: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    motivo: Mapped[str | None] = mapped_column(
        String(200), nullable=True
    )

    preco_unitario: Mapped[float | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )

    item = relationship(
        "ItemEstoque",
        back_populates="movimentacoes"
    )
