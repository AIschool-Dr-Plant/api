
from module.pear_infection_model import DiseasePredictionModel



infectionModel = DiseasePredictionModel();
print(infectionModel.predict_infection_rates(25));