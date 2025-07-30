# ML Endpoints Documentation

This module contains the machine learning endpoints for the 6MLET Tech Challenge 01 API. It provides three endpoints for working with book price prediction models.

## Endpoints

### 1. GET /api/v1/ml/features
Returns preprocessed feature vectors ready for machine learning models.

**Query Parameters:**
- `format`: Output format (default: "vector")
- `include_metadata`: Include metadata about features (default: true)
- `sample_size`: Number of samples to return (default: all)
- `shuffle`: Shuffle the data (default: false)

**Example Response:**
```json
{
  "features": [
    {
      "book_id": "0",
      "feature_vector": {
        "rating": 0.75,
        "category_Science": 1.0,
        "category_Fiction": 0.0,
        ...
      },
      "original_price": 45.17,
      "price_normalized": 0.703
    }
  ],
  "metadata": {
    "total_samples": 1000,
    "feature_names": ["rating", "category_Academic", ...],
    "feature_count": 58
  }
}
```

### 2. GET /api/v1/ml/training-data
Returns data in sklearn-ready format with train/test split.

**Query Parameters:**
- `test_size`: Proportion for test set (default: 0.2)
- `random_state`: Random seed for reproducibility (default: 42)

**Example Response:**
```json
{
  "X_train": [[0.75, 0, 0, 1, ...], ...],
  "y_train": [0.703, 0.788, ...],
  "X_test": [[0.5, 1, 0, 0, ...], ...],
  "y_test": [0.539, 0.777, ...],
  "feature_names": ["rating", "category_Academic", ...],
  "split_info": {
    "train_size": 800,
    "test_size": 200,
    "test_ratio": 0.2
  }
}
```

### 3. POST /api/v1/ml/predictions
Makes price predictions for a book based on its features.

**Request Body:**
```json
{
  "title": "Python for Data Science",
  "category": "Science",
  "rating": 4,
  "availability": "In stock"
}
```

**Field Descriptions:**
- `title`: Book title (string) - used for logging, not for prediction
- `category`: Book category (string) - must be a valid category from the dataset
- `rating`: Book rating (integer, 1-5) - customer rating
- `availability`: Availability status (string) - e.g., "In stock", "Out of stock"

**Example Response (with real model):**
```json
{
  "predicted_price": 26.87,
  "confidence_interval": {
    "lower": 22.84,
    "upper": 30.90
  },
  "feature_vector": {
    "rating": 0.75,
    "category_Science": 1.0,
    ...
  },
  "model_version": "1.0"
}
```

**Valid Categories:**
Academic, Adult Fiction, Art, Autobiography, Biography, Business, Childrens, Christian, Christian Fiction, Classics, Contemporary, Crime, Cultural, Default, Erotica, Fantasy, Fiction, Food and Drink, Health, Historical, Historical Fiction, History, Horror, Humor, Music, Mystery, New Adult, Nonfiction, Novels, Paranormal, Parenting, Philosophy, Poetry, Politics, Psychology, Religion, Romance, Science, Science Fiction, Self Help, Sequential Art, Short Stories, Spirituality, Sports and Games, Suspense, Thriller, Travel, Womens Fiction, Young Adult

## Feature Engineering

The module processes raw book data into ML-ready features:

1. **Numeric Features:**
   - `rating`: Normalized rating (0-1)
   - `price_normalized`: Target variable normalized (0-1)

2. **One-Hot Encoded Features:**
   - Categories: 50+ book categories (e.g., `category_Science`, `category_Fiction`)
   - Ratings: 5 columns (`rating_One` to `rating_Five`)
   - Availability: 2 columns (`availability_in_stock`, `availability_out_of_stock`)

3. **Data Cleaning:**
   - Invalid category "Add a comment" is reassigned to "Default"
   - Preserves all data instead of removing invalid records

## Training the Model

Before using real predictions, train the model:

```bash
# Train the model (creates model.pkl and model_metadata.pkl)
python app/ml/train_model.py
```

## Usage Examples

```bash
# Get feature vectors
curl http://127.0.0.1:8000/api/v1/ml/features?sample_size=10

# Get training data
curl http://127.0.0.1:8000/api/v1/ml/training-data?test_size=0.3

# Make prediction (example 1)
curl -X POST http://127.0.0.1:8000/api/v1/ml/predictions \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python for Data Science",
    "category": "Science",
    "rating": 4,
    "availability": "In stock"
  }'

# Make prediction (example 2)
curl -X POST http://127.0.0.1:8000/api/v1/ml/predictions \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Great Adventure",
    "category": "Fiction",
    "rating": 5,
    "availability": "Out of stock"
  }'

# Make prediction (example 3)
curl -X POST http://127.0.0.1:8000/api/v1/ml/predictions \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learn to Cook",
    "category": "Food and Drink",
    "rating": 3,
    "availability": "In stock"
  }'
```

## Module Structure

```
ml/
├── __init__.py          # Module exports
├── feature_engineering.py  # Feature transformation logic
├── training_data.py     # Training data preparation
├── prediction_service.py   # Prediction logic (mock)
└── models.py            # Pydantic models
```

## Requirements

- pandas
- numpy
- scikit-learn
- pydantic

---

# Documentação dos Endpoints ML

Este módulo contém os endpoints de machine learning para a API do Tech Challenge 01 6MLET. Fornece três endpoints para trabalhar com modelos de predição de preços de livros.

## Endpoints

### 1. GET /api/v1/ml/features
Retorna vetores de características pré-processados prontos para modelos de machine learning.

