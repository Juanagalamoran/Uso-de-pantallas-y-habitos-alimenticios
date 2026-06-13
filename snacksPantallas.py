# -*- coding: utf-8 -*-
"""
Created on Thu May 28 13:56:25 2026

@author: cuina
"""

import pandas as pd
import numpy as np

#ruta = 'C:/Users/Juani/OneDrive/Escritorio/proyectoSole/Uso-de-pantallas-y-habitos-alimenticios/' 
ruta = 'C:/Users/cuina/OneDrive/Escritorio/proyectoSole/'

# 1. CARGA DE DATOS
df_variables = pd.read_csv(ruta + 'ennys2_variables.csv', encoding='latin1', sep=';')
df_encuesta = pd.read_csv(ruta + 'ENNyS2_encuesta.csv', encoding='latin1', sep=',')

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
df_encuesta = df_encuesta.filter(regex=r'^(C_3_HAC|HAC_5_10|HAC_5_12|HAC_5_13|T_C3_FCA|FCA_|C3_EE|T_C3_EE|F_|id|region|Edadd|antropo_sex)')

#%%
#AHORA SACO DE LAS COLUMNA DE F QUE INDICAN GRUPOS DE ALIMENTOS LAS QUE NO ME INTERESAN
columnas_a_borrar = ['T_C3_EE_7_2_2', 'T_C3_EE_7_2_3', 'T_C3_EE_7_2_7' ,'T_C3_EE_7_2_8' , 'T_C3_EE_7_2_9', 'F_FF', 'F_V', 'F_LYQ', 'F_CR', 'F_PESC']
df_encuesta = df_encuesta.drop(columns=columnas_a_borrar)
