%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% WinSym Code
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
clear all; close all; clc;
addpath('utils/');addpath('dt/')
load('dt/pwrCurve.mat');

%% Load Data
load('WindSym_1.mat');

%% Kgr Grid with Nturb Turbines
Kgr = 20;   % Tamaño del Grid
Nturb = 20; % Numero de Turbinas

% For Each Time
gr = zeros(Kgr); gr(randperm(Kgr^2,Nturb)) = 1;     % Gen Nturb in a grid of Kgr x Kgr

tic
[pwr_T2,gan_T2,cost_T2,obj_T2] = f_powerPlantsT_fast(vVec,gr);
toc
fprintf('Potencia Total de %d Turbinas dispuestas aleatoriamente en un grid de %dx%d durante 1 año de simulación\n',Nturb,Kgr,Kgr);
pwr_T2