"""
Fase 1 - Recoleccion y etiquetado
==================================
Descarga URLs de phishing (PhishTank, OpenPhish) y benignas (Tranco top-1M),
luego rastrea cada pagina para obtener su HTML dentro de las 24hs.

Fuentes:
- PhishTank:  https://data.phishtank.com/data/online-valid.csv
- OpenPhish:  https://openphish.com/feed.txt
- Tranco:     https://tranco-list.eu/  (descargar CSV manualmente, ver abajo)

NOTA IMPORTANTE PARA EL EQUIPO:
- PhishTank requiere registrarse (gratis) para descargas continuas sin rate-limit.
- OpenPhish community feed se actualiza cada 6-12hs y tiene ~500 URLs vigentes
  en un momento dado (no miles), asi que para juntar volumen hay que correr
  este script varias veces a lo largo de varios dias y ACUMULAR resultados.
- Tranco: bajar el CSV desde https://tranco-list.eu/ (boton "Download CSV"),
  o usar la API: https://tranco-list.eu/api/lists/date/YYYY-MM-DD
"""
import requests
import pandas as pd
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

DATA_DIR = "../data"
os.makedirs(DATA_DIR, exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
TIMEOUT = 30  # segundos, como especifica el paper


def descargar_phishtank():
    """Descarga el feed CSV de PhishTank (URLs verificadas activas)."""
    url = "https://data.phishtank.com/data/online-valid.csv"
    try:
        df = pd.read_csv(url)
        df = df.rename(columns={"url": "url"})[["url"]]
        df["label"] = 1
        df["fuente"] = "phishtank"
        print(f"PhishTank: {len(df)} URLs descargadas")
        return df
    except Exception as e:
        print(f"Error descargando PhishTank: {e}")
        print("-> Si falla, registrate gratis en https://phishtank.org/ y usa tu API key:")
        print("   https://data.phishtank.com/data/<API_KEY>/online-valid.csv")
        return pd.DataFrame(columns=["url", "label", "fuente"])


def descargar_openphish():
    """Descarga el feed de texto plano de OpenPhish (community feed, gratis)."""
    url = "https://openphish.com/feed.txt"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        urls = [u.strip() for u in resp.text.splitlines() if u.strip()]
        df = pd.DataFrame({"url": urls})
        df["label"] = 1
        df["fuente"] = "openphish"
        print(f"OpenPhish: {len(df)} URLs descargadas")
        return df
    except Exception as e:
        print(f"Error descargando OpenPhish: {e}")
        return pd.DataFrame(columns=["url", "label", "fuente"])


def cargar_tranco(csv_path, n=5000):
    """
    Carga la lista Tranco desde un CSV descargado manualmente.
    Formato esperado: dos columnas sin header: rank,domain
    Descargar desde: https://tranco-list.eu/ -> 'Download CSV'
    """
    if not os.path.exists(csv_path):
        print(f"AVISO: no se encontro {csv_path}.")
        print("Descarga el CSV de Tranco desde https://tranco-list.eu/ y guardalo ahi.")
        return pd.DataFrame(columns=["url", "label", "fuente"])
    df = pd.read_csv(csv_path, names=["rank", "domain"])
    df = df.head(n).copy()
    df["url"] = "http://" + df["domain"].astype(str)
    df["label"] = 0
    df["fuente"] = "tranco"
    print(f"Tranco: {len(df)} dominios benignos cargados (top {n})")
    return df[["url", "label", "fuente"]]


def rastrear_url(url, label, fuente):
    """Descarga el HTML de una URL. Descarta 4xx/5xx o timeout > 30s (Fase 1)."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, verify=False, allow_redirects=True)
        if resp.status_code >= 400:
            return None
        return {
            "url": url,
            "label": label,
            "fuente": fuente,
            "html": resp.text,
            "status_code": resp.status_code,
            "timestamp_rastreo": datetime.utcnow().isoformat(),
        }
    except Exception:
        return None


def rastrear_corpus(df_urls, max_workers=20, out_path=None):
    """Rastrea en paralelo todas las URLs del dataframe y guarda el HTML crudo."""
    resultados = []
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futuros = {
            ex.submit(rastrear_url, row.url, row.label, row.fuente): row.url
            for row in df_urls.itertuples()
        }
        completados = 0
        for fut in as_completed(futuros):
            r = fut.result()
            completados += 1
            if r is not None:
                resultados.append(r)
            if completados % 100 == 0:
                print(f"  rastreadas {completados}/{len(df_urls)} - validas: {len(resultados)}")

    df_out = pd.DataFrame(resultados)
    print(f"\nRastreo finalizado: {len(df_out)}/{len(df_urls)} paginas validas "
          f"({len(df_out)/max(len(df_urls),1)*100:.1f}%)")
    if out_path:
        df_out.to_parquet(out_path, index=False)
        print(f"Guardado en {out_path}")
    return df_out


if __name__ == "__main__":
    print("=== Fase 1: Recoleccion y etiquetado ===\n")

    df_phishtank = descargar_phishtank()
    df_openphish = descargar_openphish()
    df_tranco = cargar_tranco(os.path.join(DATA_DIR, "tranco_top1m.csv"), n=5000)

    df_urls = pd.concat([df_phishtank, df_openphish, df_tranco], ignore_index=True)
    df_urls = df_urls.drop_duplicates(subset="url").reset_index(drop=True)
    print(f"\nTotal URLs unicas a rastrear: {len(df_urls)}")
    print(df_urls["label"].value_counts())

    df_urls.to_csv(os.path.join(DATA_DIR, "urls_etiquetadas.csv"), index=False)

    # Rastreo real (descomentar cuando esten listos para correrlo - puede tardar)
    # df_corpus = rastrear_corpus(df_urls, out_path=os.path.join(DATA_DIR, "corpus_crudo.parquet"))
