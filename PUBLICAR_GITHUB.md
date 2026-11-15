# Publicar en GitHub: EduHerreraC13/Monitoring_Health

URL destino: https://github.com/EduHerreraC13/Monitoring_Health

Abre PowerShell en **esta carpeta**, donde están `index.html`, `README.md` y `servidor_camara.py`.

## Si el repositorio remoto está vacío (sin commits)

```powershell
git init
git branch -M main
git remote add origin https://github.com/EduHerreraC13/Monitoring_Health.git
git add .
git status --short
git commit -m "Initial HEAMON multimodal prototype"
git push -u origin main
```

## Si el repo remoto ya tiene README, commits u otros archivos

**No fuerces el push**: clona y copia los archivos de esta carpeta *sin incluir `.git` ni `.venv`* en el clon; allí:

```powershell
git clone https://github.com/EduHerreraC13/Monitoring_Health.git
cd Monitoring_Health
git add .
git commit -m "Add HEAMON multimodal monitoring prototype"
git push origin main
```

Si tu repositorio ya existe como repo local, desde su carpeta puedes cambiar el remoto al nombre nuevo con:

```powershell
git remote -v
git remote set-url origin https://github.com/EduHerreraC13/Monitoring_Health.git
git status
git add .
git commit -m "Update HEAMON multimodal prototype"
git push -u origin main
```

No ejecutes `git init` dentro de un clon que ya contiene `.git`. Comprueba los archivos antes de `git add .` y verifica que `.gitignore` excluye modelos, biométricos y terceros. Si GitHub pide autenticación, completa el proceso con tu cuenta, nunca incluyas claves personales en commits.
