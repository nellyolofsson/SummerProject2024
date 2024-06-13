import umail
from mysecrets import secrets

# Email details
sender_email = secrets['SENDER_EMAIL']
sender_app_password = secrets['GOOGLE_APP_PASS']
email_subject = '🌞Uppdatering från växthus🌞'

def email(dayvalues, nightvalues, eveningvalues):
    daytemp = dayvalues["temp"]
    dayhumid = dayvalues["humidity"]
    #daygroundmoist = dayvalues["groundmoist"]
    #daylight = dayvalues["light"]

    eveningtemp = eveningvalues["temp"]
    eveninghumid = eveningvalues["humidity"]
    #eveninggroundmoist = eveningvalues["groundmoist"]
    #eveninglight = eveningvalues["light"]

    nighttemp = nightvalues["temp"]
    nighthumid = nightvalues["humidity"]
    #nightgroundmoist = nightvalues["groundmoist"]
    #nightlight = nightvalues["light"]

    email_body = f"""
      <html>
    <head></head>
    <body>
        <h2>Dagvärden:</h2>
        <p>Temperatur: {daytemp}</p>
        <p>Fuktighet: {dayhumid}</p>
        <p>Jordfuktighet: {daygroundmoist}</p>
        <p>Ljusnivå: {daylight}</p>
        
        <h2>Kvällsvärden:</h2>
        <p>Temperatur: {eveningtemp}</p>
        <p>Fuktighet: {eveninghumid}</p>
        <p>Jordfuktighet: {eveninggroundmoist}</p>
        <p>Ljusnivå: {eveninglight}</p>
        
        <h2>Nattvärden:</h2>
        <p>Temperatur: {nighttemp}</p>
        <p>Fuktighet: {nighthumid}</p>
        <p>Jordfuktighet: {nightgroundmoist}</p>
        <p>Ljusnivå: {nightlight}</p>
    </body>
    </html>
    """
    return email_body


def email_movment():

    email_body = f"""
    <html>
    <head></head>
    <body>
        <h2>Rörelse Upptäckt i Växthus</h2>
        <p>Rörelse har upptäckts i växthuset vid följande tidpunkt:</p>
        <p><strong>Datum och Tid:</strong> </p>
        <p><strong>Plats:</strong> Växthus</p>
        <p>Detta är ett automatiskt meddelande skickat av växthusövervakningssystemet.</p>
    </body>
    </html>
    """
    return email_body

def send_email_movment(recipient):
    smtp = umail.SMTP('smtp.gmail.com', 465, ssl=True)
    smtp.login(sender_email, sender_app_password)
    smtp.to(recipient)
    smtp.write(f"Subject: {email_subject}\n")
    smtp.write("Content-Type: text/html\n")
    smtp.write("\n")  # Empty line to separate headers from content
    smtp.write(email_movment())
    smtp.send()  # Skicka e-posten
    smtp.quit()  # Stäng SMTP-sessionen


def send_email(subject, dayvalues, nightvalues, eveningvalues):
  smtp = umail.SMTP('smtp.gmail.com', 465, ssl=True)
  smtp.login(sender_email, sender_app_password)
  smtp.to(subject)
  smtp.write(f"Subject: {email_subject}\n")
  smtp.write("Content-Type: text/html\n")
  smtp.write("\n") # Empty line to separate headers from content
  smtp.write(email(dayvalues, nightvalues, eveningvalues)) # Skriv e-postens ämne och innehåll
  smtp.send()  # Skicka e-posten
  smtp.quit()  # Stäng SMTP-sessionen