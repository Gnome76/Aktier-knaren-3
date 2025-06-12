import streamlit as st

st.set_page_config(page_title="Aktieräknaren", layout="centered")
st.title("🎯 Aktieräknaren – Beräkna Targetkurs")

with st.form("input_form"):
    namn = st.text_input("Bolagsnamn")

    st.subheader("Nyckeltal – P/E")
    pe_hist = [st.number_input(f"P/E historik {i+1}", min_value=0.0, step=0.1, key=f"pe{i}") for i in range(5)]

    st.subheader("Nyckeltal – PEG")
    peg_hist = [st.number_input(f"PEG historik {i+1}", min_value=0.0, step=0.1, key=f"peg{i}") for i in range(5)]

    st.subheader("Nyckeltal – P/S")
    ps_hist = [st.number_input(f"P/S historik {i+1}", min_value=0.0, step=0.1, key=f"ps{i}") for i in range(5)]

    st.subheader("Vinstprognoser")
    vinst_i_ar = st.number_input("Förväntad vinst i år (per aktie)", step=0.01)
    vinst_nasta_ar = st.number_input("Förväntad vinst nästa år (per aktie)", step=0.01)

    st.subheader("Omsättningstillväxt")
    oms_tillv_i_ar = st.number_input("Omsättningstillväxt i år (%)", step=0.1)
    oms_tillv_nasta_ar = st.number_input("Omsättningstillväxt nästa år (%)", step=0.1)

    submitted = st.form_submit_button("🔍 Beräkna Targetkurs")

if submitted:
    if vinst_i_ar <= 0 or vinst_nasta_ar <= 0:
        st.error("❌ Vinstvärden måste vara större än 0.")
    else:
        # Snittberäkningar
        pe_snitt = sum(pe_hist) / len(pe_hist)
        peg_snitt = sum(peg_hist) / len(peg_hist)
        ps_snitt = sum(ps_hist) / len(ps_hist)
        vinsttillvaxt = ((vinst_nasta_ar - vinst_i_ar) / vinst_i_ar) * 100
        oms_tillv_snitt = (oms_tillv_i_ar + oms_tillv_nasta_ar) / 2

        # Targetkurser
        target_pe = vinst_nasta_ar * pe_snitt
        pe_via_peg = peg_snitt * vinsttillvaxt
        target_peg = vinst_nasta_ar * pe_via_peg
        target_ps = ps_snitt * (1 + oms_tillv_snitt / 100)  # Relativt mått

        # Slutligt snitt
        target_snitt = (target_pe + target_peg + target_ps) / 3

        st.markdown(f"### 📊 Resultat för **{namn}**")
        st.success(f"📌 Targetkurs baserat på P/E: **{target_pe:.2f} kr**")
        st.success(f"📌 Targetkurs baserat på PEG: **{target_peg:.2f} kr**")
        st.success(f"📌 Targetkurs baserat på P/S (relativt): **{target_ps:.2f}**")
        st.subheader(f"🎯 Slutlig riktkurs (snitt): **{target_snitt:.2f} kr**")
