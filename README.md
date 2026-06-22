# Fiscal do UNO (RAG)

Este projeto é um assistente inteligente baseado em RAG (Retrieval-Augmented Generation) para responder perguntas sobre as regras oficiais do jogo de cartas **UNO**, utilizando o PDF oficial `uno.pdf` como única fonte da verdade.

## Tecnologias Utilizadas

* **Python**
* **Streamlit** (Interface Web altamente personalizada)
* **LangChain** (Orquestração do RAG)
* **FAISS** (Banco de Vetores)
* **Google Gemini** (Geração da Resposta com Fallbacks)
* **PyPDF** (Extração de texto do PDF)
* **Sentence-Transformers** (Embeddings Locais para busca semântica)

## Estrutura do Projeto

```text
project/
├── app.py              # Interface Streamlit temática do UNO
├── rag.py              # Lógica de processamento RAG, tradução, indexação e busca
├── config.py           # Configurações globais e leitura de ambiente
├── requirements.txt    # Lista de dependências do Python
├── README.md           # Documentação do projeto
├── PRD.md              # Requisitos do Produto (UNO)
├── SPEC.md             # Especificação Técnica (UNO)
├── .env                # Variáveis de ambiente (API Key)
├── pdf/
│   └── uno.pdf         # Documento de regras oficial do UNO
├── data/
│   └── faiss_index_uno/# Índice do FAISS gerado localmente
└── assets/             # Arquivos de mídia adicionais
```

## Como Executar o Projeto

1. Certifique-se de ter o Python instalado (recomendado v3.9+).
2. Instale todas as dependências rodando:
   ```bash
   pip install -r requirements.txt
   ```
3. Crie e configure o arquivo `.env` na raiz do projeto contendo a sua chave da API do Google:
   ```env
   GOOGLE_API_KEY=sua_chave_aqui
   ```
4. Execute a aplicação com:
   ```bash
   streamlit run app.py
   ```

## Funcionamento do RAG

1. **Geração do Índice**: Ao iniciar, a aplicação detecta se existe o índice vetorial na pasta `data/faiss_index_uno`. Caso não exista, lê o arquivo `pdf/uno.pdf` (em português), extrai o texto, divide-o em chunks de `1000` caracteres e gera os embeddings usando o modelo `all-MiniLM-L6-v2`.
2. **Expansão da Query em Português**: O sistema realiza uma expansão rápida da dúvida em português com sinônimos locais de regras de UNO (como mapear "+4" para "Coringa Comprar Quatro") para maximizar a precisão da busca.
3. **Busca Semântica**: O sistema busca os `7` trechos mais relevantes no banco FAISS baseados na query em português expandida.
4. **Prompt de Segurança**: Os trechos são fornecidos ao Gemini juntamente com regras rígidas que o impedem de usar conhecimento prévio externo ou inventar mecânicas. Se a dúvida estiver fora do escopo, ele responderá exatamente: *"Desculpe, nao encontrei essa regra no manual oficial"*.
5. **Geração com Fallback**: O processamento faz uso de múltiplos modelos do Gemini (`gemini-2.0-flash-lite`, `gemini-2.5-flash-lite`, `gemini-2.0-flash` e `gemini-2.5-flash`) de forma sequencial para contornar limites de cota e falhas na API.
