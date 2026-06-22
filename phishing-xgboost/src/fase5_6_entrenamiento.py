"""
Fase 5 - Escalado
Fase 6 - Particion + Entrenamiento XGBoost + Estudio de ablacion
===================================================================
Este script:
1. Particiona el corpus 70/15/15 (train/val/test) estratificado.
2. Ajusta StandardScaler y TfidfVectorizer SOLO sobre train.
3. Entrena XGBoost con CV de 5 pliegues sobre train para hiperparametros.
4. Evalua en test: exactitud, precision, exhaustividad, F1, TFP, matriz de confusion.
5. Corre el ESTUDIO DE ABLACION: Solo-URL / Solo-HTML / Solo-Hipervinculos / Hibrido.
6. Genera el grafico de Feature Importance de XGBoost.

Todos los resultados (tablas + graficos) se guardan en ../results/
para insertar directamente en el paper.
"""
import pandas as pd
import numpy as np
import json
import os
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
from scipy.sparse import hstack, csr_matrix
import xgboost as xgb
import joblib

from fase4_features import construir_features_lexicas_y_links, construir_tfidf

RESULTS_DIR = "../results"
os.makedirs(RESULTS_DIR, exist_ok=True)

COLS_LEXICAS = [
    "url_longitud", "url_num_subdominios", "url_tiene_ip", "url_tiene_arroba",
    "url_doble_barra_path", "url_guiones_dominio", "url_https_en_dominio",
    "url_profundidad_ruta", "url_tld_en_ruta",
]
COLS_HIPERVINCULOS = ["frac_enlaces_externos", "frac_anclas_nulas", "frac_forms_accion_externa"]


def particionar(df):
    """70/15/15 estratificado, como especifica Fase 6."""
    train, temp = train_test_split(df, test_size=0.30, stratify=df["label"], random_state=42)
    val, test = train_test_split(temp, test_size=0.50, stratify=temp["label"], random_state=42)
    print(f"Train: {len(train)} | Val: {len(val)} | Test: {len(test)}")
    return train.reset_index(drop=True), val.reset_index(drop=True), test.reset_index(drop=True)


def calcular_tfp(y_true, y_pred):
    """Tasa de Falsos Positivos = FP / (FP + TN)."""
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    return fp / (fp + tn) if (fp + tn) > 0 else 0.0


def entrenar_xgboost(X_train, y_train, cv_folds=5):
    """GridSearch + CV de 5 pliegues para seleccion de hiperparametros (Fase 6)."""
    param_grid = {
        "max_depth": [4, 6, 8],
        "n_estimators": [200, 400],
        "learning_rate": [0.05, 0.1],
    }
    base = xgb.XGBClassifier(
        objective="binary:logistic",
        eval_metric="logloss",
        use_label_encoder=False,
        random_state=42,
        n_jobs=-1,
    )
    skf = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42)
    grid = GridSearchCV(base, param_grid, cv=skf, scoring="accuracy", n_jobs=-1, verbose=1)
    grid.fit(X_train, y_train)
    print(f"Mejores hiperparametros: {grid.best_params_}")
    return grid.best_estimator_


def evaluar(modelo, X_test, y_test, nombre_escenario):
    y_pred = modelo.predict(X_test)
    metrics = {
        "escenario": nombre_escenario,
        "exactitud": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "exhaustividad": recall_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
        "tfp": calcular_tfp(y_test, y_pred),
    }
    return metrics, confusion_matrix(y_test, y_pred)


def graficar_matriz_confusion(cm, nombre_archivo):
    fig, ax = plt.subplots(figsize=(5, 4))
    im = ax.imshow(cm, cmap="Blues")
    for i in range(2):
        for j in range(2):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                     color="white" if cm[i, j] > cm.max() / 2 else "black")
    ax.set_xticks([0, 1]); ax.set_xticklabels(["Benigno", "Phishing"])
    ax.set_yticks([0, 1]); ax.set_yticklabels(["Benigno", "Phishing"])
    ax.set_xlabel("Prediccion"); ax.set_ylabel("Real")
    ax.set_title("Matriz de Confusion - Sistema Hibrido")
    fig.colorbar(im)
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS_DIR, nombre_archivo), dpi=150)
    plt.close(fig)


