# 📈 Análisis de Sentimiento en Noticias Macroeconómicas para la Generación de Señales sobre USD/PEN mediante Inteligencia Artificial

![Python](https://img.shields.io/badge/Python-3.12-blue)
![NLP](https://img.shields.io/badge/NLP-Financial-important)
![Machine Learning](https://img.shields.io/badge/MachineLearning-RandomForest-success)
![Research](https://img.shields.io/badge/MSc-AI-orange)
![Status](https://img.shields.io/badge/Status-Activo-success)

---

# 🌐 Dashboard Interactivo

El proyecto cuenta con una versión web desplegada mediante GitHub Pages:

👉 https://thomyvq.github.io/news-sentiment-pipeline-usdpen/

Características:

- Visualización de sentimiento diario.
- Comparación contra USD/PEN real.
- Semáforo de aciertos y errores.
- Probabilidad de subida del modelo.
- Ranking de días con mayor sentimiento.
- Matriz de confusión interactiva.
- Configuraciones Top-K.
- Descarga de datos filtrados.

---

# 📌 Descripción

Este proyecto desarrolla un pipeline completo de Procesamiento de Lenguaje Natural (NLP) y Machine Learning para transformar noticias macroeconómicas en indicadores cuantitativos de sentimiento capaces de generar señales experimentales sobre movimientos del tipo de cambio USD/PEN.

El objetivo es evaluar si el sentimiento agregado de noticias financieras contiene información predictiva útil para anticipar movimientos alcistas o no alcistas del mercado cambiario.

La investigación forma parte del proyecto de tesis de Maestría en Inteligencia Artificial.

---

# 🎯 Objetivos

- Automatizar la ingesta de noticias financieras.
- Analizar sentimiento en español e inglés.
- Construir indicadores diarios de sentimiento.
- Generar variables temporales predictivas.
- Evaluar modelos de Machine Learning.
- Comparar señales contra USD/PEN real.
- Implementar una plataforma reproducible de visualización.

- # 🧪 Experimentos Week 8

Durante la Semana 8 se incorporaron tres mejoras principales:

1. Validación Stratified K-Fold complementaria.
2. Optimización de hiperparámetros mediante Random Search.
3. Selección formal del modelo ganador.

---

# 📊 Comparación de variantes

| Variante | Features |
|-----------|-----------|
| Baseline_lag1 | lag_sent_1 |
| Var1_lag1_lag2 | lag_sent_1 + lag_sent_2 |
| Var2_lags_volume_shares | lags + volumen + shares |
| Var3_full_temporal | conjunto completo temporal |

---

# 📈 Resultados Stratified K-Fold

| Modelo | PR-AUC |
|----------|----------|
| Baseline_lag1 | 0.646 |
| Var1_lag1_lag2 | 0.679 |
| Var2_lags_volume_shares | 0.651 |
| Var3_full_temporal | 0.660 |

La mejor variante fue:

```text
Var1_lag1_lag2
```

---

# 🔍 Optimización de hiperparámetros

Se evaluaron aproximadamente:

- 30 configuraciones Logistic Regression
- 30 configuraciones Random Forest

Total:

```text
≈ 60 configuraciones
≈ 300 entrenamientos efectivos
```

mediante:

```python
RandomizedSearchCV
```

con:

```python
StratifiedKFold(n_splits=5)
```

# 🏆 Modelo Ganador

Modelo:

```text
Random Forest
```

Features:

```text
lag_sent_1
lag_sent_2
```

Parámetros óptimos:

```json
{
  "max_depth": 4,
  "n_estimators": 54,
  "min_samples_split": 4,
  "min_samples_leaf": 1
}
```

PR-AUC CV:

```text
0.692
```

PR-AUC Holdout:

```text
0.779
```

Accuracy Holdout:

```text
0.444
```

Precision:

```text
0.750
```

Recall:

```text
0.316
```

# 🌐 Dashboard GitHub Pages

La versión pública del proyecto se encuentra disponible en:

https://thomyvq.github.io/news-sentiment-pipeline-usdpen/

El dashboard permite:

- explorar resultados de validación,
- visualizar señales del modelo,
- comparar sentimiento y USD/PEN,
- consultar configuraciones Top-K,
- descargar datos para análisis adicional.

Esta plataforma permite reproducir visualmente los resultados obtenidos durante la Semana 8.

# 🔁 Reproducibilidad

Repositorio:

https://github.com/Thomyvq/news-sentiment-pipeline-usdpen

Dashboard:

https://thomyvq.github.io/news-sentiment-pipeline-usdpen/

Notebook principal:

```text
notebooks/eda_sentiment_week8.ipynb
```

Artefactos generados:

```text
logs/
figs/
docs/
data/artifacts/
```

Modelo ganador:

```text
data/artifacts/week8_best_model.joblib
```
