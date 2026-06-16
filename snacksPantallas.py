# -*- coding: utf-8 -*-
"""
Created on Thu May 28 13:56:25 2026

@author: cuina
"""

import pandas as pd
import numpy as np

ruta = 'C:/Users/Juani/OneDrive/Escritorio/proyectoSole/Uso-de-pantallas-y-habitos-alimenticios/' 
#ruta = 'C:/Users/cuina/OneDrive/Escritorio/proyectoSole/'

# Raw data
df_variables = pd.read_csv(ruta + 'ennys2_variables.csv', encoding='latin1', sep=';')
df_encuesta = pd.read_csv(ruta + 'ENNyS2_encuesta.csv', encoding='latin1', sep=';')

#%% Filtramos x grupo etario 
patron_variables = r'^(?:C3_HAC_5_1|C3_HAC_5_12|T_C3_FCA_6_1_1|C3_EE_7_|T_C3_EE_7_2_|C3_AAPC_8_|C3_AF_4_2|C3_AF_4_3)'
df_variables = df_variables[df_variables['id'].str.contains(patron_variables, na=False, regex=True)]
df_encuesta = df_encuesta[df_encuesta['E_CUEST'].str.contains('13 a 17', na=False)]

#%%
#Filtramos columnas por texto
df_encuesta = df_encuesta.filter(
    regex=r'^(C3_AF_4_2|C3_AF_4_3|C3_HAC_5_1_6_|C_3_HAC|HAC_5_10|HAC_5_11|HAC_5_12|HAC_5_13|T_C3_FCA|FCA_|C3_EE|T_C3_EE|F_|id|region|Edadd|antropo_sex)')

#%%
#Limpiamos otras columnas que no nos interesan porque nos brindan informacion de alimentos que no nos interesan para la investigacion
columnas_a_borrar = ['T_C3_EE_7_2_2', 'T_C3_EE_7_2_3', 'T_C3_EE_7_2_7' ,'T_C3_EE_7_2_8' , 'T_C3_EE_7_2_9', 'F_FF', 'F_V', 'F_LYQ', 'F_CR', 'F_PESC']
df_encuesta = df_encuesta.drop(columns=columnas_a_borrar)

#df_encuesta.to_csv(
#    r"C:\Users\juani\OneDrive\Escritorio\encuesta_filtrada.csv",
#    index=False,
#    encoding="utf-8"
#)
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

mapeo = {'Nunca': 0,'A veces': 1,'Siempre': 2}

df_encuesta[columnas_oferta] = (df_encuesta[columnas_oferta].replace(mapeo))


consumo_escolar = df_encuesta[['id','cant_E_NR','C3_EE_7_1','T_C3_EE_7_2_1','T_C3_EE_7_2_4','T_C3_EE_7_2_5',
'T_C3_EE_7_2_6','T_C3_EE_7_2_10']].copy()

consumo_escolar = consumo_escolar.rename(columns={'C3_EE_7_1' : 'Come en la escuela','T_C3_EE_7_2_1': 'OE_bebidas_azucaradas',
'T_C3_EE_7_2_4': 'OE_copetin','T_C3_EE_7_2_5': 'OE_golosinas','T_C3_EE_7_2_6': 'OE_facturas','T_C3_EE_7_2_10': 'OE_sandwich'})
#%%df habitos alimentarios
columnas_colaciones = [
    'C3_HAC_5_1_6_O1',
    'C3_HAC_5_1_6_O2',
    'C3_HAC_5_1_6_O3',
    'C3_HAC_5_1_6_O4',
    'C3_HAC_5_1_6_O5',
    'C3_HAC_5_1_6_O6',
    'C3_HAC_5_1_6_O7',
    'C3_HAC_5_1_6_O8',
    'C3_HAC_5_1_6_O9'
]

def cantidad_colaciones_NR(fila):

    contador = 0

    for col in columnas_colaciones:

        valor = str(fila[col])

        if ('Golosinas' in valor or
            'Productos de copet' in valor or
            'Bebidas azucaradas' in valor
            or 'Pan Blanco' in valor):

            contador += 1

    return contador

