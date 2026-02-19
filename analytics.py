"""
Big Data & Análisis Laboral en Argentina
=================
Este programa en Python analiza la distribución del empleo en Argentina, ofreciendo perspectivas a nivel nacional y provincial. 
Destaca las actividades económicas más relevantes y utiliza gráficos interactivos para visualizar la distribución del empleo por sectores. 
Además, incorpora un análisis temporal para comprender la evolución del empleo a lo largo de los años.

Author: Banegas Luis
Fecha: 2023-11-30
"""

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

# Defino el directorio con los datasets
dataset_folder = 'datasets/'

# Cargar el archivo CSV con los puestos de trabajo
archivo_puestos = dataset_folder + 'puestos_priv.csv'
df_puestos = pd.read_csv(archivo_puestos)

# Cargar el archivo CSV con los códigos y nombres de actividad económica
archivo_codigos = dataset_folder + 'clae_agg.csv'
df_codigos = pd.read_csv(archivo_codigos)

# Fusionar los DataFrames utilizando el código de actividad económica como clave
df_fusionado = pd.merge(df_puestos, df_codigos, left_on='clae2', right_on='clae2', how='left')

# Ajustar la fecha al formato '2007-01-01'
df_fusionado['fecha'] = pd.to_datetime(df_fusionado['fecha'], format='%Y-%m-%d')

# Agregar una columna de año
df_fusionado['año'] = df_fusionado['fecha'].dt.year

# Filtrar datos solo para el año 2023
df_fusionado_2022 = df_fusionado[df_fusionado['fecha'].dt.year == 2022]

# Agrupar los datos por provincia y nombre de actividad económica, sumando la cantidad de puestos
grupo = df_fusionado_2022.groupby(['zona_prov', 'clae2_desc'])['puestos'].sum().unstack()

# Convertir valores negativos a cero
grupo[grupo < 0] = 0

# Crear un gráfico de barras apiladas para cada provincia en una sola figura
fig, ax = plt.subplots(figsize=(8, 5))  # Tamaño inicial del gráfico
fig.subplots_adjust(left=0.270)  # Ajuste del parámetro left
provincias = grupo.index.tolist()
indice = 0

# Seleccionar las 5 actividades más representativas a nivel nacional
top_actividades_nacional = grupo.sum().nlargest(5)

# Definir puestos_por_provincia aquí
puestos_por_provincia = grupo.sum()

def update_plot(value):
    global indice
    if value == 'Sig' and indice < len(provincias) - 1:
        indice += 1
    elif value == 'Ant' and indice > 0:
        indice -= 1

    ax.clear()
    datos = grupo.loc[provincias[indice]]
    # Seleccionar las 10 actividades más representativas para la provincia actual
    top_actividades = datos.nlargest(10)

    # Calcular porcentaje con respecto al total de puestos de trabajo en la provincia
    porcentaje = (top_actividades / datos.sum()) * 100

    # Graficar barras apiladas con los ejes intercambiados
    porcentaje.plot(kind='barh', stacked=True, ax=ax)

    # Ajustar el diseño para mostrar los nombres en dos líneas
    yticks_labels = [text.get_text() for text in ax.get_yticklabels()]
    ax.set_yticklabels([text[:44] + '\n' + text[44:] if len(text) > 44 else text for text in yticks_labels])
    
    ax.set_xlabel('Porcentaje de Puestos de Trabajo en la provincia')
    ax.set_ylabel('Actividad Económica')
    ax.set_title(f'Top 10 empleos por actividad en {provincias[indice]} (Porcentaje)')
    plt.draw()

# Botones de página
axnext = plt.axes([0.96, 0.015, 0.03, 0.075])
axprev = plt.axes([0.01, 0.015, 0.03, 0.075])
bnext = Button(axnext, 'Sig')
bnext.on_clicked(lambda event: update_plot('Sig'))
bprev = Button(axprev, 'Ant')
bprev.on_clicked(lambda event: update_plot('Ant'))

# Mostrar el primer gráfico al inicio
update_plot('Sig')

# Botones para cambiar a la página de torta
axnext_pie = plt.axes([0.01, 0.92, 0.1, 0.075])
bnext_pie = Button(axnext_pie, 'Ver distribución nacional')

# Nuevo botón para ver el gráfico de líneas
axnext_lineas = plt.axes([0.12, 0.92, 0.1, 0.075])
bnext_lineas = Button(axnext_lineas, 'Ver gráfico de líneas')

# Función para cambiar a la página de torta
def change_page_pie(value):
    global puestos_por_provincia
    if value == 'Ver distribución nacional':
        fig_pie, ax_pie = plt.subplots(figsize=(8, 6))

        # Seleccionar las categorías top y agrupar el resto en "Resto"
        top_actividades = grupo.sum().nlargest(7)
        otros_actividades = grupo.sum().sum() - top_actividades.sum()

        # Construir manualmente la serie que representa las categorías top y "Resto"
        datos_pie = pd.Series(dict(top_actividades))
        datos_pie['Resto'] = otros_actividades if otros_actividades.sum() > 0 else 0

        # Graficar el gráfico de torta
        ax_pie.pie(datos_pie, labels=datos_pie.index, autopct='%1.1f%%', startangle=70)
        ax_pie.set_title('Composición de puestos de trabajo a nivel nacional')
        plt.show()

# Función para cambiar a la página de líneas
def change_page_lineas(value):
    global puestos_por_provincia
    if value == 'Ver gráfico de líneas':
        # Crear un gráfico de líneas para el total de puestos de trabajo por año
        fig_lineas, ax_lineas = plt.subplots(figsize=(8, 6))
        
        # Filtrar datos antes del mes 6 del año 2023
        df_lineas = df_fusionado[df_fusionado['fecha'] < '2023-01-01']
        
        # Agrupar por año y sumar la cantidad de puestos
        empleos_por_año = df_lineas.groupby('año')['puestos'].sum()

        # Graficar el gráfico de líneas
        ax_lineas.plot(empleos_por_año.index, empleos_por_año.values, marker='o')
        ax_lineas.set_xlabel('Año')
        ax_lineas.set_ylabel('Total de Puestos de Trabajo')
        ax_lineas.set_title('Total de Puestos de Trabajo por Año')
        plt.show()

# Configurar eventos de botones para cambiar a la página de torta
bnext_pie.on_clicked(lambda event: change_page_pie('Ver distribución nacional'))

# Configurar eventos de botones para cambiar a la página de líneas
bnext_lineas.on_clicked(lambda event: change_page_lineas('Ver gráfico de líneas'))

plt.show()
