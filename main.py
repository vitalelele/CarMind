import gspread
from oauth2client.service_account import ServiceAccountCredentials
import yagmail
from Auto import Auto
from tabulate import tabulate
import json


def carica_configurazione():
    # Carica i dati dal file config.json
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
    return config

def accesso_foglio_google(config):
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name(config['summer_credentials'], scope)
    client = gspread.authorize(creds)

    # Apri il foglio di calcolo
    sheet = client.open("CarMindSheet").sheet1
    return sheet

def carica_veicoli(sheet):
    veicoli = []
    records = sheet.get_all_records()

    for record in records:
        auto = Auto(
            marca=record['Marca'],
            modello=record['Modello'],
            anno=record['Anno'],
            targa=record['Targa'],
            km=record['Kilometri (KM_data)'],
            alimentazione=record['Alimentazione'],
            scadenza_bollo=record['Scadenza bollo'],
            scadenza_assicurazione=record['Scadenza assicurazione'],
            scadenza_revisione=record['Scadenza revisione']
        )
        veicoli.append(auto)
    
    return veicoli

def stampa_veicoli(veicoli):
    tabella = []
    for auto in veicoli:
        tabella.append([auto.marca, auto.modello, auto.anno, auto.targa, auto.km, auto.alimentazione])
    
    headers = ["Marca", "Modello", "Anno", "Targa", "Kilometri", "Alimentazione"]
    print(tabulate(tabella, headers, tablefmt="grid"))

def accumula_scadenze(veicoli):
    scadenze_totali = []

    for auto in veicoli:
        descrizioni, scadenze_imminenti = auto.controllo_scadenze()
        
        if scadenze_imminenti:
            for scadenza, giorni, data_scadenza in scadenze_imminenti:
                colore = "green"
                if giorni <= 10:
                    colore = "yellow"
                if giorni <= 5:
                    colore = "red"
                if giorni < 0:
                    colore = "red"
                    scadenze_totali.append({
                        'auto': f"{auto.marca} {auto.modello} ({auto.targa})",
                        'scadenza': scadenza,
                        'giorni': "URGENTE! Scaduto!",
                        'data_scadenza': data_scadenza,
                        'colore': colore
                    })
                else:
                    scadenze_totali.append({
                        'auto': f"{auto.marca} {auto.modello} ({auto.targa})",
                        'scadenza': scadenza,
                        'giorni': giorni,
                        'data_scadenza': data_scadenza,
                        'colore': colore
                    })
    
    return scadenze_totali

def invia_email(scadenze_totali, config):
    yag = yagmail.SMTP(config['email_sender'], oauth2_file=config['oauth2_credentials'])
    
    subject = "Avviso scadenze per i veicoli"

    # Raggruppa le scadenze per veicolo
    veicoli_dict = {}
    for scadenza_info in scadenze_totali:
        auto = scadenza_info['auto']
        if auto not in veicoli_dict:
            veicoli_dict[auto] = []
        veicoli_dict[auto].append(scadenza_info)
    
    contenuto = """
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 0; color: #333; background-color: #f4f4f4;">
    <div style="width: 80%; margin: 20px auto; padding: 20px; background-color: #fff; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
    <h2 style="color: #333; margin: 0 0 10px 0; border-bottom: 2px solid #333; padding-bottom: 10px;">Scadenze imminenti per i veicoli:</h2>
    """

    for auto, scadenze in veicoli_dict.items():
        contenuto += f"""
        <div style="margin-bottom: 10px; padding: 10px 0 5px; border-bottom: 1px solid #ddd;">
        <h3 style="margin: 0; color: #333; font-size: 18px;">{auto}</h3>
        """
        for scadenza_info in scadenze:
            colore = {
                'green': 'green',
                'yellow': 'yellow',
                'red': 'red'
            }.get(scadenza_info['colore'], 'transparent')

            contenuto += f"""
            <div style="margin: 5px 0; padding: 8px; border-radius: 5px; background-color: #f9f9f9; border-left: 5px solid {colore};">
                <strong style="display: block; margin-bottom: 5px; color: #333;">{scadenza_info['scadenza']}:</strong>
                <span style="color: {colore};">Scadenza il {scadenza_info['data_scadenza']}.</span>
                <br><strong>Mancano: </strong>{scadenza_info['giorni']} giorni
            </div>
            """
        contenuto += "</div>"

    contenuto += "</div></body></html>"

    # Invio email al destinatario specificato nel config
    yag.send(config['email_receiver'], subject, contenuto)
    print("Email inviata con tutte le scadenze.")

def main():
    # Carica la configurazione dal file config.json
    config = carica_configurazione()

    # Accesso al foglio Google
    sheet = accesso_foglio_google(config)

    # Caricare i veicoli
    veicoli = carica_veicoli(sheet)

    # Accumulare tutte le scadenze e inviare un'unica email
    scadenze_totali = accumula_scadenze(veicoli)
    if scadenze_totali:
        invia_email(scadenze_totali, config)

    print("Programma terminato correttamente.")

if __name__ == "__main__":
    main()