def graficar_feature_importance(modelo, nombres_features, nombre_archivo, top_n=20):
    importancias = modelo.feature_importances_
    idx_top = np.argsort(importancias)[-top_n:]
    fig, ax = plt.subplots(figsize=(7, 8))
    ax.barh(range(len(idx_top)), importancias[idx_top])
    ax.set_yticks(range(len(idx_top)))
    ax.set_yticklabels([nombres_features[i] for i in idx_top])
    ax.set_xlabel("Importancia (gain)")
    ax.set_title(f"Top {top_n} Features - XGBoost")
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS_DIR, nombre_archivo), dpi=150)
    plt.close(fig)


def correr_pipeline_completo():
    df = pd.read_parquet("../data/corpus_normalizado.parquet")
    train, val, test = particionar(df)

    # --- Features escalares (lexicas + hipervinculos) ---
    train_scalar = construir_features_lexicas_y_links(train)
    val_scalar = construir_features_lexicas_y_links(val)
    test_scalar = construir_features_lexicas_y_links(test)

    scaler = StandardScaler().fit(train_scalar)  # Fase 5: ajustar SOLO sobre train
    train_scalar_s = scaler.transform(train_scalar)
    val_scalar_s = scaler.transform(val_scalar)
    test_scalar_s = scaler.transform(test_scalar)
    joblib.dump(scaler, os.path.join(RESULTS_DIR, "scaler.joblib"))

    # --- TF-IDF (ajustado solo sobre train) ---
    vectorizer, X_tfidf_train, X_tfidf_val = construir_tfidf(
        train["texto_plano"], val["texto_plano"], max_features=5000
    )
    X_tfidf_test = vectorizer.transform(test["texto_plano"])
    joblib.dump(vectorizer, os.path.join(RESULTS_DIR, "tfidf_vectorizer.joblib"))

    nombres_features = COLS_LEXICAS + COLS_HIPERVINCULOS + \
        [f"tfidf_{t}" for t in vectorizer.get_feature_names_out()]

    # ===== ESTUDIO DE ABLACION =====
    n_lex = len(COLS_LEXICAS)
    n_link = len(COLS_HIPERVINCULOS)

    escenarios = {
        "Solo URL": (
            train_scalar_s[:, :n_lex], test_scalar_s[:, :n_lex]
        ),
        "Solo HTML (TF-IDF)": (
            X_tfidf_train, X_tfidf_test
        ),
        "Solo Hipervinculos": (
            train_scalar_s[:, n_lex:n_lex + n_link], test_scalar_s[:, n_lex:n_lex + n_link]
        ),
        "Sistema Hibrido": (
            hstack([csr_matrix(train_scalar_s), X_tfidf_train]).tocsr(),
            hstack([csr_matrix(test_scalar_s), X_tfidf_test]).tocsr(),
        ),
    }

    resultados_ablacion = []
    modelo_hibrido = None
    for nombre, (X_tr, X_te) in escenarios.items():
        print(f"\n=== Entrenando escenario: {nombre} ===")
        modelo = entrenar_xgboost(X_tr, train["label"])
        metrics, cm = evaluar(modelo, X_te, test["label"], nombre)
        resultados_ablacion.append(metrics)
        print(metrics)
        if nombre == "Sistema Hibrido":
            modelo_hibrido = modelo
            graficar_matriz_confusion(cm, "matriz_confusion_hibrido.png")
            joblib.dump(modelo, os.path.join(RESULTS_DIR, "modelo_xgboost_hibrido.joblib"))

    df_ablacion = pd.DataFrame(resultados_ablacion)
    df_ablacion.to_csv(os.path.join(RESULTS_DIR, "tabla_ablacion.csv"), index=False)
    print("\n=== TABLA DE ABLACION ===")
    print(df_ablacion.to_string(index=False))

    # Feature importance solo tiene sentido completo para el escenario hibrido
    if modelo_hibrido is not None:
        graficar_feature_importance(modelo_hibrido, nombres_features, "feature_importance.png")

    with open(os.path.join(RESULTS_DIR, "resumen_corpus.json"), "w") as f:
        json.dump({
            "total_paginas": len(df),
            "benignas": int((df["label"] == 0).sum()),
            "phishing": int((df["label"] == 1).sum()),
            "train": len(train), "val": len(val), "test": len(test),
        }, f, indent=2)

    print(f"\nListo. Resultados guardados en {RESULTS_DIR}/")
    print(" - tabla_ablacion.csv          -> tabla del paper (Seccion 6)")
    print(" - feature_importance.png      -> grafico para el paper")
    print(" - matriz_confusion_hibrido.png-> grafico para el paper")
    print(" - resumen_corpus.json         -> cifras reales del corpus")

    return df_ablacion


if __name__ == "__main__":
    correr_pipeline_completo()
