<div align="center">

  <img src="https://raw.githubusercontent.com/mykaelandradee/stremioscrapers/refs/heads/main/icon.png" alt="Stremio Scrapers Logo" width="180" />

  # 🚀 Stremio Scrapers

  <p>Addon de alta performance para o Stremio com gerenciamento dinâmico de scrapers e interface de configuração moderna.</p>

  <p>
    <a href="#-sobre-o-projeto">Sobre</a> •
    <a href="#-funcionalidades">Funcionalidades</a> •
    <a href="#-estrutura-da-fun%C3%A7%C3%A3o-get_streams">Estrutura</a> •
    <a href="#-hospedagem-deploy">Hospedagem</a> •
    <a href="#-cr%C3%A9ditos">Créditos</a>
  </p>

  ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
  ![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
  ![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=for-the-badge&logo=vite&logoColor=white)
  ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
  ![Render](https://img.shields.io/badge/Render-%46E3B7.svg?style=for-the-badge&logo=render&logoColor=white)
  ![Vercel](https://img.shields.io/badge/Vercel-000000.svg?style=for-the-badge&logo=vercel&logoColor=white)

</div>

---

## 🧐 Sobre o Projeto

O **Stremio Scrapers** (baseado no motor MegaSource) é uma solução para agregação e personalização de fontes de mídia para o Stremio. Ele combina um backend robusto em Python para processamento isolado de scrapers/streams e uma interface web moderna construída em React (Vite) para configuração rápida pelo usuário.

> ℹ️ Este projeto é baseado e derivado do projeto [megasource_stremio](https://github.com/zoreu/megasource_stremio) desenvolvido por **[zoreu](https://github.com/zoreu)**.

---

## ✨ Funcionalidades

- ⚡ **Backend em Python**: Processamento rápido de requisições do manifesto e rotas de scraping em ambiente sandbox.
- 🎨 **Interface Web Moderna (`front_vite`)**: Painel amigável para ativar, desativar e personalizar scrapers.
- 🌐 **Suporte Multilíngue (i18n)**: Interface adaptada para múltiplos idiomas.
- 🐳 **Containerizado**: Pronto para rodar via Docker sem complicações.
- ☁️ **Deploy Flexível**: Suporte nativo para hospedagem rápida no Render ou Vercel.

---

## 🏗️ Estrutura da Função (`get_streams`)

Todos os scrapers utilizados por este backend seguem rigorosamente a assinatura padrão de execução:

```python
def get_streams(media_type: str, media_id: str, config: dict = None) -> list:
    """
    Parâmetros:
        media_type (str): Tipo de mídia ('movie' ou 'series')
        media_id (str): ID do IMDb (ex: 'tt1877830')
        config (dict, optional): Configurações repassadas pelo addon
        
    Retorna:
        list: Lista de dicionários no formato {'name', 'title', 'url', 'quality'}
    """
    streams = []
    
    # Lógica de scraping / extração de links
    # ...
    
    streams.append({
        "name": "Nome do Provedor",
        "title": "🎬 Título do Conteúdo\n🔊 Áudio: PT-BR | 1080p",
        "url": "[https://link-da-stream.mp4](https://link-da-stream.mp4)",
        "quality": "1080p"
    })
    
    return streams
