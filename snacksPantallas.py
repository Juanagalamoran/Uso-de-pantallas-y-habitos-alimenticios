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
df_nutrientes = pd.read_csv(ruta + 'Base_Nutrientes.csv', encoding='latin1', sep=',')
df_alimentos = pd.read_csv(ruta + 'Base_Alimentos_Bebidas_Suplementos.csv', encoding='latin1', sep=',')

# ==========================================
# 2. LIMPIEZA DE BASE ENCUESTA
# ==========================================

# Filtrados iniciales de la encuesta
patron_variables = r'^(?:C3_HAC_5_1|C3_HAC_5_12|T_C3_FCA_6_1_1|C3_EE_7_|T_C3_EE_7_2_|C3_AAPC_8_)'
df_variables = df_variables[df_variables['id'].str.contains(patron_variables, na=False, regex=True)]
df_encuesta = df_encuesta[df_encuesta['E_CUEST'].str.contains('13 a 17', na=False)]

# Filtrar columnas por texto
df_encuesta = df_encuesta.filter(regex=r'^(C_3_HAC|HAC_|T_C3_FCA|FCA_|C3_EE|T_C3_EE|C3_AAPC|F_|id|MHDR_KEY)')

# Borrar columnas vacías con pasos simples
df_encuesta = df_encuesta.replace(r'^\s*$', np.nan, regex=True)
conteo_respuestas = df_encuesta.count()
columnas_a_borrar = conteo_respuestas[conteo_respuestas < 24].index
df_encuesta = df_encuesta.drop(columns=columnas_a_borrar)

print(f"Se eliminaron {len(columnas_a_borrar)} columnas por pocas respuestas.")

# Guardamos las claves de los adolescentes
claves_adolescentes = set(df_encuesta['MHDR_KEY'])


# ==========================================
# 3. FUNCIÓN DE LIMPIEZA BÁSICA Y REUTILIZABLE
# ==========================================

def limpiar_y_promediar_base(df, nombre_base):
    # 1. Filtrar para quedarnos solo con los adolescentes de la encuesta
    df_filtrado = df[df['clave'].isin(claves_adolescentes)].copy()
    
    # 2. Mostrar estadísticas básicas en la terminal
    filas_totales = len(df_filtrado)
    claves_unicas = df_filtrado['clave'].nunique()
    print(f"\n--- Reporte de {nombre_base} ---")
    print(f"Filas iniciales: {filas_totales}")
    print(f"Claves únicas: {claves_unicas}")
    print(f"Adolescentes con 2 recordatorios: {filas_totales - claves_unicas}")
    
    # 3. Separar las columnas de identificación del resto de los datos numéricos
    # Dejamos 'clave' afuera para usarla en el groupby
    columnas_id = ['informe_id', 'miembro_id'] 
    
    # Conseguir los primeros registros de los IDs (para no perderlos)
    df_ids = df_filtrado.groupby('clave')[columnas_id].first().reset_index()
    
    # Conseguir el promedio de todas las columnas numéricas de la base
    df_promedios = df_filtrado.groupby('clave').mean(numeric_only=True).reset_index()
    
    # 4. Juntar los IDs y los Promedios en una sola tabla limpia usando 'clave'
    df_final = pd.merge(df_ids, df_promedios, on='clave')
    
    # 5. Calcular cuántos adolescentes faltan en esta base comparado con la encuesta
    faltantes = len(claves_adolescentes - set(df_final['clave']))
    print(f"Faltantes en esta base: {faltantes}")
    
    return df_final


# ==========================================
# 4. PROCESAR NUTRIENTES Y ALIMENTOS
# ==========================================

# Primero recortamos los nutrientes a las columnas que te interesan antes de mandarlo a la función
columnas_nutr_interes = ['informe_id','miembro_id','clave','nro_R24H','tot_energia_kcal','tot_proteinas',
                         'tot_lipidos','tot_CHO_totales','tot_azucar_total','tot_azucar_agregado','tot_fibra_total','tot_sodio']
df_nutrientes = df_nutrientes[columnas_nutr_interes]
df_nutrientes = limpiar_y_promediar_base(df_nutrientes, "Nutrientes")

# Para alimentos, filtramos por columnas primero usando tu regex, y luego lo mandamos a la función
df_alimentos = df_alimentos.filter(regex=r'^(D|O|B|R|informe_id|miembro_id|clave|nro_R24H)')
df_alimentos = limpiar_y_promediar_base(df_alimentos, "Alimentos")