"""Verificador robusto de notebooks: ejecuta de corrido y valida.

- Ejecuta cada notebook con nbconvert y comprueba:
  1. codigo de salida 0,
  2. execution_count secuencial (1,2,3,...) en todas las celdas de codigo,
  3. sin ninguna salida de tipo 'error'.
Uso: python notebooks/_verify.py
"""
import json, os, subprocess, sys

# Ruta relativa al directorio del proyecto
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NB = os.path.join(ROOT, "notebooks")
PY = os.path.join(ROOT, ".venv", "Scripts", "python.exe")

TARGETS = [f for f in sorted(os.listdir(NB))
           if f.endswith(".ipynb") and not f.startswith("_")]


def verify(path):
    """Ejecuta un notebook y devuelve (ok, mensaje)."""
    # Ejecutar en modo limpio: guardar una copia temporal y validar esa
    tmp = os.path.join(NB, "_verify_tmp.ipynb")
    cmd = [PY, "-m", "jupyter", "nbconvert", "--to", "notebook",
           "--execute", "--inplace", path]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    nb_path = path
    if res.returncode != 0:
        return False, "exit!=0\n" + (res.stderr[-800:] or res.stdout[-800:])
    with open(nb_path, encoding="utf-8") as f:
        nb = json.load(f)
    code_cells = [c for c in nb["cells"] if c["cell_type"] == "code"]
    counts = [c.get("execution_count") for c in code_cells]
    errors = [i for i, c in enumerate(code_cells)
              if any(o.get("output_type") == "error" for o in c.get("outputs", []))]
    # execution_count debe ser None o secuencial 1..n cuando ejecuto --inplace
    ok_counts = all(c is not None for c in counts) and counts == list(range(1, len(counts) + 1))
    if errors:
        return False, f"error outputs en celdas {errors}"
    if not ok_counts:
        return False, f"execution_count no secuencial: {counts}"
    return True, f"{len(code_cells)} celdas de codigo ejecutadas (1..{len(code_cells)})"


def main():
    results = []
    for fname in TARGETS:
        path = os.path.join(NB, fname)
        ok, msg = verify(path)
        results.append((fname, ok, msg))
        print(f"[{'OK ' if ok else 'FAIL'}] {fname}: {msg}")

    fails = [r for r in results if not r[1]]
    print()
    if fails:
        print(f"{len(fails)} notebook(s) con fallos:")
        for fname, _, msg in fails:
            print(f" - {fname}: {msg[:300]}")
        return 1
    print(f"Todos los notebooks ({len(results)}) ejecutan de corrido y estan validados.")
    return 0


if __name__ == "__main__":
    sys.exit(main())