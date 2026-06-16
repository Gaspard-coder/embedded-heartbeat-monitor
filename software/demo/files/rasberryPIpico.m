clear
close all
device=serialport("/dev/ttyACM0",115200);
Npt=10e3; %number of points of the acquisition 
nbits_ADC=16;
FS_ADC=3.3; %Full scale 
fs_ADC=1e3; %sampling frequency ADC
t=0:1/fs_ADC:(Npt-1)/fs_ADC; %time vector
data_raw=read(device,7*Npt,"string");
data=str2num(data_raw)/2^nbits_ADC*FS_ADC-FS_ADC/2; %Converting from a digital output to the analog equivalent
data(data>FS_ADC/2)=FS_ADC/2;
data(data<-FS_ADC/2)=-FS_ADC/2;
data=data(1:length(t));
plot_spectrum(data-mean(data),1,fs_ADC);
clear("device")
sndr=perf_estim(data-mean(data),1,0,15,1);   

disp(['The SNDR is ', num2str(sndr),' dB']) 

figure()
plot(t,data,'linewidth',2)
xlabel('time(s)')
ylabel('ADC output (V)')
set(gca,'fontsize', 24)
