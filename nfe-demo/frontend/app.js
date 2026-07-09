// Endereço da API
const API_URL = "http://127.0.0.1:8000";


// ================================
// IMPORTAR XML
// ================================

async function importarXML() {

    const arquivo = document
        .getElementById("xmlFile")
        .files[0];


    const resultado =
        document.getElementById("resultadoImportacao");


    if (!arquivo) {

        resultado.innerHTML =
            "Selecione um arquivo XML.";

        resultado.className = "erro";

        return;
    }


    const formData = new FormData();

    formData.append(
        "file",
        arquivo
    );


    try {


        const resposta = await fetch(
            `${API_URL}/importar`,
            {
                method: "POST",
                body: formData
            }
        );


        const dados = await resposta.json();


        if (resposta.ok) {


            resultado.innerHTML =
                `
                ✅ ${dados.mensagem}<br>
                Chave: ${dados.chave}<br>
                Produtos: ${dados.produtos}
                `;


            resultado.className = "sucesso";


        } else {


            resultado.innerHTML =
                "Erro: " + dados.detail;

            resultado.className = "erro";

        }


    } catch (erro) {


        resultado.innerHTML =
            "Erro de conexão com a API";


        resultado.className = "erro";

        console.error(erro);

    }

}



// ================================
// BUSCAR NF-E PELA CHAVE
// ================================

async function buscarNFe() {


    const chave =
        document
        .getElementById("chaveNF")
        .value
        .replace(/\D/g, "");


    const area =
        document.getElementById("dadosNota");


    if (!chave) {

        area.innerHTML =
            "Informe a chave da NF-e.";

        return;
    }


    try {


        const resposta = await fetch(
            `${API_URL}/nfe/${chave}`
        );


        const nota =
            await resposta.json();



        if (!resposta.ok) {


            area.innerHTML =
                `
                <div class="erro">
                ❌ ${nota.detail}
                </div>
                `;


            return;

        }



        let produtos = "";


        nota.itens.forEach(item => {


            produtos +=
            `
            <div class="produto">

                <b>${item.descricao}</b><br>

                Código:
                ${item.codigo}<br>

                Quantidade:
                ${item.quantidade}<br>

                Valor:
                R$ ${item.valor_total}

            </div>
            `;


        });



        area.innerHTML =

        `
        <div class="nota">

            <h3>
            ✅ NF encontrada
            </h3>


            <p>
            <b>Fornecedor:</b>
            ${nota.fornecedor}
            </p>


            <p>
            <b>CNPJ:</b>
            ${nota.cnpj}
            </p>


            <p>
            <b>Número:</b>
            ${nota.numero}
            </p>


            <p>
            <b>Valor:</b>
            R$ ${nota.valor_total}
            </p>


            <h3>
            Produtos
            </h3>


            ${produtos}


            <br>

            <button onclick="lancarNF('${nota.chave}')">

                Lançar no ERP

            </button>


        </div>
        `;


    } catch(error) {


        area.innerHTML =
        `
        <div class="erro">
        Erro ao consultar nota.
        </div>
        `;


        console.error(error);

    }

}



// ================================
// LANÇAR NF
// ================================

async function lancarNF(chave) {


    const resposta = await fetch(

        `${API_URL}/nfe/${chave}/lancar`,

        {
            method: "POST"
        }

    );


    const dados =
        await resposta.json();



    alert(
        dados.mensagem
    );


}
// ================================
// LEITURA AUTOMÁTICA DO LEITOR
// ================================

document
.getElementById("chaveNF")
.addEventListener(
    "keydown",
    function(event) {

        if (event.key === "Enter") {

            event.preventDefault();

            buscarNFe();

        }

    }
);