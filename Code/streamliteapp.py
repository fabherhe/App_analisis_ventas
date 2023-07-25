import pandas as pd
import plotly.express as px
import streamlit as st

#Leer archivos CSV con pandas y obtener info basica
@st.cache_data
def load_data(ruta_archivo):
    df = pd.read_csv(ruta_archivo, delimiter=';', encoding='unicode_escape')
    return df

ruta_archivo1 = 'Consumo.csv'
ruta_archivo2 = 'Empresa.csv'
ruta_archivo3 = 'Persona.csv'

df_consumo = load_data(ruta_archivo1)
df_empresa = load_data(ruta_archivo2)
df_persona = load_data(ruta_archivo3)

#Archivo 1
@st.cache_data
def transform_data(df):
    # Reemplazar la coma por punto para poder transformar la columna a dato decimal
    df['Valor'] = df['Valor'].str.replace(',', '.').astype(float)

    # Convertir periodo a fecha 
    df['Periodo'] = pd.to_datetime(df['Periodo'], format= '%Y%m')

    return df

df_consumo = transform_data(df_consumo)

# Parece que si hay outliers asi que investigaremos mas a fondo
# Obteniendo los valores más altos y más bajos
valores_maximos = df_consumo.nlargest(12, 'Valor')  # Obtener los 12 valores máximos
valores_minimos = df_consumo.nsmallest(1, 'Valor')  # Obtener el valor minimo

# Título de la aplicación
st.title('Análisis de ventas Colsubsidio')

# Agregar la línea de texto antes del gráfico
st.write('A continuación se muestra un gráfico de dispersión que presenta los valores más altos y más bajos en el dataset de consumo.')

# Create the scatter plot with Plotly
fig1 = px.scatter(df_consumo, x='Periodo', y='Valor', title='Ventas por mes')

# Add the points of the highest and lowest values
fig1.add_scatter(x=valores_maximos['Periodo'], y=valores_maximos['Valor'], mode='markers', 
                 marker=dict(color='red', size=10, line=dict(color='red', width=2)), name='Valores más altos')
fig1.add_scatter(x=valores_minimos['Periodo'], y=valores_minimos['Valor'], mode='markers', 
                 marker=dict(color='green', size=10, line=dict(color='green', width=2)), name='Valores más bajos')

# Show the plot
st.plotly_chart(fig1)

@st.cache_data
def filter_data(df):
    # Filter the DataFrame
    df_filtrado = df[~df['Valor'].isin(valores_maximos['Valor'])]
    return df_filtrado

df_filtrado = filter_data(df_consumo)

# Agregar la línea de texto antes del gráfico
st.write('Vimos algunos valores muy por fuera del rango en el que se encuentran los demas registros asi que decidimos eliminar los registros con valores mayores a 200 millones. Ahora procedemos a visualizar si los cambios fueron realizados con exito:')

# Create the scatter plot with Plotly
fig2 = px.scatter(df_filtrado, x='Periodo', y='Valor', title='Ventas por mes (sin los 12 valores que estabas por encima de 200mm)')

# Show the plot
st.plotly_chart(fig2)

#Archivo 2 y 3
@st.cache_data
def transform_data(df, date_column=None, coordinate_columns=None):
    if date_column:
        df[date_column] = pd.to_datetime(df[date_column])
    if coordinate_columns:
        for column in coordinate_columns:
            df[column] = df[column].str.replace(',', '.').astype(float)
    return df

# Transformar los DataFrames
df_empresa = transform_data(df_empresa, coordinate_columns=['cx_empresa', 'cy_empresa'])
df_persona = transform_data(df_persona, date_column='FechaNacimiento', coordinate_columns=['cx_persona', 'cy_persona'])

#       ¿Existen temporadas de mayor venta de productos?
# Agrupamos ventas por temporada
ventas_por_periodo_filtrado = df_filtrado.groupby('Periodo')['Valor'].sum()

# Extraemos el periodo con mas ventas
max_periodo_ventas = ventas_por_periodo_filtrado.idxmax().strftime("%m-%Y")
st.write(f"Si eliminamos los outliers (ventas de mas de 200 millones) el periodo con más ventas fue {max_periodo_ventas}.")

# Crear figura con Plotly Express
fig3 = px.line(x=ventas_por_periodo_filtrado.index, y=ventas_por_periodo_filtrado.values, labels={'x':'Periodo', 'y':'Ventas'}, title='Ventas por Periodo')

