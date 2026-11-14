import json #transforma o texto JSON em um dicionário Python (json.loads)
from dotenv import load_dotenv #lê o arquivo .env para ter acesso a chave
from google import genai #biblioteca do Gemini
from google.genai import types #traz classes de configuração (GenerateContentConfig)
import time #usado para fazer pausas

load_dotenv() #lê o arquivo .env para ter acesso a chave do Gemini

MODELO = "gemini-3.8-flash"
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

#lista vazia para armazenar os resultados
resultados = []

#repete para cada avaliação
for texto in avaliacoes:
    print(f"Classificando {texto[:50]}...") #mostra os primeiros 50 caracteres da avaliação que está classificando 
    resultado = classificar(texto) #reusltado recebe o que a função 'classificar' retornar de acordo com o texto(avaliação)

    #caso der erro nas três tentativas ele pula para próxima avaliação
    if resultado is None:
        print( "Não consegui classificar, pulando para próxima avaliação...")
        continue

    
    resultado["Texto"] = texto #coloca no código uma nova chave chamada Texto que armazena a avaliação abixo da resposta da mesma
    resultados.append(resultado) #acrescenta o dicionário 'resultado' na lista de dicionário 'resultados'
    print(f" {resultado['Sentimento']} | {resultado["Tema"]}")
    time.sleep(2)

#mostra a quantidade de avaliações classificadas
print(f"\n{len(resultados)} de {len(avaliacoes)} avaliações classificadas.")