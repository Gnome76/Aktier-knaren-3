import streamlit as st
import pandas as pd
import os

DATAFIL = "bolag_data.csv"

# Funktion: Läs eller initiera databas
def las_data():
    if os.path.exists(DATAFIL):
        return pd.read_csv(DATAFIL)
    else:
        return pd.DataFrame(columns=[
            "Bolagsnamn", "Nuvarande kurs", "Vinst i år", "Vinst nästa år",
            "Omsättningstillväxt i år", "Omsättningstillväxt nästa år",
            "P/E 1", "P/E 2", "P/E 3", "P/E 4", "P/E 5",
            "P/S 1", "P/S 2", "P/S 3", "P/S 4", "P/S 5"
        ])

# Funktion: Spara databas
def spara_data(df):
    df.sort_values("Bolagsnamn", inplace=True)
    df.to_csv(DATAFIL, index=False)

# Funktion: Beräkna riktkurs
def berakna_riktkurs(row):
    try:
        pe_median = pd.to_numeric(row[["P/E 1", "P/E 2", "P/E 3", "P/E 4", "P/E 5"]]).median()
        ps_median = pd.to_numeric(row[["P/S 1", "P/S 2", "P/S 3", "P/S 4", "P/S 5"]]).median()

        framtida_vinst = float(row["Vinst nästa år"])
        framtida_oms = (1 + float(row["Omsättningstillväxt nästa år"]) / 100)
        nuvarande_oms = framtida_oms / (1 + float(row["Omsättningstillväxt i år"]) / 100)
        omsattning_nasta_ar = nuvarande_oms * framtida_oms
        aktier = omsattning_nasta_ar / framtida_vinst if framtida_vinst else 1  # antagande

        pe_target = framtida_vinst * pe_median
        ps_target = omsattning_nasta_ar * ps_median / aktier

        target = (pe_target + ps_target) / 2
        return round(target, 2)
    except:
        return None

# Funktion: visa analys
def visa_analys(bolag, riktkurs):
    kurs = float(bolag["Nuvarande kurs"])
    diff = riktkurs - kurs
    procent = (diff / kurs) * 100

    färg = "🟢" if procent >= 30 else "🟡" if 0 < procent < 30 else "🔴"
    status = "Undervärderad" if procent > 0 else "Övervärderad"

    st.subheader(f"{färg} {status}: {procent:.1f}%")
    st.write(f"📈 **Targetkurs:** {riktkurs} kr")
    st.write(f"✅ Köp vid 30% marginal: {riktkurs * 0.7:.2f} kr")
    st.write(f"✅ Köp vid 40% marginal: {riktkurs * 0.6:.2f} kr")

# Hämta data
data = las_data()

# 🧭 UI – Filtrering högst upp
st.title("📊 Aktieräknaren")
filtrering = st.selectbox("Filtrera bolag", ["Visa alla", "Undervärderade 30–39%", "Undervärderade 40%+"])

# Rullista med sparade bolag
val = st.selectbox("📂 Välj bolag", ["(Lägg till nytt bolag)"] + list(data["Bolagsnamn"]))

if val == "(Lägg till nytt bolag)":
    bolagsdata = {
        "Bolagsnamn": "",
        "Nuvarande kurs": "",
        "Vinst i år": "",
        "Vinst nästa år": "",
        "Omsättningstillväxt i år": "",
        "Omsättningstillväxt nästa år": "",
        **{f"P/E {i}": "" for i in range(1, 6)},
        **{f"P/S {i}": "" for i in range(1, 6)},
    }
else:
    bolagsdata = data[data["Bolagsnamn"] == val].iloc[0].to_dict()

# 🧾 Inmatningsfält
with st.form("bolagsform"):
    st.subheader("🔢 Nyckeltal & Data")
    kol1, kol2, kol3 = st.columns(3)

    with kol1:
        bolagsdata["Bolagsnamn"] = st.text_input("Bolagsnamn", bolagsdata["Bolagsnamn"])
        bolagsdata["Nuvarande kurs"] = st.number_input("Nuvarande kurs", value=float(bolagsdata["Nuvarande kurs"] or 0), format="%.2f")

    with kol2:
        bolagsdata["Vinst i år"] = st.number_input("Vinst i år", value=float(bolagsdata["Vinst i år"] or 0), format="%.2f")
        bolagsdata["Vinst nästa år"] = st.number_input("Vinst nästa år", value=float(bolagsdata["Vinst nästa år"] or 0), format="%.2f")

    with kol3:
        bolagsdata["Omsättningstillväxt i år"] = st.number_input("Omsättningstillväxt i år (%)", value=float(bolagsdata["Omsättningstillväxt i år"] or 0), format="%.2f")
        bolagsdata["Omsättningstillväxt nästa år"] = st.number_input("Omsättningstillväxt nästa år (%)", value=float(bolagsdata["Omsättningstillväxt nästa år"] or 0), format="%.2f")

    st.markdown("---")
    st.write("📘 Historiska P/E-tal:")
    pe_cols = st.columns(5)
    for i in range(1, 6):
        bolagsdata[f"P/E {i}"] = pe_cols[i - 1].number_input(f"P/E {i}", value=float(bolagsdata[f"P/E {i}"] or 0), format="%.2f")

    st.write("📗 Historiska P/S-tal:")
    ps_cols = st.columns(5)
    for i in range(1, 6):
        bolagsdata[f"P/S {i}"] = ps_cols[i - 1].number_input(f"P/S {i}", value=float(bolagsdata[f"P/S {i}"] or 0), format="%.2f")

    sparaknapp = st.form_submit_button("💾 Spara bolag")

if sparaknapp:
    try:
        if not bolagsdata["Bolagsnamn"]:
            st.error("Bolagsnamn får inte vara tomt.")
        else:
            df_ny = pd.DataFrame([bolagsdata])
            data = data[data["Bolagsnamn"] != bolagsdata["Bolagsnamn"]]
            data = pd.concat([data, df_ny], ignore_index=True)
            spara_data(data)
            st.success("Bolaget har sparats! 🚀")
            st.experimental_rerun()
    except Exception as e:
        st.error(f"Fel vid sparande: {e}")

# 🔎 Visa analys om bolag är valt
if val != "(Lägg till nytt bolag)":
    riktkurs = berakna_riktkurs(bolagsdata)
    if riktkurs:
        visa_analys(bolagsdata, riktkurs)

# 📊 Visa filtrerat innehav
if filtrering != "Visa alla":
    filtrerat = []
    for i, row in data.iterrows():
        rikt = berakna_riktkurs(row)
        if rikt:
            nu = float(row["Nuvarande kurs"])
            skillnad = (rikt - nu) / nu * 100
            if filtrering == "Undervärderade 30–39%" and 30 <= skillnad < 40:
                filtrerat.append(row["Bolagsnamn"])
            elif filtrering == "Undervärderade 40%+" and skillnad >= 40:
                filtrerat.append(row["Bolagsnamn"])
    st.write("📌 Filtrerade bolag:", ", ".join(filtrerat) if filtrerat else "Inga bolag matchar filtret.")
