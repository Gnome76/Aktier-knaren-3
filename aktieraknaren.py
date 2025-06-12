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

# -------- FILTER --------
st.title("📊 Aktieräknaren")

filter_col1, filter_col2, filter_col3 = st.columns(3)
with filter_col1:
    underv30 = st.checkbox("Undervärderade 30–39,99 %")
with filter_col2:
    underv40 = st.checkbox("Undervärderade ≥40 %")
with filter_col3:
    underv_all = st.checkbox("Alla undervärderade")

filtrerade_bolag = []
for b in st.session_state.data:
    try:
        kurs = float(b["kurs"])
        target = float(b["targetkurs"])
        diff = ((target - kurs) / kurs) * 100
        if underv_all or (underv30 and 30 <= diff < 40) or (underv40 and diff >= 40):
            filtrerade_bolag.append(b)
    except:
        continue

valt_bolag = None
if filtrerade_bolag:
    namnlista = [b["namn"] for b in filtrerade_bolag]
    valt_namn = st.selectbox("📁 Välj bolag att visa/redigera", namnlista)
    valt_bolag = next((b for b in st.session_state.data if b["namn"] == valt_namn), None)

# -------- INMATNING --------
st.markdown("### 🔧 Nyckeltal")

namn = st.text_input("Bolagsnamn", value=valt_bolag["namn"] if valt_bolag else "")
kurs = st.number_input("Nuvarande kurs (kr)", min_value=0.0, step=0.01, format="%.2f", value=float(valt_bolag["kurs"]) if valt_bolag else 0.0)

pe_values = st.columns(5)
pe_list = [pe_values[i].number_input(f"P/E {i+1}", min_value=0.0, step=0.01, format="%.2f", value=float(valt_bolag["pe"][i]) if valt_bolag else 0.0) for i in range(5)]

ps_values = st.columns(5)
ps_list = [ps_values[i].number_input(f"P/S {i+1}", min_value=0.0, step=0.01, format="%.2f", value=float(valt_bolag["ps"][i]) if valt_bolag else 0.0) for i in range(5)]

col_vinst = st.columns(2)
vinst_i_ar = col_vinst[0].number_input("Vinst i år (kr)", value=float(valt_bolag["vinst_i_ar"]) if valt_bolag else 0.0, step=0.01, format="%.2f")
vinst_next = col_vinst[1].number_input("Vinst nästa år (kr)", value=float(valt_bolag["vinst_next"]) if valt_bolag else 0.0, step=0.01, format="%.2f")

col_oms = st.columns(2)
oms_vt_i_ar = col_oms[0].number_input("Omsättningstillväxt i år (%)", value=float(valt_bolag["oms_i_ar"]) if valt_bolag else 0.0, step=0.1, format="%.1f")
oms_vt_next = col_oms[1].number_input("Omsättningstillväxt nästa år (%)", value=float(valt_bolag["oms_next"]) if valt_bolag else 0.0, step=0.1, format="%.1f")

# -------- BERÄKNING --------
avg_pe = sum(pe_list) / len(pe_list)
avg_ps = sum(ps_list) / len(ps_list)
target_pe = round(vinst_next * avg_pe, 2)
target_ps = round((1 + (oms_vt_next / 100)) * kurs * avg_ps, 2)
targetkurs = round((target_pe + target_ps) / 2, 2)

# -------- SPARA BOLAG --------
if st.button("💾 Spara bolag"):
    nytt_bolag = {
        "namn": namn,
        "kurs": kurs,
        "pe": pe_list,
        "ps": ps_list,
        "vinst_i_ar": vinst_i_ar,
        "vinst_next": vinst_next,
        "oms_i_ar": oms_vt_i_ar,
        "oms_next": oms_vt_next,
        "targetkurs": targetkurs,
    }

    finns = any(b["namn"] == namn for b in st.session_state.data)
    if finns:
        for i, b in enumerate(st.session_state.data):
            if b["namn"] == namn:
                st.session_state.data[i] = nytt_bolag
                break
    else:
        st.session_state.data.append(nytt_bolag)

    st.session_state.data = sorted(st.session_state.data, key=lambda x: x["namn"])
    save_data(st.session_state.data)
    st.success(f"{'Uppdaterade' if finns else 'Sparade'} bolaget {namn}.")

# -------- RESULTAT --------
if namn and kurs:
    st.markdown("### 📈 Analys")
    st.write(f"🎯 **Targetkurs (snitt): {targetkurs} kr**")
    st.write(f"📊 Targetkurs via P/E: {target_pe} kr")
    st.write(f"📊 Targetkurs via P/S: {target_ps} kr")
    skillnad = ((targetkurs - kurs) / kurs) * 100
    status = "Undervärderad" if skillnad >= 0 else "Övervärderad"
    st.write(f"💡 **{status} med {abs(round(skillnad, 2))}%**")

    köp_30 = round(targetkurs * 0.7, 2)
    köp_40 = round(targetkurs * 0.6, 2)
    st.write(f"📉 Köp vid 30% marginal: **{köp_30} kr**")
    st.write(f"📉 Köp vid 40% marginal: **{köp_40} kr**")

# -------- TA BORT --------
if valt_bolag and st.button("🗑️ Ta bort bolag"):
    st.session_state.data = [b for b in st.session_state.data if b["namn"] != valt_bolag["namn"]]
    save_data(st.session_state.data)
    st.success(f"Bolaget {valt_bolag['namn']} har tagits bort.")
    st.experimental_rerun()

# -------- NYTT BOLAG --------
if st.button("➕ Lägg till nytt bolag"):
    st.experimental_rerun()
