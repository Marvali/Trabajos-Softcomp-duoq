#funcion que calcule la funcion de fitness f(x) = sum(xi^2) para un array de numeros decimales
def fitness(array):
    fx = 0
    for i in range(len(array)):
        fx += array[i]**2
    return fx

#otra forma de hacerlo usando numpy
'''
def fitness_numpy(array):
    # Suma de todos los elementos del array al cuadrado
    return np.sum(array**2)
'''

#funcion para comparar los dos fitness
def comparar_fitness(array1, array2):
    f1 = fitness(array1)
    f2 = fitness(array2)
    if f1 < f2:
        return True
    elif f2 < f1:
        return False
    else:
        return True
    

#Generar un array de 30 numeros decimales aleatorios entre -100 y 100

import numpy as np
import matplotlib.pyplot as plt

arrayP = np.random.uniform(-100, 100, 30)
print("Array generado para (1+1)-ES:", arrayP)
cont = 0
low_fitness = fitness(arrayP)
desviacion = 30
hist_11_es = [low_fitness]


while fitness(arrayP) > 0.001 and cont < 200000: #precision y maximo de iteraciones
    # Generamos ruido con media 0, desviación estándar variable, y tamaño fijo de 30
    ruido = np.random.normal(0, desviacion, 30)



    arrayH = arrayP + ruido
    #print("Array hijo generado:", arrayH)

    if(comparar_fitness(arrayH, arrayP)):
        #print("El array hijo es mejor que el array padre")
        #El hijo pasa a ser el padre
        arrayP = arrayH
        if(fitness(arrayP) < low_fitness):
            low_fitness = fitness(arrayP)
            print("Iteracion numero:"+str(cont)+" Nuevo mejor fitness (1+1)-ES:", low_fitness)
            
    #ir volviendo la desviacion mas alta conforme avanzan las iteraciones
    if cont % 1000 == 0 and cont != 0:
        desviacion = desviacion * 0.9
    
    hist_11_es.append(low_fitness)
            
    cont += 1
        

print("Mejor fitness encontrado con (1+1)-ES:", low_fitness)



#Estrategia (lambda + theta)-ES
lambda_padres = 10
theta_hijos = 30
desviacion_lambda = 90

poblacion = [np.random.uniform(-100, 100, 30) for _ in range(lambda_padres)]
fitness_poblacion = [fitness(ind) for ind in poblacion]
mejor_lambda = min(fitness_poblacion)
hist_lambda_theta = [mejor_lambda]

cont_lambda = 0
while mejor_lambda > 0.001 and cont_lambda < 200000:
    descendencia = []
    for _ in range(theta_hijos):
        padre_idx = np.random.randint(0, lambda_padres)
        ruido = np.random.normal(0, desviacion_lambda, 30)
        hijo = poblacion[padre_idx] + ruido
        descendencia.append(hijo)
    
    poblacion_total = poblacion + descendencia
    fitness_total = [fitness(ind) for ind in poblacion_total]
    
    #Seleccion de los mejores lambda individuos
    orden_mejores = np.argsort(fitness_total)[:lambda_padres]
    poblacion = [poblacion_total[i] for i in orden_mejores]
    fitness_poblacion = [fitness_total[i] for i in orden_mejores]
    if fitness_poblacion[0] < mejor_lambda:
        mejor_lambda = fitness_poblacion[0]
        print("Iteracion numero:"+str(cont_lambda)+" Nuevo mejor fitness (lambda+theta)-ES:", mejor_lambda)

    if cont_lambda % 1000 == 0 and cont_lambda != 0:
        desviacion_lambda = desviacion_lambda * 0.9
    
    hist_lambda_theta.append(mejor_lambda)
    cont_lambda += 1

print("Mejor fitness encontrado con (lambda+theta)-ES:", mejor_lambda)


#Grafica comparativa
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)

ax1.plot(hist_11_es, label="(1+1)-ES")
ax1.plot(hist_lambda_theta, label="(lambda+theta)-ES")
ax1.set_ylabel("Fitness (global)")
ax1.set_title("Evolucion del fitness por generacion")
ax1.legend()
ax1.grid(True)

ax2.plot(hist_11_es, label="(1+1)-ES")
ax2.plot(hist_lambda_theta, label="(lambda+theta)-ES")
ax2.set_xlabel("Generaciones")
ax2.set_ylabel("Fitness (zoom 0-1)")
ax2.set_ylim(0, 1)
ax2.grid(True)

plt.tight_layout()
plt.show()


