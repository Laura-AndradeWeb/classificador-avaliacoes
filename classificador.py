import json #transforma o texto JSON em um dicionário Python (json.loads)
from dotenv import load_dotenv #lê o arquivo .env para ter acesso a chave
from google import genai #biblioteca do Gemini
from google.genai import types #traz classes de configuração (GenerateContentConfig)
import time #usado para fazer pausas
import sqlite3 #biblioteca do sqlite
from datetime import datetime #biblioteca para pegar o horário

load_dotenv() #lê o arquivo .env para ter acesso a chave do Gemini

MODELO = "gemini-3.1-flash-lite"
client = genai.Client() #cria conexão com o Gemini e procura a chave no código

INSTRUCAO = (
    "Você classifica avaliações de clientes de restaurante de delivery. "
    "Responda apenas com JSON neste formato: "
    '{"Sentimento": "positivo" | "negativo" | "misto", '
    '"Tema": "comida" | "entrega" | "atendimento" | "preço" | "outro", '
    '"Resumo": "uma frase curta"}'
) #é o system prompt

#função que recebe um texto de avalição como parâmetro e devolve o resultado 
def classificar(texto):
    for tentativa in range(3):
        try:
            #envia o prompt pro Gemini e gera o conteúdo requerido
            resposta = client.models.generate_content(
                    model=MODELO,
                    contents=texto, #é a avaliação (prompt do usuário)
                    config=types.GenerateContentConfig( #configurações das respostas
                        system_instruction=INSTRUCAO,
                        temperature=0, #deixa a resposta mais previsível possível, bom para classificação
                        response_mime_type="application/json", #pede pro Gemini que devolva em JSON válido
                    ),
            )
            dados = json.loads(resposta.text) #dados recebe o que a IA gerou em formato de dicinário Python JSON

            #confere se os campos exitem, se algum faltar ele mostra um erro e executa mais uma tentativa
            for chave in ["Sentimento", "Tema", "Resumo"]:
                if chave not in dados:
                    raise ValueError(f"campo ausente: {chave}")

            return dados #se tudo der certo ele retorna o dicionário

        #se algo não der certo ele mostra o erro e a tentativa, caso seja possivel faz outra tentativa de novo depois de 5 segundos
        except Exception as erro:
            print(f"Tentantiva {tentativa + 1} falhou: {erro}")
            time.sleep(5)
    return None #caso der erro ele retorna vazio

def conectar():
    conn = sqlite3.connect("avaliacoes.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS avaliacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            texto TEXT UNIQUE,
            sentimento TEXT,
            tema TEXT,
            resumo TEXT,
            criado_em TEXT
        )
    """)
    conn.commit()
    return conn

def ja_classificada(conn, texto):
    linha = conn.execute(
        "SELECT 1 FROM avaliacoes WHERE texto = ?", (texto,)
    ).fetchone()
    return linha is not None

def salvar(conn, texto, resultado):
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        "INSERT INTO avaliacoes (texto, sentimento, tema, resumo, criado_em) "
        "VALUES (?, ?, ?, ?, ?)",
        (texto, resultado["Sentimento"], resultado["Tema"], resultado["Resumo"], agora)
    )
    conn.commit()


#lista com os textos de avaliações
avaliacoes = [
    "Estava tudo uma delícia, comprarei novamente.",
    "Entrega demorada e comida chegou fria.",
    "Gostei muito do sabor, mas o pedido demorou muito pra chegar.",
    "Uma delícia!",
    "Me surpreendeu, vou pedir novamente!",
    "Entrega rápida e preço justo, ganharam mais um cliente.",
    "Estava um pouco salgado, mas deu pra comer.",
    "Que tempero maravilhoso, já não vejo a hora de comprar novamente!",
    "Amei!",
    "Demorou demais e a comida chegou fria, mas estava gostosa.",
    "Poderiam mandar as bebidas numa embalagem separada, mas de resto estava tudo okay."
]

conn = conectar()
novas = 0

for texto in avaliacoes:
    if ja_classificada(conn, texto):
        print(f"Já classificada, pulando: {texto[:50]}...")
        continue

    print(f"Classificando: {texto[:50]}...")
    resultado = classificar(texto)

    if resultado is None:
        print(" Não consegui classificar, pulando para próxima avaliação")
        continue

    salvar(conn, texto, resultado)
    novas =+ 1
    print(f" {resultado['Sentimento']} | {resultado['Tema']}")
    time.sleep(2)

print(f"\n{novas} avaliações novas salvas.")

print("\nReclamações por tema: ")
cursor = conn.execute("""
        SELECT tema, COUNT(*) AS total
        FROM avaliacoes
        WHERE sentimento = 'negativo'
        GROUP BY tema
        ORDER BY total DESC
""")
for tema, total in cursor.fetchall():
    print(f" {tema}: {total}")

conn.close()