\*\*Initial exploration\*\*  
I started with a card problem where we would choose cards  
ace, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, jack, queen, king of spades  
now place 3 cards to the bottom (for a-c-e)  
the next card should be the ace of spades  
so on for 1, and 2  
now place 5 cards to the bottom (for t-h-r-e-e)  
the next card should be the 3 of spades  
and so on  
however I found this was available in the internet



\*\*Next problem exploration\*\*  

So I started out with a bathtub solution where there would be multiple taps with varying velocities and accelerations  
Initially I started with all taps running. But since this might be too simplistic, I used only a few subset to be active at a time.  
I experimented with whether a fixed duration as a break after which the tap would start again, but I discarded that functionality.



\*\*Full requirements\*\*  

Finally, I decided on this prompt (the requirement given to qwen) -  
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

