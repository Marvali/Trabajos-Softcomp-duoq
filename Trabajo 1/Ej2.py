
import numpy as np




#clase individuo con su array  generado aleatoriamente (1000 numeros al azar que sean 0 o 1)
class Individuo:
    def __init__(self, longitud=1000, array=None):
        if array is not None:
            self.array = array
        else:
            self.array = np.random.randint(2, size=longitud)
        self.num_unos = np.sum(self.array)
        self.probabilidad_seleccion = 0.0
        
    def contar_unos(self):
        self.num_unos = np.sum(self.array)

def asignar_probabilidades_ranking_lineal(poblacion, S=1.5):
    # Ordenar la poblacion por numero de unos de mayor a menor
    poblacion.sort(key=lambda ind: ind.num_unos, reverse=True)
    
    N = len(poblacion)
    
    # Asignar probabilidades basadas en el ranking
    for i in range(N):
        # Fórmula de ranking lineal: P(i) = (2-S)/N + 2(S-1)(N-1-i)/(N(N-1))
        prob = (2 - S) / N + (2 * (S - 1) * (N - 1 - i)) / (N * (N - 1))
        poblacion[i].probabilidad_seleccion = prob

def seleccionar_y_cruzar(poblacion):
    # Extraer probabilidades de la población actual
    probabilidades = [ind.probabilidad_seleccion for ind in poblacion]
    
    # Seleccionar 200 índices de padres (100 parejas) basándose en la probabilidad
    indices_padres = np.random.choice(len(poblacion), size=200, p=probabilidades)
    
    hijos = []
    # Iterar de 2 en 2 para formar parejas
    for i in range(0, 200, 2):
        padre1 = poblacion[indices_padres[i]]
        padre2 = poblacion[indices_padres[i+1]]
        
        # Punto de cruce aleatorio (entre 1 y longitud-1 para asegurar cruce)
        punto = np.random.randint(1, len(padre1.array))
        
        # Cruce de un punto: Hijo  toma al azar la parte izquierda de uno de los padres y la derecha del otro
        if np.random.rand() < 0.5:
            array_hijo = np.concatenate((padre1.array[:punto], padre2.array[punto:]))
            
        else:
            array_hijo = np.concatenate((padre2.array[:punto], padre1.array[punto:]))
            
        
        hijos.append(Individuo(array=array_hijo))
        
        
    return hijos

        
#crear array de 100 individuos
poblacion = [Individuo() for _ in range(100)]
mejor_individuo = max(poblacion, key=lambda ind: ind.num_unos)
cont = 0

while mejor_individuo.num_unos < 1000 and cont < 5000: 
    
    # Ordenar y asignar probabilidades
    asignar_probabilidades_ranking_lineal(poblacion)
    PoblacionH = seleccionar_y_cruzar(poblacion)
    
    #TODO: añadir el ruido (MUTACIONES)
    for individuo in PoblacionH:
        for i in range(len(individuo.array)):
            if np.random.rand() < 0.001:  # Probabilidad de mutación del 0.1%
                individuo.array[i] = 1 - individuo.array[i]  # Cambiar 0 a 1 o 1 a 0
        individuo.contar_unos()  # Recalcular el número de unos después de la mutación

    
    #mirar el mejor individuo de PoblacionH
    PoblacionH.sort(key=lambda ind: ind.num_unos, reverse=True)
    
    if(PoblacionH[0].num_unos > mejor_individuo.num_unos):
        mejor_individuo = PoblacionH[0]
        print("Iteracion:", cont, " Nuevo mejor individuo con numero de unos:", mejor_individuo.num_unos)
    
    
    poblacion  = PoblacionH
    
    cont +=1
    

        
    # ... resto del algoritmo genetico ...
     # Romper para evitar bucle infinito mientras desarrollas
    
    
    










 
