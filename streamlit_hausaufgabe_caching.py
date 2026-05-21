import warnings
import sys
import streamlit as st
import pandas as pd
import numpy as np


def load_data():
    # Erzeugt ein Dataframe mit zufälligen Zahlen
    data = pd.DataFrame(np.random.randint(1, 100, size=(10, 2)), columns=["Column 1", "Column 2"])
    return data

# Lädt das Dataframe
df = load_data()

# Zeigt das Dataframe in der App
st.header("Simple Data Summary App")
st.write("Here is a random dataset:")
st.write(df)

# Zeigt Statistiken bzgl. der Daten an
st.write(f"Sum of all numbers: {df.sum().sum()}")
st.write(f"Mean of all numbers: {df.mean().mean()}")

counter = 0

# Counter Button
if st.button("Increment Counter"):
    counter += 1

# Reset Button
if st.button("Reset"):
    counter = 0

# Zeigt den aktuellen Zählerstand an
st.write(f"Counter: {counter}")