**Parâmetros de Query:**
- `format`: Formato de saída (padrão: "vector")
- `include_metadata`: Incluir metadados sobre as features (padrão: true)
- `sample_size`: Número de amostras a retornar (padrão: todas)
- `shuffle`: Embaralhar os dados (padrão: false)

**Exemplo de Resposta:**
```json
{
  "features": [
    {
      "book_id": "0",
      "feature_vector": {
        "rating": 0.75,
        "category_Science": 1.0,
        "category_Fiction": 0.0,
        ...
      },
      "original_price": 45.17,
      "price_normalized": 0.703
    }
  ],
  "metadata": {
    "total_samples": 1000,
    "feature_names": ["rating", "category_Academic", ...],
    "feature_count": 58
  }
}
```

### 2. GET /api/v1/ml/training-data
Retorna dados no formato sklearn com divisão treino/teste.

**Parâmetros de Query:**
- `test_size`: Proporção para conjunto de teste (padrão: 0.2)
- `random_state`: Semente aleatória para reprodutibilidade (padrão: 42)

**Exemplo de Resposta:**
```json
{
  "X_train": [[0.75, 0, 0, 1, ...], ...],
  "y_train": [0.703, 0.788, ...],
  "X_test": [[0.5, 1, 0, 0, ...], ...],
  "y_test": [0.539, 0.777, ...],
  "feature_names": ["rating", "category_Academic", ...],
  "split_info": {
    "train_size": 800,
    "test_size": 200,
    "test_ratio": 0.2
  }
}
```

### 3. POST /api/v1/ml/predictions
Faz predições de preço para um livro baseado em suas características.

**Corpo da Requisição:**
```json
{
  "title": "Python para Ciência de Dados",
  "category": "Science",
  "rating": 4,
  "availability": "In stock"
}
```

**Descrição dos Campos:**
- `title`: Título do livro (string) - usado para logging, não para predição
- `category`: Categoria do livro (string) - deve ser uma categoria válida do dataset
- `rating`: Avaliação do livro (inteiro, 1-5) - avaliação dos clientes
- `availability`: Status de disponibilidade (string) - ex: "In stock", "Out of stock"

**Exemplo de Resposta (com modelo real):**
```json
{
  "predicted_price": 26.87,
  "confidence_interval": {
    "lower": 22.84,
    "upper": 30.90
  },
  "feature_vector": {
    "rating": 0.75,
    "category_Science": 1.0,
    ...
  },
  "model_version": "1.0"
}
```

**Categorias Válidas:**
Academic, Adult Fiction, Art, Autobiography, Biography, Business, Childrens, Christian, Christian Fiction, Classics, Contemporary, Crime, Cultural, Default, Erotica, Fantasy, Fiction, Food and Drink, Health, Historical, Historical Fiction, History, Horror, Humor, Music, Mystery, New Adult, Nonfiction, Novels, Paranormal, Parenting, Philosophy, Poetry, Politics, Psychology, Religion, Romance, Science, Science Fiction, Self Help, Sequential Art, Short Stories, Spirituality, Sports and Games, Suspense, Thriller, Travel, Womens Fiction, Young Adult

## Engenharia de Features

O módulo processa dados brutos de livros em features prontas para ML:

1. **Features Numéricas:**
   - `rating`: Avaliação normalizada (0-1)
   - `price_normalized`: Variável alvo normalizada (0-1)

2. **Features One-Hot Encoded:**
   - Categorias: 50+ categorias de livros (ex: `category_Science`, `category_Fiction`)
   - Avaliações: 5 colunas (`rating_One` até `rating_Five`)
   - Disponibilidade: 2 colunas (`availability_in_stock`, `availability_out_of_stock`)

3. **Limpeza de Dados:**
   - Categoria inválida "Add a comment" é reatribuída para "Default"
   - Preserva todos os dados em vez de remover registros inválidos

## Treinando o Modelo

Antes de usar predições reais, treine o modelo:

```bash
# Treinar o modelo (cria model.pkl e model_metadata.pkl)
python app/ml/train_model.py
```

## Exemplos de Uso

```bash
# Obter vetores de features
curl http://127.0.0.1:8000/api/v1/ml/features?sample_size=10

# Obter dados de treino
curl http://127.0.0.1:8000/api/v1/ml/training-data?test_size=0.3

# Fazer predição (exemplo 1)
curl -X POST http://127.0.0.1:8000/api/v1/ml/predictions \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python para Ciência de Dados",
    "category": "Science",
    "rating": 4,
    "availability": "In stock"
  }'

# Fazer predição (exemplo 2)
curl -X POST http://127.0.0.1:8000/api/v1/ml/predictions \
  -H "Content-Type: application/json" \
  -d '{
    "title": "A Grande Aventura",
    "category": "Fiction",
    "rating": 5,
    "availability": "Out of stock"
  }'

# Fazer predição (exemplo 3)
curl -X POST http://127.0.0.1:8000/api/v1/ml/predictions \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Aprenda a Cozinhar",
    "category": "Food and Drink",
    "rating": 3,
    "availability": "In stock"
  }'
```

## Estrutura do Módulo

```
ml/
├── __init__.py          # Exportações do módulo
├── feature_engineering.py  # Lógica de transformação de features
├── training_data.py     # Preparação de dados de treino
├── prediction_service.py   # Lógica de predição (mock)
└── models.py            # Modelos Pydantic
```

## Requisitos

- pandas
- numpy
- scikit-learn
- pydantic