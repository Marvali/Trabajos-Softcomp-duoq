# Implementación de Paralelización y Optimización de Caché

## Resumen
Se ha modificado el algoritmo CRO (Coral Reef Optimization) para aprovechar la capacidad de procesamiento paralelo de la CPU mediante la librería `joblib`. Esto permite evaluar múltiples corales simultáneamente, reduciendo significativamente el tiempo de computación. Además, se ha optimizado el uso de la caché persistente para evitar condiciones de carrera y cálculos redundantes.

## Cambios Realizados

### 1. Extracción de Lógica Pura
- Se extrajo la lógica de cálculo de potencia a una función pura `_calculate_coral_power_pure`.
- Esta función no tiene efectos secundarios (no lee ni escribe en disco/variables globales) lo que la hace segura para su ejecución en hilos o procesos paralelos.

### 2. Paralelización de `evaluate_reef_power`
- **Estrategia**: Check-Cache-Then-Compute.
- El algoritmo primero itera sobre todos los corales para identificar cuáles ya tienen su potencia calculada en la caché (`CORAL_CACHE`).
- Los corales no cacheados se agrupan y se envían a evaluar en paralelo utilizando `joblib.Parallel` con `n_jobs=-1` (todos los núcleos disponibles).
- Los resultados se recolectan y se actualiza la caché en el proceso principal, asegurando la integridad de los datos.

### 3. Paralelización de Reproducción (Sexual y Asexual)
- Se refactorizaron los bucles de reproducción para seguir un modelo por lotes (Batch Processing):
    - **Fase 1: Generación**: Se generan todos los hijos/mutantes secuencialmente (operación rápida).
    - **Fase 2: Evaluación**: Se evalúan todos los nuevos individuos en paralelo. Se minimizan las llamadas a la función de evaluación filtrando primero por la caché.
    - **Fase 3: Inserción**: Se intenta insertar los nuevos individuos en el arrecife de forma secuencial, basándose en los valores de potencia calculados.

### 4. Seguridad y Rendimiento
- **Thread/Process Safety**: La caché (`PersistentCoralCache`) solo es modificada por el proceso principal. Los procesos trabajadores ("workers") solo realizan cálculos matemáticos.
- **Eficiencia**: Al agrupar las evaluaciones, se reduce el *overhead* de la creación de procesos. El uso de `joblib` gestiona eficientemente el pool de trabajadores.

## Archivos Modificados
- `reef_optimization.py`: Refactorización completa de funciones de evaluación y bucles del algoritmo CRO.

## Cómo Ejecutar
No se requieren cambios en la forma de ejecutar el programa. Simplemente corra:
```bash
python Main.py
```
(Asegúrese de tener instalada la librería `joblib`: `pip install joblib`)
