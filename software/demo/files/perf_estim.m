function [SNDR,SFDR,SNR,STHD,HD3,HD2,PS]= perf_estim(y,pb,k,n,OSR)
% y is the time signal
% if pb>0 the signal is low pass, if not it is high pass
%k is the bin of the input signal, if  k=0  the function detects the maximum and considers it as the input 
%n number of points around the  peak 
% OSR is the oversampling ratio


%SNDR is signal to noise and distortions ratio
%SFDR is spruouis free dynamic range
%SNR is signal to noise  ratio
%STHD is signal to total harmonic distortions ratio
%HD3 is signal to third harmonic ratio
%HD2 is signal to second harmonic ratio
%PS is the signal power


    size_y= size(y);
    if size_y(1)>1 
        y=y';
    end           %putting the vector as lign vector if it is a column vector
    

   c=round(length(y)/2/OSR);
   N=(length(y));
   w = black(N);                                         %windowing
   U = (1/N)*sum(abs(w).^2);
   w= (1/((N*U)^(1/2)))*w'*sqrt(3.504957918618154);      %Window Normalization 
    
   
   
  tfy=fft(w.*y)/sqrt(N);

  % choosing the spectrum band depending if it is HP or LP
  if (pb>0)
    tfy=tfy(1:c);
  else if (pb<0)
    tfy=tfy(length(y)/2:-1:length(y)/2-c);
  end
  end
   
    
  Ptfy=tfy.*conj(tfy);


  if (k==0)
    [maxim,k]=max(abs(Ptfy)); 
   else
     maxim=abs(Ptfy(k));
  end

  lim_low=max(k-n,3);
  lim_max=min(k+n,c);
  PS=sum(Ptfy(lim_low:lim_max));  %signal power calculation
  PND=sum(Ptfy(3:c))-PS+(2*n+1)*0.5*(Ptfy(lim_low-1)+Ptfy(lim_max+1));          %noise and distortions calculations
 
 
  PN=PND;
  harm=0;
  for i=2*k:k:c-1
   harm(round(i/k)-1)=sum(Ptfy(i-3:min(i+3,c)));
   harm(round(i/k)-1) =harm(round(i/k)-1)-3.5*(Ptfy(i-4)+Ptfy(min(i+4,c)));%replacing the tone by the noise
  end
 
  for i=1:length(harm)
    PN=PN-harm(i);
  end
  
   
   
  Spec_withoutsignal=[0,0,Ptfy(3:lim_low-n),zeros(1,lim_max-lim_low-1+2*n),Ptfy(lim_max+n:c)];
  %Spec_withoutsignal=[zeros(1,round(1.8*k)),Ptfy(round(1.8*k)+1:c)];
 n=0;
  [maxim2,ind_maxim2] = max(Spec_withoutsignal);

  Highestpeak=sum(Ptfy(max(ind_maxim2-n,2):min(ind_maxim2+n,c)));

  
  SNDR=10*log10(PS/PND);
  SFDR=10*log10(PS/Highestpeak);
  SNR=10*log10(PS/PN);



  if length(harm)==1
    HD2=0; 
    STHD=0;
    HD3=0;
  else if length(harm)==2
    HD3=0;
    HD2=10*log10(PS/harm(1));
    STHD=10*log10(PS/sum(harm(1:length(harm))));
  else 
    HD3=10*log10(PS/harm(2));
    HD2=10*log10(PS/harm(1));
    STHD=10*log10(PS/sum(harm(1:length(harm))));
  end
 end


end
