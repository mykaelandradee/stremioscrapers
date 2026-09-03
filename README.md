<div align="center">

  <img src="[https://raw.githubusercontent.com/zoreu/megasource_stremio/refs/heads/main/icon.png](https://raw.githubusercontent.com/mykaelandradee/stremioscrapers/refs/heads/main/icon.png)" alt="Stremio Scrapers
 Logo" width="160" />

  # Stremio Scrapers

  <p align="center">
    <b>Motor de extração e scrapers dinâmicos em Python para o addon MegaSource (Stremio / Nuvio).</b>
  </p>

  <p>
    <a href="#-sobre-o-projeto">Sobre</a> •
    <a href="#-estrutura-da-fun%C3%A7%C3%A3o-get_streams">Estrutura</a> •
    <a href="#-hospedagem-deploy">Hospedagem</a> •
    <a href="#-cr%C3%A9ditos">Créditos</a>
  </p>

  ![Python](https://img.shields.io/badge/Python-3.10%2B-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
  ![Stremio](https://img.shields.io/badge/Stremio-Addon-7B5294?style=for-the-badge&logo=stremio&logoColor=white)
  ![Render](https://img.shields.io/badge/Render-Deploy-46E3B7?style=for-the-badge&logo=render&logoColor=white)
  ![Vercel](https://img.shields.io/badge/Vercel-Deploy-000000?style=for-the-badge&logo=vercel&logoColor=white)

</div>

---

## 🧐 Sobre o Projeto

O **Stremio Scrapers** reúne os motores de extração (*scrapers*) desenvolvidos para alimentar o backend do **MegaSource**. Cada módulo `.py` é responsável por consultar provedores de conteúdo, extrair links de reprodução (embeds, m3u8 ou magnets) e retorná-los no formato padrão aceito pelo ecossistema do Stremio.

---

## 🏗️ Estrutura da Função (`get_streams`)

Todos os scrapers deste repositório seguem rigorosamente a assinatura padrão exigida pelo motor do MegaSource:

```python
def get_streams(media_type: str, media_id: str, config: dict = None) -> list:
    """
    Parâmetros:
        media_type (str): Tipo de mídia ('movie' ou 'series')
        media_id (str): ID do IMDb (ex: 'tt1877830')
        config (dict, optional): Configurações repassadas pelo addon
        
    Retorna:
        list: Lista de dicionários contendo as streams encontradas
    """
    streams = []
    
    # Lógica de scraping / requisição
    # ...
    
    streams.append({
        "name": "Nome do Provedor",
        "title": "🎬 Nome do Filme/Episódio\n🔊 Áudio: PT-BR | 1080p",
        "url": "[https://link-da-stream.mp4](https://link-da-stream.mp4)",
        "quality": "1080p"
    })
    
    return streams
