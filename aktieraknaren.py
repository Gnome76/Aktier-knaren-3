import streamlit as st
import pandas as pd
import os

DATA_FILE = "bolag_data.xlsx"

# Funktioner för datahantering
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_excel(DATA_FILE)
    return pd.DataFrame(columns=[
        "Bolagsnamn", "Nuvarande kurs", 
        "Vinst i år", "Vinst nästa år",
        "Omsättning i år", "Omsättning nästa år",
        "P/E 1", "P/E 2", "P/E 3", "P/E 4", "P/E 5",
        "P/S 1", "P/S 2", "P/S 3", "P/S 4", "P/S 5"
    ])

def save_data(df):
    df.to_excel(DATA_FILE, index=False)

def calculate_target_price(row):
    # Medelvärden för P/E och P/S
    pe_mean = sum([row[f"P/E {i}"] for i in range(1, 6)]) / 5
    ps_mean = sum([row[f"P/S {i}"] for i in range(1, 6)]) / 5

    # Target med P/E: (vinst nästa år) * historiskt snitt P/E
    target_pe = row["Vinst nästa år"] * pe_mean

    # Target med P/S: (omsättning nästa år) * historiskt snitt P/S
    target_ps = row["Omsättning nästa år"] * ps_mean

    # Medel av båda
    return round((target_pe + target_ps) / 2, 2)

def undervalued_percentage(now, target):
    return round((target - now) / now * 100, 2) if now > 0 else 0

# Start
st.set_page_config("Aktieräknaren", layout="centered")
st.title("📊 Aktieräknaren")

df = load_data()

# ---------------- FILTERING & BOLAGSVÄLJARE ----------------
st.subheader("🔍 Filtrera bolag")
filter_val = st.selectbox("Visa bolag som är:", [
    "Alla", "Undervärderade 30–39,99%", "Undervärderade 40%+"
])

if not df.empty:
    df["Targetkurs"] = df.apply(calculate_target_price, axis=1)
    df["Undervärdering (%)"] = df.apply(
        lambda row: undervalued_percentage(row["Nuvarande kurs"], row["Targetkurs"]), axis=1
    )
    if filter_val == "Undervärderade 30–39,99%":
        filtered_df = df[(df["Undervärdering (%)"] >= 30) & (df["Undervärdering (%)"] < 40)]
    elif filter_val == "Undervärderade 40%+":
        filtered_df = df[df["Undervärdering (%)"] >= 40]
    else:
        filtered_df = df

    selected = st.selectbox("Välj ett sparat bolag", options=filtered_df["Bolagsnamn"].tolist())
    bolag_data = df[df["Bolagsnamn"] == selected].iloc[0]
else:
    selected = None
    bolag_data = None

# ---------------- FORMULÄR ----------------
st.subheader("➕ Lägg till eller uppdatera bolag")
with st.form("bolagsformulär"):
    bolagsnamn = st.text_input("Bolagsnamn", value=bolag_data["Bolagsnamn"] if bolag_data is not None else "")
    kurs = st.number_input("Nuvarande kurs", step=0.01, value=float(bolag_data["Nuvarande kurs"]) if bolag_data is not None else None, format="%.2f")
    
    col1, col2 = st.columns(2)
    with col1:
        vinst_i_ar = st.number_input("Vinst i år", step=0.01, value=float(bolag_data["Vinst i år"]) if bolag_data is not None else None, format="%.2f")
    with col2:
        vinst_nasta_ar = st.number_input("Vinst nästa år", step=0.01, value=float(bolag_data["Vinst nästa år"]) if bolag_data is not None else None, format="%.2f")
    
    col3, col4 = st.columns(2)
    with col3:
        oms_i_ar = st.number_input("Omsättning i år", step=0.01, value=float(bolag_data["Omsättning i år"]) if bolag_data is not None else None, format="%.2f")
    with col4:
        oms_nasta_ar = st.number_input("Omsättning nästa år", step=0.01, value=float(bolag_data["Omsättning nästa år"]) if bolag_data is not None else None, format="%.2f")

    st.markdown("#### Historiska P/E-tal")
    cols_pe = st.columns(5)
    pe_vals = [cols_pe[i].number_input(f"P/E {i+1}", step=0.1, value=float(bolag_data[f"P/E {i+1}"]) if bolag_data is not None else None, format="%.2f") for i in range(5)]

    st.markdown("#### Historiska P/S-tal")
    cols_ps = st.columns(5)
    ps_vals = [cols_ps[i].number_input(f"P/S {i+1}", step=0.1, value=float(bolag_data[f"P/S {i+1}"]) if bolag_data is not None else None, format="%.2f") for i in range(5)]

    submitted = st.form_submit_button("💾 Spara bolag")
    if submitted:
        if not bolagsnamn or kurs is None or vinst_i_ar is None or vinst_nasta_ar is None:
            st.error("Vänligen fyll i alla fält korrekt.")
        else:
            new_data = {
                "Bolagsnamn": bolagsnamn,
                "Nuvarande kurs": kurs,
                "Vinst i år": vinst_i_ar,
                "Vinst nästa år": vinst_nasta_ar,
                "Omsättning i år": oms_i_ar,
                "Omsättning nästa år": oms_nasta_ar,
                **{f"P/E {i+1}": pe_vals[i] for i in range(5)},
                **{f"P/S {i+1}": ps_vals[i] for i in range(5)}
            }
            df = df[df["Bolagsnamn"] != bolagsnamn]  # remove existing
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            df = df.sort_values("Bolagsnamn")
            save_data(df)
            st.success(f"{bolagsnamn} har sparats!")

# ---------------- BORTTAGNING ----------------
if selected:
    if st.button("🗑️ Ta bort valt bolag"):
        df = df[df["Bolagsnamn"] != selected]
        save_data(df)
        st.success(f"{selected} har tagits bort.")

# ---------------- VISNING ----------------
if selected:
    st.subheader("📈 Analys")
    target = calculate_target_price(bolag_data)
    underv = undervalued_percentage(bolag_data["Nuvarande kurs"], target)
    kurs_30 = round(target * 0.7, 2)
    kurs_40 = round(target * 0.6, 2)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🎯 Targetkurs", f"{target} kr")
    with col2:
        st.metric("📉 Undervärdering", f"{underv} %")
    with col3:
        status = "✅ Undervärderad" if underv >= 0 else "❌ Övervärderad"
        st.metric("Status", status)

    st.markdown(f"📌 Köp vid 30% marginal: **{kurs_30} kr**")
    st.markdown(f"📌 Köp vid 40% marginal: **{kurs_40} kr**")

# ---------------- EXPORT ----------------
st.markdown("---")
if not df.empty:
    st.download_button("📤 Exportera till Excel", data=df.to_excel(index=False), file_name="bolag_data.xlsx")
