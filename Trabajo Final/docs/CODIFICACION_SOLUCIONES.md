# 3. CODIFICACIÓN DE SOLUCIONES

Este capítulo detalla las decisiones de diseño tomadas respecto a la representación computacional de los individuos (soluciones) en el algoritmo de *Coral Reef Optimization* (CRO), así como las estrategias implementadas para garantizar la viabilidad de dichas soluciones en el contexto de la optimización del parque eólico.

## 3.1. Opciones de codificación analizadas

Para representar la disposición espacial de las turbinas en una cuadrícula discreta de $20 \times 20$, se evaluaron tres enfoques principales. Cada uno presenta ventajas y desventajas en términos de memoria y complejidad computacional para los operadores genéticos.

### 3.1.1. Matriz binaria $20 \times 20$
Esta representación utiliza una matriz bidimensional donde cada celda $(i, j)$ toma un valor de 1 si existe una turbina en esa posición y 0 si está vacía.
*   **Ventajas:** Es la representación más intuitiva y visual. Facilita el cálculo de matrices de distancias y efectos de estela (*wake effect*), ya que mapea directamente a la geometría del problema.
*   **Desventajas:** Puede ser dispersa (*sparse*) si el número de turbinas es bajo comparado con el tamaño de la cuadrícula.

### 3.1.2. Vector binario de 400 bits
Consiste en aplanar la matriz $20 \times 20$ en un vector unidimensional de longitud $L = 400$.
*   **Ventajas:** Simplifica ciertas operaciones de cruce estándar (como el cruce de un punto o dos puntos) al tratar el individuo como una cadena simple de bits.
*   **Desventajas:** Se pierde la información de vecindad espacial directa (norte, sur, este, oeste), lo cual es relevante para entender las interferencias de viento locales.

### 3.1.3. Representación mediante lista de coordenadas
Se almacena una lista de tuplas $(x, y)$ indicando únicamente las posiciones ocupadas por las turbinas.
*   **Ventajas:** Extremadamente eficiente en memoria para soluciones dispersas.
*   **Desventajas:** Complica las operaciones de mutación y cruce, ya que es trivial generar duplicados o coordenadas inválidas que requieren validación constante. Además, dificulta la visualización rápida del "mapa" completo.

## 3.2. Codificación elegida y justificación

Se ha seleccionado la **Matriz Binaria $20 \times 20$** (implementada como arrays `NumPy` bidimensionales en Python) como la codificación definitiva.

**Justificación:**
1.  **Correspondencia Física:** El algoritmo de evaluación de energía (`f_powerPlants`) opera iterando sobre la geometría del parque. Tener la estructura 2D intacta evita conversiones constantes durante la fase más costosa del algoritmo (la evaluación de la función objetivo).
2.  **Facilidad de Depuración:** Al inspeccionar un individuo (coral) durante la ejecución, la matriz permite visualizar instantáneamente patrones espaciales (líneas, aglomeraciones) que serían invisibles en un vector plano o una lista de coordenadas.
3.  **Eficiencia en Python:** La librería `NumPy` está altamente optimizada para operaciones matriciales. Operaciones como rotaciones, desplazamientos o máscaras lógicas (usadas en la reproducción) son nativas y extremadamente rápidas en matrices.

## 3.3. Manejo de restricciones

El problema impone una restricción estricta en el número de turbinas ($N_{turb} = 20$ o $50$, dependiendo del escenario). Los operadores genéticos tradicionales (cruce y mutación) suelen violar esta restricción al alterar el número de bits activos. Por ello, se implementaron mecanismos de reparación y preservación específicos.

### 3.3.1. Asegurar exactamente $N$ turbinas en la generación inicial

Al crear la población inicial (el "arrecife"), no se generan matrices puramente aleatorias. En su lugar, se utiliza un algoritmo de permutación para garantizar que cada solución comience siendo válida.

**Pseudocódigo de Generación Inicial:**
```pseudocode
FUNCIÓN Crear_Coral(Dimension_Cuadrícula K, Numero_Turbinas N)
    // 1. Crear un vector plano de ceros del tamaño total (ej. 400)
    Vector_Plano <- Vector_Ceros(K * K)
    
    // 2. Generar índices aleatorios únicos
    Indices_Aleatorios <- Permutación_Aleatoria(0 a K*K - 1)
    
    // 3. Seleccionar los primeros N índices y activarlos
    Indices_Activos <- Indices_Aleatorios[0 : N]
    Vector_Plano[Indices_Activos] <- 1
    
    // 4. Reformar el vector a matriz 2D
    Matriz_Coral <- Reformar(Vector_Plano, (K, K))
    
    RETORNAR Matriz_Coral
FIN FUNCIÓN
```
*Implementación en código (`reef_optimization.py`):* Función `create_grid`.

