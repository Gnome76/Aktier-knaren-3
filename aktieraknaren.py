import streamlit as st
import sqlite3
import os
import pandas as pd

DB_PATH = os.path.join(os.getcwd(), "aktier_data.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS bolag (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            namn TEXT,
            kurs REAL,
            pe1 REAL, pe2 REAL, pe3 REAL, pe4 REAL, pe5 REAL,
            peg1 REAL, peg2 REAL, peg3 REAL, peg4 REAL, peg5 REAL,
            ps1 REAL, ps2 REAL, ps3 REAL, ps4 REAL, ps5 REAL,
            vinst_i_ar REAL, vinst_nasta_ar REAL,
            oms_tillv_i_ar REAL, oms_tillv_nasta_ar REAL
        )
        """)

def lagra_bolag(data):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
        INSERT INTO bolag (
            namn, kurs, pe1, pe2, pe3, pe4, pe5,
            peg1, peg2, peg3, peg4, peg5,
            ps1, ps2, ps3, ps4, ps5,
            vinst_i_ar, vinst_nasta_ar,
            oms_tillv_i_ar, oms_tillv_nasta_ar
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', data)

def uppdatera_bolag(data):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
        UPDATE bolag SET
            namn=?, kurs=?,
            pe1=?, pe2=?, pe3=?, pe4=?, pe5=?,
            peg1=?, peg2=?, peg3=?, peg4=?, peg5=?,
            ps1=?, ps2=?, ps3=?, ps4=?, ps5=?,
            vinst_i_ar=?, vinst_nasta_ar=?,
            oms_tillv_i_ar=?, oms_tillv_nasta_ar=?
        WHERE id=?
        ''', data)

def ta_bort_bolag(bolag_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM bolag WHERE id=?", (bolag_id,))

def hamta_bolag():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query("SELECT * FROM bolag", conn)

def berakna_riktkurs(data):
    snitt_pe = sum(data[3:8]) / 5
    riktkurs = data[18] * snitt_pe
    return riktkurs

init_db()
st.title("📈 Aktieräknaren")

# Lägg till nytt bolag
with st.expander("➕ Lägg till nytt bolag"):
    with st.form("lägg_till_bolag"):
        namn = st.text_input("Bolagsnamn")
        kurs = st.number_input("Nuvarande kurs", value=0.0)
        pe = [st.number_input(f"P/E kvartal {i+1}", value=0.0) for i in range(5)]
        peg = [st.number_input(f"PEG kvartal {i+1}", value=0.0) for i in range(5)]
        ps = [st.number_input(f"P/S kvartal {i+1}", value=0.0) for i in range(5)]
        vinst_i_ar = st.number_input("Vinst i år", value=0.0)
        vinst_nasta_ar = st.number_input("Vinst nästa år", value=0.0)
        oms_i_ar = st.number_input("Omsättningstillväxt i år (%)", value=0.0)
        oms_nasta_ar = st.number_input("Omsättningstillväxt nästa år (%)", value=0.0)
        submit = st.form_submit_button("Spara bolag")

        if submit:
            data = (
                namn, kurs,
                *pe, *peg, *ps,
                vinst_i_ar, vinst_nasta_ar,
                oms_i_ar, oms_nasta_ar
            )
            lagra_bolag(data)
            st.success("Bolaget har sparats!")

# Lista, redigera och ta bort bolag
st.header("📊 Sparade bolag")
df = hamta_bolag()
if not df.empty:
    st.dataframe(df)

    valt_bolag = st.selectbox("Välj bolag", df["namn"])
    rad = df[df["namn"] == valt_bolag].iloc[0]

    with st.expander("✏️ Redigera bolag"):
        with st.form("redigera_form"):
            kurs = st.number_input("Nuvarande kurs", value=rad["kurs"])
            pe = [st.number_input(f"P/E kvartal {i+1}", value=rad[f"pe{i+1}"]) for i in range(5)]
            peg = [st.number_input(f"PEG kvartal {i+1}", value=rad[f"peg{i+1}"]) for i in range(5)]
            ps = [st.number_input(f"P/S kvartal {i+1}", value=rad[f"ps{i+1}"]) for i in range(5)]
            vinst_i_ar = st.number_input("Vinst i år", value=rad["vinst_i_ar"])
            vinst_nasta_ar = st.number_input("Vinst nästa år", value=rad["vinst_nasta_ar"])
            oms_i_ar = st.number_input("Omsättningstillväxt i år", value=rad["oms_tillv_i_ar"])
            oms_nasta_ar = st.number_input("Omsättningstillväxt nästa år", value=rad["oms_tillv_nasta_ar"])
            update = st.form_submit_button("Uppdatera bolag")

            if update:
                data = (
                    rad["namn"], kurs,
                    *pe, *peg, *ps,
                    vinst_i_ar, vinst_nasta_ar,
                    oms_i_ar, oms_nasta_ar,
                    rad["id"]
                )
                uppdatera_bolag(data)
                st.success("Bolaget uppdaterat!")

    if st.button("🗑️ Ta bort detta bolag"):
        ta_bort_bolag(rad["id"])
        st.warning("Bolaget har tagits bort. Ladda om sidan.")

    if st.button("🎯 Beräkna riktkurs"):
        riktkurs = berakna_riktkurs(rad.tolist())
        st.success(f"Beräknad riktkurs: {riktkurs:.2f} kr")
else:
    st.info("Inga bolag sparade ännu.")
