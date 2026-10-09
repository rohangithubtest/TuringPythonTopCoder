https://chat.qwen.ai/c/85e39dfa-7b90-45d7-a4a7-08046187878a  
current_v is calculated before the current_a is correctly calculated  
time_to_next_change calculation logic seems to be wrong  
actual -    
time_to_next_change = 30 - time_in_current_30s_block  
should be -  
time_to_next_change = 60 - time_in_current_30s_block  
https://chat.qwen.ai/c/3f03d038-6eba-466d-96f4-24c0736d5289  
the sequence goes as 
tap1, tap2, tap3  
tap2, tap3, tap4  
and repeats instead of overflowing into  
tap3, tap4, tap1  
https://chat.qwen.ai/c/e2a12ef8-2a1e-4599-b6dd-563fdecea335  
partial completion is not counted as a run  
the check  
if not can_run:  
    sequence_idx += 1  
    continue  
does not increased the current_time, meaning it can be an infinite loop  
the sequence goes as   
tap1, tap2, tap3  
tap2, tap3, tap4   
and repeats instead of overflowing into  
tap3, tap4, tap1  
