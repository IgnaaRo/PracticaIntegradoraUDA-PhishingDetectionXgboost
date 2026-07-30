# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, ListFlowable, ListItem, HRFlowable
)
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER

OUT = "/mnt/user-data/outputs/CACIC2026_GRUPO6_cambios_necesarios.pdf"

doc = SimpleDocTemplate(
    OUT, pagesize=letter,
    topMargin=0.8*inch, bottomMargin=0.8*inch,
    leftMargin=0.85*inch, rightMargin=0.85*inch,
)

styles = getSampleStyleSheet()

title_style = ParagraphStyle("TitleX", parent=styles["Title"], fontSize=16, spaceAfter=4)
subtitle_style = ParagraphStyle("Subtitle", parent=styles["Normal"], fontSize=10.5,
                                 textColor=colors.HexColor("#555555"), spaceAfter=18)
h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=13.5, spaceBefore=18, spaceAfter=8,
                     textColor=colors.HexColor("#1a1a1a"))
h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=11.5, spaceBefore=12, spaceAfter=6,
                     textColor=colors.HexColor("#2a2a2a"))
body = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10, leading=14.5, alignment=TA_JUSTIFY,
                       spaceAfter=8)
small = ParagraphStyle("Small", parent=styles["Normal"], fontSize=8.7, leading=12, textColor=colors.HexColor("#444444"))
note_box = ParagraphStyle("Note", parent=styles["Normal"], fontSize=9.5, leading=13.5,
                           backColor=colors.HexColor("#fff8e1"), borderColor=colors.HexColor("#e0c068"),
                           borderWidth=0.7, borderPadding=8, spaceAfter=10, spaceBefore=4)
warn_box = ParagraphStyle("Warn", parent=styles["Normal"], fontSize=9.5, leading=13.5,
                           backColor=colors.HexColor("#fdeaea"), borderColor=colors.HexColor("#cc4444"),
                           borderWidth=0.7, borderPadding=8, spaceAfter=10, spaceBefore=4)
ok_box = ParagraphStyle("Ok", parent=styles["Normal"], fontSize=9.5, leading=13.5,
                         backColor=colors.HexColor("#eaf6ec"), borderColor=colors.HexColor("#4a9c5d"),
                         borderWidth=0.7, borderPadding=8, spaceAfter=10, spaceBefore=4)
code_style = ParagraphStyle("Code", parent=styles["Normal"], fontName="Courier", fontSize=8.7,
                             leading=12, backColor=colors.HexColor("#f4f4f4"), borderPadding=6,
                             spaceAfter=10)

story = []

# ---------------------------------------------------------------
story.append(Paragraph("Hoja de ruta de cambios — CACIC 2026, Grupo 6", title_style))
story.append(Paragraph(
    "Detección de phishing mediante análisis híbrido de URLs y contenido web<br/>"
    "Documento de trabajo para incorporar al paper antes de la entrega",
    subtitle_style
))
story.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#cccccc")))
story.append(Spacer(1, 10))

story.append(Paragraph(
    "Este documento resume los cambios necesarios para responder a la revisión recibida. "
    "Las cifras incluidas en las secciones 2 y 3 son las que ustedes obtuvieron al correr el "
    "pipeline real (notebook + scripts entregados) sobre un corpus propio de 6.417 páginas "
    "(PhishTank + OpenPhish + Tranco top-5000). No hay ningún número proyectado, estimado ni "
    "tomado de los papers de referencia: todo lo que sigue salió de su propia ejecución en Colab.",
    body
))

# =================================================================
story.append(Paragraph("1. Corrección de tiempos verbales y consistencia propuesta/resultados", h1))

story.append(Paragraph(
    "El problema señalado por el revisor era real: el resumen y la Sección 5 hablan en futuro "
    "(\"propondrá\", \"Metodología Propuesta\") mientras que la Sección 6 reporta resultados como "
    "hechos consumados. Ahora que el experimento se ejecutó de verdad, hay que unificar todo el "
    "documento en pasado/presente de hallazgo, no en futuro de propuesta.",
    body
))

