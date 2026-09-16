import numpy as np
from database.models.accident import Accident
from database.models.accident_vehicule import AccidentVehicule
from database.models.vehicule import Vehicule
from sqlalchemy.orm import Session


def predire_accidents_poisson(
    session: Session, vehicule_id: int, horizon_annees: float = 1.0
):
  """
    Calcule le taux d'accident lambda historique d'un véhicule 
    et simule les accidents futurs via la loi de Poisson.
    """
  vehicule = (
      session.query(Vehicule).filter(Vehicule.id == vehicule_id).first()
  )

  if not vehicule:
    raise ValueError(f"Aucun véhicule trouvé avec l'ID {vehicule_id}")

  # Récupération des accidents liés à ce véhicule via la table de jointure
  accidents_vehicule = (
      session.query(Accident)
      .join(Accident.vehicules)
      .filter(AccidentVehicule.vehicule_id == vehicule_id)
      .all()
  )

  total_accidents_passes = len(accidents_vehicule)

  # Période d'observation de référence (ex: 1 an)
  periode_observation_ans = 1.0
  lambda_estime = (
      total_accidents_passes / periode_observation_ans
      if periode_observation_ans > 0
      else 0.0
  )

  # Paramètre lambda pour l'horizon temporel voulu
  lambda_futur = lambda_estime * horizon_annees

  # Simulation stochastique par la loi de Poisson
  nb_accidents_simule = np.random.poisson(lam=lambda_futur)

  # Génération de 1000 scénarios pour évaluer la probabilité d'avoir 0 accident
  scenarios = np.random.poisson(lam=lambda_futur, size=1000)
  probabilite_aucun_accident = float(np.mean(scenarios == 0))

  return {
      "vehicule_id": vehicule_id,
      "total_accidents_passes": total_accidents_passes,
      "lambda_estime": round(lambda_estime, 4),
      "horizon_annees": horizon_annees,
      "prediction_accidents_futurs": int(nb_accidents_simule),
      "probabilite_aucun_accident": round(probabilite_aucun_accident * 100, 2),
  }