```
Inicializar Poblacion de tamaño mu (10)
Evaluar fitness inicial
sigma = 30

MIENTRAS (mejor_fitness > 0.001) Y (contador < 200000) HACER:
    Descendencia = []
    
    // Generación de hijos
    PARA i desde 1 hasta lambda (30) HACER:
        padre_idx = Elegir_Aleatorio(0, mu)
        ruido = RandomNormal(0, sigma)
        hijo = Poblacion[padre_idx] + ruido
        Descendencia.anadir(hijo)
    FIN PARA
    
    // Selección (mu + lambda)
    Poblacion_Total = Poblacion + Descendencia
    Ordenar Poblacion_Total por fitness (ascendente)
    Poblacion = Tomar los 'mu' primeros de Poblacion_Total
    
    Actualizar mejor_fitness global
    
    // Ajuste dinámico de varianza
    SI (contador % 1000 == 0) ENTONCES:
        sigma = sigma * 0.9
    FIN SI
    
    Incrementar contador
FIN MIENTRAS
```
