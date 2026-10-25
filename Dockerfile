# Utiliza uma imagem leve e oficial do Python 3.11 slim
FROM python:3.11-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos de dependências para o container
COPY requirements.txt .

# Instala as dependências de teste e execução
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o restante do código do projeto para o container
COPY . .

# Define a variável de ambiente para o python reconhecer os módulos (src)
ENV PYTHONPATH="."

# Comando padrão executado ao rodar o container (roda a suíte pytest)
CMD ["pytest", "-v"]