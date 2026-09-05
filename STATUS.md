# Estado del proyecto — Status / Punto de retoma

> **Autor:** Diego Ospina | **Proyecto:** Análisis del dataset brasileño Olist E-Commerce (portafolio)
> **Idioma objetivo:** mixto — comentarios de código en **español**, títulos/narrativa y README en **inglés**.

Este archivo documenta **dónde va el trabajo** para poder retomarlo sin perder contexto.

---

## ✅ Lo que ya está hecho y verificado

### Infraestructura
- **Dependencias instaladas** en `.venv/` y añadidas a `requirements.txt`:
  `pandas`, `numpy`, `matplotlib`, `seaborn`, `jupyter`, `scipy`, `scikit-learn`, `pyarrow`.
- Motor de parquet disponible (`pyarrow`) para guardar/leer `data/processed/*.parquet`.

### Código base para construir notebooks
- `notebooks/_nbgen.py` — helper que genera `.ipynb` de forma consistente:
  `md(text)` → celda markdown, `code(text)` → celda de código,
  `write_nb(path, cells)` → escribe el notebook con `id` determinista por celda.
- `notebooks/_gen01.py` — genera `01_data_understanding.ipynb`.

### Notebook 01 — `notebooks/01_data_understanding.ipynb` ✅ (FINALIZADO)
- **Ejecutó de corrido sin errores** (verificado con `jupyter nbconvert --execute`).
- Contenido:
  - Setup + paths de carpetas.
  - Carga de las 9 tablas crudas.
  - Inventario (filas × columnas) y memoria.
  - Granularidad (order / order_item / payment / review).
  - Diccionario de datos (dtypes por tabla).
  - Calidad: nulos (absolutos y relativos), duplicados.
  - Integridad referencial (huérfanos por par de tablas).
  - Distribución de `order_status`.
  - Rango temporal (sep-2016 → oct-2018).
  - Takeaways.

### Datos procesados — `data/processed/` ✅ (GENERADOS con la lógica validada)
Estos archivos ya existen en disco y son la **base para los notebooks 03→06**:

| Archivo | Gusto / descripción |
|---|---|
| `olist_master_orders.parquet` | 99,441 × 33, grano **orden**. Fechas parseadas, año/mes, métricas de entrega (days, delay, status), agregados de pagos, reseñas y items. |
| `olist_items.parquet` | 112,650 × 10, grano **order_item**. Precio+flete, `item_category` (EN). |
| `olist_catalog.parquet` | 32,951 × 11, catálogo limpio con columna `category` (EN) y `category_pt`. |
| `olist_geolocation_clean.parquet` | 19,015 zip → lat/lng (dedup + mediana). |
| `product_category_name_translation.parquet` | 73 traducciones PT→EN (incluye 2 manuales: `pc_gamer`, `portable_kitchen_appliances`). |

> **Importante:** `.gitignore` ignora `data/processed/*`, así que estos parquet **no se versionan**. El notebook 02 debe **regenerarlos** desde `data/raw/`. La lógica exacta ya quedó como **script reproducible** en `src/build_processed.py` (ejecutable con `python src/build_processed.py`), que es la misma que replicará el notebook 02.

### Script reproducible de limpieza — `src/build_processed.py` ✅
- Convierte la lógica validada en un pipeline con funciones reutilizables y `main()`.
- Regenera los 5 parquet de `data/processed/` desde `data/raw/` (idempotente).
- **Verificado con éxito:** regenera `olist_master_orders.parquet` (99,441×33), `olist_items` (112,650×10), `olist_catalog` (32,951×11), `olist_geolocation_clean` (19,015×4), `translation` (73×2).
- El notebook 02 repl_cará/reutilizará esta misma lógica.

---

## 🔜 Lo que falta por hacer (en orden)

1. **`notebooks/02_cleaning_preprocessing.ipynb`** *(EN PROGRESO)*
   - Replicar en un notebook profesional (markdown EN + código con comentarios ES) la lógica que ya está **validada y funcional** en `src/build_processed.py`.
   - Paso 1: recargar crudos desde `data/raw/` (idempotente, sobrescribe `data/processed/`).
   - Paso 2: limpieza geolocation (dedup), products (renombrar `lenght`, categorías, `not_specified`, 2 nulos de dimensiones), orders (fechas, año/mes, métricas de entrega).
   - Paso 3: agregaciones de pagos y reseñas a grano orden.
   - Paso 4: construir `master_orders`, `items`, `catalog`, `geolocation_clean`, `translation`.
   - Validar que ejecute de corrido con nbconvert.

2. **`notebooks/03_eda_visualizations.ipynb`**
   - Leer `data/processed/olist_master_orders.parquet` (+ `items`, `catalog`).
   - Ventas por mes/año, top categorías, distribución de precios/flete, estados de entrega, geografía (estados BR), guardar figuras en `images/`.

3. **`notebooks/04_statistical_analysis.ipynb`**
   - SciPy: correlaciones, test de hipótesis (t-de Student, chi2), distribución de review_score, relación precio↔retraso, etc.

4. **`notebooks/05_business_intelligence.ipynb`**
   - RFM, análisis de cohortes (retención), Customer Lifetime Value, top vendedores/productos, pagos, métricas key.

5. **`notebooks/06_predictive_modeling.ipynb`**
   - scikit-learn: clasificación (predicción de *pedido tardío*) y regresión (valor de pedido).
   - EDA for ML, pipeline (imputación, escalado, one-hot), validación cruzada, feature importance.

6. **SQL** — `sql/` con script de esquema (`CREATE TABLE`) y consultas de análisis; notebook de muestra pandas+SQL.

7. **`notebooks/07_conclusions.ipynb`** — resumen ejecutivo y hallazgos.

8. **`README.md`** (inglés) — documentación del proyecto.

9. Verificar todos los notebooks de corrido.

---

## 🚀 Cómo retomar (instrucciones para la próxima sesión)

1. **Abrir el proyecto** en `C:\Users\Diego\Documents\GHProjects\ecommerce-data-analysis` con la tool de leer/editar archivos.
2. **Contexto esencial:** el objetivo es construir un proyecto **completo de portafolio** (7 notebooks + SQL + README), idioma **mixto** (comentarios ES, títulos/README EN), que **cada notebook ejecute de corrido**.
3. **El dato clave ya está:** `data/processed/` contiene los datasets limpios; el notebook 02 debe regenerarlos desde crudos (NO depender de parquet que quedó en disco).
4. **Patrón de construcción de notebooks:** usar `_nbgen.py` (md/code/write_nb). **Cuidado crítico:**
   - La fuente de cada celda de código debe pasarse como cadena con `\n` reales (el bug de newline ya se resolvió usando `source` como *string único*, no lista).
   - **No** editar `_genNN.py` con `Set-Content` de PowerShell: **corrompe el UTF-8** de caracteres especiales (— → ·). Usar siempre la tool de **write/edit** del agente.
5. **Verificación por cada notebook:** `.venv\Scripts\python.exe -m jupyter nbconvert --to notebook --execute --inplace notebooks\NN_*.ipynb` y comprobar que no haya celdas con `error`.