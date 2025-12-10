###########################################################################
### Casillas
###########################################################################
import numpy as np
import numpy.polynomial as polynomial

def ppval(piecewise_ploy, array):

    result = None

    array = np.array(array)

    if array.ndim == 0:
        result = ppval_aux(piecewise_ploy, array)
    else:
        #orig_shape = array.shape
        #array = array.flatten()
        result = np.zeros(array.shape)

        for i in range(len(array)):
            result_i = ppval_aux(piecewise_ploy, array[i])
            result[i] = result_i

        #result = result.reshape(orig_shape)
    return result


def ppval_aux(piecewise_ploy, x):
    result = 0
    breaks = piecewise_ploy['breaks']
    coefs = piecewise_ploy['coefs']

    for i in range(len(breaks)-1):
        if x >= breaks[i] and x < breaks[i+1]:
            poly = polynomial.Polynomial(coefs[i,0:4])
            result = poly(x)
            break;
    return result

import time

def powerGen(vmod = None, ppPower = None):
    pwr = np.zeros(vmod.shape)
    #it_l = vmod <= 0
    #it_L = vmod > 12
    #it_in = ~(it_l | it_L)

    it_in = (vmod > 0) & (vmod < 12)

    pwr[vmod <= 0] = 0
    pwr[vmod > 12] = 1200
    #pwr[it_in] = ppval(ppPower,vmod[it_in])
    pwr[it_in] = ppPower(vmod[it_in])

    return pwr
