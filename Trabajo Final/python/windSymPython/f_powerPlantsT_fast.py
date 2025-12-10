import numpy as np
import numpy.matlib
from matplotlib import pyplot as plt
import scipy.io
from scipy.interpolate import PPoly
from windSymPython.f_powerPlants_f1 import f_powerPlants_f1
from windSymPython.f_powerPlants_f2 import f_powerPlants_f2
import time
from pathlib import Path


def uniquetol(array, tol):
    tol = tol * np.max(np.abs(array))
    array_copy = np.sort(np.copy(array))
    result = [array_copy[0]]
    # hallamos el resultado de unique con toloreancia tol
    for i in range(len(array_copy)-1):
        if np.abs(array_copy[i+1]-result[-1]) >= tol:
            result.append(array_copy[i+1])
    # hallamos ia como los indices de cada elemento de result en array
    # se usa where porque array es un numpy.darray y no tiene .index()
    ia = []
    for elem in result:
        indice_ia = np.where(np.abs(array-elem)<=tol)[0][0]
        ia.append(indice_ia)
    # hallamos ic como los indices de cada elemento de array en result
    ic = []
    result_copy=np.copy(result)
    for valor in array:
        indice_ic = np.where(np.abs(result_copy-valor)<=tol)[0][0]
        ic.append(indice_ic)
    return result, ia, ic
# PARA PROBAR EL UNIQUETOL pega en la consola de comandos las siguientes lineas:
#ej = [1,2,3,4,5,6,1,2,3,4.5]
#ej2 = np.copy(ej)
#uniquetol(ej2,1e-15)

def f_powerPlantsT_fast(vVec,gr):
    # Inputs: vVec: Vectores Directores (single) del Viento en Coordenadas Cartesianas.
    #         gr:   Matriz Cuadrada con 0s y 1s que representa la localización
    #               de los generadores
    # Ouputs: pwr_t: Potencia Total
    #         pwrGen: Potencia Individual por Generador
    #         Ux: Viento en cada Generador
    #         gan: Precio (KW) * Potencia Total
    #         cost: Coste de las Turbinas
    #         obj: cost / gan
    path = str(Path(__file__).resolve().parent) + "/"
    mat_data = scipy.io.loadmat(path + 'dt/pwrCurve.mat')
    ppPower_aux = mat_data['ppPower'][0,0]
    ppPower = PPoly(ppPower_aux[2].T, ppPower_aux[1].flatten())

    Nturb = gr.sum()
    nH = vVec.shape[1]
    pwr_T = np.zeros(nH) # nH instead of (1,nH)
    gan_T = np.zeros(nH)
    cost_T = np.zeros(nH)
    obj_T = np.zeros(nH)

    #Select Wind Dir from vVec
    avVec = np.arctan2(vVec[1,:],vVec[0,:])
    angVec, ia, ic = uniquetol(avVec,1e-15)
    ic = np.array(ic)
    ia = np.array(ia)
    rUDef_T = np.zeros((Nturb,Nturb,nH))
    # ALL GOOD UNTILL HERE

    for l in np.arange(len(angVec)):
        rUDef = f_powerPlants_f1(vVec[:, ia[l]], gr, Nturb)
        rUDef_T[:,:,ic == l] = np.tile(rUDef[:, :, None], [1, 1, np.count_nonzero(ic == l)])


    for l in np.arange(nH):
        pwr_t,__,__,gan,cost,obj = f_powerPlants_f2(vVec[:,l],gr,ppPower,rUDef_T[:,:,l],Nturb)
        pwr_T[l] = pwr_t
        gan_T[l] = gan
        cost_T[l] = cost
        obj_T[l] = obj

    pwr_T = pwr_T.sum()
    gan_T = gan_T.sum()
    cost_T = cost_T.sum()
    obj_T = obj_T.sum()
    return pwr_T, gan_T, cost_T, obj_T


def sanity_check():
    size = [20, 20]
    n_windmills = 20
    #vVec = np.array([[-1,-1], [0,-1], [-1, 0]]).T
    vVec = np.random.rand(2, 250)*40 - 20
    #vVec = vVec/np.linalg.norm(vVec, axis=0)

    gr = np.array([1] * n_windmills + [0] * (size[0]*size[1] - n_windmills))
    np.random.shuffle(gr)

    gr = gr.reshape([20,20])

    solution = f_powerPlantsT_fast(vVec, gr)
    print(solution)

def test1():
    size = [20, 20]
    n_windmills = 20

    mat_data = scipy.io.loadmat('dt/WindSym_1.mat')
    vVec = mat_data['vVec']

    gr = np.array([1] * n_windmills + [0] * (size[0]*size[1] - n_windmills))
    #gr = np.zeros(size, dtype=np.int32)
    #gr[0,:] = 1
    #np.random.shuffle(gr)

    gr = gr.reshape(size)
    print(gr)

    start = time.time()
    solution = f_powerPlantsT_fast(vVec, gr)
    end = time.time()

    print(solution)
    print(f"execution time: {(end-start)}")

def ppval_test():
    mat_data = scipy.io.loadmat('dt/pwrCurve.mat')
    ppPower_aux = mat_data['ppPower'][0,0]
    ppPower = {"breaks":ppPower_aux[1].flatten(), "coefs":np.flip(ppPower_aux[2],1)}
    ppPower = PPoly(ppPower_aux[2].T, ppPower_aux[1].flatten())
    print(dir(ppPower))

    from powerGen import ppval
    x = np.linspace(0,100,10000)
    #y = ppval(ppPower, x)
    y = ppPower(x)
    plt.plot(x,y)
    plt.show()


if __name__ == '__main__':
    #sanity_check()
    test1()
    #ppval_test()
