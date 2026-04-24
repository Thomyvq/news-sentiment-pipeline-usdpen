# \# News Sentiment Pipeline USD/PEN

# 

# Pipeline de Inteligencia Artificial para analizar noticias macroeconómicas formales en español e inglés y generar señales explicables de apoyo a decisiones de tesorería sobre el tipo de cambio USD/PEN.

# 

# \## Objetivo

# 

# Transformar noticias económicas no estructuradas en indicadores diarios de sentimiento, señales interpretables y briefs automatizados tipo tesorería.

# 

# \## Funcionalidades principales

# 

# \- Ingesta de noticias mediante RSS / scraping.

# \- Limpieza y normalización de texto.

# \- Detección de idioma ES/EN.

# \- Análisis de sentimiento por noticia.

# \- Extracción de entidades y clasificación temática.

# \- Embeddings + FAISS para recuperación semántica.

# \- Agregación diaria del sentimiento.

# \- Generación de señales para USD/PEN.

# \- Generación automática de brief mediante RAG.

# \- Evaluación inicial contra movimiento real del tipo de cambio.

# 

# \## Estructura del proyecto

# 

# ```text

# news-sentiment-pipeline/

# ├── config/

# ├── data/

# ├── docs/

# ├── notebooks/

# ├── src/

# ├── tools/

# ├── run\_pipeline.py

# ├── requirements.txt

# └── README.md

