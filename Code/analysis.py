import pandas as pd

ruta_archivo1 = 'Consumo.csv'
ruta_archivo2 = 'Empresa.csv'
ruta_archivo3 = 'Persona.csv'

#Leer archivos CSV con pandas y obtener info basica
df_consumo = pd.read_csv(ruta_archivo1, delimiter=';', encoding='unicode_escape')
print(df_consumo.info())

df_empresa = pd.read_csv(ruta_archivo2, delimiter=';', encoding='unicode_escape')
print(df_empresa.info())

df_persona = pd.read_csv(ruta_archivo3, delimiter=';', encoding='unicode_escape')
print(df_persona.info())

#Archivo 1
#Reemplazamos la coma por punto para poder transformar la columna a dato decimal
df_consumo['Valor'] = df_consumo['Valor'].str.replace(',', '.').astype(float)

#Convertir periodo a fecha 
df_consumo['Periodo'] = pd.to_datetime(df_consumo['Periodo'], format= '%Y%m')

#Analisis columna de valores de compra buscando potenciales outliers
df_consumo['Valor'].describe()

# Parece que si hay outliers asi que investigaremos mas a fondo
# Obteniendo los valores más altos y más bajos
valores_maximos = df_consumo.nlargest(12, 'Valor')  # Obtener los 12 valores máximos
valores_minimos = df_consumo.nsmallest(1, 'Valor')  # Obtener el valor minimo

import matplotlib.pyplot as plt

# Crear figura 1
fig1 = plt.figure()

# Crear el gráfico de dispersión
plt.scatter(df_consumo['Periodo'], df_consumo['Valor'], label='Valores')
plt.scatter(valores_maximos['Periodo'], valores_maximos['Valor'], color='red', label='Valores más altos')
plt.scatter(valores_minimos['Periodo'], valores_minimos['Valor'], color='green', label='Valores más bajos')

# Configurar el gráfico
plt.xlabel('Periodo')
plt.ylabel('Valor')
plt.title('Valores más altos y más bajos')
plt.legend()

# Guardar las figuras como imágenes
fig1.savefig('fig1.png')

# Mostrar el gráfico
plt.show()

# Tenemos outliers, o ventas muy grandes para las que pediriamos aprobacion antes de eliminar.

# Para efectos del ejercicio vamos a excluir los valores por encima de 200 millones
df_filtrado = df_consumo[~df_consumo['Valor'].isin(valores_maximos['Valor'])]

# Guardar el DataFrame modificado en un archivo CSV
df_filtrado.to_csv('/home/fh/exercises/PruebaTecnicoDatos/Code/df_filtrado.csv', index=False)

# Crear figura 2
fig2 = plt.figure()

# Crear el gráfico de dispersión
plt.scatter(df_filtrado['Periodo'], df_filtrado['Valor'])

# Configurar el gráfico
plt.xlabel('Periodo')
plt.ylabel('Valor')
plt.title('Columna Valor (sin los 12 más altos)')

# Guardar las figuras como imágenes
fig2.savefig('fig2.png')

# Mostrar el gráfico
plt.show()

#Archivo 2
#Transformar coordenadas de longitud y latitud
df_empresa['cx_empresa'] = df_empresa['cx_empresa'].str.replace(',', '.').astype(float)
df_empresa['cy_empresa'] = df_empresa['cy_empresa'].str.replace(',', '.').astype(float)

# Guardar el DataFrame modificado en un archivo CSV
df_empresa.to_csv('/home/fh/exercises/PruebaTecnicoDatos/Code/df_empresa.csv', index=False)

#Archivo 3
#Convertir periodo a fecha 
df_persona['FechaNacimiento'] = pd.to_datetime(df_persona['FechaNacimiento'])

#Transformar coordenadas de longitud y latitud
df_persona['cx_persona'] = df_persona['cx_persona'].str.replace(',', '.').astype(float)
df_persona['cy_persona'] = df_persona['cy_persona'].str.replace(',', '.').astype(float)

# Guardar el DataFrame modificado en un archivo CSV
df_persona.to_csv('/home/fh/exercises/PruebaTecnicoDatos/Code/df_persona.csv', index=False)

