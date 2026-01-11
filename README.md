# StreamEvents

## 📌 Descripció

**StreamEvents** és una aplicació web desenvolupada amb **Django** que
permet la gestió d'esdeveniments en directe amb un **sistema de xat en
temps real** per a la interacció entre usuaris.

El projecte està orientat a l'aprenentatge de bones pràctiques amb
Django, integració amb **MongoDB mitjançant Djongo**, comunicació
**frontend-backend amb JSON** i ús de **JavaScript (Fetch API)** per
simular funcionalitats en temps real mitjançant *polling*.

------------------------------------------------------------------------

## 🎯 Objectius del Projecte

-   Desenvolupar una aplicació Django modular i escalable.
-   Implementar un **sistema de xat en directe** associat als
    esdeveniments.
-   Treballar amb **CustomUser** i permisos.
-   Utilitzar **MongoDB** com a base de dades.
-   Comunicar frontend i backend amb **JSON (API REST)**.
-   Aplicar validacions, seguretat i bones pràctiques (CSRF, XSS, soft
    delete).
-   Simular temps real mitjançant *polling* amb JavaScript.

------------------------------------------------------------------------

## 🧱 Stack Tecnològic

-   **Backend:** Django 5\
-   **Base de dades:** MongoDB\
-   **Connector MongoDB:** Djongo / pymongo\
-   **Frontend:** HTML + Bootstrap 5\
-   **JavaScript:** Fetch API (polling)\
-   **Altres llibreries:** python-dotenv, Pillow

------------------------------------------------------------------------

## 📂 Estructura del Projecte

``` bash
streamevents/
├─ manage.py
├─ config/
├─ users/
├─ events/
├─ chat/
│  ├─ models.py
│  ├─ views.py
│  ├─ forms.py
│  ├─ urls.py
│  ├─ templates/chat/
│  │  └─ includes/chat_box.html
│  └─ static/chat/
│     ├─ js/chat.js
│     └─ css/chat.css
├─ templates/
│  └─ base.html
├─ static/
├─ media/
├─ requirements.txt
├─ .gitignore
├─ env.example
└─ README.md
```

------------------------------------------------------------------------

## ⚙️ Requisits previs

-   Python 3.10 o superior\
-   pip\
-   Entorn virtual (venv)\
-   MongoDB actiu a `localhost:27017`

------------------------------------------------------------------------

## 🚀 Instal·lació

``` bash
git clone https://github.com/usuari/streamevents.git
cd streamevents
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp env.example .env
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

------------------------------------------------------------------------

## 💬 Sistema de Xat en Directe

-   Enviament de missatges durant esdeveniments en estat **live**
-   Polling cada 3 segons
-   Validació de missatges
-   Eliminació amb permisos (soft delete)
-   Protecció CSRF i XSS
-   Disseny responsive

------------------------------------------------------------------------

## 🧪 Seeds

``` bash
python manage.py seed_users
python manage.py seed_users --users 20
python manage.py seed_users --users 15 --clear
```

------------------------------------------------------------------------