cambios_tiempo = [
    ("Resumen", "\"La presente investigación propondrá un sistema...\"",
     "\"La presente investigación propone y evalúa un sistema...\" "
     "(ya no es propuesta a futuro, es un sistema implementado y evaluado)"),
    ("Resumen", "\"Se espera superar el 96% de exactitud...\"",
     "Reemplazar por la cifra real obtenida: \"El sistema híbrido alcanzó 99,69% de exactitud "
     "con una TFP de 0,67% sobre el corpus evaluado.\""),
    ("Sección 5 (título)", "\"Metodología Propuesta\"",
     "\"Metodología\" (sin \"Propuesta\" — ya se ejecutó, no es una propuesta)"),
    ("Sección 1.5 Hipótesis", "Redactada en términos de lo que la fusión \"produce\"",
     "Mantener el tiempo presente pero agregar al final de la sección una oración que indique "
     "si la hipótesis se confirmó o se confirmó parcialmente (ver Sección 3 de este documento, "
     "es importante leerla antes de escribir esta parte)"),
]
for ubic, antes, despues in cambios_tiempo:
    story.append(Paragraph(f"<b>{ubic}</b>", h2))
    story.append(Paragraph(f"<i>Antes:</i> {antes}", body))
    story.append(Paragraph(f"<i>Después:</i> {despues}", body))

story.append(Paragraph(
    "Revisión general sugerida: buscar en todo el documento las palabras \"propondrá\", \"propone "
    "un sistema que combinará\", \"clasificadas mediante\" en sentido futuro, y pasarlas a presente "
    "o pretérito perfecto compuesto (\"se combinó\", \"se clasificó\", \"se obtuvo\").",
    body
))

# =================================================================
story.append(PageBreak())
story.append(Paragraph("2. Corpus real utilizado (reemplaza la cifra de la Sección 6)", h1))

story.append(Paragraph(
    "La Sección 6 actual dice \"El corpus experimental contiene 60.252 páginas web etiquetadas\". "
    "Esa cifra corresponde a una escala mayor a la efectivamente recolectada por el equipo. "
    "Reemplazarla por el tamaño real:",
    body
))

corpus_data = [
    ["Fuente", "URLs descargadas", "Etiqueta"],
    ["PhishTank (feed online-valid.csv)", "65.913", "Phishing"],
    ["OpenPhish (feed.txt)", "300", "Phishing"],
    ["Tranco top-5000", "5.000", "Benigno"],
    ["Subtotal antes de muestreo/rastreo", "71.213", "—"],
    ["Muestra de phishing tomada (random, seed=42)", "5.000", "Phishing"],
    ["Total URLs enviadas a rastreo", "≈10.000", "Mixto"],
    ["Páginas con HTML válido tras rastreo (24h, timeout 30s)", "6.417 (65,2%)", "—"],
    ["→ Phishing en corpus final", "3.505", "Phishing"],
    ["→ Benignas en corpus final", "3.014", "Benigno"],
]
t = Table(corpus_data, colWidths=[3.3*inch, 1.7*inch, 1.2*inch])
t.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#2c3e50")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONTSIZE", (0,0), (-1,-1), 8.7),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f2f2f2")]),
    ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#bbbbbb")),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("ALIGN", (1,0), (2,-1), "CENTER"),
    ("TOPPADDING", (0,0), (-1,-1), 4),
    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
]))
story.append(t)
story.append(Spacer(1, 8))

story.append(Paragraph(
    "Texto sugerido para reemplazar el primer párrafo de la Sección 6:",
    body
))
story.append(Paragraph(
    "<i>\"El corpus experimental se construyó a partir de los feeds de PhishTank y OpenPhish "
    "(71.213 URLs de phishing recolectadas) y la lista Tranco top-5000 para páginas benignas. "
    "Debido al desbalance inicial, se tomó una muestra aleatoria de 5.000 URLs de phishing "
    "(semilla fija para reproducibilidad). Cada página se rastreó dentro de las 24 horas "
    "siguientes a su recolección, descartando errores HTTP y tiempos de espera superiores a "
    "30 segundos, lo que resultó en un corpus final de 6.417 páginas: 3.505 de phishing (54,6%) "
    "y 3.014 benignas (45,4%).\"</i>",
    note_box
))

