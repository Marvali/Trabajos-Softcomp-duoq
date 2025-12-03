function [pwr_t,pwrGen,Ux,gan,cost,obj] = f_powerPlants_f2(vVec,gr,ppPower,rUDef)
% Inputs: vVec: Vector Director (single) del Viento en Coordenadas Cartesianas.
%         gr:   Matriz Cuadrada con 0s y 1s que representa la localización
%               de los generadores 
% Ouputs: pwr_t: Potencia Total
%         pwrGen: Potencia Individual por Generador
%         Ux: Viento en cada Generador
%         gan: Precio (KW) * Potencia Total
%         cost: Coste de las Turbinas
%         obj: cost / gan

vMod = sqrt(vVec'*vVec);                % Mod
Nturb = sum(gr,'all');
R = 40;

%% Ráfaga
Z = 60; Z0 = 0.3;
alf = 0.5 / log(Z/Z0);
CT = 0.88;

%% Price and Cost
prTW = 75/1e3; % Euros/ KW


% For each Time
Ux =  zeros(1,Nturb); Udef = Ux;
for m=1:Nturb
    if sum(rUDef(:,m))>0
        Udef(m) = sqrt( sum( ((R^2*(1-sqrt(1-CT)))./(R+alf*rUDef(rUDef(:,m)>0,m)).^2).^2));
        Ux(m)=vMod*(1-Udef(m));
%             Udef(m) = R^2*(1-sqrt(1-CT)) ./ sqrt(sum((R + alf*rUDef(rUDef(:,m)>0,m)).^4));
%             Ux(m) = vMod(l)*(1 - R^2*(1-sqrt(1-CT)) ./ sqrt(sum((R + alf*rUDef(rUDef(:,m)>0,m)).^4)));
    else
        Ux(m) = vMod;
%             Ux1(m) = vMod(l);
    end
end
pwrGen = powerGen(Ux,ppPower);
pwr_t = sum(pwrGen);
gan = prTW*pwr_t;
cost = Nturb*(2/3 - 1/3*exp(-0.0017*Nturb^2));
obj = cost/(gan+0.001);
end