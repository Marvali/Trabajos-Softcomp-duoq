
```python
Inicializar arrayP aleatoriamente entre [-100, 100]
Evaluar fitness_actual = f(arrayP)
sigma = 30
contador = 0

MIENTRAS (fitness_actual > 0.001) Y (contador < 200000) HACER:
    1. Generar ruido gaussiano: ruido = RandomNormal(media=0, desv=sigma)
    2. Crear hijo: arrayH = arrayP + ruido
    3. Evaluar hijo: fitness_hijo = f(arrayH)
    
    4. Selección (supervivencia del mejor):
       SI fitness_hijo < fitness_actual ENTONCES:
           arrayP = arrayH
           fitness_actual = fitness_hijo
       FIN SI

    5. Ajuste dinámico de parámetros (Heurística propia):
       CADA 1000 iteraciones:
           sigma = sigma * 0.9  // Reducimos el rango de búsqueda
           
    6. Incrementar contador
FIN MIENTRAS


```