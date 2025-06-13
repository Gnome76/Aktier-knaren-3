import streamlit as st
import pandas as pd
import os

DATA_FILE = "bolag_data.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=[
        "Bolagsnamn", "Nuvarande kurs", "Vinst i år", "Vinst nästa år",
        "Omsättning i år", "Omsättning nästa år",
        "P/E 1", "P/E 2", "P/E 3", "P/E 4", "P/E 5",
        "P/S 1", "P/S 2", "P/S 3", "P/S 4", "P/S 5"
    ])

def save_data(df):
    df = df.sort_values("Bolagsnamn")
    df.to_csv(DATA_FILE, index=False)

def clear_fields():
    st.session_state.clear_fields = True

st.title("📈 Aktieräknaren")

df = load_data()
bolagslista = df["Bolagsnamn"].tolist()

# Filtrering
st.subheader("🔍 Filtrera bolag")
filter_val = st.selectbox(
    "Välj filter för undervärdering",
    ["Alla", "Undervärderade 30–39%", "Undervärderade 40%+"]
)

filtered_df = df.copy()
if filter_val == "Undervärderade 30–39%":
    filtered_df = df[df["Undervärdering (%)"].between(30, 39.99)]
elif filter_val == "Undervärderade 40%+":
    filtered_df = df[df["Undervärdering (%)"] >= 40]

selected_name = st.selectbox("Välj bolag att visa eller redigera", [""] + filtered_df["Bolagsnamn"].tolist())

# Init
if "clear_fields" not in st.session_state:
    st.session_state.clear_fields = False

if selected_name and not st.session_state.clear_fields:
    selected = df[df["Bolagsnamn"] == selected_name].iloc[0]
else:
    selected = pd.Series(dtype=float)

# Input
st.subheader("✏️ Lägg till eller redigera bolag")
col1, col2, col3 = st.columns(3)
col4, col5, col6 = st.columns(3)

with col1:
    name = st.text_input("Bolagsnamn", value=selected.get("Bolagsnamn", ""))
with col2:
    price = st.number_input("Nuvarande kurs", min_value=0.0, format="%.2f", value=selected.get("Nuvarande kurs", 0.0) if not st.session_state.clear_fields else 0.0)
with col3:
    vinst_1 = st.number_input("Vinst i år", min_value=0.0, format="%.2f", value=selected.get("Vinst i år", 0.0) if not st.session_state.clear_fields else 0.0)

with col4:
    vinst_2 = st.number_input("Vinst nästa år", min_value=0.0, format="%.2f", value=selected.get("Vinst nästa år", 0.0) if not st.session_state.clear_fields else 0.0)
with col5:
    oms_1 = st.number_input("Omsättning i år", min_value=0.0, format="%.2f", value=selected.get("Omsättning i år", 0.0) if not st.session_state.clear_fields else 0.0)
with col6:
    oms_2 = st.number_input("Omsättning nästa år", min_value=0.0, format="%.2f", value=selected.get("Omsättning nästa år", 0.0) if not st.session_state.clear_fields else 0.0)

st.markdown("#### 🔢 Nyckeltalshistorik")
pe_cols = st.columns(5)
ps_cols = st.columns(5)

pe_values = [pe_cols[i].number_input(f"P/E {i+1}", min_value=0.0, format="%.2f", value=selected.get(f"P/E {i+1}", 0.0) if not st.session_state.clear_fields else 0.0) for i in range(5)]
ps_values = [ps_cols[i].number_input(f"P/S {i+1}", min_value=0.0, format="%.2f", value=selected.get(f"P/S {i+1}", 0.0) if not st.session_state.clear_fields else 0.0) for i in range(5)]

# Beräkningar
if name:
    pe_target = vinst_2 * sum(pe_values)/5 if vinst_2 else 0
    ps_target = oms_2 * sum(ps_values)/5 if oms_2 else 0
    target = round((pe_target + ps_target)/2, 2) if (pe_target and ps_target) else 0
    underv = round((target - price) / price * 100, 2) if price else 0
    buy_30 = round(target * 0.7, 2)
    buy_40 = round(target * 0.6, 2)

    st.subheader("📊 Analys")
    st.write(f"🎯 Targetkurs: **{target} kr**")
    st.write(f"📉 Undervärdering: **{underv}%**")
    st.write(f"🟡 Köpkurs med 30% marginal: {buy_30} kr")
    st.write(f"🟢 Köpkurs med 40% marginal: {buy_40} kr")
else:
    st.warning("Ange ett bolagsnamn för att göra beräkningar.")

# Spara/uppdatera
if st.button("💾 Spara bolag"):
    if not name:
        st.error("Bolagsnamn krävs.")
    else:
        new_data = {
            "Bolagsnamn": name,
            "Nuvarande kurs": price,
            "Vinst i år": vinst_1,
            "Vinst nästa år": vinst_2,
            "Omsättning i år": oms_1,
            "Omsättning nästa år": oms_2,
            **{f"P/E {i+1}": pe_values[i] for i in range(5)},
            **{f"P/S {i+1}": ps_values[i] for i in range(5)},
            "Undervärdering (%)": underv,
            "Targetkurs": target
        }
        df = df[df["Bolagsnamn"] != name]
        df = df.append(new_data, ignore_index=True)
        save_data(df)
        st.success("Bolaget sparat!")
        st.experimental_rerun()

# Ta bort bolag
if selected_name and st.button("🗑️ Ta bort valt bolag"):
    df = df[df["Bolagsnamn"] != selected_name]
    save_data(df)
    st.success(f"{selected_name} borttaget.")
    st.experimental_rerun()

# Lägg till nytt bolag
if st.button("➕ Lägg till nytt bolag"):
    st.session_state.clear_fields = True
    st.experimental_rerun()

# Export
st.download_button("⬇️ Ladda ner data som CSV", df.to_csv(index=False), "bolag_data.csv", "text/csv")
