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


REMARQUE : 
- Avant de lancer py main.py, il faut lancer le "venv"
venv\Scripts\activate

- Il ne faut pas oublier de d'arreter la version MSQL80 installer pour le système
 on passe dans la "Gestionnaire des tâches "/services/ MSQL 80 ; et on arette MSQL 80 (port : 3036)
- Pour PHP MyAdmin, pour le code user : root et mot de passe : "il n'y a pas"
- notre BD SmartAutorisk (c'est la version combiné);