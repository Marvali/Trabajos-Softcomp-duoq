%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% Casillas
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function pwr = powerGen(vmod,ppPower)
    pwr = zeros(size(vmod));
    it_l = vmod<=0; it_L = vmod>12; it_in = ~(it_l|it_L);
    pwr(it_l)  = 0;
    pwr(it_L)  = 1200;
    pwr(it_in) = ppval(ppPower,vmod(it_in));
end