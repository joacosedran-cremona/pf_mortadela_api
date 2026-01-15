### Inicializar

```bash
python -m venv venv
venv\Scripts\activate
pip install fastapi uvicorn

uvicorn main:app --reload
```

## Dependencias

```bash
pip install fastapi uvicorn mysql-connector-python
```

O usando requirements.txt:

```bash
pip install -r requirements.txt
```

### Limpiar

## pycache

# linux

```bash
find . -type d -name "__pycache__" -exec rm -r {} +
```

# windows

```bash
Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
```

## venv

# linux

```bash
rm -rf venv
```

# windows

```bash
Remove-Item venv -Recurse -Force
```
