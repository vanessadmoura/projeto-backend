from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from app.services.pagamento_service import realizar_pagamento_service


pagamento_bp = Blueprint(
    "pagamentos",
    __name__,
    url_prefix="/pagamentos"
)


def perfil_atual():
    claims = get_jwt()
    return claims.get("perfil")


@pagamento_bp.route("", methods=["POST"])
@jwt_required()
def realizar_pagamento():
    """
    Realiza pagamento mock de um pedido
    ---
    tags:
      - Pagamentos
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - pedidoId
            - valor
            - aprovado
          properties:
            pedidoId:
              type: integer
              example: 1
            valor:
              type: number
              example: 51.80
            aprovado:
              type: boolean
              example: true
    responses:
      200:
        description: Pagamento mock processado com sucesso
        examples:
          application/json:
            pedidoId: 1
            pagamentoStatus: APROVADO
            novoStatusPedido: EM_PREPARO
            message: Pagamento aprovado pelo gateway mock.
            gatewayMock:
              provedor: MOCK
              status: APROVADO
              valor: 51.8
      401:
        description: Token ausente ou inválido
      403:
        description: Usuário sem permissão
        examples:
          application/json:
            error: SEM_PERMISSAO
            message: Usuário sem permissão para pagar este pedido.
            details:
              - field: usuario
                issue: Cliente só pode pagar os próprios pedidos
            timestamp: "2026-02-05T12:00:00+00:00"
            path: /pagamentos
      404:
        description: Pedido não encontrado
        examples:
          application/json:
            error: PEDIDO_NAO_ENCONTRADO
            message: Pedido não encontrado.
            details:
              - field: pedidoId
                issue: Pedido inexistente
            timestamp: "2026-02-05T12:00:00+00:00"
            path: /pagamentos
      409:
        description: Regra de negócio violada
        examples:
          application/json:
            error: PEDIDO_NAO_PODE_SER_PAGO
            message: Somente pedidos aguardando pagamento podem receber pagamento.
            details:
              - field: status
                issue: "Status atual do pedido: CANCELADO"
            timestamp: "2026-02-05T12:00:00+00:00"
            path: /pagamentos
      422:
        description: Dados inválidos
        examples:
          application/json:
            error: DADOS_INVALIDOS
            message: pedidoId, valor e aprovado são obrigatórios.
            details:
              - field: pedidoId
                issue: Campo obrigatório
              - field: valor
                issue: Campo obrigatório
              - field: aprovado
                issue: Campo obrigatório
            timestamp: "2026-02-05T12:00:00+00:00"
            path: /pagamentos
    """
    resposta, status = realizar_pagamento_service(
        request.get_json(silent=True) or {},
        int(get_jwt_identity()),
        perfil_atual()
    )

    return jsonify(resposta), status