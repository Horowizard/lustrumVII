import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os

# Constants
PASSWORD = "Station Groningen"
DEADLINE = "2025-07-07T07:00:00"  # JavaScript ISO format
SPREADSHEET_ID = "1iq2tOmLCUxTLc0AW8zvdPRb0PvvWon553eAquQ_be6Q"  # Get it from the URL: https://docs.google.com/spreadsheets/d/THIS_ID/edit

def connect_to_gsheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Copy secrets to a new dict to allow editing
    secrets_dict = dict(st.secrets["gcp_service_account"])
    
    # Fix the private key format
    secrets_dict["private_key"] = secrets_dict["private_key"].replace("\\n", "\n")
    
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(secrets_dict, scope)
    gc = gspread.authorize(credentials)
    sh = gc.open_by_key(SPREADSHEET_ID)
    worksheet = sh.sheet1
    return worksheet



# Streamlit App
st.title("Senaat der Senaten")

# JavaScript live countdown
st.subheader("Countdown tot 7 juli 2025 07:00")
st.components.v1.html(f"""
<div id="countdown" style="
    font-size: 48px;
    font-family: 'Palace Script MT', cursive;
    color: navy;
    text-align: center;
    margin-top: 20px;
    font-weight: bold;
"></div>
<script>
var deadline = new Date("{DEADLINE}").getTime();
var x = setInterval(function() {{
    var now = new Date().getTime();
    var t = deadline - now;
    if (t > 0) {{
        var days = Math.floor(t / (1000 * 60 * 60 * 24));
        var hours = Math.floor((t % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        var minutes = Math.floor((t % (1000 * 60 * 60)) / (1000 * 60));
        var seconds = Math.floor((t % (1000 * 60)) / 1000);
        document.getElementById("countdown").innerHTML = 
            days + " dagen " + hours + " uur " 
            + minutes + " minuten " + seconds + " seconden ";
    }} else {{
        document.getElementById("countdown").innerHTML = "De deadline is verstreken!";
        clearInterval(x);
    }}
}}, 1000);
</script>
""", height=150)

# Riddle input
st.write("Als je interesse hebt in de Senaat der Senaten, voer dan het goede antwoord in:")

password_input = st.text_input("Antwoord:", type="password")

if password_input:
    if password_input.strip() == PASSWORD:
        st.success("Was ook niet heel moeilijk... Voer je naam in om te laten zien dat je interesse hebt:")
        name_input = st.text_input("Jouw naam:")

        if st.button("Verzend"):
            if name_input.strip():
                worksheet = connect_to_gsheet()
                # Append to Google Sheet
                worksheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), name_input.strip()])
                st.success("Je naam is opgeslagen!")
            else:
                st.error("Vul alsjeblieft je naam in voordat je verzendt.")
    else:
        st.error("Ongeldig antwoord. Probeer opnieuw.")
