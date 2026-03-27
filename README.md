# Search Benchmark & Predictive Analysis 🔍📊

Este proyecto desarrolla un análisis comparativo de rendimiento entre algoritmos de búsqueda clásica (**Lineal** vs. **Binaria**) mediante un flujo de trabajo híbrido que combina la eficiencia de **C** con el poder de análisis de datos de **Python**.

El objetivo es validar empíricamente las complejidades O(n) y O(log n), utilizando métodos numéricos para predecir el comportamiento de los algoritmos en escenarios de datos masivos.

## 🚀 Componentes del Proyecto

### 1. Engine de Benchmark (C)
Localizado en `main.c`, este módulo se encarga de la generación de datos y la medición de tiempos:
* **Alta Resolución:** Utiliza `QueryPerformanceCounter` de la API de Windows para obtener precisiones de microsegundos.
* **Robustez:** Implementa cálculos para evitar el desbordamiento de enteros en la búsqueda binaria y sumideros de validación para prevenir optimizaciones no deseadas del compilador.
* **Exportación:** Genera un archivo `benchmark_resultados.csv` con los tiempos promedio obtenidos.

### 2. Analizador Predictivo (Python)
Localizado en `view.py`, este script procesa los resultados experimentales:
* **Interpolación PCHIP:** Utiliza `PchipInterpolator` para generar curvas suaves que mantienen la monotonicidad, evitando oscilaciones matemáticas irreales.
* **Modelado Matemático:** Aplica regresión lineal para la búsqueda $O(n)$ y regresión logarítmica para la búsqueda O(log n).
* **Predicción de Escala:** Permite al usuario ingresar un valor de $n$ para estimar el tiempo de ejecución basado en las funciones ajustadas.

## 🛠️ Requisitos e Instalación

**1. Compilación en C (Windows)**
```
gcc main.c
```

## Ejecución en Python
Requiere Python 3.x y las siguientes librerías:

```
pip install pandas numpy matplotlib scipy scikit-learn
```


