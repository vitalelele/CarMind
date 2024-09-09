import yagmail

def invia_email(to_address, subject, body, email_user, email_password):
    yag = yagmail.SMTP(email_user, email_password)
    yag.send(to=to_address, subject=subject, contents=body)

def formatta_corpo_email(veicolo, tipo, data_scadenza, giorni_rimanenti):
    colore = 'black'
    if giorni_rimanenti <= 1:
        colore = 'red'
    elif giorni_rimanenti <= 10:
        colore = 'orange'
    elif giorni_rimanenti <= 15:
        colore = 'yellow'

    body = f"""
    <html>
    <body>
        <p style="font-family: Arial, sans-serif;">
            Ciao,<br><br>
            <strong>Attenzione:</strong> La scadenza per <strong>{tipo}</strong> del veicolo 
            <strong>{veicolo.nome} {veicolo.modello}</strong> è il 
            <strong>{data_scadenza.date()}</strong>.<br>
            Mancano <span style="color:{colore}; font-weight: bold;">{giorni_rimanenti} giorni</span>.<br><br>
            Cordiali saluti.
        </p>
    </body>
    </html>
    """
    return body
