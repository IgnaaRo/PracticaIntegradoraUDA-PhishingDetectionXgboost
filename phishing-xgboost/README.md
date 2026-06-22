# 🛡️ Detección de Phishing con XGBoost

Trabajo de investigación presentado en **CACIC 2026**.  
Implementación de un sistema híbrido para detectar sitios web de phishing en tiempo real, sin depender de listas negras ni servicios externos.

---

## ¿Qué hace este proyecto?

Analiza cada página web desde dos ángulos distintos y los combina para decidir si es phishing o no:

- **La URL** → longitud sospechosa, subdominios raros, presencia de IP, etc.
- **El contenido HTML** → palabras clave de autenticación, formularios que envían datos afuera, enlaces rotos o vacíos
- **Los hipervínculos** → qué porcentaje de los links apuntan a dominios externos

Todo esto se clasifica con **XGBoost**, un modelo de árbol de decisión potenciado que además explica qué características influyeron más en cada predicción.

## Resultados obtenidos

Sobre un corpus propio de **6.417 páginas web** (3.505 phishing + 3.014 benignas):

| Escenario | Exactitud | TFP |
|---|---|---|
| Solo URL | 99,38% | 0,45% |
| Solo HTML (TF-IDF) | 92,32% | 7,17% |
| Solo Hipervínculos | 88,37% | 17,94% |
| **Sistema Híbrido** | **99,69%** | **0,67%** |

El sistema híbrido logró **0 falsos negativos** sobre el conjunto de prueba.

---

## Estructura del proyecto

```
phishing-xgboost/
├── notebooks/
│   └── pipeline_completo.ipynb   # Notebook principal — correr esto
├── src/
│   ├── fase1_recoleccion.py      # Descarga URLs de phishing y benignas
│   ├── fase2_3_normalizacion.py  # Limpieza de HTML y URLs
│   ├── fase4_features.py         # Extracción de características
│   └── fase5_6_entrenamiento.py  # Entrenamiento XGBoost + ablación
├── data/                         # Se llena al correr la Fase 1
├── results/                      # Tabla de ablación, gráficos, modelos
└── requirements.txt
```

---

## Cómo correrlo

### Opción A — Google Colab (recomendado, sin instalar nada)

1. Subir el ZIP a Colab y descomprimirlo:
```python
from google.colab import files
uploaded = files.upload()  # subir phishing-xgboost.zip
!unzip phishing-xgboost.zip
```

2. Abrir `notebooks/pipeline_completo.ipynb` y ejecutar las celdas en orden.

### Opción B — Local

```bash
pip install -r requirements.txt
jupyter notebook notebooks/pipeline_completo.ipynb
```

---

## Fuentes de datos

Los datos **no están incluidos** en el repositorio — se descargan automáticamente al correr el notebook:

| Fuente | Tipo | Cómo se obtiene |
|---|---|---|
| [PhishTank](https://phishtank.org/) | Phishing | Automático (feed CSV público) |
| [OpenPhish](https://openphish.com/) | Phishing | Automático (feed .txt público) |
| [Tranco](https://tranco-list.eu/) | Benigno | Descarga manual del CSV, guardar en `data/tranco_top1m.csv` |

> **Nota:** PhishTank puede pedir registro gratuito si se hacen muchas descargas seguidas. OpenPhish tiene ~300-500 URLs activas en un momento dado; para un corpus grande hay que correr la Fase 1 varias veces a lo largo de varios días y acumular resultados.

---

## Fases del pipeline

```
Fase 1 → Descargar URLs de phishing (PhishTank, OpenPhish) y benignas (Tranco)
          + rastrear el HTML de cada una en menos de 24hs

Fase 2 → Limpiar el HTML: sacar <script>, <style>, comentarios
          Normalizar URLs: minúsculas, decodificar caracteres especiales

Fase 3 → Tokenizar URLs por delimitadores (. / - _ ? =)
          Tokenizar HTML a nivel de carácter para TF-IDF

Fase 4 → Extraer 3 grupos de características:
          (a) 9 features léxicas de la URL
          (b) Vectores TF-IDF del HTML (n-gramas de 1-3 caracteres)
          (c) 3 razones de hipervínculos (externos, nulos, formularios)

Fase 5 → Escalar features escalares (media 0, varianza 1)
          Normalizar TF-IDF con norma L2
          (todo ajustado SOLO sobre el conjunto de entrenamiento)

Fase 6 → Partir el corpus 70% train / 15% val / 15% test (estratificado)
          Entrenar XGBoost con validación cruzada de 5 pliegues
          Evaluar en test + estudio de ablación por grupo de features
```

---

## Resultados guardados en `results/`

Después de correr el notebook completo vas a encontrar:

- `tabla_ablacion.csv` — métricas de los 4 escenarios (para el paper)
- `feature_importance.png` — qué variables influyeron más en el modelo
- `matriz_confusion_hibrido.png` — matriz de confusión del sistema híbrido
- `modelo_xgboost_hibrido.joblib` — modelo entrenado (para reusar)
- `resumen_corpus.json` — tamaño real del corpus usado

---

## Autores

Víctor Córdoba · Lionel Gutiérrez · Nahuel Leyes · Giuliana Pessina · Ignacio Romero · Juan Ignacio Tartaglia · Jorge Tohme  
Laboratorio de Investigación en Ciencia y Tecnología — Universidad del Aconcagua, Mendoza, Argentina

---

## Referencia principal

Aljofey, A. et al. (2022). *An Effective Detection Approach for Phishing Websites Using URL and HTML Features*. Scientific Reports, 12(1), 8842. https://doi.org/10.1038/s41598-022-10841-5
