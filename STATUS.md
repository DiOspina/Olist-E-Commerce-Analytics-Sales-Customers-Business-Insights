# Estado del proyecto — Status / Punto de retoma

> **Autor:** Diego Ospina | **Proyecto:** Análisis del dataset brasileño Olist E-Commerce (portafolio)
> **Idioma:** comentarios de código en **español**, títulos/narrativa y README en **inglés**.

---

## ✅ Estado global (proyecto esencialmente COMPLETO)

| Entregable | Estado |
|---|---|
| `requirements.txt` (pandas, numpy, matplotlib, seaborn, jupyter, scipy, scikit-learn, pyarrow) | ✅ |
| `src/build_processed.py` (pipeline reproducible) | ✅ |
| `data/processed/*.parquet` (5 datasets limpios) | ✅ |
| `notebooks/01_data_understanding.ipynb` | ✅ verificado |
| `notebooks/02_cleaning_preprocessing.ipynb` | ✅ verificado |
| `notebooks/03_eda_visualizations.ipynb` | ✅ verificado (8 figuras en `images/`) |
| `notebooks/04_statistical_analysis.ipynb` | ✅ verificado |
| `notebooks/05_business_intelligence.ipynb` | ✅ verificado (RFM, cohortes, CLV) |
| `notebooks/06_predictive_modeling.ipynb` | ✅ ejecutado con métricas presentables |
| `notebooks/07_conclusions.ipynb` | ✅ ejecutado |
| `notebooks/sql_python_demo.ipynb` | ✅ ejecutado (SQLite + pandas) |
| `sql/schema.sql` + `sql/queries_analysis.sql` | ✅ |
| `README.md` (inglés) | ✅ |
| `STATUS.md` (este) | ✅ |

---

## 📊 Resultados clave (reales, verificados)

- 99,441 pedidos · 96,478 entregados · 96,096 clientes · ~R$15.4M ingreso · AOV R$159.8.
- 8.11% de entregas **tarde**; las tardías tienen **review significativamente menor** (Mann-Whitney U, p<0.001).
- Review medio ~4.09. São Paulo domina; tarjeta de crédito domina pagos.
- RFM: pequeño grupo **VIP/Champion** concentra gran parte del ingreso; gran cola **Lost/At-risk** (mayoría compra 1 vez).
- ML clasificación (pedido tardío): RF ROC-AUC **0.742**, Recall 0.469, Average Precision 0.229 (baseline 0.081).
- ML regresión (valor de pedido): RF R² **0.368**, MAE 77.56 BRL vs baseline mediana 97.00.

---

## 🛠️ Cómo continuar / verificar (próxima sesión)

1. **Verificación final (si aún no corrió):**
   ```
   .venv\Scripts\python.exe notebooks\_verify.py
   ```
   Valida que cada notebook ejecute de corrido con `execution_count` secuencial y sin errores.
   - El verificador re-ejecuta cada notebook; los ML tardan un poco.
   - Resultado esperado: `Todos los notebooks (8) ejecutan de corrido`.

2. **Commit final (opcional pero recomendado):** subir todo a git con mensaje descriptivo.

3. **Mejoras opcionales de portafolio:**
   - Añadir `reports/` con un resumen en PDF/HTML (nbconvert).
   - Añadir un mapa de Brasil (folium/geopandas) con lat/lng de geolocation limpia.
   - Añadir un modelo XGBoost o tuneo de hiperparámetros en el 06.

---

## ⚠️ Lecciones técnicas (IMPORTANTE, evitar repetir)

- **Verificar con `execution_count` secuencial**, no solo buscar `"error"` en outputs: un notebook no ejecutado
  no tiene `execution_count` y pasa como "sin errores".
- **No editar los `_genNN.py` con `Set-Content` de PowerShell**: corrompe el UTF-8 de caracteres especiales.
  Usar siempre la herramienta de write/edit.
- En notebooks, la fuente de cada celda debe ser un **string único con `\n`** (no lista), y los `import`
  multilinea NO deben abrir `(` dentro del literal de la celda (rompe el cierre del string).
- `pd.cut` con cuartiles falla si los bins no son únicos (datos degenerados, ej. frecuencia≈1). Usar
  `pd.qcut(..., duplicates='drop')` para robustez.
- RandomForest con `n_estimators=200`, `cv=5` y `n_jobs=-1` sobre ~70k filas es demasiado lento en esta
  máquina; usar submuestreo estratificado + `n_estimators=150, max_features='sqrt'` para un notebook ágil.

## 🔧 Nota de arquitectura

- `notebooks/_nbgen.py` = helper de construcción de notebooks (md/code/write_nb con ids deterministas).
- `notebooks/_genNN.py` = generadores de cada notebook.
- `notebooks/_verify.py` = verificador robusto de ejecución.
- `src/build_processed.py` = pipeline de limpieza (el notebook 02 lo replica).
- `data/processed` y `data/raw` NO se versionan (`.gitignore`); se regeneran con `src/build_processed.py`.