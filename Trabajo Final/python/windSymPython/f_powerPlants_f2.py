import numpy as np

def powerGen(vmod, ppPower):
    pwr = np.zeros(vmod.shape)
    it_l = vmod <= 0
    it_L = vmod > 12
    it_in = ~(it_l | it_L)
    pwr[it_l] = 0
    pwr[it_L] = 1200
    pwr[it_in] = ppPower(vmod[it_in])
    return pwr

def f_powerPlants_f2(vVec,gr,ppPower,rUDef,Nturb):
    # Inputs: vVec: Vector Director (single) del Viento en Coordenadas Cartesianas.
    #         gr:   Matriz Cuadrada con 0s y 1s que representa la localización
    #               de los generadores
    # Ouputs: pwr_t: Potencia Total
    #         pwrGen: Potencia Individual por Generador
    #         Ux: Viento en cada Generador
    #         gan: Precio (KW) * Potencia Total
    #         cost: Coste de las Turbinas
    #         obj: cost / gan

    vMod = np.linalg.norm(vVec)

    #Nturb = gr.sum()
    R = 40
    ## Ráfaga
    Z = 60
    Z0 = 0.3
    alf = 0.5 / np.log(Z/Z0)
    CT = 0.88
    ## Price and Cost
    prTW = 75 / 1000.0

    # For each Time
    Ux = np.zeros(Nturb)
    Udef = Ux

    for m in np.arange(Nturb):
        if rUDef[:,m].sum() > 0:
            #var1 = R ** 2 * (1 - np.sqrt(1 - CT))
            #var2 = (R + alf * rUDef[rUDef[:,m] > 0,m])**2
            #div_squared = (var1/var2)**2
            var1 = R*R * (1 - np.sqrt(1 - CT))
            var2 = (R + alf * rUDef[rUDef[:,m] > 0,m])**2
            div_squared = (var1*var1)/(var2*var2)
            Udef[m] = np.sqrt(div_squared.sum())
            Ux[m] = vMod * (1 - Udef[m])
        else:
            Ux[m] = vMod

    pwrGen = powerGen(Ux,ppPower)
    pwr_t = pwrGen.sum()
    gan = prTW * pwr_t
    cost = Nturb * (2-np.exp(-0.0017 * Nturb ** 2))/3 # good
    obj = cost / (gan + 0.001)

    return pwr_t, pwrGen, Ux, gan, cost, obj
