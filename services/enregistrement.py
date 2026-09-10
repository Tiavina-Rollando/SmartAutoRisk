from database.models.base import get_session

from database.models.historique_niveau_risk import HistoriqueNiveauRisk
from database.models.historique_profil import HistoriqueProfil
from database.models.historique_frais import HistoriqueFrais


def insert_profil(r_proprietaire_id, r_date_evaluation, r_profil, r_source):
    session = get_session()

    try:
        profil = HistoriqueProfil(
            proprietaire_id=r_proprietaire_id,
            date_evaluation=r_date_evaluation,
            profil=r_profil,
            source=r_source
        )

        session.add(profil)
        session.commit()
        session.refresh(profil)

        return profil

    except Exception as e:
        session.rollback()
        raise e

    finally:
        session.close()

def insert_risk(r_vehicule_id, r_saison_id, r_niveau_risk, r_source, r_date_evaluation, r_commentaire=None):
    session = get_session()
    try:
        risk = HistoriqueNiveauRisk(
            vehicule_id=r_vehicule_id,
            saison_id=r_saison_id,
            niveau_risk=r_niveau_risk,
            source=r_source,
            date_evaluation=r_date_evaluation,
            commentaire=r_commentaire
        )

        session.add(risk)
        session.commit()
        session.refresh(risk)

        return risk

    except Exception as e:
        session.rollback()
        raise e

    finally:
        session.close()

def insert_frais(r_frais, r_historique_niveau_risk_id):
    session = get_session()

    try:
        frais = HistoriqueFrais(
            frais=r_frais,
            historique_niveau_risk_id=r_historique_niveau_risk_id
        )   

        session.add(frais)
        session.commit()
        session.refresh(frais)

        return frais

    except Exception as e:
        session.rollback()
        raise e

    finally:
        session.close()