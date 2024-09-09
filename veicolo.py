import pandas as pd

class Veicolo:
    def __init__(self, nome, modello, anno, assicurazione, bollo, revisione, email):
        self.nome = nome
        self.modello = modello
        self.anno = anno
        self.assicurazione = pd.to_datetime(assicurazione)
        self.bollo = pd.to_datetime(bollo)
        self.revisione = pd.to_datetime(revisione)
        self.email = email

    def scadenze(self):
        return {
            'Assicurazione': self.assicurazione,
            'Bollo': self.bollo,
            'Revisione': self.revisione
        }
