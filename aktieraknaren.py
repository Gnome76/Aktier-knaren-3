import streamlit as st
import json
import os

st.set_page_config(page_title="Aktieräknaren", layout="wide")

DB_FILE = "bolag_data.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

if "data" not in st.session_state:
    st.session_state.data = load_data()

if "selected_company" not in st.session_state:
    st.session_state.selected_company = None

if "is_adding_new" not in st.session_state:
    st.session_state.is_adding_new = False

# ------------------- FILTRERING -------------------
st.title("📊 Aktieräknaren")

col1, col2, col3 = st.columns(3)
with col1:
    underv30 = st.checkbox("Undervärderade 30–39,99 %")
with col2:
    underv40 = st.checkbox("Undervärderade ≥40 %")
with col3:
    underv_all = st.checkbox("Alla undervärderade")

filtrerade = []
for b in st.session_state.data:
    try:
        kurs = float(b["kurs"])
        target = float(b["targetkurs"])
        diff = ((target - kurs) / kurs) * 100
        if underv_all or (underv30 and 30 <= diff < 40) or (underv40 and diff >= 40):
            filtrerade.append(b)
    except:
        continue

# ------------------- VÄLJ BOLAG -------------------
namnlista = sorted([b["namn"] for b in st.session_state.data])
if not st.session_state.is_adding_new and namnlista:
    valt_namn = st.selectbox("📁 Välj bolag att visa/redigera", namnlista, key="select_company")
    valt_bolag = next((b for b in st.session_state.data if b["namn"] == valt_namn), None)
    st.session_state.selected_company = valt_bolag
else:
    valt_bolag = None

if st.button("➕ Lägg till nytt bolag"):
    st.session_state.selected_company = None
    st.session_state.is_adding_new = True
    st.experimental_rerun()

# ------------------- INMATNING -------------------
st.markdown("### 🧮 Nyckeltal")
namn = st.text_input("Bolagsnamn", value=valt_bolag["namn"] if valt_bolag else "")

kurs = st.number_input("Nuvarande kurs (kr)", min_value=0.0, step=0.01, format="%.2f",
                       value=float(valt_bolag["kurs"]) if valt_bolag else None)

# P/E
pe_cols = st.columns(5)
pe_list = []
for i in range(5):
    value = float(valt_bolag["pe"][i]) if valt_bolag else None
    pe = pe_cols[i].number_input(f"P/E {i+1}", min_value=0.0, step=0.01, format="%.2f", value=value)
    pe_list.append(pe)

# P/S
ps_cols = st.columns(5)
ps_list = []
for i in range(5):
    value = float(valt_bolag["ps"][i]) if valt_bolag else None
    ps = ps_cols[i].number_input(f"P/S {i+1}", min_value=0.0, step=0.01, format="%.2f", value=value)
    ps_list.append(ps)

# Vinst
vinster = st.columns(2)
vinst_i_ar = vinster[0].number_input("Vinst i år (kr)", step=0.01, format="%.2f",
                                     value=float(valt_bolag["vinst_i_ar"]) if valt_bolag else None)
vinst_next = vinster[1].number_input("Vinst nästa år (kr)", step=0.01, format="%.2f",
                                     value=float(valt_bolag["vinst_next"]) if valt_bolag else None)

# Omsättningstillväxt
oms_cols = st.columns(2)
oms_i_ar = oms_cols[0].number_input("Omsättningstillväxt i år (%)", step=0.1, format="%.1f",
                                    value=float(valt_bolag["oms_i_ar"]) if valt_bolag else None)
oms_next = oms_cols[1].number_input("Omsättningstillväxt nästa år (%)", step=0.1, format="%.1f",
                                    value=float(valt_bolag["oms_next"]) if valt_bolag else None)

# ------------------- BERÄKNING -------------------
avg_pe = sum(pe_list) / len(pe_list)
avg_ps = sum(ps_list) / len(ps_list)

target_pe = round(vinst_next * avg_pe, 2)
target_ps = round((1 + (oms_next / 100)) * kurs * avg_ps, 2)
targetkurs = round((target_pe + target_ps) / 2, 2)

# ------------------- SPARA -------------------
if st.button("💾 Spara bolag"):
    nytt_bolag = {
        "namn": namn,
        "kurs": kurs,
        "pe": pe_list,
        "ps": ps_list,
        "vinst_i_ar": vinst_i_ar,
        "vinst_next": vinst_next,
        "oms_i_ar": oms_i_ar,
        "oms_next": oms_next,
        "targetkurs": targetkurs,
    }

    existerar = False
    for i, b in enumerate(st.session_state.data):
        if b["namn"] == namn:
            st.session_state.data[i] = nytt_bolag
            existerar = True
            break
    if not existerar:
        st.session_state.data.append(nytt_bolag)

    st.session_state.data = sorted(st.session_state.data, key=lambda x: x["namn"])
    save_data(st.session_state.data)
    st.session_state.is_adding_new = False
    st.success(f"{'Uppdaterade' if existerar else 'Sparade'} bolaget {namn}.")
    st.experimental_rerun()

# ------------------- RESULTAT -------------------
if namn and kurs:
    st.markdown("### 📈 Analys")
    st.write(f"🎯 **Targetkurs (snitt): {targetkurs} kr**")
    st.write(f"📊 P/E-baserad targetkurs: {target_pe} kr")
    st.write(f"📊 P/S-baserad targetkurs: {target_ps} kr")

    skillnad = ((targetkurs - kurs) / kurs) * 100
    status = "Undervärderad" if skillnad >= 0 else "Övervärderad"
    st.write(f"💡 **{status} med {abs(round(skillnad, 2))}%**")

    köp_30 = round(targetkurs * 0.7, 2)
    köp_40 = round(targetkurs * 0.6, 2)
    st.write(f"📉 Köp vid 30% marginal: {köp_30} kr")
    st.write(f"📉 Köp vid 40% marginal: {köp_40} kr")

# ------------------- TA BORT -------------------
if valt_bolag and st.button("🗑️ Ta bort bolag"):
    st.session_state.data = [b for b in st.session_state.data if b["namn"] != valt_bolag["namn"]]
    save_data(st.session_state.data)
    st.success(f"{valt_bolag['namn']} har tagits bort.")
    st.experimental_rerun()
