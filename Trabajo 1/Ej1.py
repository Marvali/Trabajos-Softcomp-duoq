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
arrayP = np.random.uniform(-100, 100, 30)
print("Array generado:", arrayP)
cont = 0
low_fitness = fitness(arrayP)


while fitness(arrayP) > 0.1 and cont < 1000000:
    ruido = np.random.normal(0, 10, 30)



    arrayH = arrayP + ruido
    #print("Array hijo generado:", arrayH)

    if(comparar_fitness(arrayH, arrayP)):
        #print("El array hijo es mejor que el array padre")
        #El hijo pasa a ser el padre
        arrayP = arrayH
        if(fitness(arrayP) < low_fitness):
            low_fitness = fitness(arrayP)
            print("Iteracion numero:"+str(cont)+" Nuevo mejor fitness:", low_fitness)
            
    cont += 1
        
        
   
    
    
      
        
        
   
    

print("mejor fitness encontrado:", low_fitness)
       
        



 


