import numpy as np


def calculate_bathtub_fill_percentage(taps_info, tap_sequence, check_time, bathtub_capacity):
    """
    Calculate the percentage of bathtub filled at a given time.
    
    SYSTEM RULES:
    - 3 taps run simultaneously at any given time
    - Taps run in FIFO sequence (windows of 3 consecutive taps)
    - Each tap runs for 60 seconds per activation
    - After every 30 seconds, acceleration becomes 0.9 * previous acceleration
    - When a tap restarts, it uses its PREVIOUS final velocity and acceleration
    - Each tap can run up to 10000 times maximum
    - If fill exceeds 100%, return 100%
    
    Parameters:
    -----------
    taps_info : dict
        Dictionary mapping tap names to their initial conditions
        Format: {'tap_name': (initial_velocity, initial_acceleration)}
        
    tap_sequence : list
        List of tap names in FIFO order
        Example: ['tap1', 'tap2', 'tap3', 'tap4']
        This creates sequences: [tap1,tap2,tap3], [tap2,tap3,tap4], etc.
        
    check_time : float
        Time in seconds at which to check the fill level
        
    bathtub_capacity : float
        Total capacity of the bathtub (in same units as water calculation)
    
    Returns:
    --------
    float
        Percentage of bathtub filled (capped at 100%)
    
    Example:
    --------
    >>> taps = {'tap1': (1.0, 0.5), 'tap2': (1.5, 0.3), 'tap3': (2.0, 0.4)}
    >>> seq = ['tap1', 'tap2', 'tap3']
    >>> calculate_bathtub_fill_percentage(taps, seq, 60, 1000)
    87.5  # (example value)
    """
    
    # Validate inputs
    num_taps = len(tap_sequence)
    if num_taps < 3:
        raise ValueError(f"Need at least 3 taps, got {num_taps}")
    
    if check_time <= 0:
        return 0.0
    
    if bathtub_capacity <= 0:
        raise ValueError("Bathtub capacity must be positive")
    
    # Generate all possible sequences (sliding window of size 3)
    sequences = []
    for i in range(num_taps - 2):
        seq = tap_sequence[i:i+3]
        sequences.append(seq)
    
    num_sequences = len(sequences)
    
    # Initialize tap states
    # Each tap maintains its current v and a, which persist across runs
    tap_states = {}
    for tap_id in tap_sequence:
        if tap_id not in taps_info:
            raise ValueError(f"Tap '{tap_id}' not found in taps_info")
        v_init, a_init = taps_info[tap_id]
        tap_states[tap_id] = {
            'current_v': v_init,
            'current_a': a_init,
            'run_count': 0
        }
    
    # Maximum runs per tap
    MAX_RUNS = 10000
    
    total_water = 0.0
    current_time = 0.0
    seq_index = 0
    
    # Simulation loop
    while current_time < check_time:
        # Get current sequence
        current_seq = sequences[seq_index % num_sequences]
        
        # Check if all taps in this sequence can still run
        can_run = all(tap_states[tap]['run_count'] < MAX_RUNS for tap in current_seq)
        
        if not can_run:
            # Skip this sequence
            seq_index += 1
            continue
        
        # Determine how long to run this sequence
        remaining_time = check_time - current_time
        run_duration = min(60.0, remaining_time)
        
        # Process each tap in the current sequence
        for tap_id in current_seq:
            state = tap_states[tap_id]
            
            # Calculate water contribution from this tap
            water, final_v, final_a = simulate_tap_flow(
                state['current_v'], 
                state['current_a'], 
                run_duration
            )
            
            total_water += water
            
            # Update tap state for next run
            state['current_v'] = final_v
            state['current_a'] = final_a
            state['run_count'] += 1
        
        current_time += run_duration
        seq_index += 1
    
    # Calculate and cap percentage
    percentage = (total_water / bathtub_capacity) * 100.0
    return min(percentage, 100.0)


