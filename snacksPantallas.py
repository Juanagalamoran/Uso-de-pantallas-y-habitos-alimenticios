# -*- coding: utf-8 -*-
"""
Created on Thu May 28 13:56:25 2026

@author: cuina
"""

import pandas as pd
import numpy as np

ruta = 'C:/Users/Juani/OneDrive/Escritorio/proyectoSole/Uso-de-pantallas-y-habitos-alimenticios/'

#CARGA DE DATOS 

df_variables = pd.read_csv(ruta + 'ennys2_variables.csv', encoding='latin1', sep=';')

df_encuesta = pd.read_csv(ruta + 'ENNyS2_encuesta.csv', encoding='latin1', sep=';')

df_nutrientes = pd.read_csv(ruta + 'Base_Nutrientes.csv', encoding='latin1', sep=',')

df_alimentos = pd.read_csv(ruta + 'Base_Alimentos_Bebidas_Suplementos.csv', encoding='latin1', sep=',')

#%%

#LIMPIEZA DE BASE ENCUESTA

#buscamos el patron de las columnas de interes
patron = r'^(?:C3_HAC_5_1|C3_HAC_5_12|T_C3_FCA_6_1_1|C3_EE_7_|T_C3_EE_7_2_|C3_AAPC_8_)'

df_variables = df_variables[df_variables['id'].str.contains(patron, na=False, regex=True)]

#filtramos encuestados entre 13 y 17 años en el frame de encuesta
df_encuesta = df_encuesta[df_encuesta['E_CUEST'].str.contains('13 a 17', na=False)]

#filtramos columnas de interes
df_encuesta= df_encuesta.filter(regex=r'^(C_3_HAC|HAC_|T_C3_FCA|FCA_|C3_EE|T_C3_EE|C3_AAPC|F_|id|MHDR_KEY)')

#eliminamos las col cuyas rtas son menos del 1%
umbral = 24 #rtas contestadas/total de encuestados (de 13 a 17)
def borrar_col_vacias(df_encuesta):

    df_temporal = df_encuesta.copy()
    
    df_temporal = df_temporal.replace(r'^\s*$', np.nan, regex=True)
    
    respuestas_por_columna = df_temporal.count()
    
    columnas_a_borrar = respuestas_por_columna[respuestas_por_columna < umbral].index

    print("Columnas eliminadas por tener pocas respuestas")
    if len(columnas_a_borrar) > 0:
        for col in columnas_a_borrar:
            #muestra el nombre de la columna y cuántas respuestas reales tenía
            print(f"- {col} (Respuestas reales: {respuestas_por_columna[col]})")
    else:
        print("No se eliminó ninguna columna.")
    

    df_resultado = df_encuesta.drop(columns=columnas_a_borrar)
    
    print(f"Se eliminaron {len(columnas_a_borrar)} columnas por tener menos de {umbral} respuestas reales.")
    return df_resultado


df_encuesta_filtr = borrar_col_vacias(df_encuesta)

#%%

# las que empiezan con C3_HAC, T_C3_FCA, C3_EE, T_ C3_FCA , T_C3_EE, C3_AAPC
"""
habitos alimentarios C3_HAC_5_1_
snacks T_C3_FCA_6_1
entorno escolar C3_EE_7_5 Y C3_EE_7_2
peso y talla C3_AAPC_8
"""
#%% LIMPIEZA DE BASE NUTRIENTES
claves_adolescentes = set(df_encuesta['MHDR_KEY'])

df_nutrientes = df_nutrientes[df_nutrientes['clave'].isin(claves_adolescentes)]

df_nutrientes = df_nutrientes[['informe_id','miembro_id','clave','nro_R24H','tot_energia_kcal','tot_proteinas','tot_lipidos',
        'tot_CHO_totales','tot_azucar_total','tot_azucar_agregado','tot_fibra_total','tot_sodio']]

#notamos que hay 538 claves que aparecen 2 veces en df_nutrientes. Nuestra interepretacion 
#es que, como hay 538 filas en las cuales la columna "nro_R24H" (recordatorios en 24hs) tiene valor 2,
#esas 538 claves repetidas corresponen a un mismo adolecente al cual se le realizo el estudio 2 veces.
#vamos a promediar dichos resultados para quedarnos con solo 1 fila x cada adolecente. 
print("Filas nutrientes:", len(df_nutrientes))
print("Claves únicas:", df_nutrientes['clave'].nunique())
print(df_nutrientes.groupby('clave')['nro_R24H'].count().value_counts())
print("Hay",len(df_nutrientes) - df_nutrientes['clave'].nunique(), "encuestados con 2 recordatorios en 24HS")

df_nutrientes_filtr = (df_nutrientes.groupby('clave', as_index=False).agg({'informe_id': 'first','miembro_id': 'first','tot_energia_kcal': 'mean',
        'tot_proteinas': 'mean','tot_lipidos': 'mean','tot_CHO_totales': 'mean','tot_azucar_total': 'mean',
        'tot_azucar_agregado': 'mean','tot_fibra_total': 'mean','tot_sodio': 'mean'}))

#Ademas, hay 18 adolecentes que no tienen valores de nutrientes ingresados. Puede deberse a que
#no lo completaron.
claves_encuesta = set(df_encuesta['MHDR_KEY'])
claves_nutrientes = set(df_nutrientes_filtr['clave'])

faltantes_nutr = claves_encuesta - claves_nutrientes

print("Hay",len(faltantes_nutr),"faltantes")
#%% LIMPIEZA DE BASE ALIMENTOS

claves_adolescentes = set(df_encuesta['MHDR_KEY'])

df_alimentos = df_alimentos[
    df_alimentos['clave'].isin(claves_adolescentes)]

columnas_fijas = ['informe_id', 'miembro_id', 'clave','nro_R24H']

columnas_prefijos = [c for c in df_alimentos.columns if c.startswith(('B', 'D', 'E', 'G', 'O'))]

df_alimentos = df_alimentos[columnas_fijas + columnas_prefijos]

#Notamos que sucede lo mismo que con el df nutrientes. Hay 538 encuestados que completaron 2
#veces esta parte del cuestionario. Nuevamente vamos a promediar estos resultados para tener 
#1 fila por adolecente.
print("Filas alimentos:", len(df_alimentos))
print("Claves únicas:", df_alimentos['clave'].nunique())
print(df_nutrientes.groupby('clave')['nro_R24H'].count().value_counts())
print("Hay",len(df_alimentos) - df_alimentos['clave'].nunique(), "encuestados con 2 recordatorios en 24HS")


#columnas que queremos conservar sin promediar
columnas_id = ['clave', 'informe_id', 'miembro_id']

# detectar columnas numéricas
columnas_numericas = (df_alimentos.drop(columns=columnas_id).select_dtypes(include='number').columns)

df_alimentos_filtr = (df_alimentos.groupby('clave', as_index=False).agg({'informe_id': 'first','miembro_id': 'first',
        **{col: 'mean' for col in columnas_numericas}}))

#Ademas, hay 18 adolecentes que no tienen valores de alimentos ingresados. Puede deberse a que
#no lo completaron.
claves_alimentos = set(df_alimentos_filtr['clave'])
faltantes_al = claves_encuesta - claves_alimentos
print("Hay",len(faltantes_al),"faltantes")







