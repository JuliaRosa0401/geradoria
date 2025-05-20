from flask import Flask, jsonify, request
from flask_cors import CORS
from google import genai
import os
import re
import json
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

# Configuração da API Key do Gemini
API_KEY = os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=API_KEY)

# Função para gerar a receita com base nos ingredientes
def criar_receita(ingredientes):
    try:
        # Cria o prompt para a API Gemini
        prompt = f"""
             Crie 2 recomendações de filmes  e 2 de livros  com base nos seguintes temas: {ingredientes}. Deve ser reais e existir 

            Apresente a resposta em **HTML com codificação UTF-8**, sem incluir <html>, <head> ou <body>. Use **Tailwind CSS** para o estilo.

            O layout deve ser dividido em duas seções:
            1. 🎬 **Filmes** (título: "Filmaços")
            2. 📚 **Livros** (título: "Vire a página")

            Cada recomendação deve ser exibida como um **card colorido, animado e moderno**, contendo:

            - Título grande e negrito com <h1> Na cor branca e em destaque, chama atenção
            - Badge de nota no canto superior direito (ex: ⭐ 8.6), em amarelo com texto escuro e moderno
            - Autor (livros) ou Diretor (filmes) com esse ícone 👤 e ano com esse ícone 📅 (letras brancas)
            - Sinopse envolvente em parágrafo curto 
            - Faixa etária com apenas esse ícone e legenda com cor de letra branca:
            - 🟩 Livre
            - 🟨 (para 12 até 14 anos)
            - 🟥 (para 16 até 18 anos)
            - Se houver temas sensíveis, adicione o ícone ⚠ seguido de um alerta breve, curto e em cor de letras branca. Ex: ⚠ Uso de drogas.
            - Tags temáticas como bolhas coloridas (ex: sci-fi, romance), com bordas arredondadas e fundo vibrante
            

            ### Design:

            - Fundo roxo escuro (#3b0764 ou similar)
            - Nos livos quero os generos com a cor azul e nos filmesquero o genero com a cor amarela 
            - Cantos arredondados grandes (rounded-xl)
            - Tipografia legível e expressiva
            - Organização em **grid responsivo**, com os cards lado a lado
            - Separação visual clara entre filmes e livros (ex: margem, linha ou título destacado)
            - Fundo dos cards na cor roxa mais clara

            

            Não inclua scripts. Gere apenas o conteúdo HTML formatado com os elementos descritos. Não inclua html nem aspas. deve usar os icones indicados 
        """
        
        # Envia o prompt para a API Gemini para gerar o conteúdo
        resposta = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=prompt
        )

        # Resposta esperada da API Gemini no formato HTML
        texto_bruto = resposta.text.strip()

        html_limpo = re.sub(r"^```html\s*([\s\S]+?)\s*```$", r"\1", texto_bruto)

        # Retorna o HTML gerado diretamente
        return html_limpo, 200

    except Exception as e:
        # Em caso de erro, retornamos o erro
        return jsonify({"Erro": str(e)}), 500

# Rota da API para gerar a receita
@app.route('/receita', methods=['POST'])
def make_receita():
    try:
        # Obtém os dados JSON da requisição
        dados = request.get_json()

        # Valida se a requisição contém um JSON válido
        if not dados or not isinstance(dados, dict):
            return jsonify({'error': 'Requisição JSON inválida. Esperava um dicionário.'}), 400

        # Obtém a lista de ingredientes do JSON
        ingredientes = dados.get('ingredientes')

        # Valida se o campo "ingredientes" é uma lista
        if not isinstance(ingredientes, list):
            return jsonify({'error': 'O campo "ingredientes" deve ser uma lista.'}), 400

        # Valida se a lista de ingredientes contém pelo menos 3 ingredientes
        if len(ingredientes) < 3:
            return jsonify({'error': 'São necessários pelo menos 3 ingredientes.'}), 400

        # Chama a função para gerar a receita com os ingredientes
        receita = criar_receita(ingredientes)

        # Retorna o HTML gerado pela função `criar_receita`
        return receita

    except Exception as e:
        # Se ocorrer algum erro durante o processo, retorna um erro 500
        print(f"Erro interno: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
