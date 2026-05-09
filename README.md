# 📈 Análisis de sentimiento en noticias macroeconómicas para la generación de señales sobre USD/PEN mediante Inteligencia Artificial

![Status](https://img.shields.io/badge/Status-Activo-success)
![Python](https://img.shields.io/badge/Python-3.10-blue)
![NLP](https://img.shields.io/badge/NLP-Financial-important)
![ML](https://img.shields.io/badge/MachineLearning-Baseline-yellow)
![Research](https://img.shields.io/badge/Research-AI%20Applied-orange)

---

# 📌 Descripción General

Este proyecto implementa un pipeline end-to-end de NLP financiero para analizar noticias macroeconómicas y generar señales preliminares asociadas al comportamiento del tipo de cambio USD/PEN.

El sistema integra:

- RSS
- scraping histórico
- análisis de sentimiento
- Embeddings + FAISS
- agregación temporal
- modelos baseline de Machine Learning
- comparación contra USD/PEN real

El objetivo es construir indicadores cuantitativos de sentimiento que puedan servir como apoyo analítico para decisiones relacionadas con Tesorería y mercados financieros.

---

# 🎯 Objetivos

✅ Automatizar la ingesta de noticias financieras  
✅ Analizar sentimiento en español e inglés  
✅ Construir indicadores diarios de sentimiento  
✅ Comparar sentimiento vs dirección USD/PEN  
✅ Generar señales explicables  
✅ Evaluar desempeño preliminar mediante modelos baseline

---

# 🧠 Arquitectura del Sistema

<p align="center">
  <img src="figs/arquitectura_pipeline.png" width="900">
</p>

---

# ⚙️ Tecnologías Utilizadas

| Tecnología | Uso |
|---|---|
| Python | Lenguaje principal |
| Transformers | Modelos NLP |
| FinBERT | Sentimiento financiero EN |
| RoBERTuito | Sentimiento ES |
| FAISS | Recuperación semántica |
| Pandas | Procesamiento de datos |
| Matplotlib | Visualización |
| Scikit-learn | Baselines ML |
| SQLite | Persistencia local |
| GDELT | Ingesta histórica |

---

# 📰 Fuentes de Noticias

## 🌎 Fuentes en inglés

- Reuters Business
- Yahoo Finance
- CNBC Markets
- Financial Times
- MarketWatch
- GDELT Historical News

## 🇵🇪 Fuentes en español

- Gestión
- El Comercio
- Bloomberg Línea
- América Economía

---

# 📊 Dataset Generado

El pipeline genera automáticamente:

| Archivo | Descripción |
|---|---|
| `news_raw.csv` | Noticias originales |
| `news_clean.csv` | Noticias limpias |
| `news_scores.csv` | Sentimiento por noticia |
| `daily_sentiment.csv` | Indicadores diarios agregados |
| `compare_sentiment_vs_fx.csv` | Comparación sentimiento vs USD/PEN |
| `daily_evaluation_table.csv` | Evaluación diaria |
| `brief_YYYY-MM-DD.md` | Brief automático |

---

# 🔄 Etapas del Pipeline

## 1. Ingesta de noticias

Fuentes utilizadas:

- RSS
- Reuters scraping
- Bloomberg Línea scraping
- GDELT histórico

---

## 2. Limpieza y normalización

Procesos:

- eliminación de HTML
- normalización Unicode
- filtrado de ruido
- deduplicación

---

## 3. Detección de idioma

Enrutamiento automático:

- Español → RoBERTuito
- Inglés → FinBERT

---

## 4. Embeddings + FAISS

Modelo utilizado:

- `intfloat/multilingual-e5-base`

Aplicaciones:

- recuperación semántica
- soporte RAG
- búsqueda contextual

---

## 5. Análisis de sentimiento

### Modelos utilizados

| Idioma | Modelo |
|---|---|
| EN | ProsusAI/finbert |
| ES | pysentimiento/robertuito-sentiment-analysis |

Etiquetas generadas:

- positive
- neutral
- negative

---

## 6. Agregación diaria

Se generan:

- promedio de sentimiento
- proporción positiva
- proporción negativa
- proporción neutral
- volumen de noticias
- indicadores temporales

---

## 7. Generación de señales

El sistema genera señales experimentales basadas en sentimiento y las compara contra el comportamiento real del USD/PEN.

---

# 📊 Resultados Obtenidos

## 📌 Split temporal utilizado


- Train: 2025-07-09 → 2026-03-06 | filas: 84
- Test : 2026-03-07 → 2026-05-08 | filas: 36

## 📈 Métricas Baseline

| Modelo | Accuracy | F1 Weighted | F1 Binary |
|---|---:|---:|---:|
| Dummy most_frequent | 0.25 | 0.10 | 0.00 |
| Rule sentiment | 0.96 | 0.92 | 1.00 |
| Logistic baseline | 0.50 | 0.50 | 0.67 |

## 📈 Resultados de Experimentos

| Experimento | Accuracy | F1 Weighted | F1 Binary |
|---|---:|---:|---:|
| Baseline_lag1 | 0.50 | 0.50 | 0.67 |
| Var1_lag1_lag2 | 0.50 | 0.50 | 0.67 |
| Var2_lags_volume_shares | 0.75 | 0.64 | 0.86 |
| Var3_full_temporal | 0.75 | 0.64 | 0.86 |

