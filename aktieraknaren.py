import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Aktieräknaren", layout="centered")

DATAFIL = "bolag_data.csv"

def load_data():
    if os.path.exists(DATAFIL):
        return pd.read_csv(DATAFIL)
    return pd.DataFrame(columns=[
        "Bolagsnamn", "Nuvarande kurs", "Vinst i år", "Vinst nästa år",
        "Omsättningstillväxt i år", "Omsättningstillväxt nästa år",
        "P/E1", "P/E2", "P/E3", "P/E4",
        "P/S1", "P/S2", "P/S3", "P/S4"
    ])

def save_data(df):
    df.sort_values(by="Bolagsnamn", inplace=True)
    df.to_csv(DATAFIL, index=False)

st.title("📈 Aktieräknaren")

# Ladda och visa sparade bolag
data = load_data()
bolagslista = data["Bolagsnamn"].tolist()

selected = st.selectbox("📜 Välj bolag", options=["Lägg till nytt bolag"] + bolagslista)

if selected != "Lägg till nytt bolag":
    bolag_data = data[data["Bolagsnamn"] == selected].iloc[0]
else:
    bolag_data = {col: "" for col in data.columns}

# Formulär
st.subheader("🔢 Ange nyckeltal")
with st.form("form"):
    col1, col2 = st.columns(2)
    with col1:
        namn = st.text_input("Bolagsnamn", value=bolag_data["Bolagsnamn"])
        nuvarande_kurs = st.number_input("Nuvarande kurs", value=float(bolag_data["Nuvarande kurs"] or 0), format="%.2f")
        vinst_i_ar = st.number_input("Vinst i år", value=float(bolag_data["Vinst i år"] or 0), format="%.2f")
        vinst_next_ar = st.number_input("Vinst nästa år", value=float(bolag_data["Vinst nästa år"] or 0), format="%.2f")
        oms_vinst_i_ar = st.number_input("Omsättningstillväxt i år (%)", value=float(bolag_data["Omsättningstillväxt i år"] or 0), format="%.2f")
        oms_vinst_next_ar = st.number_input("Omsättningstillväxt nästa år (%)", value=float(bolag_data["Omsättningstillväxt nästa år"] or 0), format="%.2f")
    with col2:
        pe = [st.number_input(f"P/E {i+1}", value=float(bolag_data.get(f"P/E{i+1}", 0)), format="%.2f") for i in range(4)]
        ps = [st.number_input(f"P/S {i+1}", value=float(bolag_data.get(f"P/S{i+1}", 0)), format="%.2f") for i in range(4)]

    submitted = st.form_submit_button("💾 Spara bolag")

    if submitted:
        new_entry = {
            "Bolagsnamn": namn,
            "Nuvarande kurs": nuvarande_kurs,
            "Vinst i år": vinst_i_ar,
            "Vinst nästa år": vinst_next_ar,
            "Omsättningstillväxt i år": oms_vinst_i_ar,
            "Omsättningstillväxt nästa år": oms_vinst_next_ar,
            "P/E1": pe[0], "P/E2": pe[1], "P/E3": pe[2], "P/E4": pe[3],
            "P/S1": ps[0], "P/S2": ps[1], "P/S3": ps[2], "P/S4": ps[3],
        }

        # Ta bort om det redan finns
        data = data[data["Bolagsnamn"] != namn]
        data = pd.concat([data, pd.DataFrame([new_entry])], ignore_index=True)
        save_data(data)
        st.success(f"{namn} sparat!")

# Visa analys
st.subheader("📊 Analys")
if selected != "Lägg till nytt bolag":
    pe_genomsnitt = sum([bolag_data[f"P/E{i}"] for i in range(1, 5)]) / 4
    ps_genomsnitt = sum([bolag_data[f"P/S{i}"] for i in range(1, 5)]) / 4
    vinst = bolag_data["Vinst nästa år"]
    oms_tillv = bolag_data["Omsättningstillväxt nästa år"] / 100
    kurs = bolag_data["Nuvarande kurs"]

    pe_target = pe_genomsnitt * vinst
    ps_target = ps_genomsnitt * vinst * (1 + oms_tillv)
    snitt_target = (pe_target + ps_target) / 2

    undervardering = ((snitt_target - kurs) / kurs) * 100

    st.write(f"🎯 Targetkurs P/E: **{pe_target:.2f}**")
    st.write(f"🎯 Targetkurs P/S: **{ps_target:.2f}**")
    st.write(f"📌 Snitt Targetkurs: **{snitt_target:.2f}**")
    st.write(f"📉 Nuvarande kurs: **{kurs:.2f}**")

    if undervardering >= 30:
        st.success(f"✅ Undervärderad med {undervardering:.1f}%")
    elif undervardering > 0:
        st.info(f"ℹ️ Lätt undervärderad med {undervardering:.1f}%")
    else:
        st.error(f"❌ Övervärderad med {abs(undervardering):.1f}%")

    st.markdown(f"💡 Köp vid -30%: **{snitt_target * 0.7:.2f}**, -40%: **{snitt_target * 0.6:.2f}**")

# Filter
st.subheader("🔍 Filtrera undervärderade bolag")
val = st.selectbox("Visa:", ["Alla", "≥ 30%", "≥ 40%"])

def beräkna_undervardering(row):
    pe_avg = sum([row[f"P/E{i}"] for i in range(1, 5)]) / 4
    ps_avg = sum([row[f"P/S{i}"] for i in range(1, 5)]) / 4
    vinst = row["Vinst nästa år"]
    oms = row["Omsättningstillväxt nästa år"] / 100
    kurs = row["Nuvarande kurs"]
    pe_target = pe_avg * vinst
    ps_target = ps_avg * vinst * (1 + oms)
    snitt = (pe_target + ps_target) / 2
    return ((snitt - kurs) / kurs) * 100

data["Undervärdering %"] = data.apply(beräkna_undervardering, axis=1)

if val == "≥ 30%":
    filtrerat = data[data["Undervärdering %"] >= 30]
elif val == "≥ 40%":
    filtrerat = data[data["Undervärdering %"] >= 40]
else:
    filtrerat = data

filtrerat = filtrerat.sort_values(by="Undervärdering %", ascending=False)
st.dataframe(filtrerat[["Bolagsnamn", "Undervärdering %"]])
