# -*- coding: utf-8 -*-
"""
Created on Thu May 28 13:56:25 2026

@author: cuina
"""

import pandas as pd
import numpy as np

ruta = 'C:/Users/Juani/OneDrive/Escritorio/proyectoSole/Uso-de-pantallas-y-habitos-alimenticios/' 
#ruta = 'C:/Users/cuina/OneDrive/Escritorio/proyectoSole/'

# 1. CARGA DE DATOS
df_variables = pd.read_csv(ruta + 'ennys2_variables.csv', encoding='latin1', sep=';')
df_encuesta = pd.read_csv(ruta + 'ENNyS2_encuesta.csv', encoding='latin1', sep=';')

#%%
# ==========================================
# 2. LIMPIEZA DE BASE ENCUESTA
# ==========================================

# Filtrados iniciales de la encuesta
patron_variables = r'^(?:C3_HAC_5_1|C3_HAC_5_12|T_C3_FCA_6_1_1|C3_EE_7_|T_C3_EE_7_2_|C3_AAPC_8_)'
df_variables = df_variables[df_variables['id'].str.contains(patron_variables, na=False, regex=True)]
df_encuesta = df_encuesta[df_encuesta['E_CUEST'].str.contains('13 a 17', na=False)]

#%%
# Filtrar columnas por texto
df_encuesta = df_encuesta.filter(regex=r'^(C_3_HAC|HAC_|T_C3_FCA|FCA_|C3_EE|T_C3_EE|C3_AAPC|F_|id|region|Edadd|antropo_sex)')

# Borrar columnas vacías con pasos simples
#df_encuesta = df_encuesta.replace(r'^\s*$', np.nan, regex=True)
#conteo_respuestas = df_encuesta.count()
#columnas_a_borrar = conteo_respuestas[conteo_respuestas < 24].index

#df_encuesta = df_encuesta.drop(columns=columnas_a_borrar)
#%%
columnas_a_borrar = ['T_C3_EE_7_2_2', 'T_C3_EE_7_2_3', 'T_C3_EE_7_2_7' ,'T_C3_EE_7_2_8' , 'T_C3_EE_7_2_9' ]
df_encuesta = df_encuesta.drop(columns=columnas_a_borrar)

df_encuesta.to_csv(
    r"C:\Users\juani\OneDrive\Escritorio\encuesta_filtrada.csv",
    index=False,
    encoding="utf-8"
)
#%%
#Oferta alimentaria en la escuela

columnas_kiosco = [
    'C3_EE_7_5_O1','C3_EE_7_5_O2','C3_EE_7_5_O3',
    'C3_EE_7_5_O4','C3_EE_7_5_O5','C3_EE_7_5_O6',
    'C3_EE_7_5_O9','C3_EE_7_5_O10',
    'C3_EE_7_5_O11','C3_EE_7_5_O12'
]

def cantidad_no_recomendados(fila):

    contador = 0

    for col in columnas_kiosco:

        valor = str(fila[col])

        if ('Bebidas con az' in valor or
            'Productos de copet' in valor or
            'Golosinas' in valor or
            'Facturas' in valor):

            contador += 1

    return contador


df_encuesta['cant_E_NR'] = df_encuesta.apply(
    cantidad_no_recomendados,
    axis=1
)


columnas_oferta = [
    'T_C3_EE_7_2_1',
    'T_C3_EE_7_2_4',
    'T_C3_EE_7_2_5',
    'T_C3_EE_7_2_6',
    'T_C3_EE_7_2_10'
]

mapeo = {
    'Nunca': 0,
    'A veces': 1,
    'Siempre': 2
}

df_encuesta[columnas_oferta] = (
    df_encuesta[columnas_oferta]
    .replace(mapeo)
)


consumo_escolar = df_encuesta[
    [
        'id',
        'cant_E_NR',
        'C3_EE_7_1',
          'T_C3_EE_7_2_1',
          'T_C3_EE_7_2_4',
          'T_C3_EE_7_2_5',
          'T_C3_EE_7_2_6',
          'T_C3_EE_7_2_10'
    ]
].copy()

consumo_escolar = consumo_escolar.rename(columns={
    'C3_EE_7_1' : 'Come en la escuela',
    'T_C3_EE_7_2_1': 'OE_bebidas_azucaradas',
  
  
    'T_C3_EE_7_2_4': 'OE_copetin',
    'T_C3_EE_7_2_5': 'OE_golosinas',
    'T_C3_EE_7_2_6': 'OE_facturas',
   
  
    'T_C3_EE_7_2_10': 'OE_sandwich'
})

print(consumo_escolar.head())
    