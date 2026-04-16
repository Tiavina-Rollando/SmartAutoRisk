# SmartAutoRisk
Projet universitaire M2 : Application intelligente d’évaluation du risque automobile
Après avoir cloné
Python 3.12.10
SQL port 3307
DBName : smartautorisk 

python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
Lancer serveur SQL
créer db "smartautorisk" via phpMyAdmin ou autre
alembic init migrations
alembic upgrade head
Lancer appli : py main.py
