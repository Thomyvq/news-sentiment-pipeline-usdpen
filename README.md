# 📈 Análisis de Sentimiento en Noticias Macroeconómicas Formales para la Generación de Señales de Apoyo a la Toma de Decisiones en Tesorería mediante Técnicas de Inteligencia Artificial

![Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.10-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Research](https://img.shields.io/badge/Research-AI%20Applied-orange)

Sistema basado en Inteligencia Artificial para analizar noticias macroeconómicas formales y generar señales explicables de apoyo a decisiones de Tesorería relacionadas con el tipo de cambio USD/PEN.

---

## 📌 Descripción General

Este proyecto transforma noticias económicas en indicadores cuantitativos diarios utilizando:

- NLP financiero  
- Modelos de sentimiento  
- Embeddings semánticos  
- FAISS  
- RAG  

El objetivo es apoyar decisiones analíticas en Tesorería mediante señales interpretables.

---

## 🎯 Objetivos

✅ Automatizar noticias financieras  
✅ Analizar sentimiento ES/EN  
✅ Generar señales USD/PEN  
✅ Crear brief automático  
✅ Evaluar impacto preliminar

---

## ⚙️ Tecnologías

| Tecnología | Uso |
|-----------|-----|
| Python | Lenguaje principal |
| Transformers | NLP |
| FinBERT | Sentimiento EN |
| RoBERTuito | Sentimiento ES |
| FAISS | Recuperación semántica |
| Pandas | Datos |
| Matplotlib | Visualización |

---

# 📊Dataset del Proyecto

Este proyecto utiliza noticias macroeconómicas formales en español e inglés para construir indicadores diarios de sentimiento asociados al análisis del tipo de cambio USD/PEN.

## Fuentes

Las noticias provienen de fuentes económicas formales mediante RSS y scraping.

## Archivos generados localmente

- `data/raw/news_raw.csv`  
  Noticias obtenidas directamente desde las fuentes RSS y scraping, sin procesamiento inicial.

- `data/processed/news_clean.csv`  
  Noticias luego del proceso de limpieza, normalización de texto y depuración de caracteres.

- `data/processed/news_scores.csv`  
  Resultado del análisis de sentimiento por noticia, incluyendo etiquetas y puntajes individuales.

- `data/processed/daily_sentiment.csv`  
  Indicadores agregados diarios de sentimiento construidos a partir del conjunto de noticias procesadas.

- `data/processed/compare_sentiment_vs_fx.csv`  
  Comparación entre señales generadas por sentimiento y el comportamiento real del tipo de cambio USD/PEN.

- `data/reports/brief_YYYY-MM-DD.md`  
  Brief automático diario en formato Markdown con resumen ejecutivo, contexto y principales hallazgos.

## Campos principales

- `date`
- `source`
- `title`
- `url`
- `text`
- `language`
- `topic`
- `sentiment_label`
- `sentiment_score`
- `asset`



## 🧠 Arquitectura del Sistema

# <p align="center">

# &#x20; <img src="figs/arquitectura_pipeline.png" width="900">

# </p>

## 📂 Estructura del Proyecto

```text
news-sentiment-pipeline/
├── configs/                         # Archivos de configuración del pipeline
│   ├── models.yaml                  # Configuración de modelos NLP
│   ├── pipeline.yaml                # Parámetros generales de ejecución
│   ├── scoring.yaml                 # Reglas de scoring de sentimiento
│   ├── signals.yaml                 # Reglas para generación de señales
│   └── sources.yaml                 # Fuentes RSS / scraping
│
├── data/                            # Datos generados y procesados por el pipeline
│   ├── artifacts/                   # Artefactos intermedios del proceso
│   ├── market/                      # Datos de mercado USD/PEN
│   ├── processed/                   # Noticias limpias, scores y agregados diarios
│   ├── raw/                         # Noticias crudas obtenidas de las fuentes
│   ├── reports/                     # Briefs automáticos generados por fecha
│   └── db.sqlite                    # Base SQLite local del proyecto
│
├── faiss_store/                     # Índice vectorial para recuperación semántica
│   ├── index.faiss                  # Índice FAISS de embeddings
│   └── meta.jsonl                   # Metadatos asociados a los documentos indexados
│
├── figs/                            # Figuras e imágenes usadas en README o reportes
│   └── arquitectura_pipeline.png    # Imagen de arquitectura del sistema
│
├── scripts/                         # Scripts auxiliares de análisis y visualización
│   └── make_eda_plots.py            # Generación de gráficos EDA
│
├── src/                             # Código fuente principal del sistema
│   ├── __init__.py
│   ├── pipeline.py                  # Orquestador principal del pipeline
│   │
│   ├── db/                          # Módulos de persistencia / base de datos
│   ├── eval/                        # Módulos iniciales de evaluación
│   ├── evaluation/                  # Evaluación formal de señales vs USD/PEN
│   ├── ingest/                      # Ingesta de noticias RSS / scraping
│   ├── market/                      # Obtención y tratamiento de datos de mercado
│   ├── processing/                  # Limpieza, idioma, sentimiento, NER y agregación
│   ├── rag/                         # Embeddings, recuperación y generación de brief
│   ├── signals/                     # Reglas de generación de señales
│   └── utils/                       # Funciones auxiliares y utilidades generales
│
├── tools/                           # Herramientas auxiliares de exportación
│   └── export_news_scores.py        # Exportación de resultados de sentimiento
│
├── .gitignore                       # Archivos/carpetas excluidos de Git
├── LICENSE                          # Licencia del proyecto
├── README.md                        # Documentación principal del repositorio
├── requirements.txt                 # Dependencias necesarias
└── run_pipeline.py                  # Script principal para ejecutar el pipeline
```

## ▶️ Ejecución

- pip install -r requirements.txt
- python run_pipeline.py

## 📊 Resultados Iniciales

- Pipeline funcional end-to-end
- Noticias procesadas automáticamente
- Señales diarias generadas
- Brief automático operativo
- Comparación inicial con USD/PEN

## 🗺️Roadmap Sprint 1

## Actividades completadas

| Actividad | Estado | Responsable | Fecha |
|---|---|---|---|
| Ingesta de noticias | Completado | Thomy | 2025-12-05 |
| Limpieza de texto | Completado | Thomy | 2025-12-05 |
| Detección de idioma | Completado | Thomy | 2025-12-15 |
| Embeddings + FAISS | Completado | Thomy | 2025-12-15 |
| NER y tópicos | Completado | Thomy | 2026-01-06 |
| Análisis de sentimiento | Completado | Thomy | 2026-01-07 |
| Agregación diaria | Completado | Thomy | 2026-01-08 |
| Generación de señales | Completado | Thomy | 2026-01-08 |
| Brief automático RAG | Completado | Thomy | 2026-01-09 |
| Evaluación inicial vs USD/PEN | Completado | Thomy | 2026-01-09 |
| Presentación stackholder (Ecosistema de Tipo de cambio) | Pendiente | Nicolleta Lambrushini | 2026-04-28 |
| Incorporar banda neutral | Pendiente | Thomy | 2026-04-30 |
| Mejorar calibración de señales | Pendiente | Thomy | 2026-04-30 |
| Ampliar evaluación histórica | Pendiente | Thomy | 2026-05-05 |
| Ponderar por fuente y tópico | Pendiente | Thomy | 2026-05-05 |
| Construir dashboard | Pendiente | Thomy | 2026-05-06 |
| Generar briefs históricos | Pendiente | Thomy | 2026-05-06 |
| Presentación 1er MVP | Pendiente | Nicolleta Lambrushini | 2026-05-12 |

## 👨‍💻 Autor

- Thomy Jefferson Villanueva Quinteros
   - Email: tvillanuevaq@uni.pe
   - GitHub: https://github.com/Thomyvq

