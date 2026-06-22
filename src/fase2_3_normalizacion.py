"""
Fase 2 - Normalizacion
Fase 3 - Tokenizacion
=======================
Limpia el HTML crudo (decodifica UTF-8, quita <script>/<style>/comentarios)
y normaliza las URLs (minusculas, decodificacion percent-encoding).
La tokenizacion de URL por delimitadores y de HTML a nivel de caracter
se deja preparada para el vectorizador TF-IDF en fase 4.
"""
import pandas as pd
import re
import urllib.parse
from bs4 import BeautifulSoup, Comment


def normalizar_url(url: str) -> str:
    """Minusculas + decodificacion de caracteres percent-encoded a ASCII."""
    url = url.lower().strip()
    try:
        url = urllib.parse.unquote(url)
    except Exception:
        pass
    return url


def normalizar_html(html: str) -> dict:
    """
    Decodifica a UTF-8, elimina <script>, <style> y comentarios.
    Devuelve el HTML 'ruidoso' restante (Fase 4 lo usa para TF-IDF a nivel
    de caracter) y tambien el texto visible plano.
    """
    if not isinstance(html, str) or not html.strip():
        return {"html_limpio": "", "texto_plano": ""}

    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style"]):
        tag.decompose()
    for comentario in soup.find_all(string=lambda s: isinstance(s, Comment)):
        comentario.extract()

    html_limpio = str(soup)
    texto_plano = soup.get_text(separator=" ", strip=True)
    texto_plano = re.sub(r"\s+", " ", texto_plano)

    return {"html_limpio": html_limpio, "texto_plano": texto_plano}


# Delimitadores de tokenizacion de URL especificados en el paper (Fase 3)
DELIMITADORES_URL = re.compile(r"[./\-_?=]")


def tokenizar_url(url: str) -> list:
    """Segmenta la URL usando . / - _ ? = como delimitadores."""
    tokens = [t for t in DELIMITADORES_URL.split(url) if t]
    return tokens


def procesar_corpus(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica fases 2 y 3 a todo el corpus crudo."""
    df = df.copy()
    df["url"] = df["url"].apply(normalizar_url)

    normalizados = df["html"].apply(normalizar_html)
    df["html_limpio"] = normalizados.apply(lambda d: d["html_limpio"])
    df["texto_plano"] = normalizados.apply(lambda d: d["texto_plano"])

    df["url_tokens"] = df["url"].apply(tokenizar_url)

    antes = len(df)
    df = df[df["html_limpio"].str.len() > 0].reset_index(drop=True)
    print(f"Filas descartadas por HTML vacio: {antes - len(df)}")

    return df


if __name__ == "__main__":
    df_crudo = pd.read_parquet("../data/corpus_crudo.parquet")
    df_procesado = procesar_corpus(df_crudo)
    df_procesado.to_parquet("../data/corpus_normalizado.parquet", index=False)
    print(f"Fase 2-3 completa: {len(df_procesado)} paginas procesadas")
    print(df_procesado[["url", "label"]].head())
