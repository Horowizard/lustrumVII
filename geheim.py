import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pytz

# Load secrets and texts
PASSWORD = st.secrets["app"]["PASSWORD"]
SPREADSHEET_ID = st.secrets["app"]["SPREADSHEET_ID"]
TEXTS = st.secrets["texts"]

# Define the Amsterdam timezone
amsterdam = pytz.timezone("Europe/Amsterdam")

# Create a datetime object in Amsterdam time
target_amsterdam_time = amsterdam.localize(datetime(2025, 7, 7, 19, 0, 0))

# Convert to UTC
target_utc_time = target_amsterdam_time.astimezone(pytz.utc)

# Use this UTC time as the countdown target
DEADLINE = target_utc_time.isoformat()

# def connect_to_gsheet():
#     scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
#     secrets_dict = dict(st.secrets["gcp_service_account"])
#     st.write(repr(st.secrets["gcp_service_account"]["private_key"]))
#     secrets_dict["private_key"] = secrets_dict["private_key"].replace("\\n", "\n")
#     credentials = ServiceAccountCredentials.from_json_keyfile_dict(secrets_dict, scope)
#     gc = gspread.authorize(credentials)
#     sh = gc.open_by_key(SPREADSHEET_ID)
#     return sh.sheet1

def connect_to_gsheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    
    secrets_dict = dict(st.secrets["gcp_service_account"])
    
    # Debug: show escaped private key (for troubleshooting only, remove in production)
    #st.write("Raw private key string (escaped):")
    #st.code(repr(secrets_dict["private_key"]))  # shows string with \\n

    # Fix newlines (convert escaped \\n to real newlines \n)
    secrets_dict["private_key"] = secrets_dict["private_key"].replace("\\n", "\n")

    # Debug: show fixed key (again, only for testing)
    #st.write("Parsed private key string:")
    #st.code(secrets_dict["private_key"])  # shows string with actual newlines

    # Authenticate
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(secrets_dict, scope)
    gc = gspread.authorize(credentials)
    sh = gc.open_by_key(SPREADSHEET_ID)
    return sh.sheet1

# UI
st.title("Senaat der Senaten")

# Countdown
st.subheader("Dichterbij dan je denkt...")
st.components.v1.html(f"""
<div style="width: 100%; display: flex; justify-content: center; align-items: center;">
    <div id="countdown" style="
        font-size: 6vw;
        max-width: 90%;
        font-family: 'Palace Script MT', cursive;
        color: navy;
        text-align: center;
        font-weight: bold;
        word-wrap: break-word;
        line-height: 1.2;
    "></div>
</div>
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
st.write("Als je interesse hebt in de Senaat der Senaten, voer dan het goede antwoord in (let op: er blijven 2 letters over, een 'o' en een 'n':")

password_input = st.text_input("Antwoord (kleine letters met eventuele spatie(s)):", type="password")

if password_input:
    if password_input.strip() == PASSWORD:
        st.success(TEXTS["intro"])
        name_input = st.text_input(TEXTS["label"])

        if st.button(TEXTS["button"]):
            if name_input.strip():
                worksheet = connect_to_gsheet()
                worksheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), name_input.strip()])
                st.success(TEXTS["success"])
            else:
                st.error(TEXTS["error"])
    else:
        st.error("Ongeldig antwoord. Probeer opnieuw.")
