from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    current_app
)

from app.forms import ItemForm

from app.services.item_service import (
    cadastrar_item,
    ErroCadastroItem
)


main_bp = Blueprint("main", __name__)


@main_bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@main_bp.route("/itens/novo", methods=["GET", "POST"])
def novo_item():
    form = ItemForm()

    if form.validate_on_submit():
        try:
            resultado = cadastrar_item(
                current_app.extensions["session_factory"],
                nome=form.nome.data,
                tipo_item=form.tipo_item.data,
                unidade_medida=form.unidade_medida.data,
                estoque_minimo=form.estoque_minimo.data,
                preco_venda=form.preco_venda.data
            )

            flash(
                f"Item '{resultado['nome']}' cadastrado com sucesso!",
                "success"
            )

            return redirect(url_for("main.novo_item"))

        except ErroCadastroItem as erro:
            flash(str(erro), "danger")

    return render_template("novo_item.html", form=form)