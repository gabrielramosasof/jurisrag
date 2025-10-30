# JURISRAG

Um sistema RAG (Retrieval-Augmented Generation) para conhecimentos jurídicos brasileiros, alimentado inicialmente pelos documentos do Drive do Belisário.

## Descrição

O JURISRAG utiliza técnicas de IA para responder perguntas sobre legislação brasileira, combinando recuperação de documentos relevantes com geração de respostas contextuais.

## Funcionalidades

- Carregamento e processamento de documentos legais (.docx)
- Indexação vetorial usando embeddings OpenAI
- Consultas interativas via interface de linha de comando
- Suporte a múltiplos tipos de legislação (civil, penal, administrativo, etc.)

## Instalação

1. Clone o repositório:
   ```bash
   git clone <url>
   cd jurisrag
   ```

2. Crie um ambiente virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou venv\Scripts\activate no Windows
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure a chave da API OpenAI no arquivo `.env`:
   - Abra o arquivo `.env` em um editor de texto
   - Substitua `your_openai_api_key_here` pela sua chave real da OpenAI
   - Obtenha sua chave em: https://platform.openai.com/api-keys

   Exemplo:
   ```bash
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

   **IMPORTANTE**: Nunca compartilhe ou faça commit da sua chave API!

## Uso

### Passo 1: Carregamento dos Documentos

Execute o script de carregamento para processar e indexar os documentos:

```bash
python load.py
```

Este comando irá:
1. Validar a configuração da API OpenAI
2. Verificar se o diretório de dados existe (aproximadamente 1,100 arquivos .docx)
3. Carregar todos os arquivos .docx do diretório especificado
4. Dividir os documentos em chunks (pedaços menores de texto)
5. Gerar embeddings usando OpenAI (isso consome créditos da API)
6. Criar e salvar o índice vetorial FAISS no diretório `vectorstore/`

**IMPORTANTE**: Este processo pode levar vários minutos e consumirá créditos da sua conta OpenAI. Você verá mensagens de progresso durante a execução.

**Saída esperada**:
```
======================================================================
JURISRAG - Document Loading and Embedding Pipeline
======================================================================
Validating environment...
OpenAI API key found
Loading documents from: /Users/gabrielramos/Downloads/DRIVE_DO_BELISARIO
Found 1100 .docx files
...
SUCCESS! Vectorstore created and saved successfully
======================================================================
```

### Passo 2: Consultas Interativas

Depois que o vectorstore for criado com sucesso, inicie o modo interativo:

```bash
python main.py
```

O sistema irá:
1. Carregar o vectorstore existente do disco (muito mais rápido que recriar)
2. Inicializar o modelo de linguagem GPT-3.5-turbo
3. Iniciar uma interface interativa para perguntas e respostas

**Exemplo de uso**:
```
======================================================================
JURISRAG - Sistema de Perguntas e Respostas Jurídicas
======================================================================

Instruções:
• Digite sua pergunta sobre legislação brasileira
• Digite 'sair' para encerrar o programa
• Digite 'limpar' para limpar a tela

Pergunta: O que diz o Código Civil sobre incapacidade?

Processando sua pergunta...

Resposta:
----------------------------------------------------------------------
[Resposta gerada baseada nos documentos mais relevantes]
----------------------------------------------------------------------

Baseado em 5 documentos relevantes
```

**Comandos disponíveis**:
- Digite sua pergunta normalmente
- `sair`, `exit`, ou `quit` para encerrar
- `limpar`, `clear`, ou `cls` para limpar a tela

## Estrutura do Projeto

```
jurisrag/
├── data/                    # Diretório para dados de exemplo
├── vectorstore/             # Índice vetorial salvo
├── venv/                    # Ambiente virtual
├── load.py                  # Script de carregamento e indexação
├── main.py                  # Interface principal
├── requirements.txt         # Dependências
├── .env                     # Configurações (chave API)
├── .gitignore               # Arquivos ignorados pelo Git
└── README.md                # Esta documentação
```

## Troubleshooting

### Erro: "OpenAI API key not configured"
- Verifique se você editou o arquivo `.env` e substituiu `your_openai_api_key_here` pela sua chave real
- Certifique-se de que não há espaços extras ao redor do valor da chave
- Obtenha uma nova chave em https://platform.openai.com/api-keys

### Erro: "Directory not found"
- O código está configurado para ler de `/Users/gabrielramos/Downloads/DRIVE_DO_BELISARIO`
- Verifique se este diretório existe e contém os arquivos .docx
- Para usar outro diretório, edite a variável `data_dir` em `load.py` e `main.py`

### Erro: "No .docx files found"
- Verifique se há arquivos .docx no diretório especificado
- Use o comando: `find /Users/gabrielramos/Downloads/DRIVE_DO_BELISARIO -name "*.docx" | wc -l`

### Erro: "Insufficient API credits" ou erros da OpenAI
- Verifique seu saldo de créditos em https://platform.openai.com/account/usage
- Os embeddings para ~1,100 documentos podem custar alguns dólares
- Considere processar menos documentos para testar primeiro

### Erro: "Vectorstore not found" ao executar main.py
- Você precisa executar `python load.py` primeiro
- Este script cria o diretório `vectorstore/` com os índices

### O processo é muito lento
- É normal! Processar 1,100 documentos pode levar 10-30 minutos
- O tempo depende do tamanho dos documentos e da velocidade da API OpenAI
- Você verá mensagens de progresso durante a execução

## Dependências

- **langchain** (>=0.1.0): Framework para aplicações LLM
- **langchain-community** (>=0.0.20): Extensões da comunidade LangChain
- **langchain-openai** (>=0.0.5): Integração com OpenAI
- **langchain-text-splitters** (>=0.0.1): Divisores de texto
- **openai** (>=1.12.0): Cliente oficial da API OpenAI
- **faiss-cpu** (>=1.7.4): Biblioteca de busca vetorial de alta performance
- **docx2txt** (>=0.8): Extração de texto de arquivos .docx
- **python-dotenv** (>=1.0.0): Gerenciamento de variáveis de ambiente
- **tqdm** (>=4.66.0): Barras de progresso

## Dados

Os documentos legais são carregados do diretório `/Users/gabrielramos/Downloads/DRIVE_DO_BELISARIO`, que contém legislações organizadas por categoria.

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto é distribuído sob a licença MIT.