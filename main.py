import gspread, yagmail, json
from oauth2client.service_account import ServiceAccountCredentials
from Auto import Auto
from tabulate import tabulate


def carica_configurazione():
    # Carica i dati dal file config.json
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
    return config

def accesso_foglio_google(config):
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name(config['service_account_credentials'], scope)
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

# Per debug, serve a stampare i veicoli in una tabella
# Non è necessario per il funzionamento del programma
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

        for scadenza, giorni, data_scadenza in scadenze_imminenti:
            colore = "green"
            
            # Evita duplicazioni nelle scadenze già trattate
            if giorni == 0:
                colore = "red"
                scadenze_totali.append({
                    'auto': f"{auto.marca} {auto.modello} ({auto.targa})",
                    'scadenza': scadenza,
                    'giorni': "URGENTE! Oggi è il giorno della scadenza!",
                    'data_scadenza': data_scadenza,
                    'colore': colore
                })
            elif giorni < 0:
                scadenze_totali.append({
                    'auto': f"{auto.marca} {auto.modello} ({auto.targa})",
                    'scadenza': scadenza,
                    'giorni': "URGENTE! Scaduto!",
                    'data_scadenza': data_scadenza,
                    'colore': "red"
                })

            # Evita l'inclusione di giorni già notificati
            elif giorni > 0 and giorni <= 15:
                if giorni <= 5:
                    colore = "red"
                elif giorni <= 10:
                    colore = "yellow"
                else:
                    colore = "green"

                # Aggiungi solo le scadenze imminenti
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

    subject = "CarMind - Avviso Scadenze per i veicoli ⚠️"

    veicoli_dict = {}
    for scadenza_info in scadenze_totali:
        auto = scadenza_info['auto']
        if auto not in veicoli_dict:
            veicoli_dict[auto] = []
        veicoli_dict[auto].append(scadenza_info)

    contenuto = """
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.8; margin: 0; padding: 0; color: #333; background-color: #f9f9f9;">
        <div style="width: 90%; margin: 20px auto; padding: 20px; background-color: #fff; border-radius: 10px; box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);">
            <h2 style="color: #4CAF50; text-align: center; margin-bottom: 20px;">Scadenze Imminenti per i veicoli 🚗</h2>
    """

    for auto, scadenze in veicoli_dict.items():
        contenuto += f"""
        <div style="margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 8px;">
            <h3 style="margin: 0 0 10px 0; color: #333; font-size: 20px; border-bottom: 2px solid #4CAF50; padding-bottom: 5px;">{auto}</h3>
        """
        for scadenza_info in scadenze:
            colore = {
                'green': '#4CAF50',
                'yellow': '#FFC107',
                'red': '#F44336'
            }.get(scadenza_info['colore'], 'transparent')

            if scadenza_info['giorni'] == "URGENTE! Oggi è il giorno della scadenza!":
                urgenza = "URGENTE! Oggi è il giorno della scadenza!"
                giorni_mancanti = ""  # Non mostrare i giorni mancanti
            elif scadenza_info['giorni'] == "URGENTE! Scaduto!":
                urgenza = "URGENTE! Scaduto!"
                giorni_mancanti = ""  # Non mostrare i giorni mancanti per scadenze passate
            else:
                urgenza = ""
                giorni_mancanti = f"<br><strong>Mancano: </strong>{scadenza_info['giorni']} giorni"

            contenuto += f"""
            <div style="margin: 10px 0; padding: 10px; border-radius: 5px; background-color: #f9f9f9; border-left: 5px solid {colore};">
                <strong style="color: {colore}; display: block; font-size: 16px;">{scadenza_info['scadenza']}</strong>
                <p style="margin: 5px 0 0 0; font-size: 14px;">
                    <span style="color: {colore}; font-weight: bold;">{urgenza}</span> Scadenza il: <strong>{scadenza_info['data_scadenza']}</strong>.
                    {giorni_mancanti}
                </p>
            </div>
            """
        contenuto += "</div>"

    contenuto += """
        </div>
        <footer style="text-align: center; margin-top: 20px; color: #888; font-size: 12px;">
            <p>Questo è un promemoria automatico. Non rispondere a questa email.</p>
        </footer>
    </body>
    </html>
    """
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
