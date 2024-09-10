from datetime import datetime

class Auto:
    def __init__(self, marca, modello, anno, targa, km, alimentazione, scadenza_bollo, scadenza_assicurazione, scadenza_revisione):
        self.marca = marca
        self.modello = modello
        self.anno = anno
        self.targa = targa
        self.km = km
        self.alimentazione = alimentazione
        self.scadenza_bollo = scadenza_bollo
        self.scadenza_assicurazione = scadenza_assicurazione
        self.scadenza_revisione = scadenza_revisione

    def giorni_alla_scadenza(self, data_scadenza):
        today = datetime.today().date()
        return (data_scadenza - today).days

    def controllo_scadenze(self):
        descrizioni = []
        notifiche = []

        # Controllo scadenza bollo
        scadenza_bollo_date = datetime.strptime(self.scadenza_bollo, '%d/%m/%Y').date()
        giorni_bollo = self.giorni_alla_scadenza(scadenza_bollo_date)

        if giorni_bollo < 0:
            descrizioni.append(f"Bollo scaduto il {self.scadenza_bollo}.")
        elif giorni_bollo <= 15:
            descrizioni.append(f"Bollo valido fino al {self.scadenza_bollo}. Mancano {giorni_bollo} giorni.")
            notifiche.append(("Bollo", giorni_bollo, self.scadenza_bollo))

        # Controllo scadenza assicurazione
        scadenza_assicurazione_date = datetime.strptime(self.scadenza_assicurazione, '%d/%m/%Y').date()
        giorni_assicurazione = self.giorni_alla_scadenza(scadenza_assicurazione_date)

        if giorni_assicurazione < 0:
            descrizioni.append(f"Assicurazione scaduta il {self.scadenza_assicurazione}.")
        elif giorni_assicurazione <= 15:
            descrizioni.append(f"Assicurazione valida fino al {self.scadenza_assicurazione}. Mancano {giorni_assicurazione} giorni.")
            notifiche.append(("Assicurazione", giorni_assicurazione, self.scadenza_assicurazione))

        # Controllo scadenza revisione
        scadenza_revisione_date = datetime.strptime(self.scadenza_revisione, '%d/%m/%Y').date()
        giorni_revisione = self.giorni_alla_scadenza(scadenza_revisione_date)

        if giorni_revisione < 0:
            descrizioni.append(f"Revisione scaduta il {self.scadenza_revisione}.")
        elif giorni_revisione <= 15:
            descrizioni.append(f"Revisione valida fino al {self.scadenza_revisione}. Mancano {giorni_revisione} giorni.")
            notifiche.append(("Revisione", giorni_revisione, self.scadenza_revisione))

        return descrizioni, notifiche
