# -*- coding: utf-8 -*-
"""
Created on Thu May 28 13:56:25 2026

@author: cuina
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

ruta = 'C:/Users/cuina/OneDrive/Escritorio/proyectoSole/'
#ruta = 'C:/Users/Juani/OneDrive/Escritorio/proyectoSole/Uso-de-pantallas-y-habitos-alimenticios/' 

df_variables = pd.read_csv(ruta + 'ennys2_variables.csv', encoding='latin1', sep=';')
df_encuesta = pd.read_csv(ruta + 'ENNyS2_encuesta.csv', encoding='latin1', sep=';')
#%%
# Filtramos x grupo etario 
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

#%%corregimos la edad
df_encuesta["Edadd"] = pd.to_numeric(
    df_encuesta["Edadd"],
    errors="coerce"
)

df_encuesta["Edadd"] = np.floor(df_encuesta["Edadd"] / 365).astype("Int64")

#%% Filtramos encuestados según completitud

# Umbral mínimo de respuestas completas
umbral = 0.80

# Cantidad de encuestados antes del filtro
n_inicial = len(df_encuesta)

# Copia para calcular la completitud
df_completitud = df_encuesta.copy()

# Reemplazamos valores que representan falta de respuesta
df_completitud = df_completitud.replace(["", " ", "NS/NC"], np.nan)

# Columnas correspondientes a la pregunta C3_EE_7_5 (checkbox: qué se ofrece en el kiosco)
columnas_ee_75 = [f"C3_EE_7_5_O{i}" for i in range(1, 13)]

# La pregunta cuenta como respondida si se completó al menos una opción
df_completitud["C3_EE_7_5"] = (
    df_completitud[columnas_ee_75]
    .notna()
    .any(axis=1)
)

# Eliminamos las 12 columnas originales para que la pregunta pese una sola vez
df_completitud = df_completitud.drop(columns=columnas_ee_75)

# Variables que NO deben penalizar la completitud:
# - Checkboxes de opción múltiple: un campo vacío significa "no marcado", no "sin responder"
# - Variables con patrón de salto: solo se preguntan si se respondió Sí a un filtro previo;
#   un campo vacío significa "no aplica", no "sin responder"
vars_checkbox = [f"C3_HAC_5_1_6_O{i}" for i in range(1, 10)]

vars_skip_pattern = [
    'T_C3_EE_7_2_1', 'T_C3_EE_7_2_4', 'T_C3_EE_7_2_5', 'T_C3_EE_7_2_6', 'T_C3_EE_7_2_10',
    'C3_EE_7_3', 'C3_EE_7_4', 'HAC_5_11'
]

vars_excluidas_completitud = vars_checkbox + vars_skip_pattern

# Calculamos la completitud por encuestado, excluyendo checkbox/skip pattern del cálculo
df_completitud_calculo = df_completitud.drop(columns=vars_excluidas_completitud, errors='ignore')
completitud_filas = df_completitud_calculo.notna().mean(axis=1)

# Conservamos solo quienes respondieron al menos el umbral de preguntas (ya corregido)
df_encuesta = df_encuesta[completitud_filas >= umbral].copy()

print(f"Encuestados iniciales: {n_inicial}")
print(f"Encuestados luego del filtro: {len(df_encuesta)}")
print(f"Eliminados: {n_inicial - len(df_encuesta)}")
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
mapeo_frecuencia = {
    'Nunca o menos de 1 vez al mes': 'Nunca o menos de 1 vez al mes',
    'Entre 1 y 3 veces al mes': 'Entre 1 y 3 veces al mes',
    '1 vez por semana': '1 vez por semana',
    '2 a 4 veces por semana': '2 a 4 veces por semana',
    '5 a 6 veces por semana': '5 a 6 veces por semana',
    '1 vez al d?¡a': '1 vez al dia',
    'Entre 2 y 3 veces al d?¡a': 'Entre 2 y 3 veces al dia',
    'Entre 4 y 5 veces al d?¡a': 'Entre 4 y 5 veces al dia',
    '6 veces o m?¡s por d?¡a': '6 veces o mas por dia'
}

columnas_frecuencia = ['T_C3_FCA_6_1_11','T_C3_FCA_6_1_12','T_C3_FCA_6_1_13','T_C3_FCA_6_1_14','T_C3_FCA_6_1_16']

# --- Creación correcta de frecuencia_consumo ---
frecuencia_consumo = pd.DataFrame()

frecuencia_consumo['id'] = df_encuesta['id']

# Mapeamos 'Si' / '1' / frecuencias mayores a 0 como 1 (consumidor), y el resto como 0
def a_binario(val):
    if pd.isna(val):
        return 0
    val_str = str(val).strip().lower()
    return 1 if val_str in ['si', 'sí', '1', '1.0', 'true'] or (val_str.isdigit() and int(val_str) > 0 and val_str != '0') else 0

# Asignación de variables según correspondencia ENNyS2
frecuencia_consumo['copetin'] = df_encuesta['C3_HAC_5_1_6_O1'].apply(a_binario)
frecuencia_consumo['FC_bebidas_con_azucar'] = df_encuesta['C3_HAC_5_1_6_O2'].apply(a_binario)
frecuencia_consumo['golosinas'] = df_encuesta['HAC_5_10'].apply(a_binario)
frecuencia_consumo['facturas'] = df_encuesta['HAC_5_11'].apply(a_binario)
frecuencia_consumo['preelaborados'] = df_encuesta['HAC_5_12'].apply(a_binario)

# Guardamos el CSV ya limpio y numérico (para que a tu amiga le lea exacto con ;)
frecuencia_consumo.to_csv(ruta + 'frecuencia_consumo.csv', index=False, sep=';')
#frecuencia_consumo = df_encuesta[['id'] + columnas_frecuencia].copy()

#frecuencia_consumo[columnas_frecuencia] = (frecuencia_consumo[columnas_frecuencia].replace(mapeo_frecuencia))

#frecuencia_consumo = frecuencia_consumo.rename(columns={
#    'T_C3_FCA_6_1_11': 'copetin',
#    'T_C3_FCA_6_1_12': 'golosinas',
#    'T_C3_FCA_6_1_13': 'facturas',
#    'T_C3_FCA_6_1_14': 'preelaborados',
#    'T_C3_FCA_6_1_16': 'FC_bebidas_con_azucar'
#})
#%% Frecuencia de consumo: dataframe base (categorías completas, sin colapsar)

mapeo_frecuencia = {
    'Nunca o menos de 1 vez al mes': 'Nunca o menos de 1 vez al mes',
    'Entre 1 y 3 veces al mes': 'Entre 1 y 3 veces al mes',
    '1 vez por semana': '1 vez por semana',
    '2 a 4 veces por semana': '2 a 4 veces por semana',
    '5 a 6 veces por semana': '5 a 6 veces por semana',
    '1 vez al d?¡a': '1 vez al dia',
    'Entre 2 y 3 veces al d?¡a': 'Entre 2 y 3 veces al dia',
    'Entre 4 y 5 veces al d?¡a': 'Entre 4 y 5 veces al dia',
    '6 veces o m?¡s por d?¡a': '6 veces o mas por dia'
}

columnas_frecuencia = ['T_C3_FCA_6_1_11', 'T_C3_FCA_6_1_12', 'T_C3_FCA_6_1_13', 'T_C3_FCA_6_1_14', 'T_C3_FCA_6_1_16']

frecuencia_consumo = df_encuesta[['id'] + columnas_frecuencia].copy()
frecuencia_consumo[columnas_frecuencia] = frecuencia_consumo[columnas_frecuencia].replace(mapeo_frecuencia)

frecuencia_consumo = frecuencia_consumo.rename(columns={
    'T_C3_FCA_6_1_11': 'copetin',
    'T_C3_FCA_6_1_12': 'golosinas',
    'T_C3_FCA_6_1_13': 'facturas',
    'T_C3_FCA_6_1_14': 'preelaborados',
    'T_C3_FCA_6_1_16': 'FC_bebidas_con_azucar'
})

columnas_alimentos = ['copetin', 'golosinas', 'facturas', 'preelaborados', 'FC_bebidas_con_azucar']

#%% Definimos los tres umbrales de "alta frecuencia" a comparar

# El orden de las categorías, de menor a mayor frecuencia, nos sirve para armar cada umbral
orden_frecuencias = [
    'Nunca o menos de 1 vez al mes',
    'Entre 1 y 3 veces al mes',
    '1 vez por semana',
    '2 a 4 veces por semana',
    '5 a 6 veces por semana',
    '1 vez al dia',
    'Entre 2 y 3 veces al dia',
    'Entre 4 y 5 veces al dia',
    '6 veces o mas por dia'
]

# Cada umbral define desde qué categoría (inclusive) se considera "alta frecuencia"
umbrales = {
    'umbral1': '2 a 4 veces por semana',
    'umbral2': '5 a 6 veces por semana',
    'umbral3': '1 vez al dia'
}

def construir_df_umbral(nombre_umbral, categoria_de_corte):
    """
    Construye un dataframe de frecuencia de consumo marcando como
    'alta frecuencia' (1) a quienes consumen desde categoria_de_corte
    en adelante, según el orden de orden_frecuencias.
    """
    indice_corte = orden_frecuencias.index(categoria_de_corte)
    categorias_alta_frecuencia = orden_frecuencias[indice_corte:]

    df_umbral = frecuencia_consumo.copy()

    for col in columnas_alimentos:
        df_umbral[col + '_altafrecuencia'] = df_umbral[col].isin(categorias_alta_frecuencia).astype(int)

    columnas_altafrecuencia = [c + '_altafrecuencia' for c in columnas_alimentos]
    df_umbral['consume_NR'] = df_umbral[columnas_altafrecuencia].max(axis=1)
    df_umbral['cant_NR'] = df_umbral[columnas_altafrecuencia].sum(axis=1, skipna=False)

    # Documentamos el umbral usado como atributo del propio dataframe,
    # para que quede explícito de dónde salió sin tener que ir a buscar el código
    df_umbral.attrs['umbral_alta_frecuencia'] = categoria_de_corte
    df_umbral.attrs['categorias_incluidas'] = categorias_alta_frecuencia

    return df_umbral

frecuencia_consumo_umbral1 = construir_df_umbral('umbral1', umbrales['umbral1'])
frecuencia_consumo_umbral2 = construir_df_umbral('umbral2', umbrales['umbral2'])
frecuencia_consumo_umbral3 = construir_df_umbral('umbral3', umbrales['umbral3'])
#%%


# Resultados obtenidos (ya calculados en el chequeo anterior)
etiquetas_umbral = [
    'Umbral 1\n(2 a 4 veces\npor semana o más)',
    'Umbral 2\n(5 a 6 veces\npor semana o más)',
    'Umbral 3\n(1 vez al día\no más)'
]

porcentaje_alta_frecuencia = [91.0, 69.0, 56.6]
porcentaje_baja_frecuencia = [9.0, 31.0, 43.4]

x = np.arange(len(etiquetas_umbral))
ancho = 0.5

fig, ax = plt.subplots(figsize=(9, 6))

barras_alta = ax.bar(
    x, porcentaje_alta_frecuencia, ancho,
    label='Alta frecuencia', color='#C44E52', edgecolor='white', linewidth=1.2
)
barras_baja = ax.bar(
    x, porcentaje_baja_frecuencia, ancho, bottom=porcentaje_alta_frecuencia,
    label='Baja frecuencia', color='#B0B0B0', edgecolor='white', linewidth=1.2
)

# Etiquetas dentro de cada segmento
for i in range(len(x)):
    ax.text(x[i], porcentaje_alta_frecuencia[i] / 2,
            f'{porcentaje_alta_frecuencia[i]:.1f}%'.replace('.', ','),
            ha='center', va='center', fontsize=11, fontweight='bold', color='white')
    ax.text(x[i], porcentaje_alta_frecuencia[i] + porcentaje_baja_frecuencia[i] / 2,
            f'{porcentaje_baja_frecuencia[i]:.1f}%'.replace('.', ','),
            ha='center', va='center', fontsize=11, fontweight='bold', color='white')

ax.set_title('Comparación de umbrales para definir "alta frecuencia"\nde consumo de alimentos no recomendados',
              fontsize=13, fontweight='bold', pad=15)
ax.set_ylabel('Porcentaje de adolescentes (%)', fontsize=11)
ax.set_xticks(x)
ax.set_xticklabels(etiquetas_umbral, fontsize=10)
ax.set_ylim(0, 100)

ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False, fontsize=10)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.set_yticks([])

plt.tight_layout()
plt.savefig('comparacion_umbrales_alta_frecuencia.png', dpi=300, bbox_inches='tight')
plt.show()
#%% Chequeo rápido: cuánta gente cae en "alta frecuencia" (consume_NR) según cada umbral

for nombre, df in [
    ('umbral1 (2 a 4 veces/sem o más)', frecuencia_consumo_umbral1),
    ('umbral2 (5 a 6 veces/sem o más)', frecuencia_consumo_umbral2),
    ('umbral3 (1 vez al día o más)', frecuencia_consumo_umbral3),
]:
    print(f"{nombre}: umbral usado = '{df.attrs['umbral_alta_frecuencia']}'")
    print(df['consume_NR'].value_counts(normalize=True).multiply(100).round(1))
    print()
#%%Pantallas
pantallas = df_encuesta[['id', 'Edadd', 'C3_AF_4_2', 'C3_AF_4_3']].copy()

pantallas = pantallas.rename(columns={
    'Edadd': 'edad',
    'C3_AF_4_2': 'horas_pantallas_sem',
    'C3_AF_4_3': 'horas_videojuegos_sem'
})

pantallas["horas_pantallas_sem"] = pd.to_numeric(
    pantallas["horas_pantallas_sem"],
    errors="coerce"
)

pantallas["horas_videojuegos_sem"] = pd.to_numeric(
    pantallas["horas_videojuegos_sem"],
    errors="coerce"
)

pantallas.loc[pantallas["horas_pantallas_sem"] == 999, "horas_pantallas_sem"] = np.nan
pantallas.loc[pantallas["horas_videojuegos_sem"] == 999, "horas_videojuegos_sem"] = np.nan

# Convertir de minutos/semana a horas/semana
pantallas["horas_pantallas_sem"] = (
    pantallas["horas_pantallas_sem"] / 60
).round(2)

pantallas["horas_videojuegos_sem"] = (
    pantallas["horas_videojuegos_sem"] / 60
).round(2)

pantallas["horas_totales_pantalla_sem"] = (
    pantallas["horas_pantallas_sem"] +
    pantallas["horas_videojuegos_sem"]
).round(2)

#%% Categorización por terciles de horas de pantalla
# pd.qcut divide automáticamente la variable en 3 grupos con igual cantidad
# de observaciones (33% cada uno), calculando los puntos de corte (XX y ZZZ)

pantallas["horas_totales_pantalla_dia"] = (
    pantallas["horas_totales_pantalla_sem"] / 7
).round(2)

pantallas["tercil_pantalla"], cortes = pd.qcut(
    pantallas["horas_totales_pantalla_dia"],
    q=3,
    labels=["Bajo consumo", "Consumo medio", "Alto consumo"],
    retbins=True
)

print("Puntos de corte de los terciles (horas diarias):")
print(f"  Grupo 1 - Bajo consumo:   < {cortes[1]:.2f} hs/día")
print(f"  Grupo 2 - Consumo medio: {cortes[1]:.2f} a {cortes[2]:.2f} hs/día")
print(f"  Grupo 3 - Alto consumo:  > {cortes[2]:.2f} hs/día")
print()
print(pantallas["tercil_pantalla"].value_counts(dropna=False).sort_index())
#%%guardamos los csv
consumo_escolar.to_csv(
    ruta + "consumo_escolar.csv",
    index=False,
    encoding="utf-8"
)
habitos_alimentarios.to_csv(
    ruta + "habitos_alimentarios.csv",
    index=False,
    encoding="utf-8"
)
frecuencia_consumo.to_csv(
    ruta + "frecuencia_consumo.csv",
    index=False,
    encoding="utf-8"
)
pantallas.to_csv(
    ruta + "tiempo_pantallas.csv",
    index=False,
    encoding="utf-8"
)
df_encuesta.to_csv(ruta + "encuesta_filtrado.csv", index=False, encoding="utf-8")

frecuencia_consumo_umbral1.to_csv(
    ruta + "frecuencia_consumo_umbral1_2a4vecesSem.csv",
    index=False,
    encoding="utf-8"
)
frecuencia_consumo_umbral2.to_csv(
    ruta + "frecuencia_consumo_umbral2_5a6vecesSem.csv",
    index=False,
    encoding="utf-8"
)
frecuencia_consumo_umbral3.to_csv(
    ruta + "frecuencia_consumo_umbral3_1vezDia.csv",
    index=False,
    encoding="utf-8"
)
#%% Por ultimo, eliminamos las columnas que ya usamos
""""
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

"""


