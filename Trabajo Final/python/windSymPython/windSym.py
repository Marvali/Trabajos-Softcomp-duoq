#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 26 19:46:29 2021

@author: cosminmarina
"""
import numpy as np
import scipy
import scipy.io
from f_powerPlantsT_fast import f_powerPlantsT_fast
from f_powerPlantsT_fast import uniquetol
from f_powerPlants_f1 import f_powerPlants_f1
from scipy.io import loadmat
WindSym_1 = loadmat('../windSym/dt/WindSym_1.mat')
loadmat('../windSym/dt/pwrCurve.mat')

Nturb=20
Kgr=20

gr = [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0],
      [0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,1],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0],
      [0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
      [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]

[pwr_T2,gan_T2,cost_T2,obj_T2] = f_powerPlantsT_fast(WindSym_1['vVec'],np.copy(gr));

print('Potencia Total de %d Turbinas dispuestas aleatoriamente en un grid de %dx%d durante 1 año de simulación:\n'% (Nturb,Kgr,Kgr));
print(pwr_T2)

#
#vVec=WindSym_1['vVec']
#avVec = np.arctan2(vVec[1,:],vVec[0,:])
#angVec, ia, ic = uniquetol(avVec,1e-15)
#ic = np.array(ic).flatten()
#ia = np.array(ia).flatten()
#rUDef = f_powerPlants_f1(vVec[:, ia[0]], np.copy(gr))