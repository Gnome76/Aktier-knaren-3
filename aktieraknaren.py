import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Aktieräknaren", layout="centered")
st.title("🎯 Aktieräknaren – Spara & Beräkna Targetkurs")

DATA_FILE = "bolag_data.csv"

# Ladda eller initiera databas
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=[
        "Bolagsnamn", "Nuvarande kurs", "Vinst i år", "Vinst nästa år",
        "Oms tillväxt i år", "Oms tillväxt nästa år",
        "PE1", "PE2", "PE3", "PE4", "PE5",
        "PEG1", "PEG2", "PEG3", "PEG4", "PEG5",
        "PS1", "PS2", "PS3", "PS4", "PS5"
    ])

st.sidebar.header("📁 Sparade bolag")
if not df.empty:
    selected = st.sidebar.selectbox("Välj bolag att visa eller redigera", df["Bolagsnamn"])
    if st.sidebar.button("❌ Ta bort bolag"):
        df = df[df["Bolagsnamn"] != selected]
        df.to_csv(DATA_FILE, index=False)
        st.sidebar.success("Bolaget togs bort. Ladda om sidan.")
        st.stop()
    else:
        data = df[df["Bolagsnamn"] == selected].iloc[0]
else:
    selected = None
    data = None

with st.form("input_form"):
    namn = st.text_input("Bolagsnamn", value=data["Bolagsnamn"] if data is not None else "")
    kurs = st.number_input("Nuvarande aktiekurs", min_value=0.0, step=0.1, value=data["Nuvarande kurs"] if data is not None else 0.0)
    vinst_i_ar = st.number_input("Förväntad vinst i år", value=data["Vinst i år"] if data is not None else 0.0)
    vinst_nasta_ar = st.number_input("Förväntad vinst nästa år", value=data["Vinst nästa år"] if data is not None else 0.0)
    oms_tillv_i_ar = st.number_input("Omsättningstillväxt i år (%)", value=data["Oms tillväxt i år"] if data is not None else 0.0)
    oms_tillv_nasta_ar = st.number_input("Omsättningstillväxt nästa år (%)", value=data["Oms tillväxt nästa år"] if data is not None else 0.0)

    st.subheader("P/E historik")
    pe_hist = [st.number_input(f"P/E {i+1}", value=data[f"PE{i+1}"] if data is not None else 0.0, key=f"pe{i}") for i in range(5)]
    st.subheader("PEG historik")
    peg_hist = [st.number_input(f"PEG {i+1}", value=data[f"PEG{i+1}"] if data is not None else 0.0, key=f"peg{i}") for i in range(5)]
    st.subheader("P/S historik")
    ps_hist = [st.number_input(f"P/S {i+1}", value=data[f"PS{i+1}"] if data is not None else 0.0, key=f"ps{i}") for i in range(5)]

    submitted = st.form_submit_button("💾 Spara & Beräkna")

if submitted:
    pe_snitt = sum(pe_hist) / 5
    peg_snitt = sum(peg_hist) / 5
    ps_snitt = sum(ps_hist) / 5
    vinsttillvaxt = ((vinst_nasta_ar - vinst_i_ar) / vinst_i_ar) * 100 if vinst_i_ar != 0 else 0
    oms_tillv_snitt = (oms_tillv_i_ar + oms_tillv_nasta_ar) / 2

    target_pe = vinst_nasta_ar * pe_snitt
    target_peg = vinst_nasta_ar * (peg_snitt * vinsttillvaxt)
    target_ps = ps_snitt * (1 + oms_tillv_snitt / 100)
    riktkurs = (target_pe + target_peg + target_ps) / 3

    undervarderad = kurs < riktkurs
    margin_30 = riktkurs * 0.7
    margin_40 = riktkurs * 0.6

    st.markdown(f"### 📊 Resultat för **{namn}**")
    st.success(f"🎯 Targetkurs (snitt): **{riktkurs:.2f} kr**")
    st.info(f"📌 Baserat på P/E: {target_pe:.2f}, PEG: {target_peg:.2f}, P/S: {target_ps:.2f}")
    st.write(f"📉 Nuvarande kurs: **{kurs:.2f} kr**")
    st.write(f"🔍 Aktien är **{'undervärderad ✅' if undervarderad else 'övervärderad ❌'}**")

    st.markdown("#### 📐 Säkerhetsmarginal")
    st.write(f"💰 Köp om du vill ha 30% marginal: **{margin_30:.2f} kr**")
    st.write(f"💰 Köp om du vill ha 40% marginal: **{margin_40:.2f} kr**")

    # Uppdatera databas
    new_row = {
        "Bolagsnamn": namn,
        "Nuvarande kurs": kurs,
        "Vinst i år": vinst_i_ar,
        "Vinst nästa år": vinst_nasta_ar,
        "Oms tillväxt i år": oms_tillv_i_ar,
        "Oms tillväxt nästa år": oms_tillv_nasta_ar,
    }
    for i in range(5):
        new_row[f"PE{i+1}"] = pe_hist[i]
        new_row[f"PEG{i+1}"] = peg_hist[i]
        new_row[f"PS{i+1}"] = ps_hist[i]

    df = df[df["Bolagsnamn"] != namn]
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    st.success("✅ Bolaget har sparats!")
