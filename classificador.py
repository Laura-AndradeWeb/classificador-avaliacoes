import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv() #lê o arquivo .env para ter acesso a chave do Gemini

MODELO = "gemini-3.8-flash"
client = genai.Client() #cria conexão com o Gemini

INSTRUCAO = (
    "Você classifica avaliações de clientes de restaurante de delivery. "
    "Responda apenas com JSON neste formato: "
    '{"Sentimento": "positivo" | "negativo" | "misto", '
    '"tema": "comida" | "entrega" | "atendimento" | "preço" | "outro", '
    '"resumo": "uma frase curta"}'
) #é o system prompt

def classificar(texto):
    resposta = client.models.generate_content(
        model=MODELO,
        contents=texto, #é a avaliação (prompt do usuário)
        config=types.GenerateContentConfig(
            system_instruction=INSTRUCAO,
            temperature=0, #deixa a resposta mais previsível possível, bom para classificação
            response_mime_type="application/json", #pede pro Gemini que devolva em JSON válido
        ),
    )
    return json.loads(resposta.text) #transforma o texto em um dicionário python

avaliacao = "Gostei muito do sabor, mas o pedido demorou muito pra chegar."
resultado = classificar(avaliacao)
print(resultado)
print(resultado["sentimento"])