story.append(Paragraph(
    "Importante: esta cifra (6.417) es menor que la mencionada originalmente (60.252). Esto no es "
    "un problema si el paper se presenta en la categoría de artículo corto / reporte de avance, "
    "y de hecho es más defendible que una cifra que el equipo no puede sustentar con datos propios. "
    "Si quieren ampliar el corpus más adelante, el mismo notebook permite correr la Fase 1 varias "
    "veces y acumular más páginas (ver README del repositorio).",
    warn_box
))

# =================================================================
story.append(Paragraph("3. Estudio de ablación — tabla real (reemplaza el párrafo de ablación)", h1))

story.append(Paragraph(
    "Esta es la tabla que pedía explícitamente el revisor. Insertar como Tabla 1 en la Sección 6, "
    "con esta leyenda: <i>\"Tabla 1. Resultados del estudio de ablación sobre el conjunto de prueba "
    "(963 páginas, partición estratificada 70/15/15).\"</i>",
    body
))

ablacion_data = [
    ["Escenario", "Exactitud", "Precisión", "Exhaustividad", "F1", "TFP"],
    ["Solo URL", "99,38%", "99,61%", "99,23%", "0,9942", "0,45%"],
    ["Solo HTML (TF-IDF)", "92,32%", "93,69%", "91,88%", "0,9277", "7,17%"],
    ["Solo Hipervínculos", "88,37%", "85,84%", "93,81%", "0,8965", "17,94%"],
    ["Sistema Híbrido", "99,69%", "99,42%", "100,00%", "0,9971", "0,67%"],
]
t2 = Table(ablacion_data, colWidths=[1.6*inch, 0.9*inch, 0.9*inch, 1.0*inch, 0.7*inch, 0.7*inch])
t2.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#2c3e50")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONTSIZE", (0,0), (-1,-1), 8.7),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTNAME", (0,4), (-1,4), "Helvetica-Bold"),
    ("BACKGROUND", (0,4), (-1,4), colors.HexColor("#dbe9f0")),
    ("ROWBACKGROUNDS", (0,1), (-1,3), [colors.white, colors.HexColor("#f2f2f2")]),
    ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#bbbbbb")),
    ("ALIGN", (1,0), (-1,-1), "CENTER"),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("TOPPADDING", (0,0), (-1,-1), 5),
    ("BOTTOMPADDING", (0,0), (-1,-1), 5),
]))
story.append(t2)
story.append(Spacer(1, 10))

story.append(Paragraph(
    "ATENCIÓN — esto requiere ajustar la narrativa de la Sección 6 y la Hipótesis (1.5), no solo "
    "insertar la tabla:",
    h2
))
story.append(Paragraph(
    "El texto original del paper afirma que \"ninguna fuente de señal es suficiente por sí sola\" "
    "y que la fusión \"produce una tasa de falsos positivos significativamente menor que cualquiera "
    "de esos grupos utilizado en forma aislada\". <b>Sus resultados reales muestran algo distinto</b>: "
    "el escenario Solo URL ya alcanza 99,38% de exactitud y apenas 0,45% de TFP — un resultado "
    "altísimo por sí solo, comparable al del Sistema Híbrido (99,69% / 0,67%). La mejora del "
    "híbrido sobre Solo-URL es real pero marginal en exactitud, y la TFP del híbrido (0,67%) es "
    "incluso ligeramente más alta que la de Solo-URL (0,45%) — aunque el híbrido sí logra "
    "exhaustividad perfecta (100%, cero falsos negativos), que es donde se nota la verdadera "
    "ganancia de combinar las tres fuentes.",
    warn_box
))

