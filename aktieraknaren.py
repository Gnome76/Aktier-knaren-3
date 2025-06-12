import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Aktieräknaren", layout="wide")

DB_FILE = "bolag_db.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame()

def save_data(df):
    df.to_csv(DB_FILE, index=False)

def calculate_target_price(pe_values, ps_values, earnings_this_year, earnings_next_year, revenue_growth_this_year, revenue_growth_next_year):
    avg_pe = sum(pe_values) / len(pe_values)
    avg_ps = sum(ps_values) / len(ps_values)
    future_earnings = (earnings_this_year + earnings_next_year) / 2
    avg_growth = (revenue_growth_this_year + revenue_growth_next_year) / 2 / 100
    target_price_pe = future_earnings * avg_pe
    target_price_ps = (future_earnings / (1 + avg_growth)) * avg_ps
    return round((target_price_pe + target_price_ps) / 2, 2)

def clear_form():
    st.session_state.clear_selection = True

# === LADDA DATA ===
df = load_data()

st.title("📈 Aktieräknaren")

# === FILTER ===
st.subheader("🔍 Filtrera bolag")
filter_option = st.selectbox("Filtrera efter undervärdering", ["Inget filter", "Undervärderade 30-39.99%", "Undervärderade 40%+", "Alla undervärderade"])

filtered_df = df.copy()
if filter_option == "Undervärderade 30-39.99%":
    filtered_df = df[(df["Undervärdering %"] >= 30) & (df["Undervärdering %"] < 40)]
elif filter_option == "Undervärderade 40%+":
    filtered_df = df[df["Undervärdering %"] >= 40]
elif filter_option == "Alla undervärderade":
    filtered_df = df[df["Undervärdering %"] > 0]

if not filtered_df.empty:
    selected_name = st.selectbox("Välj bolag", filtered_df["Bolagsnamn"].sort_values().tolist())
else:
    selected_name = st.selectbox("Välj bolag", [""])

# === LÄGG TILL NYTT BOLAG ===
st.button("➕ Lägg till nytt bolag", on_click=clear_form)

# === FORMULÄR ===
st.subheader("📋 Nyckeltal & Input")

if selected_name and not st.session_state.get("clear_selection"):
    selected_row = df[df["Bolagsnamn"] == selected_name].iloc[0]
else:
    selected_row = pd.Series(dtype="float64")
    selected_name = ""

# === ÖVERSTA DELEN – Bolagsnamn och nuvarande kurs ===
col_top1, col_top2 = st.columns(2)
bolagsnamn = col_top1.text_input("Bolagsnamn", selected_name)
kurs = col_top2.number_input(
    "Nuvarande kurs",
    step=0.01,
    value=selected_row.get("Nuvarande Kurs") if "Nuvarande Kurs" in selected_row else None,
    format="%.2f"
)

# === P/E och P/S ===
cols = st.columns(5)
pe_values = []
ps_values = []

for i in range(5):
    pe = cols[i].number_input(
        f"P/E {i+1}",
        step=0.01,
        value=selected_row.get(f"PE_{i+1}") if f"PE_{i+1}" in selected_row else None,
        format="%.2f",
        key=f"pe{i}"
    )
    pe_values.append(pe)

cols2 = st.columns(5)
for i in range(5):
    ps = cols2[i].number_input(
        f"P/S {i+1}",
        step=0.01,
        value=selected_row.get(f"PS_{i+1}") if f"PS_{i+1}" in selected_row else None,
        format="%.2f",
        key=f"ps{i}"
    )
    ps_values.append(ps)

# === VINST & TILLVÄXT ===
col1, col2 = st.columns(2)
earnings_this_year = col1.number_input(
    "Beräknad vinst i år",
    step=0.01,
    value=selected_row.get("Vinst i år") if "Vinst i år" in selected_row else None,
    format="%.2f"
)
earnings_next_year = col2.number_input(
    "Beräknad vinst nästa år",
    step=0.01,
    value=selected_row.get("Vinst nästa år") if "Vinst nästa år" in selected_row else None,
    format="%.2f"
)

col3, col4 = st.columns(2)
revenue_growth_this_year = col3.number_input(
    "Omsättningstillväxt i år (%)",
    step=0.1,
    value=selected_row.get("Omsättningstillväxt i år") if "Omsättningstillväxt i år" in selected_row else None,
    format="%.1f"
)
revenue_growth_next_year = col4.number_input(
    "Omsättningstillväxt nästa år (%)",
    step=0.1,
    value=selected_row.get("Omsättningstillväxt nästa år") if "Omsättningstillväxt nästa år" in selected_row else None,
    format="%.1f"
)

# === SPARA BOLAG ===
if st.button("💾 Spara bolag"):
    if not bolagsnamn:
        st.error("Ange bolagsnamn.")
    else:
        target_price = calculate_target_price(pe_values, ps_values, earnings_this_year, earnings_next_year, revenue_growth_this_year, revenue_growth_next_year)
        undervaluation = round(((target_price - kurs) / target_price) * 100, 2)
        buy_30 = round(target_price * 0.70, 2)
        buy_40 = round(target_price * 0.60, 2)

        data = {
            "Bolagsnamn": bolagsnamn,
            "Nuvarande Kurs": kurs,
            "Vinst i år": earnings_this_year,
            "Vinst nästa år": earnings_next_year,
            "Omsättningstillväxt i år": revenue_growth_this_year,
            "Omsättningstillväxt nästa år": revenue_growth_next_year,
            "Targetkurs": target_price,
            "Undervärdering %": undervaluation,
            "Köp vid -30%": buy_30,
            "Köp vid -40%": buy_40,
        }

        for i in range(5):
            data[f"PE_{i+1}"] = pe_values[i]
            data[f"PS_{i+1}"] = ps_values[i]

        df = df[df["Bolagsnamn"] != bolagsnamn]
        df = df.append(data, ignore_index=True)
        df = df.sort_values(by="Bolagsnamn")
        save_data(df)
        st.success(f"{bolagsnamn} sparat!")

# === VISNING AV RESULTAT ===
st.subheader("📊 Översikt")
if not df.empty:
    df_display = df[["Bolagsnamn", "Nuvarande Kurs", "Targetkurs", "Undervärdering %", "Köp vid -30%", "Köp vid -40%"]].copy()
    df_display["Undervärdering %"] = df_display["Undervärdering %"].map(lambda x: f"{x:.1f}%")
    st.dataframe(df_display, use_container_width=True)

# === EXPORT ===
if not df.empty:
    st.download_button("⬇️ Exportera till Excel", df.to_csv(index=False), file_name="aktier.csv", mime="text/csv")
