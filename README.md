
<h1 align="center">
  Api Backend Projeto Start+ Cyber - Plataforma Osint
</h1>

<p align="center">
 <a href="https://www.linkedin.com/in/rodrigofelixf/" target="_blank">
    <img src="https://img.shields.io/static/v1?label=Linkedin&message=@rodrigofelixf&color=8257E5&labelColor=000000" alt="@rodrigofelixf" />
</a>
 <img src="https://img.shields.io/static/v1?label=Tipo&message=Hackathon&color=8257E5&labelColor=000000" alt="Hackathon" />
</p>

# API de Informações de Dados Vazados - OSINT

Esta API foi desenvolvida para suportar a plataforma OSINT, permitindo aos usuários verificar se seus dados pessoais, especialmente e-mails, foram expostos em vazamentos de dados. Além disso, a API oferece funcionalidades para notificação automatizada de novos vazamentos relacionados aos dados cadastrados.

## Funcionalidades

### Verificação de dados vazados
O usuário, ao se cadastrar na plataforma, pode consultar se seu e-mail foi exposto em algum vazamento, recebendo informações detalhadas, como:  
- **Local do vazamento.**  
- **Data do vazamento.**  
- **Motivo do vazamento.**  
- **Dados que foram expostos.**  

### Notificações automatizadas de vazamentos
- O usuário pode ativar notificações para ser informado por e-mail sobre novos vazamentos relacionados aos seus dados cadastrados.  
- As notificações são enviadas automaticamente, garantindo que o usuário esteja sempre atualizado em relação à segurança de suas informações.  


Referência do projeto: [Have i been pwned?](https://haveibeenpwned.com/).

## Tecnologias
 
- [Python](https://www.python.org/)
- [Pycharm](https://www.jetbrains.com/pt-br/pycharm/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Swagger](https://swagger.io/docs/)
- [Docker](https://docs.docker.com/get-started/get-docker/)
- [PostgreSql](https://www.postgresql.org/download/)
- [Redis Db](https://redis.io/docs/latest/)


## Práticas adotadas

- API RESTful
- Autenticação e Autorização
- Cacheamento com Redis + FastApi
- Conceitos do SOLID
- Respostas padronizadas (Responses)
- Geração automática de documentação com Swagger

# Como Executar

- Clonar repositório git
- Navegar ate o projeto:
```bash
$ cd backend-osint
```

### 1- Instalar e Ativar Ativar o ambiente de desenvolvimento:

```bash
#Instalar ambiente de desenvolvimento
$ python3 -m venv venv

#O Python tem que ser corretamente instalado. 
#Em ambiente Windows baixar a ultima versão (preferencialmente a 3.12 do Python pelo Microsfot Store
```

```bash
#Ativar ambiente de deesnvolvimento: 

#Linux
$ source venv/bin/activate 

#Windows
$ venv\bin\activate

## Deve aparecer (venv) ou com a nomeclatura escolhida, no inicio do terminal.
## Em algumas configurações de interpretadores a ativação pode ficar com o Scripts no meio: venv\Scripts\activate  
```

### 2 - Instalar as Dependências


 O projeto possui um arquivo requirements.txt com todas as dependências necessárias. Para instalar, execute o seguinte comando no terminal da raíz do projeto:
```bash
$ pip install -r requirements.txt
```

Isso instalará todas as bibliotecas necessárias, como FastAPI, scikit-learn, joblib, entre outras.
obs: Pode haver algumas inconsistências na instalação da dependência do psycopg2/psycopg2-binary. Recomendo verificar o interpretador
que está usando ou a versão do python. 


### 3 - Subir o banco de dados via Docker
O projeto vai subir via container no docker. Então é preciso instalar o docker nos links de cima.
Ambiente Windows precisa instalar o Docker e o WSL2 (que ja vem dentro do instalador do docker) - Logar a conta e deixar o docker-desktop aberto
para poder a aplicacao se conectar ao container  do banco de dados. 

Subir o banco via docker-compose.yml abrindo o terminal na raíz do projeto onde se encontra o arquivo: 

```bash
$ docker-compose up --build
```

Ao subir, verifique se esta rodando o Banco PostgreSql e o Redis:
```bash
#Containers rodando no momentos
$ docker ps 

#Docker images buildadas.
$ docker images -a
```

### 4 - Rodar a Api

Depois de instalar as dependências, você pode rodar a API usando o Uvicorn, que é o servidor ASGI recomendado para FastAPI. Execute o seguinte comando:

```bash
$ uvicorn main:app --reload
```


Isso iniciará a API no modo de desenvolvimento com recarregamento automático (hot reload) no endereço http://127.0.0.1:8000.

A documentação com Swagger poderá ser visualizado em http://127.0.0.1:8000/docs


# API Endpoints

Para fazer as requisições HTTP abaixo, foi utilizada a ferramenta [httpie](https://httpie.io):
(Você pode usar o swagger da propria documentação e outros como: Insomnia, postman, etc.)

## Obeter vazamentos pelo e-mail do usuario: 
 Endpoint -  http://127.0.0.1:8000/v1/api/vazamentos/procurar/{email}

### Retorno:
```Json
[
  {
    "id": 0,
    "nome": "string",
    "titulo": "string",
    "dominio_url": "string",
    "data_vazamento": "2024-12-09",
    "data_adicao": "2024-12-09T14:04:18.905Z",
    "data_atualizacao": "2024-12-09T14:04:18.905Z",
    "pwn_count": 0,
    "descricao": "string",
    "image_uri": "string",
    "data_classes": [],
    "usuario_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
  }
]
```


## Outros Endpoints:

Na documentação do Swagger clicando [aqui](http://127.0.0.1:8000/docs) você visualizará todos os endpoints documentados.


Atenciosamente: Rodrigo Felix -  <a href="https://www.linkedin.com/in/rodrigofelixf/" target="_blank">
    <img src="https://img.shields.io/static/v1?label=Linkedin&message=@rodrigofelixf&color=8257E5&labelColor=000000" alt="@rodrigofelixf" />
</a>