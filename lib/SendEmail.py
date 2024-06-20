import umail
from mysecrets import secrets
import time

# Email details
sender_email = secrets['SENDER_EMAIL']
sender_app_password = secrets['GOOGLE_APP_PASS']
email_subject = '🌞Uppdatering från fönstret🌞'

def email(dayvalues, nightvalues, eveningvalues):
    daytemp = dayvalues["temp"]
    dayhumid = dayvalues["humidity"]
    daygroundmoist = dayvalues["groundmoist"]
    daylight = dayvalues["light"]
    daytime = dayvalues["time"]

    eveningtemp = eveningvalues["temp"]
    eveninghumid = eveningvalues["humidity"]
    eveninggroundmoist = eveningvalues["groundmoist"]
    eveninglight = eveningvalues["light"]
    eveningtime = eveningvalues["time"]

    nighttemp = nightvalues["temp"]
    nighthumid = nightvalues["humidity"]
    nightgroundmoist = nightvalues["groundmoist"]
    nightlight = nightvalues["light"]
    nighttime = nightvalues["time"]


    email_body = f"""
      <html>
    <head></head>
    <body>
        <h2>Dagvärden ({daytime}):</h2>
        <p>Temperatur: {daytemp}°C</p>
        <p>Fuktighet: {dayhumid}%</p>
        <p>Jordfuktighet: {daygroundmoist}%</p>
        <p>Ljusnivå: {daylight}lm</p>
        
        <h2>Kvällsvärden ({eveningtime}):</h2>
        <p>Temperatur: {eveningtemp}°C</p>
        <p>Fuktighet: {eveninghumid}%</p>
        <p>Jordfuktighet: {eveninggroundmoist}%</p>
        <p>Ljusnivå: {eveninglight}lm</p>
        
        <h2>Nattvärden ({nighttime}):</h2>
        <p>Temperatur: {nighttemp}°C</p>
        <p>Fuktighet: {nighthumid}%</p>
        <p>Jordfuktighet: {nightgroundmoist}%</p>
        <p>Ljusnivå: {nightlight}lm</p>
    </body>
    </html>
    """
    return email_body


def test_email(dayvalues):
   daytemp = dayvalues["temp"]
   dayhumid = dayvalues.get("humidity", "N/A")
   daygroundmoist = dayvalues["groundmoist"]
   daylight = dayvalues.get("light", "N/A")
   email_body = f"""
      <html>
    <head></head>
    <body>
       <h2>Dagvärden:</h2>
        <p>Temperatur: {daytemp}°C</p>
        <p>Fuktighet: {dayhumid}%</p>
        <p>Jordfuktighet: {daygroundmoist}%</p>
        <p>Ljusnivå: {daylight}%</p>
    </body>
    </html>
    """
   return email_body
   

def test_send_email(subject, dayvalues):
   smtp = umail.SMTP('smtp.gmail.com', 465, ssl=True)
   smtp.login(sender_email, sender_app_password)
   smtp.to(subject)
   smtp.write(f"Subject: {email_subject}\n")
   smtp.write("Content-Type: text/html\n")
   smtp.write("\n") # Empty line to separate headers from content
   smtp.write(test_email(dayvalues)) # Skriv e-postens ämne och innehåll
   smtp.send()  # Skicka e-posten
   smtp.quit()  # Stäng SMTP-sessionen
   

#ändra 2 timmar framåt
def get_current_time():
   current_time = time.localtime()
   hour = (current_time[3] + 2) % 24  # Adjust for timezone
   return f"{hour:02}:{current_time[4]:02}"
   

def email_movment():
    current_time = get_current_time()
    email_body = f"""
    <html>
    <head></head>
    <body>
        <h2>Rörelse Upptäckt i fönstret 🐈</h2>
        <p>Rörelse har upptäckts i fönstret vid följande tidpunkt:</p>
        <p><strong>Tid:</strong> {current_time} </p>
        <p><strong>Plats:</strong> Fönstret</p>
        <p>Detta är ett automatiskt meddelande skickat av övervakningssystemet.</p>
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