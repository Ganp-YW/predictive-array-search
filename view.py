import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse
from scipy.interpolate import PchipInterpolator
from sklearn.linear_model import LinearRegression

#  Argument Parser Setup
parser = argparse.ArgumentParser(description='Visualizar, interpolar y predecir resultados de benchmark.')
parser.add_argument('--n_points', '-p', type=int, default=500, help='Número de puntos para la interpolación suave.')
parser.add_argument('--predict_n', '-pred', type=int, default=0, help='Valor máximo de n para realizar predicciones.')
parser.add_argument('--file', '-f', default='output/benchmark_resultados.csv', help='Ruta al archivo CSV con los datos de entrada.')
args = parser.parse_args()

#  Interacción para pedir n a predecir 

if args.predict_n == 0:
    while True:
        try:
            user_pred_n = int(input("¿Qué valor de n quieres predecir? (debe ser positivo): "))
            if user_pred_n > 0:
                args.predict_n = user_pred_n
                break
            else:
                print("Por favor, ingresa un número positivo mayor a cero.")
        except Exception:
            print("Entrada inválida. Intenta de nuevo.")

# Cargar y Validar Datos
try:
    df = pd.read_csv(args.file)
except FileNotFoundError:
    raise SystemExit(f"Error: No se encontró el archivo '{args.file}'. Asegúrate de haber ejecutado primero el programa en C.")
except pd.errors.EmptyDataError:
    raise SystemExit(f"Error: El archivo '{args.file}' está vacío. Ejecuta el programa en C para generar los datos.")

if df.empty or 'n' not in df.columns:
    raise SystemExit(f"El archivo '{args.file}' no contiene datos válidos o le falta la columna 'n'.")

 # Seleccionar columnas de tiempo, priorizando promedios
if 'tiempo_lineal_prom' in df.columns:
    t_lineal = df['tiempo_lineal_prom']
    t_binaria = df['tiempo_binario_prom']
else:
    t_lineal = df.get('tiempo_lineal', pd.Series(dtype=float))
    t_binaria = df.get('tiempo_binaria', pd.Series(dtype=float))

# Siempre convertir a milisegundos ya que el script en C envía el tiempo en segundos puros
t_lineal = t_lineal * 1000 
t_binaria = t_binaria * 1000

n_muestras = df['n'] # Busca la columna con el nombre n en el CSV

# Interpolación para Curvas Suaves Monótonas (PCHIP elimina oscilaciones irreales) ---
# --- Crear interpoladores PCHIP ---

n_interp = np.linspace(n_muestras.min(), n_muestras.max(), args.n_points)
f_interp_lineal = PchipInterpolator(n_muestras, t_lineal)
f_interp_binaria = PchipInterpolator(n_muestras, t_binaria)



# Modelado y Predicción para 'n' grandes 

# Eje X extendido para las predicciones
n_pred = np.linspace(n_muestras.min(), args.predict_n, args.n_points)

# Modelo Lineal para Búsqueda Lineal O(n)
coef_lineal = np.polyfit(n_muestras, t_lineal, 1)
pred_lineal = coef_lineal[0] * n_pred + coef_lineal[1]

# Modelo Logarítmico para Búsqueda Binaria O(log n)
mask = n_muestras > 0
coef_binaria = np.polyfit(np.log(n_muestras[mask]), t_binaria[mask], 1)
pred_binaria = coef_binaria[0] * np.log(n_pred[n_pred > 0]) + coef_binaria[1]

print("\n--- Funciones Matematicas Ajustadas ---")
print(f"Búsqueda Lineal O(n)     : T(n) = {coef_lineal[0]:.6e} * n + {coef_lineal[1]:.6e} ms")
print(f"Búsqueda Binaria O(log n): T(n) = {coef_binaria[0]:.6e} * ln(n) + {coef_binaria[1]:.6e} ms")

# --- Mostrar predicción para el n solicitado ---
pred_n = args.predict_n


if pred_n > 0:
    pred_lineal_val = coef_lineal[0] * pred_n + coef_lineal[1]
    pred_binaria_val = coef_binaria[0] * np.log(pred_n) + coef_binaria[1]
    print(f"\nPredicción para n = {pred_n}:")
    print(f"  Búsqueda Lineal: {pred_lineal_val:.15f} segundos")
    print(f"  Búsqueda Binaria: {pred_binaria_val:.15f} segundos\n")


# Graficar Resultados y Predicciones
plt.figure(figsize=(14, 8))

# Datos originales con mayor tamaño y borde
plt.scatter(n_muestras, t_lineal, color='red', label='Lineal (Muestras de C)', zorder=5, s=80, edgecolor='black', linewidth=1.5)
plt.scatter(n_muestras, t_binaria, color='blue', label='Binaria (Muestras de C)', zorder=5, s=80, edgecolor='black', linewidth=1.5)

# Curvas interpoladas (suavizadas monótonas) en el rango original, más gruesas
plt.plot(n_interp, f_interp_lineal(n_interp), 'r-', alpha=0.8, linewidth=2.5, label='Interpolación PCHIP Lineal')
plt.plot(n_interp, f_interp_binaria(n_interp), 'b-', alpha=0.8, linewidth=2.5, label='Interpolación PCHIP Binaria')

# Curvas de predicción para n grande, más visibles
plt.plot(n_pred[n_pred > 0], pred_lineal[n_pred > 0], 'r--', alpha=0.7, linewidth=2, label=f'Predicción Lineal O(n) hasta n={args.predict_n}')
plt.plot(n_pred[n_pred > 0], pred_binaria, 'b--', alpha=0.7, linewidth=2, label=f'Predicción Binaria O(log n) hasta n={args.predict_n}')

# --- Configuraciones del Gráfico ---

#Variables para la leyenda

titulo = "Análisis de Rendimiento y Predicción de Algoritmos de Búsqueda"
eje_x = 'Tamaño del Arreglo (n)'
eje_y = 'Tiempo de Ejecución Promedio (milisegundos)'

#Leyenda de la gráfica.

plt.title(titulo)
plt.xlabel(eje_x)
plt.ylabel(eje_y)
plt.legend(loc='upper left', fontsize=12)
plt.grid(True, which='both', linestyle='--', linewidth=0.7)


# Escala lineal en Y para mejor visibilidad

# plt.yscale('log')
plt.xscale('log') # Escala logarítmica en X ayuda a visualizar la relación

print(f"Mostrando interpolación y predicción hasta n={args.predict_n}.")
print("Cierra la ventana del gráfico para finalizar el script.")
plt.show()