### 3.3.2. Corrección tras cruce (Reproducción Sexual)

El operador de cruce utilizado es una **Unión Lógica (OR)** de las posiciones de dos padres. Esto tiende a producir hijos con un exceso de turbinas (si los padres tienen turbinas en posiciones diferentes, la suma superará $N$).

Para corregir esto, se aplica un filtro de selección aleatoria negativa (eliminación de sobrantes) para reducir el número de turbinas exactamente al límite permitido.

**Pseudocódigo de Reproducción Sexual con Reparación:**
```pseudocode
FUNCIÓN Reproducción_Sexual(Padre1, Padre2, Max_Turbinas)
    // 1. Cruce por Superposición (OR lógico)
    // Combina todas las turbinas de ambos padres
    Hijo_Combinado <- Padre1 OR Padre2
    
    // 2. Identificar posiciones ocupadas
    Posiciones_Turbinas <- Encontrar_Indices(Hijo_Combinado == 1)
    Cantidad_Actual <- Longitud(Posiciones_Turbinas)
    
    // 3. Reparación de Restricción (Si excede el límite)
    SI Cantidad_Actual > Max_Turbinas ENTONCES
        // Seleccionar aleatoriamente Max_Turbinas para MANTENER
        Indices_A_Conservar <- Selección_Aleatoria(Posiciones_Turbinas, Max_Turbinas)
        
        // Reiniciar hijo y asignar solo las seleccionadas
        Hijo_Combinado <- Matriz_Ceros()
        Hijo_Combinado[Indices_A_Conservar] <- 1
    FIN SI
    
    // Nota: Si Cantidad_Actual < Max_Turbinas (raro en OR), 
    // se podría rellenar, pero el OR garantiza >= turbinas que el padre con más solapamiento.
    
    RETORNAR Hijo_Combinado
FIN FUNCIÓN
```
*Implementación en código (`reef_optimization.py`):* Función `sexual_reproduction`.

### 3.3.3. Corrección en Mutación (Reproducción Asexual)

Para la mutación, en lugar de invertir bits aleatoriamente (lo que alteraría el conteo total), se utiliza un operador de **Movimiento (Swap)**. Este operador selecciona una turbina existente y la mueve a una celda vacía.

Esta estrategia es superior porque es **intrínsecamente conservativa**: mantiene invariantemente el número de turbinas, eliminando la necesidad de una fase de reparación posterior.

**Pseudocódigo de Mutación Preservativa:**
```pseudocode
FUNCIÓN Mutación_Asexual(Individuo)
    Hijo <- Copiar(Individuo)
    Numero_Mutaciones <- Entero_Aleatorio(1, 5) // Intensidad de mutación
    
    PARA i DESDE 1 HASTA Numero_Mutaciones HACER
        // 1. Identificar posiciones
        Posiciones_Turbinas <- Indices_Donde(Hijo == 1)
        Posiciones_Vacias   <- Indices_Donde(Hijo == 0)
        
        SI (No hay turbinas O No hay espacio) CONTINUAR
        
        // 2. Seleccionar turbina a mover (origen) y destino
        Origen  <- Elemento_Aleatorio(Posiciones_Turbinas)
        Destino <- Elemento_Aleatorio(Posiciones_Vacias)
        
        // 3. Ejecutar movimiento (Swap)
        Hijo[Origen]  <- 0  // Apagar origen
        Hijo[Destino] <- 1  // Encender destino
        
        // Actualizar listas locales para la siguiente iteración del bucle
        Actualizar_Listas(Posiciones_Turbinas, Posiciones_Vacias)
    FIN PARA
    
    RETORNAR Hijo
FIN FUNCIÓN
```
*Implementación en código (`reef_optimization.py`):* Función `asexual_reproduction`.

### 3.3.4. Distancia mínima

El manejo de la distancia mínima entre turbinas se realiza de forma implícita a través de la **discretización del espacio**. La cuadrícula de $20 \times 20$ divide el terreno disponible en celdas.

*   Al imponer que solo puede haber una turbina por celda (codificación binaria), se garantiza automáticamente una distancia mínima equivalente al tamaño de la celda.
*   Si la celda representa, por ejemplo, $4D \times 4D$ (donde D es el diámetro del rotor), entonces ninguna turbina estará jamás más cerca de 4 diámetros de otra, cumpliendo las restricciones de seguridad física y reducción de turbulencias sin necesidad de funciones de penalización explícitas o cálculos de distancia euclídea continuos durante la generación.