#       ¿Existen temporadas de mayor venta de productos?
#Agrupamos ventas por temporada
ventas_por_periodo_filtrado = df_filtrado.groupby('Periodo')['Valor'].sum()

#Extraemos el periodo con mas ventas
max_periodo_ventas = ventas_por_periodo_filtrado.idxmax().strftime("%m-%Y")
print(f"Si quitamos los outliers(ventas de mas de 200mm) el periodo con más ventas fue {max_periodo_ventas}")

# Crear figura 3
fig3 = plt.figure()

#Visualizamos los resultados para un facil analisis
ventas_por_periodo_filtrado.plot(kind='line')
plt.xlabel('Periodo')
plt.ylabel('Ventas')
plt.title('Ventas por Periodo')

# Guardar las figuras como imágenes
fig3.savefig('fig3.png', bbox_inches='tight')

# Mostrar el gráfico
plt.show()

#       ¿Cual es la participación en el consumo de personas afiliadas y no afiliadas?
#Total consumo sin outliers 
total_consumo_sin_outliers = df_filtrado['Valor'].sum()
total_consumo_sin_outliers_formateado = "{:,.0f}".format(total_consumo_sin_outliers)
print("Consumo total fue de:", total_consumo_sin_outliers_formateado)

#Filtrando los registros de consumo para seleccionar únicamente aquellos que corresponden a los afiliados
afiliados_sin_outliers = df_filtrado[df_filtrado['NumIdPersona'].isin(df_persona['NumIdPersona'])]

#Sumando el valor del consumo de los afiliados 
suma_afiliados_so = afiliados_sin_outliers['Valor'].sum()
suma_consumo_afiliados_formateado_so = "{:,.0f}".format(suma_afiliados_so)
print("Suma del valor de consumo de los afiliados:", suma_consumo_afiliados_formateado_so)

#Filtrando los registros de consumo para seleccionar únicamente aquellos que NO corresponden a los afiliados
no_afiliados_so = df_filtrado[~df_filtrado['NumIdPersona'].isin(df_persona['NumIdPersona'])]

#Sumando el valor del consumo de los NO afiliados 
suma_no_afiliados_so = no_afiliados_so['Valor'].sum()
suma_consumo_no_afiliados_formateado_so = "{:,.0f}".format(suma_no_afiliados_so)
print("Suma del valor de consumo de los NO afiliados:", suma_consumo_no_afiliados_formateado_so)

#Calculamos participaciones
participacion_afiliados_so = round((suma_afiliados_so / total_consumo_sin_outliers)*100,2)
participacion_no_afiliados_so = round((suma_no_afiliados_so / total_consumo_sin_outliers)*100,2)

print("Participación en el consumo de afiliados:", participacion_afiliados_so, "%")
print("Participación en el consumo de NO afiliados:", participacion_no_afiliados_so, "%")

# Visualizamos los resultados 

# Crear figura 4
fig4 = plt.figure()

# Etiquetas para la leyenda
etiquetas_so = ['Afiliados', 'No afiliados']

# Valores para la gráfica
valores_so = [participacion_afiliados_so, participacion_no_afiliados_so]

# Configuración de colores
colores = ['#1f77b4', '#ff7f0e']

# Crear la gráfica de pastel
plt.pie(valores_so, labels=etiquetas_so, colors=colores, autopct='%1.1f%%', startangle=90)

# Configuración adicional
plt.axis('equal')  # Para que el gráfico sea un círculo
plt.title('Participación en el consumo')
plt.legend()

# Guardar las figuras como imágenes
fig4.savefig('fig4.png')

# Mostrar la gráfica
plt.show()

#       ¿Cual es el consumo por unidad de negocio?
#Unidades de negocio
suma_consumo_por_ues_so = df_filtrado.groupby('UES')['Valor'].sum().sort_values(ascending=False)

# Graficar la suma del consumo total por UES
fig5 = plt.figure()
suma_consumo_por_ues_so.plot(kind='bar')
plt.xlabel('UES')
plt.ylabel('Consumo total')
plt.title('Consumo total por UES')
fig5.savefig('fig5.png', bbox_inches='tight')
plt.show()