# Agregar marcadores al gráfico
fig3.update_traces(mode='lines+markers', marker=dict(size=6, color='red'))

# Mostrar el gráfico
st.plotly_chart(fig3)

import plotly.graph_objects as go

def long_scale_formatter(num):
    if num >= 1e9:
        return f'{num / 1e9:.2f} mil millones'
    elif num >= 1e6:
        return f'{num / 1e6:.2f} millones'
    elif num >= 1e3:
        return f'{num / 1e3:.2f} mil'
    else:
        return str(num)

#       ¿Cual es la participación en el consumo de personas afiliadas y no afiliadas?
#Total consumption without outliers
total_consumo_sin_outliers = df_filtrado['Valor'].sum()

#Filtering the consumption records to select only those that correspond to affiliates
afiliados_sin_outliers = df_filtrado[df_filtrado['NumIdPersona'].isin(df_persona['NumIdPersona'])]

#Summing the consumption value of the affiliates
suma_afiliados_so = afiliados_sin_outliers['Valor'].sum()

#Filtering the consumption records to select only those that do NOT correspond to the affiliates
no_afiliados_so = df_filtrado[~df_filtrado['NumIdPersona'].isin(df_persona['NumIdPersona'])]

#Summing the consumption value of the NON affiliates
suma_no_afiliados_so = no_afiliados_so['Valor'].sum()

#Calculate participations
participacion_afiliados_so = round((suma_afiliados_so / total_consumo_sin_outliers)*100,2)
participacion_no_afiliados_so = round((suma_no_afiliados_so / total_consumo_sin_outliers)*100,2)

#Visualize the results
labels = ['Afiliados', 'No afiliados']
values = [participacion_afiliados_so, participacion_no_afiliados_so]

# Configuración de colores
colors = ['#1f77b4', '#ff7f0e']

# Create pie chart
fig4 = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])

# Set title
fig4.update_layout(title_text="Participación en el consumo")

# Streamlit code
st.markdown(f"El consumo total fue de: {long_scale_formatter(total_consumo_sin_outliers)}")
st.markdown(f"La suma del valor de consumo de los afiliados fue: {long_scale_formatter(suma_afiliados_so)}")
st.markdown(f"La suma del valor de consumo de los NO afiliados fue: {long_scale_formatter(suma_no_afiliados_so)}")
st.markdown(f"La participación en el consumo de afiliados fue: {participacion_afiliados_so} %")
st.markdown(f"La participación en el consumo de NO afiliados fue: {participacion_no_afiliados_so} %")

fig4 = go.Figure(data=[go.Pie(labels=labels, values=values, textinfo='percent')])

fig4.update_traces(hoverinfo='label+percent', marker=dict(colors=colors, line=dict(color='#000000', width=2)))

fig4.update_layout(title_text='Participación en el consumo', legend_title="Categorías")

st.plotly_chart(fig4)

#       ¿Cual es el consumo por unidad de negocio?
# Unidades de negocio
suma_consumo_por_ues_so = df_filtrado.groupby('UES')['Valor'].sum().sort_values(ascending=False)

st.write("En la siguiente grafica podemos observar que Crédito es la unidad especializada de negocio con mayores ventas, con un monto de 40.4 mil millones.")

# Crear un gráfico de barras con Plotly
fig5 = go.Figure(data=[
    go.Bar(
        x=suma_consumo_por_ues_so.index, 
        y=suma_consumo_por_ues_so.values,
        text=[long_scale_formatter(val) for val in suma_consumo_por_ues_so.values],
        textposition='outside',
        textfont=dict(color='white')
    )
])

fig5.update_layout(
    title='Consumo total por Unidad Espezialiada de Servicio',
    xaxis=dict(title='UES'),
    yaxis=dict(title='Consumo total'),
)

# Visualizar el gráfico en Streamlit
st.plotly_chart(fig5)

# Unidades de mayor uso en cada categoria 
# Merge tabla consumo con tabla personas para poder agrupar por categoria
merged_df_so = df_filtrado.merge(df_persona, on='NumIdPersona', how='left')

# Agrupar por categoria y contamos las apariciones de UES 
grouped_ues_df_so = merged_df_so.groupby('Categoria')['UES'].value_counts()
grouped_ues_df_so = grouped_ues_df_so.reset_index(name='Apariciones')

import plotly.express as px

# Colores de Plotly
colors = px.colors.qualitative.Plotly

