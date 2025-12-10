import numpy as np
import math
from windSymPython.polygon import Polygon


#def inpolygon(points, poly):
    #return [[p.x, p.y] for p in filter(lambda x: poly.covers(x), point_list)]
#    return [poly.contains(Point(p)) for p in points]

def rot_mat(theta):
    return np.array([[np.cos(theta), -np.sin(theta)],[np.sin(theta),np.cos(theta)]])

def f_powerPlants_f1(vVec,gr,Nturb):
    # Inputs: vVec: Vector Director (single) del Viento en Coordenadas Cartesianas.
    #         gr:   Matriz Cuadrada con 0s y 1s que representa la localización
    #               de los generadores
    # Ouputs: pwr_t: Potencia Total
    #         pwrGen: Potencia Individual por Generador
    #         Ux: Viento en cada Generador
    #         gan: Precio (KW) * Potencia Total
    #         cost: Coste de las Turbinas
    #         obj: cost / gan

    vMod = np.linalg.norm(vVec, axis = 0)
    vDir = vVec / vMod

    #Nturb = gr.sum()
    Kgr = gr.shape[0]
    R = 40
    D = 2 * R
    dSec = 5

    rang = np.arange(1, dSec*D*Kgr, dSec*D)
    secScale = dSec*D*(Kgr-1)+2

    grPosX, grPosY = np.meshgrid(rang, rang)
    secGR = np.array([[0, 0, secScale, secScale, 0],[0, secScale, secScale, 0, 0]])

    #dmaxGR = np.sqrt(2*(dSec*D*Kgr)**2) * 1.1
    dmaxGR = math.sqrt(2)*abs(dSec*D*Kgr)*1.1

    ## Ráfaga
    Z = 60
    Z0 = 0.3
    alf = 0.5 / np.log(Z/Z0)
    a = np.arctan(alf)

    ## Detect Turbins
    turPos = np.array([grPosY, grPosX])[:,gr.T == 1]

    # For each Time
    v1 = np.matmul(rot_mat(a), vDir)
    v2 = np.matmul(rot_mat(-a), vDir)
    rUDef = np.zeros((Nturb,Nturb))

    # Rafagas
    #poly1 = Polygon(secGR.T) #poly1 = polyshape(secGR[1,:],secGR[2,:])

    M1 = rot_mat(np.pi/2)
    M2 = rot_mat(-np.pi/2)

    new_vDir1 =  R * np.matmul(M1, vDir)
    new_vDir2 =  R * np.matmul(M2, vDir)

    for m in np.arange(Nturb):
        # Recorremos todos los pares
        b1 = turPos[:,m] + new_vDir1
        b2 = turPos[:,m] + new_vDir2

        b1_f = b1 + dmaxGR * v1
        b2_f = b2 + dmaxGR * v2

        stlCon = np.vstack([b1, b1_f, b2_f, b2, b1]).T

        # Intersection
        polyout = Polygon(stlCon) #poly2 = polyshape(stlCon[1,:],stlCon[2,:])
        #polyout = Path(stlCon.T)

        # Query I
        Qpts = np.delete(np.arange(Nturb), m)

        #in_ = inpolygon(turPos[:,Qpts].T, polyout)
        in_ = polyout.covers(turPos[:,Qpts])
        #in_ = polyout.contains_points(turPos[:,Qpts].T)

        if np.count_nonzero(in_) > 0:

            dTur = turPos[:,Qpts[in_]] - turPos[:,[m]]
            x1 = np.abs(np.matmul(dTur.T,vDir))
            in_ = np.concatenate([in_, [False]])
            rUDef[m,in_] = x1.T

    return rUDef