#       Unidades y productos de mayor uso en cada categoria
#Unidades de mayor uso en cada categoria 
#Merge tabla consumo con tabla personas para poder agrupar por categoria
merged_df_so = df_filtrado.merge(df_persona, on='NumIdPersona', how='left')

#Agrupar por categoria y contamos las apariciones de UES 
grouped_ues_df_so = merged_df_so.groupby('Categoria')['UES'].value_counts()
grouped_ues_df_so = grouped_ues_df_so.reset_index(name='Apariciones')

# Definir los colores para cada categoría
colors = {'A': 'blue', 'B': 'green', 'C': 'red'}

# Crear el gráfico de barras con los colores personalizados
ax = grouped_ues_df_so.plot(kind='bar', x='UES', y='Apariciones', figsize=(10, 6), color=[colors.get(x, 'gray') for x in grouped_ues_df_so['Categoria']])

plt.xlabel('UES')
plt.ylabel('Apariciones')
plt.title('Apariciones de UES por Categoría')

# Crear una leyenda personalizada para los colores
legend_handles = [plt.Rectangle((0,0),1,1, color=color) for color in colors.values()]
plt.legend(legend_handles, colors.keys())

plt.savefig('fig6.png', bbox_inches='tight')
plt.show()


#Agrupaos por categoria y contamos las apariciones de Producto
grouped_produ_df_so = merged_df_so.groupby('Categoria')['Producto'].value_counts()
grouped_produ_df_so = grouped_produ_df_so.reset_index(name='Apariciones')

import seaborn as sns

pivot_table = grouped_produ_df_so.pivot(index='Categoria', columns='Producto', values='Apariciones')
fig7 = plt.figure(figsize=(10, 6))
sns.heatmap(pivot_table, cmap='YlGnBu', fmt='d')
plt.xlabel('Producto')
plt.ylabel('Categoría')
plt.title('Apariciones de producto por Categoría')
fig7.savefig('fig7.png', bbox_inches='tight')
plt.show()

#       Identifique los clientes (afiliados y no afiliados) con mayor frecuencia de uso y mayor valor neto de venta.
#Identificar clientes afiliados con mayor frecuencia de uso 
frecuencia_uso_afiliados_so = afiliados_sin_outliers.groupby('NumIdPersona')['NumTransacciones'].sum().sort_values(ascending=False)

#Identificar mayor valor neto de venta
valor_neto_venta_afiliados_so = afiliados_sin_outliers.groupby('NumIdPersona')['Valor'].max().sort_values(ascending=False)

#Identificar clientes NO afiliados con mayor frecuencia de uso 
frecuencia_uso_no_afiliados_so = no_afiliados_so.groupby('NumIdPersona')['NumTransacciones'].sum().sort_values(ascending=False)

#Identificar mayor valor neto de venta NO afiliados
valor_neto_venta_no_afiliados_so = no_afiliados_so.groupby('NumIdPersona')['Valor'].max().sort_values(ascending=False)

# Crear el gráfico de dispersión para afiliados y no afiliados
fig8 = plt.figure()
plt.scatter(frecuencia_uso_afiliados_so, valor_neto_venta_afiliados_so, color='blue', label='Afiliados')
plt.scatter(frecuencia_uso_no_afiliados_so, valor_neto_venta_no_afiliados_so, color='red', label='No Afiliados')

# Configurar el gráfico
plt.xlabel('Frecuencia de Uso')
plt.ylabel('Valor Neto de Venta')
plt.title('Clientes con Mayor Frecuencia de Uso y Valor Neto de Venta')
plt.legend()

fig8.savefig('fig8.png')

# Mostrar el gráfico
plt.show()

#       ¿Cómo ha sido el porcentaje histórico de penetración en la población afiliada de los servicios Colsubsidio?
#Calcular el número total de clientes atendidos en cada período de tiempo
clientes_totales_so = df_filtrado.groupby('Periodo')['NumIdPersona'].nunique()

