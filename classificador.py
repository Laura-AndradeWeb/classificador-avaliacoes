import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
import time

load_dotenv() #lê o arquivo .env para ter acesso a chave do Gemini

MODELO = "gemini-3.8-flash"
client = genai.Client() #cria conexão com o Gemini

INSTRUCAO = (
    "Você classifica avaliações de clientes de restaurante de delivery. "
    "Responda apenas com JSON neste formato: "
    '{"Sentimento": "positivo" | "negativo" | "misto", '
    '"Tema": "comida" | "entrega" | "atendimento" | "preço" | "outro", '
    '"Resumo": "uma frase curta"}'
) #é o system prompt

def classificar(texto):
    for tentativa in range(3):
        try:
            resposta = client.models.generate_content(
                    model=MODELO,
                    contents=texto, #é a avaliação (prompt do usuário)
                    config=types.GenerateContentConfig(
                        system_instruction=INSTRUCAO,
                        temperature=0, #deixa a resposta mais previsível possível, bom para classificação
                        response_mime_type="application/json", #pede pro Gemini que devolva em JSON válido
                    ),
            )
            dados = json.loads(resposta.text)
            dados = {chave.lower(): valor for chave, valor in dados.items()}

            for chave in ["Sentimento", "Tema", "Resumo"]:
                if chave not in dados:
                    raise ValueError(f"campo ausente: {chave}")

            return dados
        except Exception as erro:
            print(f"Tentantiva {tentativa + 1} falhou: {erro}")
            time.sleep(5)
    return None
    
    return json.loads(resposta.text) #transforma o texto em um dicionário python

avaliacao = "Gostei muito do sabor, mas o pedido demorou muito pra chegar."
resultado = classificar(avaliacao)
print(resultado)
print(resultado["Sentimento"])