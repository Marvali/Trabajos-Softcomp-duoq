function rUDef = f_powerPlants_f1(vVec,gr)
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
vDir = vVec/vMod;          % Dir

Nturb = sum(gr,'all'); Kgr = size(gr,1);

R = 40; D = 2*R; dSec = 5;
[grPosX,grPosY] = meshgrid(1:dSec*D:dSec*D*Kgr,1:dSec*D:dSec*D*Kgr);
secGR = [0,0,dSec*D*(Kgr-1)+2,dSec*D*(Kgr-1)+2,0;0,dSec*D*(Kgr-1)+2,dSec*D*(Kgr-1)+2,0,0];
dmaxGR = sqrt(2*(dSec*D*Kgr)^2)*1.1;


%% Ráfaga
Z = 60; Z0 = 0.3;
alf = 0.5 / log(Z/Z0); a = atan(alf);

%% Detect Turbins

turPosX = grPosX(gr==1);
turPosY = grPosY(gr==1);

% For each Time
v1 = [cos(a) -sin(a);sin(a) cos(a)]*vDir;
v2 = [cos(-a) -sin(-a);sin(-a) cos(-a)]*vDir;
rUDef = zeros(Nturb);

% Rafagas
poly1 = polyshape(secGR(1,:),secGR(2,:));
M1 = [cos(pi/2) -sin(pi/2);sin(pi/2) cos(pi/2)];
M2 = [cos(-pi/2) -sin(-pi/2);sin(-pi/2) cos(-pi/2)];

for m=1:Nturb
    % Recorremos todos los pares
    b1 = [turPosX(m);turPosY(m)] + R * M1 * vDir;
    b2 = [turPosX(m);turPosY(m)] + R * M2 * vDir;
    b1_f = b1 + dmaxGR*v1; b2_f = b2 + dmaxGR*v2;
    stlCon = [b1(1),b1_f(1),b2_f(1),b2(1),b1(1);b1(2),b1_f(2),b2_f(2),b2(2),b1(2)];

    % Intersection
    poly2 = polyshape(stlCon(1,:),stlCon(2,:));
%     poly2 = poly2_0; poly2.Vertices = poly2.Vertices+[turPosX(m),turPosY(m)];
%     polyout = intersect(poly1,poly2);
    polyout = poly2;

    % Query I
    Qpts = setdiff(1:Nturb,m);

    [in,on] = inpolygon(turPosX(Qpts,:),turPosY(Qpts,:),polyout.Vertices(:,1),polyout.Vertices(:,2));
    in = in | on;
%   %% Picture
%         figure; plot(secGR(1,:),secGR(2,:),'ro-');hold on;
%         plot(stlCon(1,:),stlCon(2,:),'bo-');plot(poly1); plot(poly2); plot(polyout);
%         plot(b1(1),b1(2),'ro'); plot(b2(1),b2(2),'ro'); plot(turPosX(m),turPosY(m),'bo')
%         plot(turPosX,turPosY,'g*'); plot(polyout.Vertices(:,1),polyout.Vertices(:,2),'m*')
%         quiver(turPosX(m),turPosY(m),vDir(1),vDir(2)); axis equal;
%   %%

    if sum(in)> 0
        dTur = [turPosX(Qpts(in),:)';turPosY(Qpts(in),:)'] - [turPosX(m);turPosY(m)];
        x1 = abs(dTur'*vDir);
        rUDef(m,in) = x1';
    end
end
end