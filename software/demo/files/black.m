function w=black(N)  
alpha=0.16;
a0=(1-alpha)/2;
a1=0.5;
a2=alpha/2;

n=1:N;

w=a0 - a1* cos( 2 *pi*n/(N-1)) + a2*cos( 4*pi* n*(N-1));
w=w';
   