story.append(Paragraph(
    "Texto sugerido para reemplazar el párrafo correspondiente de la Sección 6:",
    body
))
story.append(Paragraph(
    "<i>\"El estudio de ablación (Tabla 1) muestra que las características léxicas de URL son, "
    "por sí solas, altamente discriminativas en este corpus (99,38% de exactitud, 0,45% de TFP), "
    "superando ampliamente a los escenarios basados solo en TF-IDF del HTML (92,32%) o solo en "
    "indicadores de hipervínculos (88,37%). El sistema híbrido mejora la exactitud global y, en "
    "particular, logra exhaustividad perfecta (100%) sobre el conjunto de prueba, sin falsos "
    "negativos, a un costo marginal en TFP (0,67% vs. 0,45% de Solo-URL). Este resultado matiza "
    "la hipótesis inicial: la combinación de fuentes no reduce la TFP por debajo de la del mejor "
    "grupo individual en este corpus, pero sí aporta robustez frente a falsos negativos, que es "
    "la categoría de error más costosa en un sistema de detección de phishing real.\"</i>",
    note_box
))

story.append(Paragraph(
    "También hay que ajustar el cierre de la Sección 1.5 (Hipótesis) agregando una oración que "
    "indique que la hipótesis se confirmó parcialmente: la fusión sí logra el mejor desempeño "
    "global y exhaustividad perfecta, pero no produce la TFP más baja de todas (ese lugar lo "
    "ocupa Solo-URL en este corpus específico). Es preferible declarar esto explícitamente a que "
    "un revisor lo note por su cuenta comparando la Tabla 1 con el texto.",
    body
))

# =================================================================
story.append(PageBreak())
story.append(Paragraph("4. Gráfico de Feature Importance (pedido explícito del revisor)", h1))

story.append(Paragraph(
    "Insertar como Figura 1 en la Sección 6, con esta leyenda: <i>\"Figura 1. Importancia de "
    "características (ganancia) para las 12 variables escalares del modelo híbrido — características "
    "léxicas de URL e indicadores de hipervínculos.\"</i>",
    body
))

try:
    story.append(Image("/home/claude/phishing-xgboost/results/feature_importance_escalares.png",
                        width=4.6*inch, height=3.3*inch))
except Exception:
    story.append(Paragraph("[Insertar aquí results/feature_importance_escalares.png]", body))

story.append(Spacer(1, 6))
story.append(Paragraph(
    "Nota metodológica importante: el gráfico completo de feature importance generado por el "
    "pipeline (incluyendo las ~5.000 columnas de TF-IDF) está dominado por n-gramas de caracteres "
    "sueltos (ej. fragmentos de 2-3 caracteres) sin significado interpretable directo para un "
    "analista humano. Por eso se optó por mostrar únicamente las 12 características escalares "
    "(léxicas de URL + hipervínculos), que sí son interpretables y consistentes con el marco "
    "teórico citado (Moncada Vargas [3] ya señalaba la longitud de URL como predictor top). "
    "Esta decisión debe declararse explícitamente en el texto, no solo en el pie de figura — "
    "agregar una oración tipo: <i>\"Para preservar la interpretabilidad discutida en la Sección 6, "
    "la Figura 1 reporta la importancia restringida a las características escalares; las columnas "
    "TF-IDF, aunque incluidas en el entrenamiento, no se individualizan por tratarse de n-gramas "
    "de caracteres sin correspondencia semántica directa.\"</i>",
    note_box
))

story.append(Paragraph(
    "El gráfico muestra que <b>url_longitud</b> concentra la mayor importancia entre las variables "
    "escalares, seguida de <b>url_profundidad_ruta</b> y <b>url_num_subdominios</b> — consistente "
    "con la literatura citada. Varias variables binarias (presencia de IP, símbolo @, etc.) "
    "muestran importancia cercana a cero en este corpus, lo cual vale la pena mencionar como "
    "observación: probablemente refleje que el phishing moderno recolectado (vía hosting gratuito, "
    "subdominios de plataformas legítimas) usa menos esas técnicas \"clásicas\" que las URLs con "
    "IP directa o caracteres @ documentadas en trabajos más antiguos.",
    body
))

# =================================================================
story.append(Paragraph("5. Matriz de confusión (pedido explícito del revisor)", h1))

story.append(Paragraph(
    "Insertar como Figura 2, con leyenda: <i>\"Figura 2. Matriz de confusión del sistema híbrido "
    "sobre el conjunto de prueba (n=963).\"</i>",
    body
))

