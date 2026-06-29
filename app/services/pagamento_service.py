from flask import current_app

from app import db
from app.models.pagamento import Pagamento
from app.models.pedido import Pedido, StatusPedido
from app.models.estoque import Estoque
from app.utils.responses import erro_response


def realizar_pagamento_service(data, usuario_id, perfil):
    pedido_id = data.get("pedidoId")
    valor = data.get("valor")
    aprovado = data.get("aprovado")

    if pedido_id is None or valor is None or aprovado is None:
        return erro_response(
            "DADOS_INVALIDOS",
            "pedidoId, valor e aprovado são obrigatórios.",
            422,
            [
                {"field": "pedidoId", "issue": "Campo obrigatório"},
                {"field": "valor", "issue": "Campo obrigatório"},
                {"field": "aprovado", "issue": "Campo obrigatório"}
            ]
        )

    try:
        pedido_id = int(pedido_id)
    except (TypeError, ValueError):
        return erro_response(
            "PEDIDO_INVALIDO",
            "pedidoId deve ser um número inteiro.",
            422,
            [{"field": "pedidoId", "issue": "Deve ser um número inteiro"}]
        )

    if not isinstance(aprovado, bool):
        return erro_response(
            "APROVADO_INVALIDO",
            "O campo aprovado deve ser true ou false.",
            422,
            [{"field": "aprovado", "issue": "Deve ser booleano: true ou false"}]
        )

    try:
        valor = float(valor)
    except (TypeError, ValueError):
        return erro_response(
            "VALOR_INVALIDO",
            "O valor do pagamento deve ser numérico.",
            422,
            [{"field": "valor", "issue": "Deve ser numérico"}]
        )

    if valor <= 0:
        return erro_response(
            "VALOR_INVALIDO",
            "O valor do pagamento deve ser maior que zero.",
            422,
            [{"field": "valor", "issue": "Deve ser maior que zero"}]
        )

    pedido = Pedido.query.get(pedido_id)

    if not pedido:
        return erro_response(
            "PEDIDO_NAO_ENCONTRADO",
            "Pedido não encontrado.",
            404,
            [{"field": "pedidoId", "issue": "Pedido inexistente"}]
        )

    perfis_permitidos = ["CLIENTE", "ATENDENTE", "GERENTE"]

    if perfil not in perfis_permitidos:
        return erro_response(
            "SEM_PERMISSAO",
            "Usuário sem permissão para realizar pagamento.",
            403,
            [{"field": "perfil", "issue": "Perfil não autorizado para pagamento"}]
        )

    if perfil == "CLIENTE" and pedido.cliente_id != usuario_id:
        return erro_response(
            "SEM_PERMISSAO",
            "Usuário sem permissão para pagar este pedido.",
            403,
            [{"field": "usuario", "issue": "Cliente só pode pagar os próprios pedidos"}]
        )

    if pedido.status != StatusPedido.AGUARDANDO_PAGAMENTO:
        return erro_response(
            "PEDIDO_NAO_PODE_SER_PAGO",
            "Somente pedidos aguardando pagamento podem receber pagamento.",
            409,
            [
                {
                    "field": "status",
                    "issue": f"Status atual do pedido: {pedido.status.value}"
                }
            ]
        )

    if round(valor, 2) != round(pedido.total, 2):
        return erro_response(
            "VALOR_DIVERGENTE",
            "O valor informado não corresponde ao total do pedido.",
            409,
            [
                {
                    "field": "valor",
                    "issue": f"Valor esperado: {round(pedido.total, 2)}"
                }
            ]
        )

    pagamento = Pagamento(
        pedido_id=pedido.id,
        valor=valor,
        status="APROVADO" if aprovado else "RECUSADO"
    )

    if aprovado:
        pedido.status = StatusPedido.EM_PREPARO
        mensagem = "Pagamento aprovado pelo gateway mock."
    else:
        pedido.status = StatusPedido.CANCELADO
        mensagem = "Pagamento recusado pelo gateway mock."

        for item in pedido.itens:
            estoque = Estoque.query.filter_by(
                produto_id=item.produto_id,
                unidade_id=pedido.unidade_id
            ).first()

            if estoque:
                estoque.quantidade += item.quantidade

    db.session.add(pagamento)
    db.session.commit()

    current_app.logger.info(
        f"Pagamento {pagamento.status}: "
        f"pedido={pedido.id}, "
        f"cliente={pedido.cliente_id}, "
        f"valor={pagamento.valor}, "
        f"novo_status={pedido.status.value}, "
        f"perfil={perfil}"
    )

    return {
        "pedidoId": pedido.id,
        "pagamentoStatus": pagamento.status,
        "novoStatusPedido": pedido.status.value,
        "createdAt": pagamento.created_at.isoformat(),
        "message": mensagem,
        "gatewayMock": {
            "provedor": "MOCK",
            "status": pagamento.status,
            "valor": pagamento.valor
        }
    }, 200