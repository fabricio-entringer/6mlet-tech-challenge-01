
# Tech Challenge - Fase 1 - Machine Learning Engineering

## Tech Challenge

**Tech Challenge** é o projeto da fase que englobará os conhecimentos obtidos em todas as disciplinas da fase. Esta é uma atividade que, a princípio, deve ser desenvolvida em grupo. Importante atentar-se ao prazo de entrega, pois trata-se de uma atividade obrigatória, uma vez que sua pontuação se refere a **90% da nota final**.

---

## O Problema

**Desafio: Criação de uma API Pública para Consulta de Livros**

Você foi contratado(a) como Engenheiro(a) de Machine Learning para um projeto de recomendação de livros. A empresa está em sua fase inicial e ainda não possui uma base de dados estruturada.

Seu primeiro desafio será montar a infraestrutura de extração, transformação e disponibilização de dados via API pública para que cientistas de dados e serviços de recomendação possam usar esses dados com facilidade.

Assim, seu objetivo será **desenvolver um pipeline completo de dados e uma API pública para servir esses dados**, pensando na escalabilidade e reusabilidade futura em modelos de machine learning.

---

## Entregáveis Obrigatórios

1. **Repositório do GitHub Organizado**
   - Código estruturado em módulos (`scripts/`, `api/`, `data/`, etc.)
   - README completo contendo:
     - Descrição do projeto e arquitetura.
     - Instruções de instalação e configuração.
     - Documentação das rotas da API.
     - Exemplos de chamadas com requests/responses.
     - Instruções para execução.

2. **Sistema de Web Scraping**
   - Script automatizado para extrair dados de [https://books.toscrape.com/](https://books.toscrape.com/)
   - Dados armazenados localmente em um arquivo CSV.
   - Script executável e bem documentado.

3. **API RESTful Funcional**
   - API implementada em Flask ou FastAPI.
   - Endpoints obrigatórios (listados abaixo).
   - Documentação da API (Swagger).

4. **Deploy Público**
   - API deployada em Heroku, Render, Vercel, Fly.io ou similar.
   - Link compartilhável funcional.
   - API operacional no ambiente de produção.

5. **Plano Arquitetural**
   - Diagrama ou documento detalhando:
     - Pipeline desde ingestão → processamento → API → consumo.
     - Arquitetura pensada para escalabilidade futura.
     - Cenário de uso para cientistas de dados/ML.
     - Plano de integração com modelos de ML.

6. **Vídeo de Apresentação (3-12 minutos)**
   - Demonstração técnica (macro).
   - Apresentação da arquitetura e pipeline de dados.
   - Execução de chamadas reais à API.
   - Comentários sobre boas práticas.

---

## Objetivos Técnicos Core

### Web Scraping Robusto

- Extrair todos os livros disponíveis no site.
- Capturar: título, preço, rating, disponibilidade, categoria, imagem.

---

## Endpoints Obrigatórios da API

### Endpoints Core

- `GET /api/v1/books`: Lista todos os livros disponíveis na base de dados.
- `GET /api/v1/books/{id}`: Detalhes completos de um livro específico pelo ID.
- `GET /api/v1/books/search?title={title}&category={category}`: Busca por título e/ou categoria.
- `GET /api/v1/categories`: Lista todas as categorias.
- `GET /api/v1/health`: Verifica status da API.

---

### Endpoints Opcionais (Insights)

- `GET /api/v1/stats/overview`: Estatísticas gerais (total de livros, preço médio, etc.).
- `GET /api/v1/stats/categories`: Estatísticas por categoria.
- `GET /api/v1/books/top-rated`: Livros com melhor avaliação.
- `GET /api/v1/books/price-range?min={min}&max={max}`: Livros por faixa de preço.

---

## Desafios Adicionais (Bônus)

### Desafio 1: Sistema de Autenticação

- Implementar JWT para proteger rotas sensíveis:
  - `POST /api/v1/auth/login`
  - `POST /api/v1/auth/refresh`
  - Proteger `/api/v1/scraping/trigger`

### Desafio 2: Pipeline ML-Ready

- `GET /api/v1/ml/features`: Dados formatados para features.
- `GET /api/v1/ml/training-data`: Dataset para treinamento.
- `POST /api/v1/ml/predictions`: Receber predições.

### Desafio 3: Monitoramento & Analytics

- Logs estruturados de todas as chamadas.
- Métricas de performance da API.
- Dashboard simples (recomenda-se Streamlit).

---

## Certificação Extra: Google Cloud GenAI

- Curso de ~30h incluindo 3 skill badges.
- Postar badges no LinkedIn.
- Garante até **10 pontos extras na nota final**.
- Comprovação de conclusão deve ser enviada junto aos entregáveis.

---

**Boa sorte!**
