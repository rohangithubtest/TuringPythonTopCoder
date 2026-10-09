## Prompt given to qwen
given a bathtub -  
given a number of taps as input ( <= 10)  
given an initial acceleration and velocity for each tap  
given after 30 secs intervals, the acceleration changes to 0.9 the old one  
given the tap stops after 60 secs  
given 3 taps run at any given time  
given the sequence of taps is fixed (in FIFO fashion) - an input to the system with all taps mentioned  
for example -  
tap1, tap2, tap3, tap4...  
in that case -  
seq1 = tap1, tap2, tap3),  
seq2 =tap2, tap3, tap4 and so on  
given each tap can run up to 10000 times  
given each tap restarts with it's previous v and a  
find the percentage of the bathtub which is full at a given time? if more than 100%, just say 100%
