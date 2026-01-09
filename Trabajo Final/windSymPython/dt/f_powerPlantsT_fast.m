function [pwr_T,gan_T,cost_T,obj_T] = f_powerPlantsT_fast(vVec,gr)
% Inputs: vVec: Vectores Directores (single) del Viento en Coordenadas Cartesianas.
%         gr:   Matriz Cuadrada con 0s y 1s que representa la localización
%               de los generadores 
% Ouputs: pwr_t: Potencia Total
%         pwrGen: Potencia Individual por Generador
%         Ux: Viento en cada Generador
%         gan: Precio (KW) * Potencia Total
%         cost: Coste de las Turbinas
%         obj: cost / gan
load('dt/pwrCurve.mat');

Nturb = sum(gr,'all');
nH     = size(vVec,2);
pwr_T  = zeros(1,nH);
gan_T  = zeros(1,nH);
cost_T = zeros(1,nH);
obj_T  = zeros(1,nH);

%Select Wind Dir from vVec
avVec = atan2(vVec(2,:),vVec(1,:));
[angVec, ia, ic] = uniquetol(avVec,1e-15);

rUDef_T = zeros(Nturb,Nturb,nH);
for l=1:length(angVec)
    rUDef = f_powerPlants_f1(vVec(:,ia(l)),gr);
    rUDef_T(:,:,ic==l) = repmat(rUDef,1,1,sum(ic==l));
end

for l=1:nH
    [pwr_t,~,~,gan,cost,obj] = f_powerPlants_f2(vVec(:,l),gr,ppPower,rUDef_T(:,:,l));   % Vector + Logical Matrix
    pwr_T(l)  = pwr_t;
    gan_T(l)  = gan;
    cost_T(l) = cost;
    obj_T(l)  = obj;
end
pwr_T = sum(pwr_T,'all');
gan_T = sum(gan_T,'all');
cost_T = sum(cost_T,'all');
obj_T = sum(obj_T,'all');
end