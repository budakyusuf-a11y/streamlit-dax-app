import streamlit as st
import pandas as pd
import numpy as np


# 1. CACHING: @st.cache_data sorgt dafür, dass load_data() nur einmal
#    ausgeführt wird und das Dataframe nicht bei jedem Rerun neu generiert wird.
@st.cache_data
def load_data():
    data = pd.DataFrame(np.random.randint(1, 100, size=(10, 2)), columns=["Column 1", "Column 2"])
    return data


# 2. SESSION STATE: Counter wird in st.session_state gespeichert,
#    damit der Wert bei einem Rerun nicht auf 0 zurückgesetzt wird.
if "counter" not in st.session_state:
    st.session_state.counter = 0

df = load_data()

st.header("Simple Data Summary App")
st.write("Here is a random dataset:")
st.write(df)

st.write(f"Sum of all numbers: {df.sum().sum()}")
st.write(f"Mean of all numbers: {df.mean().mean()}")

# 3. BUTTONS: Werte werden direkt in st.session_state geändert
if st.button("Increment Counter"):
    st.session_state.counter += 1

if st.button("Reset"):
    st.session_state.counter = 0

st.write(f"Counter: {st.session_state.counter}")