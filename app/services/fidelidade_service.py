from flask import current_app

from app import db
from app.models.fidelidade import Fidelidade
from app.models.usuario import Usuario
from app.utils.responses import erro_response


def consultar_pontos_service(cliente_id, perfil):
    if perfil != "CLIENTE":
        return erro_response(
            "SEM_PERMISSAO",
            "Apenas clientes podem consultar pontos de fidelidade.",
            403
        )

    cliente = Usuario.query.get(cliente_id)

    if not cliente:
        return erro_response(
            "CLIENTE_NAO_ENCONTRADO",
            "Cliente não encontrado.",
            404,
            [{"field": "clienteId", "issue": "Cliente inexistente"}]
        )

    fidelidade = Fidelidade.query.filter_by(cliente_id=cliente_id).first()

    if not fidelidade:
        fidelidade = Fidelidade(cliente_id=cliente_id, pontos=0)
        db.session.add(fidelidade)
        db.session.commit()

    return {
        "clienteId": cliente_id,
        "pontos": fidelidade.pontos,
        "consentimentoLgpd": fidelidade.consentimento_lgpd,
        "dataConsentimento": (
            fidelidade.data_consentimento.isoformat()
            if fidelidade.data_consentimento
            else None
        )
    }, 200


def registrar_consentimento_service(cliente_id, perfil):
    if perfil != "CLIENTE":
        return erro_response(
            "SEM_PERMISSAO",
            "Apenas clientes podem registrar consentimento de fidelidade.",
            403
        )

    cliente = Usuario.query.get(cliente_id)

    if not cliente:
        return erro_response(
            "CLIENTE_NAO_ENCONTRADO",
            "Cliente não encontrado.",
            404,
            [{"field": "clienteId", "issue": "Cliente inexistente"}]
        )

    if cliente.perfil.value != "CLIENTE":
        return erro_response(
            "PERFIL_INVALIDO",
            "Consentimento de fidelidade só pode ser registrado para clientes.",
            422,
            [{"field": "perfil", "issue": "Usuário não possui perfil CLIENTE"}]
        )

    fidelidade = Fidelidade.query.filter_by(cliente_id=cliente_id).first()

    if not fidelidade:
        fidelidade = Fidelidade(cliente_id=cliente_id, pontos=0)
        db.session.add(fidelidade)

    fidelidade.registrar_consentimento()

    db.session.commit()

    current_app.logger.info(
        f"Consentimento LGPD registrado: cliente={cliente_id}, "
        f"fidelidade={fidelidade.id}"
    )

    return {
        "clienteId": cliente_id,
        "consentimentoLgpd": fidelidade.consentimento_lgpd,
        "dataConsentimento": fidelidade.data_consentimento.isoformat(),
        "message": "Consentimento registrado com sucesso para o programa de fidelidade."
    }, 200


