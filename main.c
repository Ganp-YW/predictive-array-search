#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <windows.h> // Para cronometraje de altísima resolución (QueryPerformanceCounter)

// Búsqueda Lineal: Complejidad O(n).

int busquedaLineal(int *arr, int n, int objetivo) {
    for (int i = 0; i < n; i++) {
        if (arr[i] == objetivo) return i;
    }
    return -1;
}

// Búsqueda Binaria: Complejidad O(log n).

int busquedaBinaria(int *arr, int n, int objetivo) { // n es el tamaño del array, 
    int bajo = 0, alto = n - 1;
    while (bajo <= alto) {
        // Se utiliza esta fórmula para evitar el desbordamiento de enteros en sistemas de 32 bits.
        int medio = (alto + bajo) / 2;
        if (arr[medio] == objetivo) return medio;
        if (arr[medio] < objetivo) bajo = medio + 1;
        else alto = medio - 1;
    }
    return -1;
}

int main() {
    system("color F1");
    

    /* Parámetros configurables desde línea de comandos */

    int min_n;    // tamaño mínimo del arreglo
    int max_n;  // tamaño máximo del arreglo
    int num_samples; // número de muestras
    int base_iter; // repeticiones base

        printf("Ingrese tamano minimo del arreglo: ");

while (scanf("%d", &min_n) != 1 || min_n <= 0) {

    printf("Valor inválido. Ingrese un entero positivo: ");
    while(getchar() != '\n');
}

    

printf("Ingrese el tamano maximo del arreglo: ");

while (scanf("%d", &max_n) != 1 || max_n <= min_n) {

    printf("Valor invalido. Ingrese un entero mayor que el minimo: ");
    while(getchar() != '\n');
}

    

printf("Ingrese el numero de muestras: ");

while (scanf("%d", &num_samples) != 1 || num_samples <= 1) {

    printf("Valor invalido. Ingrese un entero mayor que 1: ");
    while(getchar() != '\n');
}

printf("Ingrese la base de iteraciones: ");

while (scanf("%d", &base_iter) != 1 || base_iter <= 0) {

    printf("Valor inválido. Ingrese un entero positivo: ");
    while(getchar() != '\n');
}

printf("Intentando abrir benchmark_resultados.csv para escritura...\n");

FILE *archivo = fopen("benchmark_resultados.csv", "w");

    if (archivo == NULL) {
        perror("No se pudo abrir benchmark_resultados.csv");
        return 1;
    }
    printf("Archivo abierto correctamente. Escribiendo cabecera...\n");
    if (fprintf(archivo, "n,tiempo_lineal_prom,tiempo_binario_prom\n") < 0) {
        fprintf(stderr, "Error escribiendo cabecera en CSV\n");
        fclose(archivo);
        return 1;
    }
    
    printf("Cabecera escrita correctamente.\n");

    int step = (max_n - min_n) / (num_samples - 1);
    if (step < 1) step = 1;

    // MEJORA: Reservar memoria UNA SOLA VEZ para el array más grande requerido.
    int *datos = malloc(max_n * sizeof(int));
    if (datos == NULL) {
        fprintf(stderr, "Error de memoria para n = %d\n", max_n);
        fclose(archivo);
        return 1;
    }

    printf("Memoria reservada exitosamente para el tamano maximo (%d elementos).\n", max_n);

    // Llenar el arreglo completo (los algoritmos solo buscarán en una sub-sección de 'n' cada vez)
    for (int i = 0; i < max_n; i++) {
        datos[i] = i * 2;
    }

    // Configuración del temporizador de alta precisión de Windows
    LARGE_INTEGER frecuencia, inicio, fin;
    QueryPerformanceFrequency(&frecuencia);

    // Sumidero global para evitar la optimización agresiva del compilador
    long long validacion_busqueda = 0;

    for (int n = min_n; n <= max_n; n += step) {
        // Objetivo a encontrar: buscamos el último elemento de la sección (Peor caso teórico)
        int objetivo = datos[n - 1];

        long long iter = base_iter;
        if (n > 0) {
            iter = (long long)(base_iter * (1000.0 / n));
            if (iter < base_iter / 10) iter = base_iter / 10;
        }

        // --- BÚSQUEDA LINEAL ---
        QueryPerformanceCounter(&inicio);
        for (long long i = 0; i < iter; i++) {
            validacion_busqueda += busquedaLineal(datos, n, objetivo);
        }
        QueryPerformanceCounter(&fin);
        // Tiempo en segundos puros medido con microsegundos de resolución interna.
        double tLineal_prom = (double)(fin.QuadPart - inicio.QuadPart) / frecuencia.QuadPart / iter; 

        // --- BÚSQUEDA BINARIA ---
        QueryPerformanceCounter(&inicio);
        for (long long i = 0; i < iter; i++) {
            validacion_busqueda += busquedaBinaria(datos, n, objetivo);
        }
        QueryPerformanceCounter(&fin);
        double tBinario_prom = (double)(fin.QuadPart - inicio.QuadPart) / frecuencia.QuadPart / iter; 

        if (fprintf(archivo, "%d,%.15f,%.15f\n", n, tLineal_prom, tBinario_prom) < 0) {
            fprintf(stderr, "Error escribiendo datos en CSV para n=%d\n", n);
            break;

        } else {
            printf("Datos n = %d | Lineal: %.7f s | Binaria: %.9f s\n", n, tLineal_prom, tBinario_prom);
        }

        fflush(archivo);
    }

    // Asegurar que el compilador no borre los bucles usándolos en un chequeo silencioso
    if (validacion_busqueda == -1) printf(" ");

    free(datos);
    printf("Cerrando archivo CSV...\n");
    fclose(archivo);
    printf("Resultados guardados en benchmark_resultados.csv\n");
    return 0;
}