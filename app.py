import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Projekt DAX-Analyse",
    layout="wide"
)

# ── Styling ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.stApp { background-color: #020817; color: white; }
section[data-testid="stSidebar"] { background-color: #1e1e2f; }
section[data-testid="stSidebar"] * { color: white !important; }
label { color: white !important; }
div[data-baseweb="select"] * { color: black !important; }

/* Aktien-Buttons in Sidebar */
.stButton > button {
    background-color: #2a2a3d;
    color: white !important;
    border: 1px solid #444;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 12px;
    margin: 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 100%;
}
.stButton > button:hover {
    background-color: #3a3a5c;
    border-color: #888;
}
</style>
""", unsafe_allow_html=True)

# ── Hilfsfunktionen (aus streamlit_analysis.py) ───────────────────────────────
def average_price(dataframe, selected_metric):
    results = {}
    stock_names = dataframe.iloc[:, 1].unique()
    for stock in stock_names:
        selected_stock_data = dataframe[dataframe.iloc[:, 1] == stock]
        avg = selected_stock_data[selected_metric].mean()
        results[stock] = avg
    return results

def volatility(dataframe, selected_avg, selected_metric):
    results = {}
    stock_names = dataframe.iloc[:, 1].unique()
    for stock in stock_names:
        selected_stock_data = dataframe[dataframe.iloc[:, 1] == stock].copy()
        if selected_avg == "Standardabweichung":
            avg = selected_stock_data[selected_metric].std()
            results[stock] = avg
        elif selected_avg == "Durchschnittliche Schwankungsbreite":
            if all(c in selected_stock_data.columns for c in ["High", "Low", "Close"]):
                selected_stock_data["Previous Close"] = selected_stock_data["Close"].shift(1)
                selected_stock_data["TR"] = np.maximum(
                    selected_stock_data["High"] - selected_stock_data["Low"],
                    np.maximum(
                        abs(selected_stock_data["High"] - selected_stock_data["Previous Close"]),
                        abs(selected_stock_data["Low"] - selected_stock_data["Previous Close"])
                    )
                )
                selected_stock_data.dropna(subset=["TR"], inplace=True)
                atr_period = len(selected_stock_data)
                if atr_period > 1:
                    selected_stock_data["ATR"] = selected_stock_data["TR"].rolling(window=atr_period).mean()
                    results[stock] = selected_stock_data["ATR"].iloc[-1]
                else:
                    results[stock] = np.nan
            else:
                results[stock] = np.nan
    return results

def insights(dataframe, sector):
    sector_data = dataframe[dataframe.iloc[:, -2] == sector]
    stock_names = sector_data.iloc[:, 1].unique()
    sector_return = 0
    for i in stock_names:
        stock_data = sector_data[sector_data.iloc[:, 1] == i]
        roi = stock_data["Close"].iloc[-1] - stock_data["Close"].iloc[0]
        sector_return += roi
    return sector_return / len(stock_names) if len(stock_names) > 0 else 0

# ── Daten laden ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("DAXDataStreamlit.csv")
    df["Date"] = pd.to_datetime(df["Date"], utc=True)
    return df

df = load_data()
alle_aktien = sorted(df["Long Name"].unique().tolist())

# ── Session State: ausgewählte Aktien ─────────────────────────────────────────
if "selected_stocks" not in st.session_state:
    st.session_state.selected_stocks = [alle_aktien[0]]

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("Sidebar")
st.sidebar.write("Hier kannst du die zu analysierenden Aktien auswählen:")
st.sidebar.write("**Auswahl**")

# Aktien als klickbare Buttons (Toggle)
cols = st.sidebar.columns(3)
for i, aktie in enumerate(alle_aktien):
    with cols[i % 3]:
        is_selected = aktie in st.session_state.selected_stocks
        label = aktie.replace(" AG", "").replace(" SE", "").replace(" KGaA", "")[:10]
        if is_selected:
            label = "✓ " + label
        if st.button(label, key=f"btn_{aktie}"):
            if aktie in st.session_state.selected_stocks:
                if len(st.session_state.selected_stocks) > 1:
                    st.session_state.selected_stocks.remove(aktie)
            else:
                st.session_state.selected_stocks.append(aktie)
            st.rerun()

selected_stocks = st.session_state.selected_stocks

# ── Zeitraum Filter ───────────────────────────────────────────────────────────
max_date = df["Date"].max()
zeitraum_map = {
    "1 Monat": 30,
    "3 Monate": 90,
    "6 Monate": 180,
    "1 Jahr": 365
}

# ── Hauptbereich ──────────────────────────────────────────────────────────────
left, right = st.columns([2, 1])

with left:
    zeitraum = st.selectbox("Zeit-Einstellungen", list(zeitraum_map.keys()), index=2)
    tage = zeitraum_map[zeitraum]
    start_date = max_date - pd.Timedelta(days=tage)
    df_filtered = df[(df["Date"] >= start_date) & (df["Long Name"].isin(selected_stocks))]

    st.title("Projekt DAX-Analyse")
    st.write("Mit dieser App kannst du die letzten **sechs Monate** des DAX analysieren. 📊")
    st.write("Wähle Aktien aus der Sidebar aus um Analysen durchzuführen!")

    # Chart
    if not df_filtered.empty:
        chart_data = df_filtered.pivot_table(index="Date", columns="Long Name", values="Close")
        st.subheader("Aktienkurs im Zeitverlauf")
        st.line_chart(chart_data)

    # Dataframe Toggle
    show_data = st.toggle("Dataframe anzeigen")
    if show_data:
        st.dataframe(df_filtered)

with right:
    st.markdown("## Analyse-Tools")

    tab1, tab2, tab3 = st.tabs(["Average", "Volatility", "Insights"])

    with tab1:
        wert = st.selectbox("Welcher Wert?", ["Open", "High", "Low", "Close", "Volume"], key="avg_wert")
        if not df_filtered.empty:
            avg_results = average_price(df_filtered, wert)
            st.write(f"**Durchschnittl. {wert}-Preis:**")
            for stock, val in avg_results.items():
                st.write(f"{stock}: **{val:,.2f}**")

    with tab2:
        methode = st.selectbox(
            "Methode",
            ["Standardabweichung", "Durchschnittliche Schwankungsbreite"],
            key="vol_methode"
        )
        vola_wert = st.selectbox("Welcher Wert?", ["Open", "High", "Low", "Close", "Volume"], key="vol_wert")
        if not df_filtered.empty:
            vol_results = volatility(df_filtered, methode, vola_wert)
            st.write(f"**{methode}:**")
            for stock, val in vol_results.items():
                if not np.isnan(val):
                    st.write(f"{stock}: **{val:,.2f}**")

    with tab3:
        sektoren = df["Sector"].dropna().unique().tolist()
        sektor = st.selectbox("Sektor auswählen", sorted(sektoren), key="sektor")
        if not df_filtered.empty:
            roi = insights(df_filtered, sektor)
            farbe = "🟢" if roi >= 0 else "🔴"
            st.write(f"**Ø Return im Sektor '{sektor}':**")
            st.metric(label="ROI", value=f"{roi:,.2f} €", delta=f"{roi:,.2f}")