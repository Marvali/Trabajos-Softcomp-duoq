# Optimización de Algoritmo Genético: Análisis de Mejoras

## Este documento detalla las mejoras implementadas en el algoritmo genético para optimizar su rendimiento, centrándose en tres áreas clave: vectorización de la mutación, optimización de la selección por ruleta y seguimiento del mejor individuo global.

## 1. Vectorización de la Mutación (NumPy vs. Bucles)

El cambio más drástico en términos de velocidad de ejecución.

### Situación Original (El problema)

En la versión inicial, la mutación se realizaba iterando bit a bit sobre cada individuo.

- **Coste:** Para una población de 100 individuos y longitud 1000, se hacían **100.000 iteraciones** explícitas en Python por generación.
- [cite_start]**Impacto:** En 5000 generaciones[cite: 22], esto resultaba en 500 millones de comprobaciones en bucles `for`, lo cual es extremadamente lento en Python puro.

### Solución Implementada (Vectorización)

Utilizamos la capacidad de `numpy` para operar sobre arrays completos usando "máscaras booleanas".

**Código Original:**

```python
for individuo in PoblacionH:
    for i in range(len(individuo.array)):  # Bucle ineficiente
        if np.random.rand() < 0.001:       # 1000 llamadas al random por individuo
            individuo.array[i] = 1 - individuo.array[i]
```
