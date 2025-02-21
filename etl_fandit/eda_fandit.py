import matplotlib.pyplot as plt
import seaborn as sns

# Ajustes de estilo para gráficos
plt.style.use('seaborn-darkgrid')
sns.set_palette('Set2')

# Información general del dataset
info = df.info()

# Primeras filas del dataset
head = df.head()

# Descripción estadística de las columnas numéricas
description = df.describe(include='all')

# Análisis de valores nulos
missing_values = df.isnull().sum().reset_index()
missing_values.columns = ['Column', 'MissingValues']
missing_values['Percentage'] = (missing_values['MissingValues'] / len(df)) * 100

# Análisis de valores 0.0 en columnas numéricas
zero_values = df.select_dtypes(include=['float64', 'int64']).eq(0).sum().reset_index()
zero_values.columns = ['Column', 'ZeroValues']
zero_values['Percentage'] = (zero_values['ZeroValues'] / len(df)) * 100

# Análisis de columnas categóricas (cantidad de categorías por columna)
categorical_columns = df.select_dtypes(include=['object']).nunique().reset_index()
categorical_columns.columns = ['Column', 'UniqueCategories']

# Análisis de rangos de fechas (si hubiera columnas de fechas)
date_columns = df.select_dtypes(include=['datetime64[ns]']).columns
date_ranges = {}
for col in date_columns:
    date_ranges[col] = {'Min': df[col].min(), 'Max': df[col].max()}

# Visualización de valores nulos
plt.figure(figsize=(10, 6))
sns.heatmap(df.isnull(), cbar=False, cmap='viridis')
plt.title('Mapa de Calor de Valores Nulos en el Dataset')
plt.xlabel('Columnas')
plt.ylabel('Filas')
plt.show()

# Visualización de distribución de valores numéricos
numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
df[numeric_columns].hist(bins=20, figsize=(15, 10), color='skyblue', edgecolor='black')
plt.suptitle('Distribución de Columnas Numéricas', fontsize=16)
plt.show()

# Análisis de correlación (solo para columnas numéricas)
correlation_matrix = df.corr(numeric_only=True)
plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
plt.title('Matriz de Correlación entre Columnas Numéricas')
plt.show()

# Resultados preliminares
{
    "info": info,
    "head": head,
    "description": description,
    "missing_values": missing_values.head(10),
    "zero_values": zero_values.head(10),
    "categorical_columns": categorical_columns.head(10),
    "date_ranges": date_ranges
}
