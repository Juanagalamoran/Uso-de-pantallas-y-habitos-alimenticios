# -*- coding: utf-8 -*-
"""
Created on Thu May 28 13:56:25 2026

@author: cuina
"""

import pandas as pd
import numpy as np

ruta = 'C:/Users/cuina/OneDrive/Escritorio/proyectoSole/'

#CARGA DE DATOS 

df_variables = pd.read_csv(ruta + 'ennys2_variables.csv', encoding='latin1', sep=';')

df_encuesta = pd.read_csv(ruta + 'ENNyS2_encuesta.csv', encoding='latin1', sep=',')

df_nutrientes = pd.read_csv(ruta + 'Base_Nutrientes.csv', encoding='latin1', sep=',')

df_alimentos = pd.read_csv(ruta + 'Base_Alimentos_Bebidas_Suplementos.csv', encoding='latin1', sep=',')

#%%

#LIMPIEZA DE DATOS

#este patron es para el frame de variables
patron = r'^(?:C3_HAC_5_1|C3_HAC_5_12|T_C3_FCA_6_1_1|C3_EE_7_|T_C3_EE_7_2_|C3_AAPC_8_)'

df_variables = df_variables[df_variables['id'].str.contains(patron, na=False, regex=True)]

# filtramos encuestados entre 13 y 17 años en el frame d e encuesta
df_encuesta = df_encuesta[df_encuesta['E_CUEST'].str.contains('13 a 17', na=False)]

#filtramos col de interes
df_encuesta= df_encuesta.filter(regex=r'^(C_3_HAC|HAC_|T_C3_FCA|FCA_|C3_EE|T_C3_EE|C3_AAPC|F_|id)')

# esta func elimina las col cuyas rtas son menos del 1%
umbral = 24 # representa el 1% de las rta rta_contestadas / rta en el rango etario de interes
def borrar_col_vacias(df_encuesta):

    df_temporal = df_encuesta.copy()
    
    df_temporal = df_temporal.replace(r'^\s*$', np.nan, regex=True)
    
    respuestas_por_columna = df_temporal.count()
    
    columnas_a_borrar = respuestas_por_columna[respuestas_por_columna < umbral].index

    print("--- Columnas eliminadas por tener pocas respuestas ---")
    if len(columnas_a_borrar) > 0:
        for col in columnas_a_borrar:
            # Muestra el nombre de la columna y cuántas respuestas reales tenía
            print(f"- {col} (Respuestas reales: {respuestas_por_columna[col]})")
    else:
        print("No se eliminó ninguna columna.")
    print("------------------------------------------------------\n")

    df_resultado = df_encuesta.drop(columns=columnas_a_borrar)
    
    print(f"Se eliminaron {len(columnas_a_borrar)} columnas por tener menos de 214 respuestas reales.")
    return df_resultado


df_encuesta = borrar_col_vacias(df_encuesta)

#%%

# las que empiezan con C3_HAC, T_C3_FCA, C3_EE, T_ C3_FCA , T_C3_EE, C3_AAPC
"""
habitos alimentarios C3_HAC_5_1_
snacks T_C3_FCA_6_1
entorno escolar C3_EE_7_5 Y C3_EE_7_2
peso y talla C3_AAPC_8
"""