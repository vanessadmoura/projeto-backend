import bcrypt

from run import app
from app import db
from app.models.usuario import Usuario, Perfil


def gerar_hash_senha(senha):
    return bcrypt.hashpw(
        senha.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def criar_usuario(nome, email, senha, perfil):
    usuario_existente = Usuario.query.filter_by(email=email).first()

    if usuario_existente:
        print(f"Usuário {email} já existe.")
        return

    usuario = Usuario(
        nome=nome,
        email=email,
        senha=gerar_hash_senha(senha),
        perfil=perfil
    )

    db.session.add(usuario)
    db.session.commit()

    print(f"Usuário {email} criado com sucesso.")


def criar_usuarios_teste():
    with app.app_context():
        criar_usuario(
            nome="Gerente Teste",
            email="gerente@email.com",
            senha="123456",
            perfil=Perfil.GERENTE
        )

        criar_usuario(
            nome="Cliente Teste",
            email="cliente@email.com",
            senha="123456",
            perfil=Perfil.CLIENTE
        )

        criar_usuario(
            nome="Atendente Teste",
            email="atendente@email.com",
            senha="123456",
            perfil=Perfil.ATENDENTE
        )

        criar_usuario(
            nome="Cozinha Teste",
            email="cozinha@email.com",
            senha="123456",
            perfil=Perfil.COZINHA
        )


if __name__ == "__main__":
    criar_usuarios_teste()