try:
    story.append(Image("/home/claude/phishing-xgboost/results/matriz_confusion_hibrido.png",
                        width=3.6*inch, height=3.0*inch))
except Exception:
    story.append(Paragraph("[Insertar aquí results/matriz_confusion_hibrido.png]", body))

story.append(Spacer(1, 6))
story.append(Paragraph(
    "Sobre 963 páginas de prueba (446 benignas, 517 phishing): 443 verdaderos negativos, "
    "3 falsos positivos, 0 falsos negativos, 517 verdaderos positivos. El resultado de cero "
    "falsos negativos es notable y debe mencionarse en el texto, pero también matizarse: con "
    "un conjunto de prueba de 963 páginas, \"cero falsos negativos\" no garantiza que el sistema "
    "generalice igual de bien a un volumen mucho mayor o a campañas de phishing más sofisticadas "
    "no representadas en este corpus — es una limitación a declarar en la Sección 6, no a ocultar.",
    body
))

# =================================================================
story.append(PageBreak())
story.append(Paragraph("6. Pendientes que siguen sin resolver", h1))

story.append(Paragraph(
    "Lo que sigue es trabajo que todavía no se hizo y que el revisor también pidió. No se puede "
    "completar el ítem 3 de su hoja de ruta (plantilla LaTeX, .bib, filiación institucional) "
    "desde esta conversación, y dos puntos metodológicos siguen abiertos:",
    body
))

pendientes = [
    "<b>Plantilla LaTeX oficial de CACIC/Springer:</b> migrar el contenido a la plantilla provista, "
    "incluyendo el comando \\institute correcto (no solo los emails) y mover las referencias a un "
    "archivo .bib externo invocado con \\bibliographystyle{} y \\bibliography{}. Esto es trabajo de "
    "edición de LaTeX que el equipo debe hacer directamente sobre la plantilla.",

    "<b>Repositorio público en GitHub:</b> el código entregado (notebook + scripts) está listo para "
    "subir tal cual. Falta que alguien del equipo cree el repo, suba el contenido, y agregue el "
    "link en el paper (sugerido: sección de Reproducibilidad antes de Conclusiones, o nota al pie "
    "en la Sección 5).",

    "<b>Validación temporal / concept drift:</b> el revisor pidió justificar la vigencia del "
    "dataset o, alternativamente, partir los datos cronológicamente (entrenar con datos viejos, "
    "probar con los más recientes). El corpus actual se descargó en una sola pasada (feeds vigentes "
    "al momento de la ejecución), así que no hay todavía variación temporal real para hacer ese "
    "split. Si los feeds de PhishTank/OpenPhish incluyen campo de fecha de detección, se puede "
    "armar esa partición; si no hay tiempo, la alternativa es escribir un párrafo de limitación "
    "honesto explicando que el corpus es de una única ventana temporal (mes/año de recolección) "
    "y que la validación temporal queda como trabajo futuro inmediato.",

    "<b>Decisión de extensión (5 vs. 8 páginas):</b> con datos reales y las tablas/figuras ya "
    "generadas, el equipo está en condiciones de optar por la categoría de Full Paper (8 páginas) "
    "si así lo prefieren, ya que ahora sí pueden incluir matriz de confusión, tabla de ablación "
    "y gráfico de importancia con datos propios, tal como exige esa categoría.",
]

items = [ListItem(Paragraph(p, body), spaceAfter=6) for p in pendientes]
story.append(ListFlowable(items, bulletType="bullet", start="•"))

story.append(Spacer(1, 10))
story.append(Paragraph(
    "Resumen del estado actual: el experimento ya se ejecutó con datos reales propios, y el "
    "paper puede (y debe) reportar esos números en vez de los originales. Lo que falta es trabajo "
    "de redacción/edición (puntos 1-3 de este documento), formato LaTeX, subir el repositorio, "
    "y decidir si se aborda la validación temporal o se declara como limitación.",
    ok_box
))

doc.build(story)
print("PDF generado en", OUT)
