# Trabajos Soft-Computing — Aplicaciones del Soft-Computing en Energía

Prácticas de la asignatura **Aplicaciones del Soft-Computing en Energía** (Escuela Politécnica Superior, Teoría de la Señal y Comunicaciones — Grado en Ingeniería en Sistemas de Información).

**Autores:** Isaac Marval Hernández y Juan Carlos Negrín de la Fe

El repositorio recoge la progresión de la asignatura: desde estrategias evolutivas y un algoritmo genético básicos sobre funciones de prueba (Práctica 1) hasta un algoritmo de **Arrecifes de Coral (CRO)** que optimiza la disposición de aerogeneradores en un parque eólico (Trabajo Final).

---

## Índice

- [Estructura del repositorio](#estructura-del-repositorio)
- [Requisitos e instalación](#requisitos-e-instalación)
- [Trabajo 1 — Estrategias evolutivas y algoritmo genético binario](#trabajo-1--estrategias-evolutivas-y-algoritmo-genético-binario)
- [Trabajo 2](#trabajo-2)
- [Trabajo Final — Optimización del layout de un parque eólico con CRO](#trabajo-final--optimización-del-layout-de-un-parque-eólico-con-cro)
- [Referencias](#referencias)
- [Uso de herramientas de IA](#uso-de-herramientas-de-ia)

---

## Estructura del repositorio

```
Trabajos-Softcomp-duoq/
├── Trabajo 1/                       # Práctica 1: ES (1+1), (μ+λ) y AG binario
│   ├── Ej1.py                       # (1+1)-ES y (μ+λ)-ES sobre la función esfera
│   ├── Ej2.py                       # Algoritmo genético binario (OneMax, 1000 bits)
│   ├── Ej1.md / Ej2.md              # Pseudocódigo de cada ejercicio
│   ├── doc/                         # Gráficas y notas de mejoras (Mejoras_EJ2.md)
│   ├── Practica_1_ES-GA.pdf         # Enunciado
│   ├── Practica_1.pdf               # Memoria entregada
│   └── Practica_1.zip               # Entrega (código + memoria)
├── Trabajo 2/
│   └── main.py                      # (vacío)
└── Trabajo Final/                   # Práctica final: layout de parque eólico con CRO
    ├── main.py                      # Punto de entrada y parámetros del experimento
    ├── reef_optimization.py         # Algoritmo CRO, operadores, caché y evaluación
    ├── windSymPython/               # Simulador de viento / estelas (port Python del código MATLAB)
    │   ├── f_powerPlants_f1.py, f_powerPlants_f2.py, f_powerPlantsT_fast.py
    │   ├── powerGen.py, powCurve.py, polygon.py, windSym.py
    │   └── dt/                      # Datos (WindSym_1.mat, pwrCurve.mat) y scripts .m originales
    ├── docs/                        # Notas técnicas de diseño e implementación
    ├── ffast_hardcoded.m            # Evaluación de layouts clásicos de la literatura (MATLAB)
    ├── progresion20x20.png          # Evolución del CRO, caso 20×20
    ├── progresion 50x50.png         # Evolución del CRO, caso 50×50
    ├── Isaac_Marval_JuanCarlos_Negrin.docx   # Memoria final
    └── *.pdf                        # Enunciado y artículos de referencia
```

---

## Requisitos e instalación

- Python 3.10 o superior
- Librerías: `numpy`, `scipy`, `matplotlib`, `numba`, `joblib`

```bash
pip install numpy scipy matplotlib numba joblib
```

---

## Trabajo 1 — Estrategias evolutivas y algoritmo genético binario

📄 [Enunciado](Trabajo%201/Practica_1_ES-GA.pdf) · [Memoria](Trabajo%201/Practica_1.pdf)

### Ejercicio 1: (1+1)-ES y (μ+λ)-ES

Minimización de la **función esfera** en 30 dimensiones:

$$f_1(x) = \sum_{i=1}^{30} x_i^2, \qquad x_i \in [-100, 100]$$

Es una función convexa y unimodal, con mínimo global $f(0)=0$.

| Parámetro | (1+1)-ES | (μ+λ)-ES |
|---|---|---|
| Población | 1 padre, 1 hijo | μ = 10 padres, λ = 30 hijos |
| Mutación | Ruido gaussiano N(0, σ) | Ruido gaussiano N(0, σ) sobre un padre aleatorio |
| Selección | El hijo sustituye al padre si es mejor | Los μ mejores de padres ∪ hijos |
| σ inicial | 30 (también se probaron 60 y 90) | 30 (también se probaron 60 y 90) |
| Ajuste de σ | σ ← 0.9·σ cada 1000 iteraciones | σ ← 0.9·σ cada 1000 iteraciones |
| Parada | fitness < 0.001 o 200 000 iteraciones | fitness < 0.001 o 200 000 iteraciones |

**Conclusiones principales:**
- Una σ alta explora rápido pero no afina; una σ baja afina pero tarda mucho en recorrer el dominio. El **decaimiento dinámico** de σ combina ambas cosas y converge de forma consistente.
- Con σ = 30 y σ = 60, la (μ+λ)-ES converge en menos generaciones y con una curva más suave que la (1+1)-ES.
- Con σ = 90 la tendencia se invierte: la (1+1)-ES llega antes, porque la población de la (μ+λ) se dispersa demasiado.
- Por número de evaluaciones, la (μ+λ) es más cara: 30 evaluaciones por generación frente a 1.

```bash
cd "Trabajo 1"
python Ej1.py
```

| σ = 30 | σ = 60 | σ = 90 |
|---|---|---|
| ![σ=30](Trabajo%201/doc/EJ1_(desviacion30).png) | ![σ=60](Trabajo%201/doc/Ej1_(desvciacion60).png) | ![σ=90](Trabajo%201/Figure_1(desviacion90).png) |

### Ejercicio 2: Algoritmo genético binario (OneMax)

Maximizar el número de unos de un vector binario de **1000 bits**.

| Parámetro | Valor |
|---|---|
| Población | 100 individuos |
| Generaciones máximas | 5000 |
| Selección | Ranking lineal (Baker), presión selectiva S = 1.5 |
| Cruce | Un punto, con orden de los fragmentos aleatorio (100 parejas → 100 hijos) |
| Mutación | Flip bit a bit con p = 0.001, vectorizada con máscaras de NumPy |
| Elitismo | El mejor de la generación anterior sustituye al peor hijo |

**Resultado:** el algoritmo encontró la cadena óptima (1000 unos) en la **generación 2062**, muy por debajo del límite de 5000.

Mejoras de implementación, documentadas en [`doc/Mejoras_EJ2.md`](Trabajo%201/doc/Mejoras_EJ2.md):
- **Mutación vectorizada** con máscaras booleanas, en lugar de bucles bit a bit.
- **Elitismo**, para que el mejor fitness nunca baje de una generación a la siguiente.
- **Evaluación perezosa**: el fitness solo se recalcula si el individuo ha mutado.

```bash
cd "Trabajo 1"
python Ej2.py   # guarda la gráfica en doc/ej2_evolucion_fitness.png
```

![Evolución del fitness del AG](Trabajo%201/doc/ej2_evolucion_fitness.png)

---

## Trabajo 2

La carpeta [`Trabajo 2/`](Trabajo%202/) solo contiene un `main.py` vacío; este trabajo no tiene contenido en el repositorio.

---

## Trabajo Final — Optimización del layout de un parque eólico con CRO

📄 [Enunciado](Trabajo%20Final/Práctica_Final_Turbine_Layout.pdf) · [Memoria (Word)](Trabajo%20Final/Isaac_Marval_JuanCarlos_Negrin.docx)

### El problema

El objetivo es encontrar las celdas de una cuadrícula discreta en las que colocar exactamente N aerogeneradores para **maximizar la potencia media anual** del parque. Para ello se usa una simulación de viento de un año completo (8760 horas, `WindSym_1.mat`) y el **modelo de estelas de Jensen**, en el que el radio de la estela crece linealmente con la distancia: $r = \alpha x + R$.

Hay dos escenarios:

| Escenario | Cuadrícula | Posiciones | Turbinas |
|---|---|---|---|
| Base | 20 × 20 | 400 | 20 |
| Extendido | 50 × 50 | 2500 | 50 |

Función objetivo, donde $G_r$ es la matriz binaria del layout:

$$\max_{G_r} \; \bar{P} = \frac{1}{8760} \sum_{t=1}^{8760} \sum_{i=1}^{N} P_i(t)$$

### Codificación de las soluciones

Cada solución es una **matriz binaria `numpy` de Kgr × Kgr** (1 = turbina). Se eligió frente a un vector de 400 bits, que pierde la vecindad 2D necesaria para calcular las estelas, y frente a una lista de coordenadas, cuyos operadores generan con facilidad duplicados o posiciones fuera de rango. La matriz:

- es la misma estructura que consume el simulador, así que no hace falta transformarla antes de evaluar;
- se puede operar de forma vectorizada con NumPy;
- sirve para 20×20 y para 50×50 sin cambiar la lógica.

**Gestión de la restricción de N turbinas exactas:**

| Fase | Estrategia |
|---|---|
| Inicialización | Permutación aleatoria de índices; se activan exactamente los N primeros |
| Cruce (reproducción sexual) | OR lógico entre los dos padres y **reparación** eliminando turbinas al azar hasta volver a N |
| Mutación (reproducción asexual) | **Swap**: una turbina se mueve a una celda vacía, con lo que el número de turbinas no cambia |
| Distancia mínima | Implícita en la discretización: como máximo una turbina por celda |

### El algoritmo CRO (Coral Reef Optimization)

El arrecife es una matriz de 8×8 huecos. Cada hueco puede estar vacío o contener un **coral**, que es un layout completo del parque. En cada iteración:

1. **Reproducción sexual** (*broadcast spawning*), con una fracción de 0.80: se cruzan parejas de corales y se generan larvas. Una larva ocupa un hueco vacío o, si no lo hay, compite con el peor coral.
2. **Reproducción asexual** (*budding*), con una fracción de 0.20: los corales de élite se mutan e intentan asentarse en el arrecife.
3. **Depredación**: los corales del 10 % peor se eliminan con probabilidad Pd = 0.08. Así se mantiene la diversidad y se libera espacio.
4. **Parada**: al llegar al número máximo de iteraciones o tras 10 iteraciones seguidas sin mejora (*early stopping*).

| Parámetro | Valor |
|---|---|
| Tamaño del arrecife | 8 × 8 (64 huecos) |
| Ocupación inicial ρ₀ | 0.60 |
| Fracción sexual F_b | 0.80 |
| Fracción asexual F_a | 0.20 |
| Probabilidad de depredación P_d | 0.08 (sobre el 10 % peor) |
| Iteraciones máximas | 100 en la memoria (150 en el `main.py` actual) |
| Estancamiento máximo | 10 iteraciones |

### Optimizaciones computacionales

| Técnica | Descripción | Documentación |
|---|---|---|
| **Caché persistente** | `PersistentCoralCache` usa `matriz.tobytes()` como clave de un diccionario, de modo que comprobar si un layout ya está evaluado cuesta O(1). La caché se guarda en disco (`coral_cache.pkl`) y se reutiliza entre ejecuciones. | [`Implemtation_changes_cache.md`](Trabajo%20Final/docs/Implemtation_changes_cache.md) |
| **Paralelismo** | Las larvas y los mutantes se evalúan en lotes con `joblib.Parallel(n_jobs=-1)`, aprovechando todos los núcleos. Fue la mejora que más redujo el tiempo de ejecución. | [`implementation_parallelization.md`](Trabajo%20Final/docs/implementation_parallelization.md) |
| **JIT con Numba** | `unique_tol`, que agrupa las direcciones de viento con tolerancia, se compila con `@njit`. Esa subrutina pasa a ser unas 15 veces más rápida. | [`implementation_changes.md`](Trabajo%20Final/docs/implementation_changes.md) |

Más detalles en [`CODIFICACION_SOLUCIONES.md`](Trabajo%20Final/docs/CODIFICACION_SOLUCIONES.md) y [`unidades_resultados.md`](Trabajo%20Final/docs/unidades_resultados.md).

### Ejecución

```bash
cd "Trabajo Final"
python main.py
```

El escenario se elige en `main.py`:

```python
Kgr = 20     # tamaño de la cuadrícula (20 o 50)
Nturb = 20   # número de turbinas (20 o 50)
```

Por consola se muestran el ranking inicial, el estado del arrecife en cada iteración y la mejor disposición encontrada. Al final se genera la gráfica de progresión.

### Resultados

| Escenario | Referencia (aleatorio) | Resultado CRO |
|---|---|---|
| 20 × 20, 20 turbinas | ≈ 5.20·10⁷ W | **5.30·10⁷ W** |
| 50 × 50, 50 turbinas | — | **1.3252·10⁸ W** |

En el caso 20×20, el fitness sube deprisa durante las primeras ~20 iteraciones (de 5.20·10⁷ a 5.25·10⁷ W). Entre las iteraciones 20 y 60 avanza por mesetas y saltos, y hacia la iteración 60 se estabiliza en 5.30·10⁷ W, el rango de calidad que pide la rúbrica.

| 20 × 20 | 50 × 50 |
|---|---|
| ![Progresión 20x20](Trabajo%20Final/progresion20x20.png) | ![Progresión 50x50](Trabajo%20Final/progresion%2050x50.png) |

Para tener una referencia, también se evaluaron los layouts clásicos de la literatura (Mosetti, Grady, Marmidis…) con el mismo perfil de viento, usando el script `ffast_hardcoded.m`.

**Impacto económico:** 1 MW más de potencia media equivale a 8760 MWh al año. A 80 €/MWh son unos 700 000 € al año, es decir, más de 14 M€ en los 20 años de vida útil de un parque.

### Trabajo futuro

- Sustituir el modelo de Jensen por un **modelo de estela gaussiano**, que es más realista.
- Admitir **parques no cuadrados** y zonas prohibidas.
- **Reducir simetrías**: no evaluar layouts que solo se diferencian por una rotación de 90°.

---

## Referencias

- Saavedra-Moreno, B. et al. (2011): uso de algoritmos evolutivos para posicionar turbinas ([PDF](Trabajo%20Final/Evol_Comput_Turbine_Layout.pdf)).
- Zergane, S. et al. (2018): optimización de parques con métodos pseudo-aleatorios y el modelo de Jensen ([PDF](Trabajo%20Final/Pseudo_Random_Turbine_Layout.pdf)).
- Mosetti, G. et al. (1994) y Grady, S. A. et al. (2005): trabajos clásicos con algoritmos genéticos, usados como benchmark.
- Gatscha, P. (2018): tesis de máster sobre modelos de estela (modelo gaussiano frente a Jensen).


## Uso de herramientas de IA

Como se indica en la memoria final, se usaron ChatGPT para revisar la redacción de la memoria y GitHub Copilot como apoyo puntual al escribir código. Todas las sugerencias se revisaron y validaron. Las decisiones de diseño, implementación y validación experimental fueron de los autores.
