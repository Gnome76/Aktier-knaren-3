import streamlit as st
import sqlite3
import pandas as pd

def init_db():
    conn = sqlite3.connect('aktieraknaren.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        kurs REAL,
        pe1 REAL, pe2 REAL, pe3 REAL, pe4 REAL, pe5 REAL,
        peg1 REAL, peg2 REAL, peg3 REAL, peg4 REAL, peg5 REAL,
        ps1 REAL, ps2 REAL, ps3 REAL, ps4 REAL, ps5 REAL,
        vinst_nuvarande REAL,
        vinst_next REAL,
        omsattning_nuvarande REAL,
        omsattning_next REAL
    )
    ''')
    conn.commit()
    conn.close()

def get_companies():
    conn = sqlite3.connect('aktieraknaren.db')
    df = pd.read_sql_query("SELECT * FROM companies", conn)
    conn.close()
    return df

def save_company(data, edit_id=None):
    conn = sqlite3.connect('aktieraknaren.db')
    cursor = conn.cursor()
    if edit_id:
        cursor.execute('DELETE FROM companies WHERE id=?', (edit_id,))
    cursor.execute('''
        INSERT INTO companies (name, kurs, pe1, pe2, pe3, pe4, pe5,
        peg1, peg2, peg3, peg4, peg5,
        ps1, ps2, ps3, ps4, ps5,
        vinst_nuvarande, vinst_next, omsattning_nuvarande, omsattning_next)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', data)
    conn.commit()
    conn.close()

def delete_company(company_id):
    conn = sqlite3.connect('aktieraknaren.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM companies WHERE id=?', (company_id,))
    conn.commit()
    conn.close()

st.set_page_config(page_title="Aktieraknaren")
st.title("📈 Aktieraknaren")

init_db()

st.header("Lägg till / Redigera bolag")

companies = get_companies()
edit_id = None
selected = st.selectbox("Välj bolag att redigera", [""] + companies["name"].tolist())
if selected:
    edit_row = companies[companies["name"] == selected].iloc[0]
    edit_id = int(edit_row["id"])
else:
    edit_row = {}

name = st.text_input("Bolagsnamn", edit_row.get("name", ""))
kurs = st.number_input("Nuvarande aktiekurs", value=edit_row.get("kurs", 0.0))

pe = [st.number_input(f"P/E kvartal {i+1}", value=edit_row.get(f"pe{i+1}", 0.0)) for i in range(5)]
peg = [st.number_input(f"PEG kvartal {i+1}", value=edit_row.get(f"peg{i+1}", 0.0)) for i in range(5)]
ps = [st.number_input(f"P/S kvartal {i+1}", value=edit_row.get(f"ps{i+1}", 0.0)) for i in range(5)]

vinst_nu = st.number_input("Vinst i år", value=edit_row.get("vinst_nuvarande", 0.0))
vinst_next = st.number_input("Vinst nästa år", value=edit_row.get("vinst_next", 0.0))

oms_iår = st.number_input("Omsättningstillväxt i år (%)", value=edit_row.get("omsattning_nuvarande", 0.0))
oms_next = st.number_input("Omsättningstillväxt nästa år (%)", value=edit_row.get("omsattning_next", 0.0))

if st.button("Spara bolag"):
    if name:
        all_data = [name, kurs] + pe + peg + ps + [vinst_nu, vinst_next, oms_iår, oms_next]
        save_company(all_data, edit_id)
        st.success("Bolaget har sparats!")
        st.experimental_rerun()
    else:
        st.warning("Fyll i bolagsnamn först")

if selected and st.button("❌ Ta bort bolag"):
    delete_company(edit_id)
    st.warning(f"Bolaget {selected} togs bort")
    st.experimental_rerun()

st.header("Alla bolag")
st.dataframe(get_companies())
