from database.models.historique_frais import HistoriqueFrais
from database.models.base import get_session
from database.models.proprietaire import Proprietaire
from database.models.vehicule import Vehicule
from database.models.saison import Saison
from database.models.historique_niveau_risk import HistoriqueNiveauRisk
from sqlalchemy.orm import joinedload

from contextlib import contextmanager

@contextmanager
def session_scope():
    session = get_session()
    try:
        yield session
    finally:
        session.close()

def get_owner(owner_id):
    session = get_session()

    owner = session.get(Proprietaire, owner_id)

    session.close()

    return owner

from sqlalchemy.orm import joinedload

def get_vehicle(vehicle_id):
    session = get_session()


    vehicle = (
        session.query(Vehicule)
        .options(
            joinedload(Vehicule.proprietaire)
                .joinedload(Proprietaire.profils),

            joinedload(Vehicule.risques)
                .joinedload(HistoriqueNiveauRisk.saison),

            joinedload(Vehicule.risques)
                .joinedload(HistoriqueNiveauRisk.frais)
                .joinedload(HistoriqueFrais.historique_risk)
                .joinedload(HistoriqueNiveauRisk.saison),
        )
        .filter(Vehicule.id == vehicle_id)
        .first()
    )

    session.close()
    return vehicle
def get_all_seasons():
    session = get_session()

    seasons = session.query(Saison).all()

    session.close()

    return seasons

def get_niveau_risque(vehicle_id):
    with session_scope() as session:

        return session.query(HistoriqueNiveauRisk)\
            .options(
                joinedload(HistoriqueNiveauRisk.saison),
                joinedload(HistoriqueNiveauRisk.vehicule)
            )\
            .filter(HistoriqueNiveauRisk.vehicule_id == vehicle_id)\
            .all()
    