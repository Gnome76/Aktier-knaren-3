import streamlit as st
import sqlite3
import os
import pandas as pd

DB_PATH = os.path.join(os.getcwd(), "aktier_data.db")

# Initiera databasen
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS bolag (
                id INTEGER PRIMARY KEY,
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
        conn.execute(
            """
            INSERT INTO bolag (
                namn, kurs, pe1, pe2, pe3, pe4, pe5,
                peg1, peg2, peg3, peg4, peg5,
                ps1, ps2, ps3, ps4, ps5,
                vinst_i_ar, vinst_nasta_ar,
                oms_tillv_i_ar, oms_tillv_nasta_ar
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, data)

def hamta_bolag():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query("SELECT * FROM bolag", conn)

def berakna_riktkurs(data):
    snitt_pe = sum(data[2:7]) / 5
    riktkurs = data[17] * snitt_pe
    return riktkurs

# App start
init_db()
st.title("AktierÃ¤knaren")

with st.form("lÃ¤gg_till_bolag"):
    namn = st.text_input("Bolagsnamn")
    kurs = st.number_input("Nuvarande kurs", value=0.0)
    pe = [st.number_input(f"P/E kvartal {i+1}", value=0.0) for i in range(5)]
    peg = [st.number_input(f"PEG kvartal {i+1}", value=0.0) for i in range(5)]
    ps = [st.number_input(f"P/S kvartal {i+1}", value=0.0) for i in range(5)]
    vinst_i_ar = st.number_input("Vinst i Ã¥r", value=0.0)
    vinst_nasta_ar = st.number_input("Vinst nÃ¤sta Ã¥r", value=0.0)
    oms_i_ar = st.number_input("OmsÃ¤ttningstillvÃ¤xt i Ã¥r (%)", value=0.0)
    oms_nasta_ar = st.number_input("OmsÃ¤ttningstillvÃ¤xt nÃ¤sta Ã¥r (%)", value=0.0)
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

st.header("Sparade bolag")
bolag = hamta_bolag()
if not bolag.empty:
    st.dataframe(bolag)

    valt_bolag = st.selectbox("VÃ¤lj bolag fÃ¶r riktkurs", bolag["namn"])
    if st.button("BerÃ¤kna riktkurs"):
        data = bolag[bolag["namn"] == valt_bolag].iloc[0].tolist()
        riktkurs = berakna_riktkurs(data)
        st.success(f"BerÃ¤knad riktkurs: {riktkurs:.2f} kr")
else:
    st.info("Inga bolag sparade Ã¤n.")