st.write("La unidad especializada de negocio que mas apariciones tiene en el conjunto de datos es Mercadeo Social en las 3 categorias objeto de analisis.")

# Crear el gráfico de barras con Plotly Express
fig6 = px.bar(
    grouped_ues_df_so, 
    x='UES', 
    y='Apariciones', 
    color='Categoria',
    color_discrete_sequence=colors,
    title='Apariciones de Unidad Espezialiada de Servicio por Categoría',
    labels={'UES': 'UES', 'Apariciones': 'Apariciones'},
    barmode='group'  # Este modo permite que las barras de diferentes categorías se coloquen una al lado de la otra
)

# Visualizar el gráfico en Streamlit
st.plotly_chart(fig6)

st.write("Ahora veremos que el producto con mas apariciones por categoria es Supermercados.")

import plotly.figure_factory as ff

pivot_table = merged_df_so.pivot_table(
    index='Categoria', 
    columns='Producto', 
    aggfunc='size'  # Esto cuenta las apariciones
)

fig7 = ff.create_annotated_heatmap(
    z=pivot_table.values, 
    x=list(pivot_table.columns), 
    y=list(pivot_table.index), 
    colorscale='YlGnBu',
    showscale=True,
    annotation_text=pivot_table.values
)

fig7.update_layout(
    title='Apariciones de producto por Categoría',
    yaxis=dict(title='Categoría'),
)

fig7.update_xaxes(
    title_text='Producto',
    side='bottom'
)

# Visualizar el gráfico en Streamlit
st.plotly_chart(fig7)

# Número de principales clientes a considerar
top_clients = 100

# Identificar clientes afiliados con mayor frecuencia de uso 
frecuencia_uso_afiliados_so = afiliados_sin_outliers.groupby('NumIdPersona')['NumTransacciones'].sum().nlargest(top_clients)

# Identificar mayor valor neto de venta de esos clientes afiliados
afiliados_top = afiliados_sin_outliers.loc[afiliados_sin_outliers['NumIdPersona'].isin(frecuencia_uso_afiliados_so.index)]
valor_neto_venta_afiliados_so = afiliados_top.groupby('NumIdPersona')['Valor'].max()

# Identificar clientes NO afiliados con mayor frecuencia de uso 
frecuencia_uso_no_afiliados_so = no_afiliados_so.groupby('NumIdPersona')['NumTransacciones'].sum().nlargest(top_clients)

# Identificar mayor valor neto de venta de esos clientes NO afiliados
no_afiliados_top = no_afiliados_so.loc[no_afiliados_so['NumIdPersona'].isin(frecuencia_uso_no_afiliados_so.index)]
valor_neto_venta_no_afiliados_so = no_afiliados_top.groupby('NumIdPersona')['Valor'].max()

st.write("En el siguiente grafico de dispersion podemos apreciar los clientes que mas compras realizarón en el eje x, y en el eje y vemos el valor de su mayor compra.")

# Crear el gráfico de dispersión para afiliados y no afiliados
fig8 = go.Figure()

fig8.add_trace(go.Scatter(
    x=frecuencia_uso_afiliados_so, 
    y=valor_neto_venta_afiliados_so, 
    mode='markers', 
    marker_color='blue', 
    name='Afiliados'
))

fig8.add_trace(go.Scatter(
    x=frecuencia_uso_no_afiliados_so, 
    y=valor_neto_venta_no_afiliados_so, 
    mode='markers', 
    marker_color='red', 
    name='No Afiliados'
))

# Configurar el gráfico
fig8.update_layout(
    title='Top 100 Clientes con Mayor Frecuencia de Uso y su Valor Neto de Venta',
    xaxis=dict(title='Frecuencia de Uso'),
    yaxis=dict(title='Valor Neto de Venta'),
)

# Visualizar el gráfico en Streamlit
st.plotly_chart(fig8)


#       ¿Cómo ha sido el porcentaje histórico de penetración en la población afiliada de los servicios Colsubsidio?
# Calcular el número total de clientes atendidos en cada período de tiempo
clientes_totales_so = df_filtrado.groupby('Periodo')['NumIdPersona'].nunique()

# Calcular el número de clientes afiliados en cada período de tiempo
clientes_afiliados_so = afiliados_sin_outliers.groupby('Periodo')['NumIdPersona'].nunique()

# Calcular el porcentaje de penetración en cada período de tiempo
penetracion_so = (clientes_afiliados_so / clientes_totales_so) 

