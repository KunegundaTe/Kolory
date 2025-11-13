# color_atlas_app.py
import streamlit as st
import numpy as np
import pandas as pd
from matplotlib import colors
import matplotlib.pyplot as plt
from colorspacious import cspace_convert

st.title("Generator siatki kolorów")

# Wprowadzanie koloru HEX
hex_color = st.text_input("Wpisz kolor bazowy HEX (np. #FF0000):", "#FF0000")

if st.button("Generuj atlas"):
    try:
        # konwersja HEX do RGB
        rgb = colors.to_rgb(hex_color)
        rgb_arr = np.array(rgb)

        # liczba kroków
        steps = 21  # 10 w prawo, 10 w lewo + bazowy

        # generowanie rozjaśniania/przyciemniania
        lighter = [np.clip(rgb_arr + (1 - rgb_arr)*(i/10), 0, 1) for i in range(1, 11)]
        darker = [np.clip(rgb_arr * (1 - i/10), 0, 1) for i in range(10,0,-1)]
        row_rgb = darker + [rgb_arr] + lighter

        # konwersja do LAB
        row_lab = [cspace_convert(c, "sRGB1", "CIELab") for c in row_rgb]

        # desaturacja w dół
        final_grid = []
        for i in range(11):
            factor = 1 - i*0.1  # desaturacja co 10%
            new_row = []
            for lab in row_lab:
                L, a, b = lab
                a *= factor
                b *= factor
                new_row.append([L, a, b])
            final_grid.append(new_row)

        # konwersja LAB z powrotem do RGB
        final_rgb_grid = [[np.clip(cspace_convert(c, "CIELab", "sRGB1"),0,1) for c in row] for row in final_grid]

        # rysowanie siatki
        fig, ax = plt.subplots(figsize=(12,6))
        ax.imshow(final_rgb_grid, aspect='auto')
        ax.axis('off')
        st.pyplot(fig)

        # tworzenie pliku XLSX
        df_list = []
        for r, row in enumerate(final_rgb_grid):
            for c, rgb_val in enumerate(row):
                df_list.append({
                    "Wiersz": r+1,
                    "Kolumna": c+1,
                    "HEX": colors.to_hex(rgb_val),
                    "R": int(rgb_val[0]*255),
                    "G": int(rgb_val[1]*255),
                    "B": int(rgb_val[2]*255)
                })
        df = pd.DataFrame(df_list)
        df.to_excel("color_grid.xlsx", index=False)
        st.success("XLSX wygenerowany: color_grid.xlsx")
    except Exception as e:
        st.error(f"Coś poszło nie tak: {e}")