#Calcular el número de clientes afiliados en cada período de tiempo
clientes_afiliados_so = afiliados_sin_outliers.groupby('Periodo')['NumIdPersona'].nunique()

#Calcular el porcentaje de penetración en cada período de tiempo
penetracion_so = (clientes_afiliados_so / clientes_totales_so) * 100

#Visualizar el porcentaje histórico de penetración

fig9 = plt.figure(figsize=(10, 6))
penetracion_so.plot(kind='line')
plt.title('Porcentaje histórico de penetración en la población afiliada')
plt.xlabel('Período')
plt.ylabel('Porcentaje de penetración')
fig9.savefig('fig9.png')
plt.show()

#       ¿Cuáles son los productos más consumidos en cada segmento poblacional?
# Agrupar los registros de consumo por segmento poblacional y producto, y calcular la suma de los valores de consumo
productos_por_segmento_so = merged_df_so.groupby(['Segmento_poblacional', 'Producto'])['Valor'].sum()

# Encontrar los productos más consumidos en cada segmento poblacional
productos_mas_consumidos_so = productos_por_segmento_so.groupby('Segmento_poblacional').idxmax().apply(lambda x: x[1])

# Crear la figura y los ejes del gráfico
fig, ax = plt.subplots()

# Definir los colores para cada producto 
colores = {'Supermercados': 'blue', 'No Libranza': 'green'}

# Recorrer cada segmento poblacional y su producto más consumido
for segmento, producto in productos_mas_consumidos_so.items():
    # Filtrar los datos para el segmento poblacional y producto más consumido
    datos_segmento_producto = productos_por_segmento_so.loc[(segmento, producto)]
    
    # Obtener el valor de consumo y el nombre del segmento poblacional
    valor_consumo = datos_segmento_producto
    nombre_segmento = segmento
    
    # Agregar barra al gráfico
    ax.bar(nombre_segmento, valor_consumo, color=colores[producto], label=producto)
    
# Agregar etiquetas y título
ax.set_xlabel('Segmento poblacional')
ax.set_ylabel('Valor de consumo')
ax.set_title('Productos más consumidos por segmento poblacional')

# Agregar leyenda
handles, labels = ax.get_legend_handles_labels()
# Eliminar duplicados en la leyenda
by_label = dict(zip(labels, handles))
ax.legend(by_label.values(), by_label.keys())

plt.savefig('fig10.png')
# Mostrar el gráfico
plt.show()

#       ¿Cuáles son las mejores empresas en cuanto a consumo individual de sus empleados?
#juntamos la tabla merge entre consumo y persona, con la tabla empresa 
merged_df2_so = merged_df_so.merge(df_empresa, on='id_empresa', how='left')

#Sumar y agrupar por NumIdPersona y id_empresa para obtener el consumo individual de los empleados por empresa
consumo_por_empleado_so = merged_df_so.groupby(['NumIdPersona', 'id_empresa'])['Valor'].sum()

# Obtener los 10 empleados con mayor consumo
top_10_empleados_so = consumo_por_empleado_so.nlargest(10)

# Crear la figura y los ejes del gráfico
fig, ax10 = plt.subplots()

# Crear una columna de etiquetas para el eje x
etiquetas = [f'{num}-{emp}' for num, emp in top_10_empleados_so.index]

# Crear la gráfica de barras
ax10.bar(etiquetas, top_10_empleados_so.values)

# Agregar etiquetas y título
ax10.set_xlabel('NumIdPersona - Id_empresa')
ax10.set_ylabel('Valor')
ax10.set_title('Distribución de Valores')

# Establecer los lugares de las marcas del eje x
ax10.set_xticks(range(len(etiquetas)))

# Girar las etiquetas del eje x y alinearlas a la derecha
ax10.set_xticklabels(etiquetas, rotation=90, ha='right')

plt.savefig('fig11.png', bbox_inches='tight')
# Mostrar la gráfica
plt.show()

#Calcular el valor promedio por transaccion 
valor_promedio_transaccion_so = merged_df_so.groupby('NumTransacciones')['Valor'].mean()