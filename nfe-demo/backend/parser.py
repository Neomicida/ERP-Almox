import xml.etree.ElementTree as ET


NS = {
    "nfe": "http://www.portalfiscal.inf.br/nfe"
}


def texto(elemento):
    """
    Retorna o texto do elemento ou string vazia.
    """
    if elemento is None:
        return ""

    return elemento.text.strip() if elemento.text else ""


def ler_xml(caminho_arquivo):
    tree = ET.parse(caminho_arquivo)
    root = tree.getroot()

    inf_nfe = root.find(".//nfe:infNFe", NS)

    emit = root.find(".//nfe:emit", NS)

    ide = root.find(".//nfe:ide", NS)

    total = root.find(".//nfe:ICMSTot", NS)

    dados = {
        "chave": "",
        "numero": "",
        "serie": "",
        "data_emissao": "",
        "fornecedor": "",
        "cnpj": "",
        "valor_total": 0,
        "itens": []
    }

    # Chave de acesso
    if inf_nfe is not None:
        chave = inf_nfe.attrib.get("Id", "")
        dados["chave"] = chave.replace("NFe", "")

    # Dados da nota
    dados["numero"] = texto(ide.find("nfe:nNF", NS))
    dados["serie"] = texto(ide.find("nfe:serie", NS))
    dados["data_emissao"] = texto(ide.find("nfe:dhEmi", NS))

    # Emitente
    dados["fornecedor"] = texto(emit.find("nfe:xNome", NS))
    dados["cnpj"] = texto(emit.find("nfe:CNPJ", NS))

    # Total
    valor = texto(total.find("nfe:vNF", NS))

    if valor:
        dados["valor_total"] = float(valor)

    # Produtos
    for det in root.findall(".//nfe:det", NS):

        prod = det.find("nfe:prod", NS)

        item = {

            "codigo": texto(prod.find("nfe:cProd", NS)),

            "descricao": texto(prod.find("nfe:xProd", NS)),

            "ncm": texto(prod.find("nfe:NCM", NS)),

            "cfop": texto(prod.find("nfe:CFOP", NS)),

            "unidade": texto(prod.find("nfe:uCom", NS)),

            "quantidade": float(
                texto(prod.find("nfe:qCom", NS)) or 0
            ),

            "valor_unitario": float(
                texto(prod.find("nfe:vUnCom", NS)) or 0
            ),

            "valor_total": float(
                texto(prod.find("nfe:vProd", NS)) or 0
            )

        }

        dados["itens"].append(item)

    return dados