def adicionar_pontos_service(data, perfil):
    if perfil != "GERENTE":
        return erro_response(
            "SEM_PERMISSAO",
            "Usuário sem permissão para adicionar pontos.",
            403
        )

    cliente_id = data.get("clienteId")
    pontos = data.get("pontos")

    if cliente_id is None or pontos is None:
        return erro_response(
            "DADOS_INVALIDOS",
            "clienteId e pontos são obrigatórios.",
            422,
            [
                {"field": "clienteId", "issue": "Campo obrigatório"},
                {"field": "pontos", "issue": "Campo obrigatório"}
            ]
        )

    try:
        cliente_id = int(cliente_id)
    except (TypeError, ValueError):
        return erro_response(
            "CLIENTE_INVALIDO",
            "clienteId deve ser um número inteiro.",
            422,
            [{"field": "clienteId", "issue": "Deve ser um número inteiro"}]
        )

    try:
        pontos = int(pontos)
    except (TypeError, ValueError):
        return erro_response(
            "PONTOS_INVALIDOS",
            "Os pontos devem ser um número inteiro.",
            422,
            [{"field": "pontos", "issue": "Deve ser um número inteiro"}]
        )

    if pontos <= 0:
        return erro_response(
            "PONTOS_INVALIDOS",
            "Os pontos devem ser maiores que zero.",
            422,
            [{"field": "pontos", "issue": "Deve ser maior que zero"}]
        )

    cliente = Usuario.query.get(cliente_id)

    if not cliente:
        return erro_response(
            "CLIENTE_NAO_ENCONTRADO",
            "Cliente não encontrado.",
            404,
            [{"field": "clienteId", "issue": "Cliente inexistente"}]
        )

    if cliente.perfil.value != "CLIENTE":
        return erro_response(
            "PERFIL_INVALIDO",
            "Pontos de fidelidade só podem ser atribuídos a clientes.",
            422,
            [{"field": "perfil", "issue": "Usuário não possui perfil CLIENTE"}]
        )

    fidelidade = Fidelidade.query.filter_by(cliente_id=cliente_id).first()

    if not fidelidade or not fidelidade.consentimento_lgpd:
        return erro_response(
            "CONSENTIMENTO_NECESSARIO",
            "O cliente precisa registrar consentimento para participar do programa de fidelidade.",
            409,
            [{"field": "consentimentoLgpd", "issue": "Consentimento não registrado"}]
        )

    fidelidade.pontos += pontos

    db.session.commit()

    current_app.logger.info(
        f"Pontos adicionados: cliente={cliente_id}, "
        f"pontos={pontos}, total={fidelidade.pontos}"
    )

    return {
        "clienteId": cliente_id,
        "pontos": fidelidade.pontos,
        "consentimentoLgpd": fidelidade.consentimento_lgpd,
        "dataConsentimento": (
            fidelidade.data_consentimento.isoformat()
            if fidelidade.data_consentimento
            else None
        )
    }, 200


def resgatar_pontos_service(cliente_id, data, perfil):
    if perfil != "CLIENTE":
        return erro_response(
            "SEM_PERMISSAO",
            "Apenas clientes podem resgatar pontos de fidelidade.",
            403
        )

    pontos_resgate = data.get("pontos")

    if pontos_resgate is None:
        return erro_response(
            "PONTOS_OBRIGATORIOS",
            "Informe a quantidade de pontos.",
            422,
            [{"field": "pontos", "issue": "Campo obrigatório"}]
        )

    try:
        pontos_resgate = int(pontos_resgate)
    except (TypeError, ValueError):
        return erro_response(
            "PONTOS_INVALIDOS",
            "Os pontos devem ser um número inteiro.",
            422,
            [{"field": "pontos", "issue": "Deve ser um número inteiro"}]
        )

    if pontos_resgate <= 0:
        return erro_response(
            "PONTOS_INVALIDOS",
            "Os pontos devem ser maiores que zero.",
            422,
            [{"field": "pontos", "issue": "Deve ser maior que zero"}]
        )

    fidelidade = Fidelidade.query.filter_by(cliente_id=cliente_id).first()

    if not fidelidade or not fidelidade.consentimento_lgpd:
        return erro_response(
            "CONSENTIMENTO_NECESSARIO",
            "É necessário registrar consentimento antes de resgatar pontos de fidelidade.",
            409,
            [{"field": "consentimentoLgpd", "issue": "Consentimento não registrado"}]
        )

    if fidelidade.pontos < pontos_resgate:
        return erro_response(
            "PONTOS_INSUFICIENTES",
            "Saldo de pontos insuficiente.",
            409,
            [{"field": "pontos", "issue": f"Saldo disponível: {fidelidade.pontos}"}]
        )

    fidelidade.pontos -= pontos_resgate

    db.session.commit()

    current_app.logger.info(
        f"Pontos resgatados: cliente={cliente_id}, "
        f"pontos={pontos_resgate}, restante={fidelidade.pontos}"
    )

    return {
        "clienteId": cliente_id,
        "pontosRestantes": fidelidade.pontos,
        "consentimentoLgpd": fidelidade.consentimento_lgpd,
        "dataConsentimento": (
            fidelidade.data_consentimento.isoformat()
            if fidelidade.data_consentimento
            else None
        ),
        "message": "Pontos resgatados com sucesso."
    }, 200