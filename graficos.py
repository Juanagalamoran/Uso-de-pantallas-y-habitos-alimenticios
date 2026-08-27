# -*- coding: utf-8 -*-
"""
Created on Sat Aug  1 17:52:38 2026

@author: juani
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

sns.set_theme(style='whitegrid', context='notebook')  # antes 'talk' -> ahora 'notebook' (letras más chicas)

ruta = 'C:/Users/cuina/OneDrive/Escritorio/proyectoSole/'
#ruta = 'C:/Users/Juani/OneDrive/Escritorio/proyectoSole/Uso-de-pantallas-y-habitos-alimenticios/' 


encuesta = pd.read_csv(ruta + 'encuesta_filtrado.csv', encoding='latin1', sep=',')
frecuencia_consumo = pd.read_csv(ruta + 'frecuencia_consumo.csv', encoding='latin1', sep=',')
tiempo_pantallas = pd.read_csv(ruta + 'tiempo_pantallas.csv', encoding='latin1', sep=',')
habitos_alimentarios = pd.read_csv(ruta + 'habitos_alimentarios.csv', encoding='latin1', sep=',')
consumo_escolar = pd.read_csv(ruta + 'consumo_escolar.csv', encoding='latin1', sep=',')

#%% Primero vamos a hacer un histograma para ver la distribucion de "Edad" en la muestra
edades = encuesta['Edadd'].dropna()
edad_min = int(edades.min())
edad_max = int(edades.max())

#hacemos las barras
bins = np.arange(edad_min - 0.5, edad_max + 1.5, 1)

fig, ax = plt.subplots(figsize=(8, 5))

n, bins_out, patches = ax.hist(
    edades,
    bins=bins,
    color='#4C72B0',
    edgecolor='white',
    linewidth=1.2
)

#eje x
ax.set_xticks(np.arange(edad_min, edad_max + 1, 1))

#legends
ax.set_title('Distribución de la edad de los adolescentes en la muestra',
              fontsize=13, fontweight='bold', pad=15)
ax.set_xlabel('Edad (años cumplidos)', fontsize=11)
ax.set_ylabel('Cantidad de adolescentes', fontsize=11)

#Diseño 
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', linestyle='--', alpha=0.4)
ax.set_axisbelow(True)

# Etiquetas de frecuencia sobre cada barra (opcional, prolijo para informes)
for count, patch in zip(n, patches):
    if count > 0:
        ax.text(patch.get_x() + patch.get_width()/2, count + max(n)*0.01,
                f'{int(count)}', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig('distribucion_edad.png', dpi=300, bbox_inches='tight')
plt.show()
#%% grafico 2: Distribucion de horas de pantalla
variables_pantallas = ['horas_pantallas_sem', 'horas_videojuegos_sem', 'horas_totales_pantalla_sem']
titulos = ['Pantallas', 'Videojuegos', 'Total de pantallas']
datos = [tiempo_pantallas[var].dropna() for var in variables_pantallas]

valor_min = 0
valor_max = max(d.max() for d in datos)
print('valor_max:', valor_max)  # chequeo rápido de rango

ancho_bin = 5
bins = np.arange(valor_min, valor_max + ancho_bin, ancho_bin)

umbral_horas = 14

fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(8, 10), sharex=True, sharey=True)
fig.suptitle('Distribución del tiempo semanal de uso de pantallas en adolescentes',
             fontsize=14, fontweight='bold', y=0.98)

colores = ['#4C72B0', '#DD8452', '#55A868']

for i, (ax, dato, titulo, color) in enumerate(zip(axes, datos, titulos, colores)):
    ax.hist(dato, bins=bins, color=color, edgecolor='white', linewidth=1.0, zorder=2)
    ax.axvline(
        umbral_horas,
        color='red',
        linestyle='--',
        linewidth=2,
        zorder=5,
        label=f'tiempo maximo sugerido de consumo de pantallas ({umbral_horas} hs)' if i == 0 else None
    )
    ax.set_title(titulo, fontsize=11, fontweight='bold', loc='left')
    ax.set_ylabel('Cantidad de\nadolescentes', fontsize=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_axisbelow(True)
    ax.grid(axis='y', linestyle='--', alpha=0.4, zorder=0)

axes[-1].set_xlabel('Horas semanales', fontsize=11)
fig.legend(loc='upper right', bbox_to_anchor=(0.98, 0.97), fontsize=9, frameon=False)

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('distribucion_pantallas.png', dpi=300, bbox_inches='tight')
plt.show()
#%% Grafico 3: distribucion de frecuencia de consumo

# 1. Definimos la correspondencia entre los códigos de la encuesta y las etiquetas
columnas_ennys = {
    'HAC_5_12': 'Preelaborados',
    'C3_HAC_5_1_6_O1': 'Copetín',
    'HAC_5_10': 'Golosinas',
    'HAC_5_11': 'Facturas',
    'C3_HAC_5_1_6_O2': 'Bebidas\nazucaradas'
}

# 2. Copiamos las columnas existentes
cols_validas = [col for col in columnas_ennys.keys() if col in encuesta.columns]
df_temp = encuesta[cols_validas].copy()

# 3. Convertimos dinámicamente: todo lo que NO sea 'no', 'nunca' o '0' cuenta como consumo (1)
for col in cols_validas:
    # Limpiamos espacios alrededor de los textos
    s = df_temp[col].astype(str).str.strip().str.lower()
    # Si contiene 'si', números > 0 o palabras distintas de 'no'/'nunca', es 1
    df_temp[col] = np.where(s.isin(['no', 'nunca', '0', '0.0', 'nan', 'none', '']), 0, 1)

# 4. Calculamos porcentajes y ordenamos
porcentajes = (
    df_temp
    .mean()
    .multiply(100)
    .rename(index=columnas_ennys)
    .sort_values(ascending=False)
)

fig, ax = plt.subplots(figsize=(9, 6))

barras = ax.bar(
    porcentajes.index,
    porcentajes.values,
    color='#C44E52',
    edgecolor='white',
    linewidth=1.2,
    width=0.6
)

# Etiquetas de porcentaje sobre cada barra
for barra, valor in zip(barras, porcentajes.values):
    ax.text(
        barra.get_x() + barra.get_width() / 2,
        valor + 1,
        f'{valor:.1f}%'.replace('.', ','),
        ha='center', va='bottom',
        fontsize=10, fontweight='bold'
    )

ax.set_title('Consumo semanal de alimentos no recomendados en adolescentes',
              fontsize=13, fontweight='bold', pad=15)
ax.set_xlabel('Grupo de alimentos', fontsize=11)
ax.set_ylabel('Porcentaje de adolescentes (%)', fontsize=11)

max_val = np.nanmax(porcentajes.values) if len(porcentajes.dropna()) > 0 else 100
ax.set_ylim(0, min(100, max_val * 1.25))

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', linestyle='--', alpha=0.4)
ax.set_axisbelow(True)
ax.tick_params(axis='x', labelsize=10)

plt.tight_layout()
plt.savefig('consumo_alimentos_no_recomendados.png', dpi=300, bbox_inches='tight')
plt.show()
#%% Grafico 4 Histograma de adolecentes que comen o no en la escuela.
def clasificar_come_escuela(val):
    val = str(val).strip()
    if val in ['No', 'NS/NC']:
        return val
    elif val == '' or val.lower() == 'nan':
        return np.nan
    else:
        return 'Sí'  # cualquier variante corrupta de "Sí" cae acá

consumo_escolar['come_escuela'] = consumo_escolar['Come en la escuela'].apply(clasificar_come_escuela)

print(consumo_escolar['come_escuela'].value_counts(dropna=False))
consumo_escolar['come_escuela'].value_counts(dropna=False)

porcentajes_come = (
    consumo_escolar['come_escuela']
    .value_counts(normalize=True, dropna=False)
    .multiply(100)
    .rename(index={np.nan: 'Sin dato'})
)

# Orden explícito: No, Sí, NS/NC, Sin dato
orden = ['No', 'Sí', 'NS/NC', 'Sin dato']
porcentajes_come = porcentajes_come.reindex(orden)

fig, ax = plt.subplots(figsize=(7, 5))

barras = ax.bar(
    porcentajes_come.index,
    porcentajes_come.values,
    color=['#C44E52', '#55A868', '#8172B2', '#999999'],
    edgecolor='white',
    linewidth=1.2,
    width=0.5
)

for barra, valor in zip(barras, porcentajes_come.values):
    ax.text(
        barra.get_x() + barra.get_width() / 2,
        valor + 1,
        f'{valor:.1f}%'.replace('.', ','),
        ha='center', va='bottom',
        fontsize=10, fontweight='bold'
    )

ax.set_title('Adolescentes que conusmen alimentos en el establecimiento escolar',
              fontsize=13, fontweight='bold', pad=15)
ax.set_xlabel('¿Come en la escuela?', fontsize=11)
ax.set_ylabel('Porcentaje de adolescentes (%)', fontsize=11)
ax.set_ylim(0, max(porcentajes_come.values) * 1.2)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', linestyle='--', alpha=0.4)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig('come_en_escuela.png', dpi=300, bbox_inches='tight')
plt.show()
#%% grafico 5.De los adelcentes que comen en la escuela. Con que frecuencia del dan alimentos NR

consumo_escolar['come_escuela'] = consumo_escolar['come_escuela'].replace('nan', np.nan)
consumo_escolar['come_escuela'].value_counts(dropna=False)

variables_oferta = ['OE_copetin', 'OE_golosinas', 'OE_facturas', 'OE_sandwich', 'OE_bebidas_azucaradas']

nombres_legibles = {
    'OE_copetin': 'Copetín',
    'OE_golosinas': 'Golosinas',
    'OE_facturas': 'Facturas',
    'OE_sandwich': 'Sándwich',
    'OE_bebidas_azucaradas': 'Bebidas\nazucaradas'
}

etiquetas_frecuencia = {0: 'Nunca', 1: 'A veces', 2: 'Siempre'}

for col in variables_oferta:
    consumo_escolar[col] = pd.to_numeric(consumo_escolar[col], errors='coerce')

consumo_escolar_come = consumo_escolar[consumo_escolar['come_escuela'] == 'Sí'].copy()

tabla_frecuencias = pd.DataFrame({
    nombres_legibles[col]: (
        consumo_escolar_come[col]
        .value_counts(normalize=True)
        .multiply(100)
        .rename(index=etiquetas_frecuencia)
        .reindex(['Nunca', 'A veces', 'Siempre'])
    )
    for col in variables_oferta
}).T

tabla_frecuencias = tabla_frecuencias.sort_values('Nunca', ascending=True)

fig, ax = plt.subplots(figsize=(9, 6))

colores = {'Nunca': '#B0B0B0', 'A veces': '#F0A860', 'Siempre': '#C44E52'}
izquierda = np.zeros(len(tabla_frecuencias))

for categoria in ['Nunca', 'A veces', 'Siempre']:
    valores = tabla_frecuencias[categoria].values
    barras = ax.barh(
        tabla_frecuencias.index, valores, left=izquierda,
        color=colores[categoria], edgecolor='white', linewidth=1.2,
        label=categoria, height=0.6
    )
    for barra, valor in zip(barras, valores):
        if valor > 5:
            ax.text(
                barra.get_x() + barra.get_width() / 2,
                barra.get_y() + barra.get_height() / 2,
                f'{valor:.0f}%',
                ha='center', va='center', fontsize=9.5, color='white', fontweight='bold'
            )
    izquierda += valores

n_come_escuela = len(consumo_escolar_come)

ax.set_title('Frecuencia de oferta de alimentos no recomendados en la escuela',
              fontsize=13, fontweight='bold', pad=15)
ax.set_xlabel('Porcentaje de adolescentes (%)', fontsize=11)
ax.set_ylabel('Grupo de alimentos', fontsize=11)
ax.set_xlim(0, 100)

ax.legend(
    title='Frecuencia', loc='upper center', bbox_to_anchor=(0.5, -0.12),
    ncol=3, frameon=False, fontsize=10
)

ax.text(
    1.0, 1.08, f'Base: adolescentes que reciben alimentos en la escuela (n = {n_come_escuela})',
    transform=ax.transAxes, ha='right', va='bottom', fontsize=8.5, style='italic', color='gray'
)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)

plt.tight_layout()
plt.savefig('oferta_alimentos_escuela.png', dpi=300, bbox_inches='tight')
plt.show()
#%% grafico 6. porcetaje de cant de alimentos nr que los adolecentes compran en el bufet de la escuela
porcentajes = (
    consumo_escolar['cant_E_NR']
    .value_counts(normalize=True)
    .multiply(100)
    .sort_index()
)

fig, ax = plt.subplots(figsize=(8, 6))

barras = ax.bar(
    porcentajes.index,
    porcentajes.values,
    color='#8172B2',
    edgecolor='white',
    linewidth=1.2,
    width=0.6
)

for barra, valor in zip(barras, porcentajes.values):
    ax.text(
        barra.get_x() + barra.get_width() / 2,
        valor + 1,
        f'{valor:.1f}%'.replace('.', ','),
        ha='center', va='bottom',
        fontsize=10, fontweight='bold'
    )

ax.set_title('Distribución del número de grupos de alimentos no recomendados comprados en el kiosco o buffet escolar',
              fontsize=13, fontweight='bold', pad=15)
ax.set_xlabel('Cantidad de tipos de alimentos no recomendados', fontsize=11)
ax.set_ylabel('Porcentaje de adolescentes (%)', fontsize=11)
ax.set_xticks(porcentajes.index)
ax.set_ylim(0, max(porcentajes.values) * 1.15)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', linestyle='--', alpha=0.4)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig('cant_E_NR.png', dpi=300, bbox_inches='tight')
plt.show()
#%%
cols_frecuencia = ['copetin', 'golosinas', 'facturas', 'preelaborados', 'FC_bebidas_con_azucar']

frecuencia_consumo['cant_NR'] = (
    frecuencia_consumo[cols_frecuencia] != 'Nunca o menos de 1 vez al mes'
).sum(axis=1)
datos_grafico7 = pd.merge(
    tiempo_pantallas[['id', 'horas_totales_pantalla_sem']],
    frecuencia_consumo[['id', 'cant_NR']],
    on='id',
    how='inner'
)

print(f'Adolescentes con datos completos para este cruce: {len(datos_grafico7)}')
datos_grafico7['cant_NR'].value_counts(dropna=False).sort_index()
#%%grafico 7
categorias = sorted(datos_grafico7['cant_NR'].dropna().unique())
datos_por_categoria = [
    datos_grafico7.loc[datos_grafico7['cant_NR'] == cat, 'horas_totales_pantalla_sem'].dropna()
    for cat in categorias
]

fig, ax = plt.subplots(figsize=(9, 6))

bp = ax.boxplot(
    datos_por_categoria,
    labels=categorias,
    patch_artist=True,
    widths=0.5,
    medianprops=dict(color='black', linewidth=1.8),
    boxprops=dict(facecolor='#4C72B0', edgecolor='black', linewidth=1),
    whiskerprops=dict(color='black', linewidth=1),
    capprops=dict(color='black', linewidth=1),
    flierprops=dict(
        marker='o', markerfacecolor='#C44E52', markersize=5,
        markeredgecolor='black', alpha=0.6
    )
)

ax.set_title('Tiempo de uso de pantallas según cantidad de alimentos no\nrecomendados consumidos semanalmente',
              fontsize=13, fontweight='bold', pad=15)
ax.set_xlabel('Cantidad de alimentos no recomendados consumidos', fontsize=11)
ax.set_ylabel('Horas totales de pantalla por semana', fontsize=11)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', linestyle='--', alpha=0.4)
ax.set_axisbelow(True)


plt.tight_layout()
plt.savefig('boxplot_pantallas_vs_consumo_NR.png', dpi=300, bbox_inches='tight')
plt.show()
#%%grafico 8
orden_categorias = ['Nunca', 'Algunas veces', 'Frecuentemente', 'Siempre']

# Excluimos NS/NC del cálculo (es solo 1 caso) y mantenemos el orden natural de la escala
porcentajes_influencia = (
    habitos_alimentarios['se siente influenciado por publicidades']
    .value_counts(normalize=True)
    .multiply(100)
    .reindex(orden_categorias)
)

fig, ax = plt.subplots(figsize=(8, 6))

barras = ax.bar(
    porcentajes_influencia.index,
    porcentajes_influencia.values,
    color='#DD8452',
    edgecolor='white',
    linewidth=1.2,
    width=0.6
)

for barra, valor in zip(barras, porcentajes_influencia.values):
    ax.text(
        barra.get_x() + barra.get_width() / 2,
        valor + 1,
        f'{valor:.1f}%'.replace('.', ','),
        ha='center', va='bottom',
        fontsize=10, fontweight='bold'
    )

ax.set_title('Percepción de influencia de la publicidad sobre el consumo de alimentos',
              fontsize=13, fontweight='bold', pad=15)
ax.set_xlabel('¿Con qué frecuencia se siente influenciado por publicidades?', fontsize=11)
ax.set_ylabel('Porcentaje de adolescentes (%)', fontsize=11)
ax.set_ylim(0, max(porcentajes_influencia.values) * 1.15)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', linestyle='--', alpha=0.4)
ax.set_axisbelow(True)

ax.text(
    0.99, -0.16, 'Nota: variable de autopercepción, no de comportamiento observado',
    transform=ax.transAxes, ha='right', va='top', fontsize=8, style='italic', color='gray'
)

plt.tight_layout()
plt.savefig('influencia_publicidad.png', dpi=300, bbox_inches='tight')
plt.show()
#%% grafico 9.
datos_grafico11 = (
    habitos_alimentarios[['id', 'come viendo pantallas']]
    .merge(tiempo_pantallas[['id', 'horas_totales_pantalla_sem']], on='id', how='inner')
    .merge(frecuencia_consumo[['id', 'cant_NR']], on='id', how='inner')
)

categorias_cvp = ['No', 'Si']
datos_por_grupo = [
    datos_grafico11.loc[datos_grafico11['come viendo pantallas'] == cat, 'horas_totales_pantalla_sem'].dropna()
    for cat in categorias_cvp
]

fig, ax = plt.subplots(figsize=(7, 6))

ax.boxplot(
    datos_por_grupo,
    labels=['No come\nviendo pantallas', 'Sí come\nviendo pantallas'],
    patch_artist=True,
    widths=0.4,
    medianprops=dict(color='black', linewidth=1.8),
    boxprops=dict(facecolor='#4C72B0', edgecolor='black', linewidth=1),
    whiskerprops=dict(color='black', linewidth=1),
    capprops=dict(color='black', linewidth=1),
    flierprops=dict(marker='o', markerfacecolor='#C44E52', markersize=5, markeredgecolor='black', alpha=0.6)
)

for i, cat in enumerate(categorias_cvp):
    n_cat = len(datos_por_grupo[i])
    ax.text(i + 1, ax.get_ylim()[1] * 0.02, f'n={n_cat}', ha='center', va='bottom', fontsize=8.5, color='gray')

ax.set_title('Tiempo de uso de pantallas según hábito de comer\nmirando pantallas', fontsize=13, fontweight='bold', pad=15)
ax.set_ylabel('Horas totales de pantalla por semana', fontsize=11)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', linestyle='--', alpha=0.4)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig('boxplot_come_viendo_pantallas.png', dpi=300, bbox_inches='tight')
plt.show()
#%%grafico 10
promedio_nr = datos_grafico11.groupby('come viendo pantallas')['cant_NR'].mean().reindex(['No', 'Si'])

fig, ax = plt.subplots(figsize=(7, 6))

barras = ax.bar(
    ['No come\nviendo pantallas', 'Sí come\nviendo pantallas'],
    promedio_nr.values,
    color=['#55A868', '#C44E52'],
    edgecolor='white', linewidth=1.2, width=0.5
)

for barra, valor in zip(barras, promedio_nr.values):
    ax.text(barra.get_x() + barra.get_width()/2, valor + 0.05, f'{valor:.2f}'.replace('.', ','),
            ha='center', va='bottom', fontsize=11, fontweight='bold')

ax.set_title('Cantidad promedio de alimentos no recomendados consumidos\nsemanalmente, según hábito de comer viendo pantallas',
              fontsize=12.5, fontweight='bold', pad=15)
ax.set_ylabel('Promedio de grupos de NR consumidos (0 a 5)', fontsize=11)
ax.set_ylim(0, 5)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', linestyle='--', alpha=0.4)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig('promedio_NR_come_viendo_pantallas.png', dpi=300, bbox_inches='tight')
plt.show()

#%% Grafico 8: cant_NR (consumo general) según tercil de horas de pantalla

cols_frecuencia = ['copetin', 'golosinas', 'facturas', 'preelaborados', 'FC_bebidas_con_azucar']
frecuencia_consumo['cant_NR'] = (
    frecuencia_consumo[cols_frecuencia] != 'Nunca o menos de 1 vez al mes'
).sum(axis=1)

datos_g8 = pd.merge(
    tiempo_pantallas[['id', 'tercil_pantalla']],
    frecuencia_consumo[['id', 'cant_NR']],
    on='id',
    how='inner'
).dropna(subset=['tercil_pantalla'])

orden_terciles = ['Bajo consumo', 'Consumo medio', 'Alto consumo']
datos_g8['tercil_pantalla'] = pd.Categorical(
    datos_g8['tercil_pantalla'],
    categories=orden_terciles,
    ordered=True
)

resumen_g8 = datos_g8.groupby('tercil_pantalla', observed=True)['cant_NR'].agg(['mean', 'sem'])
resumen_g8 = resumen_g8.reindex(orden_terciles)

paleta_terciles = sns.color_palette('Blues', n_colors=3)  # degradé sobrio, discreto

fig, ax = plt.subplots(figsize=(6.5, 4.5))
barras = ax.bar(
    resumen_g8.index.astype(str),
    resumen_g8['mean'],
    yerr=resumen_g8['sem'],
    capsize=5,
    color=paleta_terciles,
    edgecolor='white',
    linewidth=1,
    width=0.55
)

for barra, valor in zip(barras, resumen_g8['mean']):
    ax.text(
        barra.get_x() + barra.get_width() / 2,
        valor + 0.05,
        f'{valor:.2f}'.replace('.', ','),
        ha='center', va='bottom', fontsize=9, fontweight='bold'
    )

ax.set_title('Consumo de alimentos no recomendados según nivel de uso de pantallas',
              fontsize=11, fontweight='bold', pad=12)
ax.set_xlabel('Tercil de horas de pantalla (diarias)', fontsize=9)
ax.set_ylabel('Promedio de grupos de alimentos\nno recomendados consumidos (0-5)', fontsize=9)
ax.tick_params(axis='both', labelsize=8.5)
sns.despine(ax=ax)

n_total = len(datos_g8)
ax.text(1.0, 1.05, f'n = {n_total}', transform=ax.transAxes,
        ha='right', va='bottom', fontsize=7.5, style='italic', color='gray')

plt.tight_layout()
plt.savefig('cant_NR_por_tercil.png', dpi=300, bbox_inches='tight')
plt.show()

print(datos_g8.groupby('tercil_pantalla', observed=True)['cant_NR'].describe())

#%% Grafico 9: cant_colaciones_NR según tercil de horas de pantalla

datos_g9 = pd.merge(
    tiempo_pantallas[['id', 'tercil_pantalla']],
    habitos_alimentarios[['id', 'cant_colaciones_NR']],
    on='id',
    how='inner'
).dropna(subset=['tercil_pantalla'])

orden_terciles = ['Bajo consumo', 'Consumo medio', 'Alto consumo']
datos_g9['tercil_pantalla'] = pd.Categorical(
    datos_g9['tercil_pantalla'],
    categories=orden_terciles,
    ordered=True
)

resumen_g9 = datos_g9.groupby('tercil_pantalla', observed=True)['cant_colaciones_NR'].agg(['mean', 'sem'])
resumen_g9 = resumen_g9.reindex(orden_terciles)

paleta_terciles = sns.color_palette('Blues', n_colors=3)

fig, ax = plt.subplots(figsize=(6.5, 4.5))
barras = ax.bar(
    resumen_g9.index.astype(str),
    resumen_g9['mean'],
    yerr=resumen_g9['sem'],
    capsize=5,
    color=paleta_terciles,
    edgecolor='white',
    linewidth=1,
    width=0.55
)

for barra, valor in zip(barras, resumen_g9['mean']):
    ax.text(
        barra.get_x() + barra.get_width() / 2,
        valor + 0.05,
        f'{valor:.2f}'.replace('.', ','),
        ha='center', va='bottom', fontsize=9, fontweight='bold'
    )

ax.set_title('Consumo de colaciones no recomendadas según nivel de uso de pantallas',
              fontsize=11, fontweight='bold', pad=12)
ax.set_xlabel('Tercil de horas de pantalla (diarias)', fontsize=9)
ax.set_ylabel('Promedio de colaciones\nno recomendadas', fontsize=9)
ax.tick_params(axis='both', labelsize=8.5)
sns.despine(ax=ax)

n_total = len(datos_g9)
ax.text(1.0, 1.05, f'n = {n_total}', transform=ax.transAxes,
        ha='right', va='bottom', fontsize=7.5, style='italic', color='gray')

plt.tight_layout()
plt.savefig('cant_colaciones_NR_por_tercil.png', dpi=300, bbox_inches='tight')
plt.show()

#%% Grafico 10: cant_E_NR (compras en el kiosco escolar) según tercil de horas de pantalla
# Solo entre quienes efectivamente comen en la escuela

datos_g10 = pd.merge(
    tiempo_pantallas[['id', 'tercil_pantalla']],
    consumo_escolar[consumo_escolar['come_escuela'] == 'Sí'][['id', 'cant_E_NR']],
    on='id',
    how='inner'
).dropna(subset=['tercil_pantalla'])

orden_terciles = ['Bajo consumo', 'Consumo medio', 'Alto consumo']
datos_g10['tercil_pantalla'] = pd.Categorical(
    datos_g10['tercil_pantalla'],
    categories=orden_terciles,
    ordered=True
)

resumen_g10 = datos_g10.groupby('tercil_pantalla', observed=True)['cant_E_NR'].agg(['mean', 'sem'])
resumen_g10 = resumen_g10.reindex(orden_terciles)

paleta_terciles = sns.color_palette('Blues', n_colors=3)

fig, ax = plt.subplots(figsize=(6.5, 4.5))
barras = ax.bar(
    resumen_g10.index.astype(str),
    resumen_g10['mean'],
    yerr=resumen_g10['sem'],
    capsize=5,
    color=paleta_terciles,
    edgecolor='white',
    linewidth=1,
    width=0.55
)

for barra, valor in zip(barras, resumen_g10['mean']):
    ax.text(
        barra.get_x() + barra.get_width() / 2,
        valor + 0.05,
        f'{valor:.2f}'.replace('.', ','),
        ha='center', va='bottom', fontsize=9, fontweight='bold'
    )

ax.set_title('Compra de alimentos no recomendados en el kiosco escolar\nsegún nivel de uso de pantallas',
              fontsize=11, fontweight='bold', pad=12)
ax.set_xlabel('Tercil de horas de pantalla (diarias)', fontsize=9)
ax.set_ylabel('Promedio de tipos de alimentos\nno recomendados comprados', fontsize=9)
ax.tick_params(axis='both', labelsize=8.5)
sns.despine(ax=ax)

n_total = len(datos_g10)
ax.text(1.0, 1.05, f'Base: come en la escuela, n = {n_total}', transform=ax.transAxes,
        ha='right', va='bottom', fontsize=7.5, style='italic', color='gray')

plt.tight_layout()
plt.savefig('cant_E_NR_por_tercil.png', dpi=300, bbox_inches='tight')
plt.show()