st.write("Este grafico ilustra la proporcion de afiliados vs los clientes atendidos por mes. Vemos que en febrero el 90 por ciento de los compradores estaba afiliado")

# Visualizar el porcentaje histórico de penetración
fig9 = go.Figure()

fig9.add_trace(go.Scatter(
    x=penetracion_so.index, 
    y=penetracion_so.values, 
    mode='lines+markers',
    hovertemplate='%{y:.2%}<extra></extra>',  # Formato de porcentaje con 2 decimales para las hover labels
))

fig9.update_layout(
    title='Porcentaje histórico de penetración en la población afiliada',
    xaxis=dict(title='Período'),
    yaxis=dict(
        title='Porcentaje de penetración',
        tickformat=".2%",  # Formato de porcentaje con 2 decimales
    ),
)

# Visualizar el gráfico en Streamlit
st.plotly_chart(fig9)

#       ¿Cuáles son los productos más consumidos en cada segmento poblacional?
# Agrupar los registros de consumo por segmento poblacional y producto, y calcular la suma de los valores de consumo
productos_por_segmento_so = merged_df_so.groupby(['Segmento_poblacional', 'Producto'])['Valor'].sum()

# Encontrar los productos más consumidos en cada segmento poblacional
productos_mas_consumidos_so = productos_por_segmento_so.groupby('Segmento_poblacional').idxmax().apply(lambda x: x[1])

# Definir los colores para cada producto 
colores = {'Supermercados': 'blue', 'No Libranza': 'green'}

# Crear un trazo para cada producto
traces = []
for producto, color in colores.items():
    # Filtrar los datos para el producto
    datos_producto = productos_mas_consumidos_so[productos_mas_consumidos_so == producto]
    
    # Crear un trazo para el producto
    traces.append(go.Bar(
        x=datos_producto.index, 
        y=[productos_por_segmento_so.loc[(segmento, producto)] for segmento in datos_producto.index],
        name=producto,
        marker_color=color
    ))

st.write("Los productos de la empresa mas consumidos por segmento son:")
st.write("Segmento alto: Supermercados")
st.write("Segmento basico: Supermercados")
st.write("Segmento medio: Supermercados")
st.write("El unico segmento con un producto mas consumido diferente es Joven, con No Libranza.")

# Crear el gráfico de barras con Plotly
fig10 = go.Figure(data=traces)

fig10.update_layout(
    title='Productos más consumidos por segmento poblacional',
    xaxis=dict(title='Segmento poblacional'),
    yaxis=dict(title='Valor de consumo'),
    barmode='stack'
)

# Visualizar el gráfico en Streamlit
st.plotly_chart(fig10)

#       ¿Cuáles son las mejores empresas en cuanto a consumo individual de sus empleados?
# juntamos la tabla merge entre consumo y persona, con la tabla empresa 
merged_df2_so = merged_df_so.merge(df_empresa, on='id_empresa', how='left')

# Sumar y agrupar por NumIdPersona y id_empresa para obtener el consumo individual de los empleados por empresa
consumo_por_empleado_so = merged_df_so.groupby(['NumIdPersona', 'id_empresa'])['Valor'].sum()

# Obtener los 10 empleados con mayor consumo
top_10_empleados_so = consumo_por_empleado_so.nlargest(10)

# Crear una columna de etiquetas para el eje x
etiquetas = [f'{num}-{emp}' for num, emp in top_10_empleados_so.index]

st.write("Finalmente podemos ver el id del empleado que mas ha consumido, junto con el id de la empresa a la que pertenece.")

# Crear el gráfico de barras con Plotly
fig11 = go.Figure(data=[
    go.Bar(x=etiquetas, y=top_10_empleados_so.values)
])

fig11.update_layout(
    title='Distribución de Valores',
    xaxis=dict(
        title='NumIdPersona - Id_empresa',
        tickmode='array',
        tickvals=list(range(len(etiquetas))),
        ticktext=etiquetas,
        tickangle=-45,  # Girar las etiquetas del eje x
    ),
    yaxis=dict(title='Valor'),
)

# Visualizar el gráfico en Streamlit
st.plotly_chart(fig11)

feedback = st.radio(
    "¿Le ha gustado?",
    ('👍', '👎')
)

if feedback == '👍':
    st.write("¡Gracias por su feedback positivo!")
elif feedback == '👎':
    st.write("Lo siento, trataré de mejorar.")

comentario = st.text_input("Algún comentario?")

if comentario:
    st.write(f"Gracias por su comentario: {comentario}")




