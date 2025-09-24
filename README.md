# StreamEvents

## Objectius
Aplicació **Django** per gestionar esdeveniments i usuaris de forma extensible.  
Es tracta d’una base educativa amb bones pràctiques: ús d’entorns, estructura clara, separació de `templates`/`static`, i integració opcional de **MongoDB** (via `djongo`).  

### Objectius principals
- Practicar un projecte Django modular.
- Treballar amb un usuari personalitzat (app `users`).
- Organitzar `templates`, `static` i `media` correctament.
- Introduir fitxers d’entorn (`.env`) i bones pràctiques amb Git.
- Preparar el terreny per a futures funcionalitats (API, auth avançada, etc.).

## Stack Principal
- **Backend:** Django 5
- **Base de dades:** MongoDB (opcional)
- **ORM Mongo:** djongo / pymongo
- **Frontend:** Templates HTML + CSS a `static/`
- **Altres:** python-dotenv per gestionar secrets, Pillow per a imatges

## Estructura Simplificada
streamevents/
├─ manage.py
├─ config/
├─ users/
├─ templates/
│ └─ base.html
├─ static/
│ └─ css/
│ └─ main.css
├─ media/
├─ requirements.txt
├─ .gitignore
├─ env.example
└─ README.md


## Requisits previs
- Python 3.10 o superior
- pip
- Entorn virtual (venv)
- MongoDB instal·lat i actiu a `localhost:27017` (si es vol usar)

## Instal·lació ràpida

```bash
# 1. Clonar el repositori
git clone https://github.com/usuari/streamevents.git
cd streamevents

# 2. Crear i activar entorn virtual
python -m venv venv
# Linux/macOS
source venv/bin/activate
# Windows PowerShell
venv\Scripts\Activate.ps1

# 3. Instal·lar dependències
pip install -r requirements.txt

# 4. Configurar variables d'entorn
cp env.example .env

# 5. Instal·la dependències
pip install -r requirements.txt

# 6. Configura fitxer .env
cp env.example .env

# 7. Migracions inicials
python manage.py migrate

# 8. Crea superusuari
python manage.py createsuperuser

# 9. Executa el servidor
python manage.py runserver
````

## Variables d'entorn (env.example)
```bash
SECRET_KEY=canvia-aixo
DEBUG=1
ALLOWED_HOSTS=localhost,127.0.0.1
MONGO_URL=mongodb://localhost:27017
DB_NAME=streamevents_db
````

## Comandes útils
```bash
````

## Migrar a MongoDB
```bash
````

## Fixtures (exemple)
```bash
````

## Seeds (exemple d'script)
```bash
````