def simulate_tap_flow(initial_v, initial_a, duration):
    """
    Simulate water flow from a single tap over a given duration.
    
    The tap operates with kinematic motion where:
    - Position (water volume) follows: s = v₀t + ½at²
    - Velocity updates as: v = v₀ + at
    - Every 30 seconds, acceleration is multiplied by 0.9
    
    Parameters:
    -----------
    initial_v : float
        Initial velocity at start of this run
        
    initial_a : float
        Initial acceleration at start of this run
        
    duration : float
        Duration of the run in seconds (≤ 60)
    
    Returns:
    --------
    tuple
        (total_water, final_velocity, final_acceleration)
    """
    
    total_water = 0.0
    elapsed = 0.0
    current_v = initial_v
    current_a = initial_a
    
    while elapsed < duration:
        # Calculate time until next acceleration change point
        # Acceleration changes at t=30, t=60, etc.
        time_in_current_interval = elapsed % 30
        time_to_next_change = 30.0 - time_in_current_interval
        
        # Determine segment duration
        segment_duration = min(time_to_next_change, duration - elapsed)
        
        # Calculate water for this segment using kinematic equation
        water_segment = current_v * segment_duration + 0.5 * current_a * segment_duration ** 2
        total_water += water_segment
        
        # Update velocity at end of segment
        new_v = current_v + current_a * segment_duration
        
        # Check if we've crossed an acceleration change boundary
        new_elapsed = elapsed + segment_duration
        
        # Apply acceleration decay if we hit a 30-second boundary
        new_a = current_a
        if abs(new_elapsed % 30) < 1e-10 or (new_elapsed > 0 and abs((new_elapsed % 30) - 30) < 1e-10):
            new_a = 0.9 * current_a
        
        current_v = new_v
        current_a = new_a
        elapsed = new_elapsed
    
    return total_water, current_v, current_a


# ============================================================================
# MAIN EXECUTION AND TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("BATHTUB FILL CALCULATOR")
    print("=" * 80)
    
    # Example 1: Basic usage
    print("\n[Example 1] Basic 4-tap system")
    print("-" * 80)
    taps = {
        'tap1': (1.0, 0.5),
        'tap2': (1.5, 0.3),
        'tap3': (2.0, 0.4),
        'tap4': (1.2, 0.6),
    }
    sequence = ['tap1', 'tap2', 'tap3', 'tap4']
    capacity = 10000
    
    test_times = [30, 60, 90, 120, 180, 240, 300]
    for t in test_times:
        pct = calculate_bathtub_fill_percentage(taps, sequence, t, capacity)
        print(f"  Time = {t:3d}s: Bathtub is {pct:6.2f}% full")
    
    # Example 2: System that reaches 100%
    print("\n[Example 2] Small capacity system")
    print("-" * 80)
    taps_small = {
        'A': (5.0, 2.0),
        'B': (4.0, 1.5),
        'C': (3.0, 1.0),
    }
    seq_small = ['A', 'B', 'C']
    capacity_small = 1000
    
    for t in [30, 60, 90]:
        pct = calculate_bathtub_fill_percentage(taps_small, seq_small, t, capacity_small)
        print(f"  Time = {t:3d}s: Bathtub is {pct:6.2f}% full")
    
    # Example 3: Interactive input
    print("\n" + "=" * 80)
    print("INTERACTIVE MODE")
    print("=" * 80)
    print("\nEnter your system parameters:")
    
    try:
        # Get number of taps
        num_taps = int(input("\nNumber of taps (3-10): ").strip())
        if num_taps < 3 or num_taps > 10:
            print("Error: Number of taps must be between 3 and 10")
            exit(1)
        
        # Get tap information
        taps_info = {}
        tap_sequence = []
        
        print(f"\nEnter details for {num_taps} taps:")
        for i in range(1, num_taps + 1):
            tap_name = f"tap{i}"
            print(f"\n{tap_name}:")
            v = float(input(f"  Initial velocity: ").strip())
            a = float(input(f"  Initial acceleration: ").strip())
            taps_info[tap_name] = (v, a)
            tap_sequence.append(tap_name)
        
        # Get bathtub capacity
        capacity = float(input("\nBathtub capacity: ").strip())
        
        # Get check time
        check_time = float(input("Time to check (seconds): ").strip())
        
        # Calculate result
        result = calculate_bathtub_fill_percentage(taps_info, tap_sequence, check_time, capacity)
        
        print("\n" + "=" * 80)
        print(f"RESULT: At t={check_time}s, the bathtub is {result:.2f}% full")
        print("=" * 80)
        
    except KeyboardInterrupt:
        print("\n\nProgram interrupted.")
    except Exception as e:
        print(f"\nError: {e}")