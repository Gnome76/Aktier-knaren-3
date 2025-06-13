import streamlit as st
import pandas as pd
import os

# Fil för att spara data
DATA_FILE = "bolag_data.csv"

# Hjälpfunktion för att läsa data
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=[
            "Bolagsnamn", "Vinst_i_år", "Vinst_nästa_år", "Omsättningstillväxt_i_år", "Omsättningstillväxt_nästa_år",
            "Nuvarande_kurs", "PE1", "PE2", "PE3", "PE4", "PE5",
            "PS1", "PS2", "PS3", "PS4", "PS5"
        ])

# Hjälpfunktion för att spara data
def save_data(df):
    df.sort_values("Bolagsnamn", inplace=True)
    df.to_csv(DATA_FILE, index=False)

# Beräkning av targetkurs
def calculate_target_price(row):
    vinst_snitt = (row["Vinst_i_år"] + row["Vinst_nästa_år"]) / 2
    oms_tillv = (row["Omsättningstillväxt_i_år"] + row["Omsättningstillväxt_nästa_år"]) / 2

    pe_snitt = (row["PE1"] + row["PE2"] + row["PE3"] + row["PE4"] + row["PE5"]) / 5
    ps_snitt = (row["PS1"] + row["PS2"] + row["PS3"] + row["PS4"] + row["PS5"]) / 5

    pe_target = vinst_snitt * pe_snitt
    ps_target = vinst_snitt * (1 + oms_tillv / 100) * ps_snitt

    return round((pe_target + ps_target) / 2, 2)

# Appen startar här
st.set_page_config(page_title="Aktieräknaren", layout="centered")
st.title("📈 Aktieräknaren")

df = load_data()

# Filtreringsalternativ
with st.expander("🔍 Filtrera bolag"):
    filter_option = st.selectbox("Visa bolag som är undervärderade:", ["Alla", "30–39,99%", "Över 40%"])
    filtered_df = df.copy()

    if not df.empty:
        df["Targetkurs"] = df.apply(calculate_target_price, axis=1)
        df["Undervärdering (%)"] = ((df["Targetkurs"] - df["Nuvarande_kurs"]) / df["Nuvarande_kurs"]) * 100

        if filter_option == "30–39,99%":
            filtered_df = df[(df["Undervärdering (%)"] >= 30) & (df["Undervärdering (%)"] < 40)]
        elif filter_option == "Över 40%":
            filtered_df = df[df["Undervärdering (%)"] >= 40]

        selected_name = st.selectbox("Välj bolag", options=[""] + list(filtered_df["Bolagsnamn"]))
    else:
        selected_name = ""

# Förvalt värden
data = {
    "Bolagsnamn": "",
    "Vinst_i_år": None, "Vinst_nästa_år": None,
    "Omsättningstillväxt_i_år": None, "Omsättningstillväxt_nästa_år": None,
    "Nuvarande_kurs": None,
    "PE1": None, "PE2": None, "PE3": None, "PE4": None, "PE5": None,
    "PS1": None, "PS2": None, "PS3": None, "PS4": None, "PS5": None
}

if selected_name:
    selected_row = df[df["Bolagsnamn"] == selected_name].iloc[0]
    for key in data:
        data[key] = selected_row[key]

with st.form("form"):
    st.subheader("Lägg till eller redigera bolag")

    col1, col2 = st.columns(2)
    data["Bolagsnamn"] = st.text_input("Bolagsnamn", value=data["Bolagsnamn"])

    with col1:
        data["Vinst_i_år"] = st.number_input("Vinst i år", value=data["Vinst_i_år"] or 0.0, step=0.01, format="%.2f")
        data["Omsättningstillväxt_i_år"] = st.number_input("Omsättningstillväxt i år (%)", value=data["Omsättningstillväxt_i_år"] or 0.0, step=0.1, format="%.2f")
    with col2:
        data["Vinst_nästa_år"] = st.number_input("Vinst nästa år", value=data["Vinst_nästa_år"] or 0.0, step=0.01, format="%.2f")
        data["Omsättningstillväxt_nästa_år"] = st.number_input("Omsättningstillväxt nästa år (%)", value=data["Omsättningstillväxt_nästa_år"] or 0.0, step=0.1, format="%.2f")

    data["Nuvarande_kurs"] = st.number_input("Nuvarande aktiekurs", value=data["Nuvarande_kurs"] or 0.0, step=0.1, format="%.2f")

    st.markdown("#### Historiska P/E-tal")
    cols_pe = st.columns(5)
    for i in range(5):
        data[f"PE{i+1}"] = cols_pe[i].number_input(f"P/E {i+1}", value=data[f"PE{i+1}"] or 0.0, step=0.1, format="%.2f")

    st.markdown("#### Historiska P/S-tal")
    cols_ps = st.columns(5)
    for i in range(5):
        data[f"PS{i+1}"] = cols_ps[i].number_input(f"P/S {i+1}", value=data[f"PS{i+1}"] or 0.0, step=0.1, format="%.2f")

    submitted = st.form_submit_button("💾 Spara bolag")
    if submitted:
        if not data["Bolagsnamn"]:
            st.error("⚠️ Bolagsnamn krävs för att spara.")
        else:
            df = df[df["Bolagsnamn"] != data["Bolagsnamn"]]
            df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
            save_data(df)
            st.success(f"✅ Bolaget '{data['Bolagsnamn']}' har sparats.")

# Visar analys för valt bolag
if selected_name and not df.empty:
    selected_row = df[df["Bolagsnamn"] == selected_name].iloc[0]
    targetkurs = calculate_target_price(selected_row)
    kurs = selected_row["Nuvarande_kurs"]
    undervärdering = ((targetkurs - kurs) / kurs) * 100

    st.markdown("---")
    st.subheader(f"📊 Analys för {selected_name}")
    st.markdown(f"**Targetkurs:** {targetkurs:.2f} kr")
    st.markdown(f"**Nuvarande kurs:** {kurs:.2f} kr")

    if undervärdering >= 0:
        st.markdown(f"✅ **Undervärdering:** {undervärdering:.2f}%", unsafe_allow_html=True)
    else:
        st.markdown(f"⚠️ **Övervärdering:** {undervärdering:.2f}%", unsafe_allow_html=True)

    st.markdown(f"💰 Köp vid -30% marginal: **{targetkurs * 0.7:.2f} kr**")
    st.markdown(f"💰 Köp vid -40% marginal: **{targetkurs * 0.6:.2f} kr**")

# Lägg till nytt bolag
st.markdown("---")
if st.button("➕ Lägg till nytt bolag"):
    st.experimental_rerun()

# Export
if not df.empty:
    st.download_button("⬇️ Exportera till CSV", data=df.to_csv(index=False), file_name="aktier_export.csv", mime="text/csv")

# Förbättringsförslag
st.markdown("---")
st.info("💡 Förslag: Lägg till diagram, exportera till Excel, molnsynk mellan enheter m.m.")
