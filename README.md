# Stremio Scrapers

> Addon para Stremio com arquitetura modular de scrapers, agregação de streams e painel web para configuração.

[![Python](https://img.shields.io/badge/Python-3-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=20232A)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-8-646CFF?logo=vite&logoColor=white)](https://vite.dev/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

---

## Visão geral

O **Stremio Scrapers** é um addon para o **Stremio** voltado à agregação de fontes de mídia por meio de scrapers independentes.

O projeto combina um backend em Python responsável pelo processamento das requisições e execução dos scrapers com uma interface web em React/Vite para configuração e gerenciamento das fontes disponíveis.

O código é baseado no projeto **megasource_stremio**, de [zoreu](https://github.com/zoreu/megasource_stremio).

---

## Principais recursos

- Arquitetura modular para scrapers
- Agregação de streams em uma única resposta do addon
- Suporte a filmes e séries
- Interface web para configuração das fontes
- Ativação e desativação de scrapers
- Suporte a múltiplos idiomas na interface
- Backend assíncrono em Python
- Execução containerizada com Docker
- Deploy compatível com serviços como Render e Vercel

---

## Arquitetura

```text
Stremio
   │
   ▼
Addon / Manifest
   │
   ▼
Backend Python
   │
   ├── Scraper A
   ├── Scraper B
   ├── Scraper C
   └── ...
   │
   ▼
Streams agregados
   │
   ▼
Stremio
```

Cada scraper segue uma interface simples baseada em `get_streams`:

```python
def get_streams(media_type: str, media_id: str, config: dict = None) -> list:
    """Retorna as streams encontradas para uma obra."""
    streams = []

    # Lógica de extração da fonte
    # ...

    streams.append({
        "name": "Nome do provedor",
        "title": "Título da stream",
        "url": "https://exemplo.com/stream",
        "quality": "1080p",
    })

    return streams
```

O contrato pode evoluir conforme as necessidades do addon, mas a separação por scraper facilita manutenção, testes e expansão de novas fontes.

---

## Stack

| Camada | Tecnologias |
| --- | --- |
| Backend | Python, Flask, ASGI |
| HTTP | aiohttp, requests |
| Scraping | BeautifulSoup, lxml |
| Frontend | React, Vite |
| Container | Docker |
| Servidor | Waitress |
| Deploy | Render / Vercel |

---

## Desenvolvimento local

### Pré-requisitos

- Python 3
- Node.js
- npm
- Docker, opcional

### Backend

Instale as dependências:

```bash
pip install -r requirements.txt
```

Inicie o servidor conforme a configuração do projeto.

### Frontend

Entre no diretório do frontend e instale as dependências:

```bash
cd front_vite
npm install
npm run dev
```

> Os comandos exatos podem variar conforme a configuração atual do ambiente de deploy e dos arquivos do projeto.

---

## Docker

Para executar em container, utilize a configuração Docker fornecida pelo projeto:

```bash
docker build -t stremio-scrapers .
docker run -p 8080:8080 stremio-scrapers
```

A porta pode ser ajustada de acordo com a configuração utilizada no ambiente de execução.

---

## Organização do projeto

```text
stremioscrapers/
├── front_vite/          # Interface web
├── scrapers/            # Implementações das fontes
├── *.py                 # Backend e rotas do addon
├── requirements.txt     # Dependências Python
├── Dockerfile           # Containerização
└── README.md
```

---

## Boas práticas para scrapers

Cada scraper deve:

- Ser independente das demais fontes;
- Retornar uma lista de streams válida;
- Evitar bloquear a execução do addon;
- Tratar falhas da fonte sem interromper os demais scrapers;
- Informar qualidade e metadados quando disponíveis;
- Evitar armazenar credenciais ou dados sensíveis no código.

---

## Deploy

O projeto pode ser executado em ambientes que suportem Python/ASGI e também pode ser containerizado para facilitar a publicação.

Antes do deploy, configure as variáveis de ambiente e demais parâmetros necessários para as fontes utilizadas. Nunca versione credenciais, cookies ou tokens privados.

---

## Créditos

Projeto baseado no **megasource_stremio**, desenvolvido por [zoreu](https://github.com/zoreu/megasource_stremio).

---

## Status

**Em desenvolvimento ativo.**

---

<div align="center">

Desenvolvido por **Mykael Andrade**

</div>
