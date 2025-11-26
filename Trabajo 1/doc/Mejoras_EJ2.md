Aquí tienes un documento en formato Markdown (`.md`) listo para ser usado como nota de estudio o guía para tu defensa.

[cite\_start]Este documento estructura los cambios técnicos justificándolos desde el punto de vista de la **Eficiencia Computacional** (velocidad) y la **Convergencia Algorítmica** (capacidad de encontrar la solución), que son los dos pilares que el profesor valorará en la "discusión crítica"[cite: 26].

---

````markdown
# Optimización de Algoritmo Genético: Análisis de Mejoras

Este documento detalla la evolución del código desde su versión inicial hasta la versión optimizada, justificando cada cambio técnico. Estas notas sirven como base para la defensa de la práctica y la redacción de la memoria.

---

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
````

**Código Optimizado:**

```python
for individuo in PoblacionH:
    # Genera 1000 aleatorios de golpe (C optimizado)
    mask = np.random.random(1000) < 0.001

    if np.any(mask): # Solo si hay cambios, operamos
        # Invierte los bits donde la máscara es True
        individuo.array[mask] = 1 - individuo.array[mask]
```

### Justificación para la Defensa

> _"Hemos sustituido los bucles explícitos por operaciones vectorizadas de NumPy. Esto delega la carga computacional a librerías de bajo nivel (C), reduciendo el tiempo de ejecución drásticamente y permitiendo alcanzar las 5000 generaciones exigidas sin cuellos de botella."_

---

## 2\. Introducción de Elitismo

El cambio más importante para asegurar que el algoritmo encuentre la solución óptima (1000 unos).

### Situación Original (El problema)

El código utilizaba un reemplazo generacional total (`poblacion = PoblacionH`).

- **Riesgo:** El algoritmo genético es estocástico (aleatorio). Es posible que, tras cruzar y mutar, los hijos sean peores que los padres.
- **Consecuencia:** Se perdía la mejor solución encontrada hasta el momento ("olvido catastrófico"), haciendo que la gráfica de fitness subiera y bajara erráticamente.

### Solución Implementada

Se fuerza la supervivencia del mejor individuo de la generación anterior.

**Lógica Implementada:**

1.  Antes de crear la nueva generación, guardamos una copia profunda (`deepcopy`) del mejor padre.
2.  Generamos los hijos.
3.  Sustituimos al peor hijo de la nueva generación con el mejor padre guardado.

### Justificación para la Defensa

> _"Implementamos una estrategia elitista para garantizar la convergencia monótona. Al preservar siempre al mejor individuo de la generación anterior, aseguramos que la calidad de la solución nunca decrezca, actuando como un 'trinquete' evolutivo que solo permite mejorar o mantenerse."_

---

## 3\. Eficiencia en Recálculos (Lazy Evaluation)

Una mejora menor pero importante para no desperdiciar recursos.

### Situación Original

Se llamaba a `individuo.contar_unos()` para **todos** los individuos en cada ciclo, independientemente de si habían mutado o no.

### Solución Implementada

Solo recalculamos el fitness si el genotipo ha cambiado.

**Código Optimizado:**

```python
if np.any(mask): # Si la máscara tiene algún True (hubo mutación)
    individuo.array[mask] = 1 - individuo.array[mask]
    individuo.contar_unos() # Solo recalculamos aquí
```

### Justificación para la Defensa

> _"Optimizamos el coste computacional evitando recálculos redundantes de la función de fitness. Dado que la probabilidad de mutación es baja (0.1%), la mayoría de individuos no cambian en esta fase, por lo que ahorramos tiempo de procesador saltando el recálculo."_

---

## 4\. Resumen Visual: ¿Por qué funciona mejor ahora?

[cite\_start]Si te piden explicar la gráfica de evolución (Fitness vs Generaciones)[cite: 25], puedes usar esta comparativa:

| Característica       | Código Original                        | Código Optimizado                                     |
| :------------------- | :------------------------------------- | :---------------------------------------------------- |
| **Velocidad**        | Lenta (O(N\*L) en Python puro)         | **Rápida** (Vectorizada en C)                         |
| **Curva de Fitness** | "Dientes de sierra" (sube y baja)      | **Ascendente suave** (nunca baja gracias al elitismo) |
| **Estabilidad**      | Puede perder el óptimo si lo encuentra | **Retiene el óptimo** hasta el final                  |
| **Memoria**          | Reasignación constante                 | **Gestión eficiente** con deepcopy                    |

---

## 5\. Respuestas a Posibles Preguntas del Profesor

**P: ¿Por qué usaron `copy.deepcopy`?**
_R: En Python, los objetos se pasan por referencia. Si simplemente asignamos `mejor = actual`, al modificar la población en la siguiente línea, también modificaríamos al "mejor" guardado. `deepcopy` crea una copia totalmente independiente en memoria._

**P: ¿Cómo afecta la probabilidad de mutación (0.001) a la convergencia?**
_R: Una probabilidad baja permite una exploración fina cerca del óptimo local sin destruir la estructura de los individuos buenos. Si fuera muy alta, el algoritmo se comportaría como una búsqueda aleatoria sin memoria._

**P: ¿Cumple esto con el enunciado?**
_R: Sí. [cite\_start]El enunciado pide maximizar el número de unos en vectores de 1000 bits [cite: 20, 21] [cite\_start]usando selección por ranking[cite: 19]. [cite\_start]Las optimizaciones realizadas son a nivel de implementación y estrategia de reemplazo (elitismo), lo cual es parte de la discusión algorítmica esperada en la práctica[cite: 26]._

```

```
