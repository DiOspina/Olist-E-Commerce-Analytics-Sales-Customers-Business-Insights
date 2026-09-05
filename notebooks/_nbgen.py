"""Helper minimo para construir notebooks de forma consistente.

- `md(text)`  -> celda markdown
- `code(text)`-> celda de codigo (sin salida)
- `write_nb()`-> escribe el .ipynb con celdas e ids deterministas
"""
import json, os, hashlib

NB_META = {
    "kernelspec": {
        "display_name": "Python 3 (ipykernel)",
        "language": "python",
        "name": "python3"
    },
    "language_info": {
        "codemirror_mode": {"name": "ipython", "version": 3},
        "file_extension": ".py",
        "mimetype": "text/x-python",
        "name": "python",
        "nbconvert_exporter": "python",
        "pygments_lexer": "ipython3",
        "version": "3.10.11"
    }
}


def _cell_id(src):
    # Id determinista a partir del contenido: estable entre ejecuciones.
    h = hashlib.sha1(src.encode("utf-8")).hexdigest()[:16]
    return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[6:10]}-{h[10:16]}"


def md(src):
    return {"cell_type": "markdown", "metadata": {}, "source": src, "id": _cell_id(src)}


def code(src):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": src, "id": _cell_id(src)}


def write_nb(path, cells):
    nb = {"cells": cells, "metadata": NB_META, "nbformat": 4, "nbformat_minor": 5}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    print("wrote", path)