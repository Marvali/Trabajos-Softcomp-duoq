###########################################################################
### Code
###########################################################################
import numpy as np
import matplotlib.pyplot as plt
clear('all')
close_('all')
# Pts
D = np.array([[4.73,97.2],[5.27,107.2],[5.76,162.5],[6.33,203.8],[6.76,259.2],[7.26,340.4],[7.72,431.7],[8.26,538.6],[8.75,628.7],[9.24,739.4],[9.72,848.0],[10.25,968.4],[10.73,1084.3],[11.25,1144.8],[11.74,1167.3],[12.27,1177.9],[12.77,1188.3],[13.49,1186.4],[14.56,1182.6],[15.42,1173.6],[16.48,1168.7],[17.29,1184.4],[18.31,1179.3]])
D2 = np.array([[np.arange(13,20+1)],[1200 * np.ones((1,8))]])
D1 = np.array([[np.arange(0,4+1)],[np.zeros((1,5))]])
xq = np.arange(0,20+1)
ind = np.find(D[:,1] < 13)
ptsTrns = D(ind,1)
p = polyfit(ptsTrns,D(ind,2),7)
ppPower = pchip(np.array([D1[1,:],D[1,:],D2[1,:]]),np.array([D1[2,:],D[2,:],D2[2,:]]))
y1 = polyval(p,ptsTrns)
#save('dt/pwrCurve.mat','ppPower')
### uncoment to see
#figure
#plt.plot(D(:,1),D(:,2),'ro')
#grid('on')
#hold('on')
#plt.plot(ptsTrns,D(ind,2),'bo')
#plt.plot(D(ind,1),y1,'b*-')
# plot(xq,ppval(ppPower,xq),'m-');
###
