from dotenv import load_dotenv
from google import genai
import time

load_dotenv() #lê o arquivos .env e pode utilizar a chave disponível para o programa

MODELO = "gemini-3.8-flash"

client = genai.Client() #cria conexão com o Gemini

prompt = (
    "O Dólar está em R$ 5,46 e ontem fechou em R$ 5,40. "
    "Escreva uma frase curta, em português, dizendo se subiu ou caiu."
)

for tentativa in range(3):
    try:
        resposta = client.models.generate_content(model=MODELO, contents=prompt)
        print(resposta.text)
        break
    except Exception as erro:
        print(f"Tentativa {tentativa + 1} falhou: {erro}")
        time.sleep(5) #espera 5 segundos antes da próxima tentativa
else: 
    print("Não consegui após 3 tentativas.")