from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


class NFe(Base):
    __tablename__ = "nfe"

    id = Column(Integer, primary_key=True, index=True)

    chave = Column(String(44), unique=True, nullable=False, index=True)

    numero = Column(String(20))
    serie = Column(String(10))
    data_emissao = Column(String(30))

    fornecedor = Column(String(255))
    cnpj = Column(String(20))

    valor_total = Column(Float)

    status = Column(
        String(30),
        default="PENDENTE_RECEBIMENTO"
    )

    data_importacao = Column(
        DateTime,
        default=datetime.utcnow
    )


    itens = relationship(
        "ItemNFe",
        back_populates="nota",
        cascade="all, delete-orphan"
    )


    recebimentos = relationship(
        "Recebimento",
        back_populates="nota"
    )



class ItemNFe(Base):

    __tablename__ = "itens_nfe"


    id = Column(Integer, primary_key=True)


    nfe_id = Column(
        Integer,
        ForeignKey("nfe.id")
    )


    codigo = Column(String(60))

    descricao = Column(String(255))

    ncm = Column(String(20))

    cfop = Column(String(10))

    unidade = Column(String(10))

    quantidade = Column(Float)

    quantidade_recebida = Column(
        Float,
        default=0
    )


    valor_unitario = Column(Float)

    valor_total = Column(Float)



    nota = relationship(
        "NFe",
        back_populates="itens"
    )



class Produto(Base):

    __tablename__ = "produtos"


    id = Column(
        Integer,
        primary_key=True
    )


    codigo = Column(
        String(60),
        unique=True
    )


    descricao = Column(String(255))


    unidade = Column(String(10))


    estoque = relationship(
        "Estoque",
        back_populates="produto"
    )



class Estoque(Base):

    __tablename__ = "estoque"


    id = Column(
        Integer,
        primary_key=True
    )


    produto_id = Column(
        Integer,
        ForeignKey("produtos.id")
    )


    quantidade = Column(
        Float,
        default=0
    )


    atualizado_em = Column(
        DateTime,
        default=datetime.utcnow
    )


    produto = relationship(
        "Produto",
        back_populates="estoque"
    )



class Recebimento(Base):

    __tablename__ = "recebimentos"


    id = Column(
        Integer,
        primary_key=True
    )


    nfe_id = Column(
        Integer,
        ForeignKey("nfe.id")
    )


    data = Column(
        DateTime,
        default=datetime.utcnow
    )


    acao = Column(
        String(100)
    )


    nota = relationship(
        "NFe",
        back_populates="recebimentos"
    )