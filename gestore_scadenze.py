import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from veicolo import Veicolo
from email_utils import invia_email, formatta_corpo_email

class GestoreScadenze:
    def __init__(self, sheet_id, email_user, email_password, credentials_file):
        self.sheet_id = sheet_id
        self.email_user = email_user
        self.email_password = email_password
        self.credentials_file = credentials_file
        self.veicoli = self.carica_dati()

    def carica_dati(self):
        # Configura le credenziali e accedi al foglio di calcolo
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_file, scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(self.sheet_id).sheet1

        # Leggi i dati
        data = sheet.get_all_records()
        veicoli = []
        for row in data:
            veicolo = Veicolo(
                nome=row['Nome'],
                modello=row['Modello'],
                anno=row['Anno'],
                assicurazione=row['Assicurazione'],
                bollo=row['Bollo'],
                revisione=row['Revisione'],
                email=row['Email']
            )
            veicoli.append(veicolo)
        return veicoli

    def controlla_scadenze(self):
        oggi = datetime.now().date()
        for veicolo in self.veicoli:
            scadenze = veicolo.scadenze()
            for tipo, data_scadenza in scadenze.items():
                giorni_rimanenti = (data_scadenza.date() - oggi).days
                if giorni_rimanenti in [15, 10] or giorni_rimanenti < 1:
                    subject = f'Promemoria: Scadenza {tipo} per {veicolo.nome} {veicolo.modello}'
                    body = formatta_corpo_email(veicolo, tipo, data_scadenza, giorni_rimanenti)
                    invia_email(veicolo.email, subject, body, self.email_user, self.email_password)
