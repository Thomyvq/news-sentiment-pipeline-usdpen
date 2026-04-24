# \# News Sentiment Pipeline USD/PEN

# 

# Pipeline de Inteligencia Artificial orientado al análisis de sentimiento en noticias macroeconómicas formales para generar señales explicables de apoyo a decisiones de tesorería relacionadas con el tipo de cambio USD/PEN.

# 

# \---

# 

# \## Descripción General

# 

# Este proyecto implementa un pipeline reproducible de Procesamiento de Lenguaje Natural (NLP) que procesa noticias económicas en español e inglés, estima sentimiento financiero, agrega indicadores diarios, genera señales interpretables y construye briefs automáticos mediante técnicas de Retrieval-Augmented Generation (RAG).

# 

# El proyecto forma parte de una investigación aplicada enfocada en el uso de Inteligencia Artificial como herramienta de soporte analítico para Tesorería.

# 

# \---

# 

# \## Objetivo de Investigación

# 

# Desarrollar un sistema basado en técnicas de Inteligencia Artificial capaz de analizar noticias macroeconómicas formales y generar señales explicables basadas en sentimiento que apoyen la toma de decisiones en Tesorería.

# 

# \---

# 

# \## Funcionalidades Principales

# 

# \- Ingesta automática de noticias mediante RSS y scraping.

# \- Limpieza y normalización de texto.

# \- Detección de idioma (español / inglés).

# \- Análisis de sentimiento financiero.

# \- Reconocimiento de entidades (NER).

# \- Clasificación temática.

# \- Generación de embeddings semánticos.

# \- Recuperación semántica con FAISS.

# \- Agregación diaria de sentimiento.

# \- Generación de señales para USD/PEN.

# \- Brief automático diario mediante RAG.

# \- Evaluación inicial frente al comportamiento real del mercado.

# 

# \---

# 

# \## Estructura del Proyecto

# 

# ```text

# news-sentiment-pipeline/

# ├── config/

# ├── data/

# ├── docs/

# ├── notebooks/

# ├── scripts/

# ├── src/

# │   ├── evaluation/

# │   ├── ingest/

# │   ├── market/

# │   ├── processing/

# │   ├── rag/

# │   ├── signals/

# │   └── utils/

# ├── tools/

# ├── run\_pipeline.py

# ├── requirements.txt

# ├── .gitignore

# ├── LICENSE

# └── README.md

