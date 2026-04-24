# \# 📈 News Sentiment Pipeline USD/PEN

# 

# Sistema basado en Inteligencia Artificial para analizar noticias macroeconómicas formales en español e inglés y generar señales explicables de apoyo a decisiones de Tesorería relacionadas con el tipo de cambio USD/PEN.

# 

# \---

# 

# \## 📌 Tabla de Contenido

# 

# 1\. Descripción General  

# 2\. Objetivos  

# 3\. Metodología  

# 4\. Tecnologías Utilizadas  

# 5\. Arquitectura del Sistema  

# 6\. Estructura del Proyecto  

# 7\. Instalación  

# 8\. Ejecución  

# 9\. Resultados Preliminares  

# 10\. Roadmap  

# 11\. Contexto Académico  

# 12\. Autor

# 

# \---

# 

# \## 📖 Descripción General

# 

# En los mercados financieros, la información macroeconómica influye constantemente en expectativas, liquidez, percepción de riesgo y decisiones operativas.

# 

# Este proyecto propone un pipeline reproducible de Inteligencia Artificial que transforma noticias económicas no estructuradas en indicadores cuantitativos diarios de sentimiento, señales interpretables y briefs automáticos de apoyo analítico.

# 

# El sistema utiliza técnicas modernas de NLP, embeddings semánticos y Retrieval-Augmented Generation (RAG).

# 

# \---

# 

# \## 🎯 Objetivos

# 

# \### Objetivo General

# 

# Desarrollar un sistema basado en IA capaz de analizar noticias macroeconómicas formales y generar señales explicables de apoyo a decisiones en Tesorería.

# 

# \### Objetivos Específicos

# 

# \- Automatizar la recolección de noticias financieras.

# \- Limpiar y normalizar texto en español e inglés.

# \- Aplicar modelos de análisis de sentimiento financiero.

# \- Agregar resultados en indicadores diarios.

# \- Generar señales interpretables para USD/PEN.

# \- Construir briefs automáticos con contexto relevante.

# \- Evaluar resultados frente al comportamiento del mercado.

# 

# \---

# 

# \## 🧠 Metodología

# 

# El proyecto sigue un enfoque iterativo basado en investigación aplicada, integrando prácticas de:

# 

# \- Agile + AI

# \- MLOps académico

# \- NLP financiero

# \- Evaluación incremental

# \- Versionamiento en GitHub

# 

# \### Etapas del pipeline

# 

# 1\. Ingesta de noticias  

# 2\. Limpieza de texto  

# 3\. Detección de idioma  

# 4\. NER y clasificación temática  

# 5\. Análisis de sentimiento  

# 6\. Embeddings semánticos  

# 7\. Agregación diaria  

# 8\. Generación de señales  

# 9\. Brief automático con RAG  

# 10\. Evaluación vs USD/PEN

# 

# \---

# 

# \## ⚙️ Tecnologías Utilizadas

# 

# | Área | Herramienta |

# |------|-------------|

# | Lenguaje principal | Python |

# | NLP | Transformers |

# | Sentimiento EN | FinBERT |

# | Sentimiento ES | RoBERTuito |

# | Embeddings | multilingual-e5-base |

# | Vector Store | FAISS |

# | Datos | Pandas |

# | Visualización | Matplotlib |

# | Versionamiento | Git + GitHub |

# 

# \---

# 

# \## 🏗️ Arquitectura del Sistema

# 

# ```text

# Fuentes de Noticias

# &#x20;       ↓

# Ingesta RSS / Scraping

# &#x20;       ↓

# Limpieza y Normalización

# &#x20;       ↓

# Detección de Idioma

# &#x20;       ↓

# NER + Topics

# &#x20;       ↓

# Sentimiento

# &#x20;       ↓

# Embeddings + FAISS

# &#x20;       ↓

# Agregación Diaria

# &#x20;       ↓

# Señales USD/PEN

# &#x20;       ↓

# Brief Automático

# &#x20;       ↓

# Evaluación