habitos_alimentarios = pd.DataFrame({
    'id': df_encuesta['id'],
    'cant_colaciones_NR': df_encuesta.apply(cantidad_colaciones_NR, axis=1),
    'se siente influenciado por publicidades': df_encuesta['HAC_5_10'],
    'compra productos vistos en publicidades': df_encuesta['HAC_5_11'],
    'come viendo pantallas': df_encuesta['HAC_5_13']
})
#%% frecuencia de alimentos
mapeo_frecuencia = {'Nunca o menos de 1 vez al mes': 0,'Entre 1 y 3 veces al mes': 1,'1 vez por semana': 2,
'2 a 4 veces por semana': 3,'5 a 6 veces por semana': 4,'1 vez al d?¡a': 5,'Entre 2 y 3 veces al d?¡a': 6,'Entre 4 y 5 veces al d?¡a':7,'6 veces o m?¡s por d?¡a':8}

columnas_frecuencia = ['T_C3_FCA_6_1_11','T_C3_FCA_6_1_12','T_C3_FCA_6_1_13','T_C3_FCA_6_1_14','T_C3_FCA_6_1_16']

frecuencia_consumo = df_encuesta[['id'] + columnas_frecuencia].copy()

frecuencia_consumo[columnas_frecuencia] = (frecuencia_consumo[columnas_frecuencia].replace(mapeo_frecuencia))

frecuencia_consumo = frecuencia_consumo.rename(columns={
    'T_C3_FCA_6_1_11': 'copetin',
    'T_C3_FCA_6_1_12': 'golosinas',
    'T_C3_FCA_6_1_13': 'facturas',
    'T_C3_FCA_6_1_14': 'preelaborados',
    'T_C3_FCA_6_1_16': 'FC_bebidas_con_azucar'
})
#%% Ahora eliminamos la columnas que usamos para consumo_escolar y las eliminamos de df_encuesta
#%% Por ultimo, eliminamos las columnas que ya usamos
columnas_a_eliminar = ['C3_EE_7_1','C3_EE_7_5_O1','C3_EE_7_5_O2','C3_EE_7_5_O3','C3_EE_7_5_O4','C3_EE_7_5_O5',
'C3_EE_7_5_O6','C3_EE_7_5_O9','C3_EE_7_5_O10','C3_EE_7_5_O11','C3_EE_7_5_O12','T_C3_EE_7_2_1','T_C3_EE_7_2_4',
'T_C3_EE_7_2_5','T_C3_EE_7_2_6','T_C3_EE_7_2_10']

df_encuesta = df_encuesta.drop(columns=columnas_a_eliminar)

columnas_a_eliminar = ['C3_HAC_5_1_6_O1','C3_HAC_5_1_6_O2','C3_HAC_5_1_6_O3','C3_HAC_5_1_6_O4','C3_HAC_5_1_6_O5','C3_HAC_5_1_6_O6','C3_HAC_5_1_6_O7','C3_HAC_5_1_6_O8','C3_HAC_5_1_6_O9',
                       'HAC_5_13','HAC_5_11','HAC_5_10']

df_encuesta = df_encuesta.drop(columns=columnas_a_eliminar)

columnas_a_eliminar = ['T_C3_FCA_6_1_1','T_C3_FCA_6_1_2','T_C3_FCA_6_1_3','T_C3_FCA_6_1_4','T_C3_FCA_6_1_5','T_C3_FCA_6_1_6','T_C3_FCA_6_1_7','T_C3_FCA_6_1_8'
                       ,'T_C3_FCA_6_1_9','T_C3_FCA_6_1_10','T_C3_FCA_6_1_11','T_C3_FCA_6_1_12','T_C3_FCA_6_1_13','T_C3_FCA_6_1_14','T_C3_FCA_6_1_16','T_C3_FCA_6_1_17']
df_encuesta = df_encuesta.drop(columns=columnas_a_eliminar)




