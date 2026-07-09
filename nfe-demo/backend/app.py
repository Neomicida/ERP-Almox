import os
import shutil

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import Base, engine, SessionLocal
from models import NFe, ItemNFe, Produto, Estoque, Recebimento
from parser import ler_xml

# Cria as tabelas automaticamente
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Demo Importador NF-e")

# Permite acesso pelo frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.get("/")
def home():
    return {
        "status": "online",
        "mensagem": "API Importador NF-e funcionando"
    }


@app.post("/importar")
async def importar_xml(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".xml"):
        raise HTTPException(
            status_code=400,
            detail="Arquivo precisa ser XML"
        )

    caminho = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(caminho, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    dados = ler_xml(caminho)

    db: Session = SessionLocal()

    try:

        existe = db.query(NFe).filter(
            NFe.chave == dados["chave"]
        ).first()

        if existe:
            return {
                "mensagem": "NF já importada",
                "chave": existe.chave
            }

        nota = NFe(
            chave=dados["chave"],
            numero=dados["numero"],
            serie=dados["serie"],
            data_emissao=dados["data_emissao"],
            fornecedor=dados["fornecedor"],
            cnpj=dados["cnpj"],
            valor_total=dados["valor_total"],
            status="IMPORTADA"
        )

        db.add(nota)
        db.commit()
        db.refresh(nota)

        for produto in dados["itens"]:

            item = ItemNFe(
                nfe_id=nota.id,
                codigo=produto["codigo"],
                descricao=produto["descricao"],
                ncm=produto["ncm"],
                cfop=produto["cfop"],
                unidade=produto["unidade"],
                quantidade=produto["quantidade"],
                valor_unitario=produto["valor_unitario"],
                valor_total=produto["valor_total"]
            )

            db.add(item)

        db.commit()

        return {
            "mensagem": "NF importada com sucesso",
            "nota_id": nota.id,
            "chave": nota.chave,
            "produtos": len(dados["itens"])
        }

    finally:
        db.close()
@app.get("/nfe/{chave}")
def buscar_nfe(chave: str):

    db: Session = SessionLocal()

    try:

        nota = db.query(NFe).filter(
            NFe.chave == chave
        ).first()

        if not nota:
            raise HTTPException(
                status_code=404,
                detail="NF-e não encontrada"
            )

        return {
            "id": nota.id,
            "chave": nota.chave,
            "numero": nota.numero,
            "serie": nota.serie,
            "data_emissao": nota.data_emissao,
            "fornecedor": nota.fornecedor,
            "cnpj": nota.cnpj,
            "valor_total": nota.valor_total,
            "status": nota.status,
            "itens": [
                {
                    "codigo": item.codigo,
                    "descricao": item.descricao,
                    "quantidade": item.quantidade,
                    "valor_unitario": item.valor_unitario,
                    "valor_total": item.valor_total
                }
                for item in nota.itens
            ]
        }

    finally:
        db.close()
@app.post("/nfe/{chave}/lancar")
def lancar_nfe(chave: str):

    db: Session = SessionLocal()

    try:

        nota = db.query(NFe).filter(
            NFe.chave == chave
        ).first()


        if not nota:

            raise HTTPException(
                status_code=404,
                detail="NF-e não encontrada"
            )


        if nota.status == "RECEBIDA":

            return {
                "mensagem": "NF-e já foi recebida",
                "status": nota.status
            }


        for item in nota.itens:


            # Procura o produto pelo código
            produto = db.query(Produto).filter(
                Produto.codigo == item.codigo
            ).first()


            # Se não existe, cria
            if not produto:

                produto = Produto(

                    codigo=item.codigo,

                    descricao=item.descricao,

                    unidade=item.unidade

                )

                db.add(produto)

                db.commit()

                db.refresh(produto)



            # Procura estoque

            estoque = db.query(Estoque).filter(
                Estoque.produto_id == produto.id
            ).first()



            if not estoque:

                estoque = Estoque(

                    produto_id=produto.id,

                    quantidade=0

                )

                db.add(estoque)



            # Soma quantidade recebida

            estoque.quantidade += item.quantidade


            item.quantidade_recebida = item.quantidade



        # Atualiza status da NF

        nota.status = "RECEBIDA"



        # Histórico

        recebimento = Recebimento(

            nfe_id=nota.id,

            acao="Entrada de estoque realizada"

        )


        db.add(recebimento)


        db.commit()



        return {

            "mensagem": "NF lançada e estoque atualizado",

            "nota": nota.numero,

            "produtos_processados": len(nota.itens),

            "status": nota.status

        }


    finally:

        db.close()