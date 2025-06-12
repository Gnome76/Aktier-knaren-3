import streamlit as st
import pandas as pd
import os

DATA_FILE = "bolag_data.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame()

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

st.set_page_config(page_title="Aktieräknaren", layout="centered")

st.title("📈 Aktieräknaren")

df = load_data()

# --- FILTRERING OCH RULLISTA ÖVERST ---
with st.expander("🔍 Filtrera bolag", expanded=True):
    undervarderade_filter = st.selectbox(
        "Filtrera efter undervärdering",
        ["Visa alla bolag", "Undervärderade ≥ 30%", "Undervärderade ≥ 40%"]
    )

    filtrerade_bolag = df.copy()
    if "Undervärderade" in undervarderade_filter:
        procent = 30 if "30%" in undervarderade_filter else 40
        filtrerade_bolag = df[df["Undervärdering (%)"] >= procent]

    bolagsval = st.selectbox("Välj bolag att visa eller redigera", [""] + filtrerade_bolag["Bolagsnamn"].tolist())

if bolagsval:
    valt_bolag = df[df["Bolagsnamn"] == bolagsval].iloc[0]
    bolagsnamn = valt_bolag["Bolagsnamn"]
    nuvarande_kurs = valt_bolag["Nuvarande kurs"]
    pe_tal = [valt_bolag[f"P/E {i}"] for i in range(1, 6)]
    ps_tal = [valt_bolag[f"P/S {i}"] for i in range(1, 6)]
    vinst_i_ar = valt_bolag["Vinst i år"]
    vinst_nasta_ar = valt_bolag["Vinst nästa år"]
    oms_tillv_i_ar = valt_bolag["Omsättningstillväxt i år"]
    oms_tillv_nasta_ar = valt_bolag["Omsättningstillväxt nästa år"]
else:
    bolagsnamn = ""
    nuvarande_kurs = ""
    pe_tal = [""] * 5
    ps_tal = [""] * 5
    vinst_i_ar = ""
    vinst_nasta_ar = ""
    oms_tillv_i_ar = ""
    oms_tillv_nasta_ar = ""

st.markdown("### 🏢 Lägg till eller redigera bolag")

with st.form("bolagsform"):
    col1, col2 = st.columns(2)
    with col1:
        bolagsnamn_input = st.text_input("Bolagsnamn", value=bolagsnamn)
        vinst_i_ar_input = st.number_input("Vinst i år", value=float(vinst_i_ar) if vinst_i_ar != "" else 0.0)
        oms_tillv_i_ar_input = st.number_input("Omsättningstillväxt i år (%)", value=float(oms_tillv_i_ar) if oms_tillv_i_ar != "" else 0.0)
    with col2:
        nuvarande_kurs_input = st.number_input("Nuvarande kurs", value=float(nuvarande_kurs) if nuvarande_kurs != "" else 0.0)
        vinst_nasta_ar_input = st.number_input("Vinst nästa år", value=float(vinst_nasta_ar) if vinst_nasta_ar != "" else 0.0)
        oms_tillv_nasta_ar_input = st.number_input("Omsättningstillväxt nästa år (%)", value=float(oms_tillv_nasta_ar) if oms_tillv_nasta_ar != "" else 0.0)

    st.markdown("#### P/E-tal (historiska 5)")
    pe_inputs = [st.number_input(f"P/E {i+1}", value=float(pe_tal[i]) if pe_tal[i] != "" else 0.0, key=f"pe_{i}") for i in range(5)]

    st.markdown("#### P/S-tal (historiska 5)")
    ps_inputs = [st.number_input(f"P/S {i+1}", value=float(ps_tal[i]) if ps_tal[i] != "" else 0.0, key=f"ps_{i}") for i in range(5)]

    submitted = st.form_submit_button("💾 Spara bolag")

if submitted:
    try:
        pe_medel = sum(pe_inputs) / len(pe_inputs)
        ps_medel = sum(ps_inputs) / len(ps_inputs)

        target_pe = vinst_nasta_ar_input * pe_medel
        target_ps = vinst_nasta_ar_input * ps_medel * (1 + oms_tillv_nasta_ar_input / 100)

        final_target = (target_pe + target_ps) / 2

        undervardering = (final_target - nuvarande_kurs_input) / final_target * 100

        kop_30 = final_target * 0.70
        kop_40 = final_target * 0.60

        data = {
            "Bolagsnamn": bolagsnamn_input,
            "Nuvarande kurs": nuvarande_kurs_input,
            "Vinst i år": vinst_i_ar_input,
            "Vinst nästa år": vinst_nasta_ar_input,
            "Omsättningstillväxt i år": oms_tillv_i_ar_input,
            "Omsättningstillväxt nästa år": oms_tillv_nasta_ar_input,
            "Undervärdering (%)": undervardering,
            "Targetkurs": final_target,
            "Köp med 30% marginal": kop_30,
            "Köp med 40% marginal": kop_40,
        }

        for i in range(5):
            data[f"P/E {i+1}"] = pe_inputs[i]
            data[f"P/S {i+1}"] = ps_inputs[i]

        df = df[df["Bolagsnamn"] != bolagsnamn_input]
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
        df = df.sort_values(by="Bolagsnamn")
        save_data(df)
        st.success(f"{bolagsnamn_input} har sparats!")
        st.experimental_rerun()

    except Exception as e:
        st.error(f"Fel vid sparning: {e}")

# --- VISA ANALYS OM BOLAG ÄR VALT ---
if bolagsval:
    st.markdown("### 📊 Analys")
    st.markdown(f"**Nuvarande kurs:** {nuvarande_kurs} kr")
    st.markdown(f"**Targetkurs:** {round(valt_bolag['Targetkurs'], 2)} kr")

    if valt_bolag["Undervärdering (%)"] >= 30:
        st.success(f"💰 Undervärderad med **{round(valt_bolag['Undervärdering (%)'], 1)}%**")
    else:
        st.warning(f"📈 Undervärdering endast **{round(valt_bolag['Undervärdering (%)'], 1)}%**")

    st.markdown(f"**Köp vid 30% marginal:** {round(valt_bolag['Köp med 30% marginal'], 2)} kr")
    st.markdown(f"**Köp vid 40% marginal:** {round(valt_bolag['Köp med 40% marginal'], 2)} kr")

    if st.button("🗑️ Ta bort detta bolag"):
        df = df[df["Bolagsnamn"] != bolagsval]
        save_data(df)
        st.success(f"{bolagsval} har tagits bort.")
        st.experimental_rerun()

# --- KNAPP FÖR ATT LÄGGA TILL NYTT BOLAG ---
if st.button("➕ Lägg till nytt bolag"):
    st.experimental_rerun()
