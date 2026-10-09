class BathtubSimulator:
    """
    Simulates a bathtub being filled by multiple taps in a FIFO sequence.
    
    Rules:
    - 3 taps run simultaneously at any given time
    - Taps follow a fixed FIFO sequence (sliding window of 3)
    - Each tap runs for 60 seconds max per activation
    - Acceleration changes to 0.9x every 30 seconds
    - Each tap can be activated up to 10000 times total
    - When a tap restarts, it uses its original initial velocity and acceleration
    """
    
    def __init__(self, tap_data, tap_sequence, bathtub_capacity):
        """
        Initialize the simulator.
        
        Parameters:
        - tap_data: dict mapping tap names to {'initial_velocity': float, 'initial_acceleration': float}
        - tap_sequence: list of tap names in FIFO order
        - bathtub_capacity: total capacity of the bathtub (in same units as water flow)
        """
        self.tap_data = tap_data
        self.tap_sequence = tap_sequence
        self.bathtub_capacity = bathtub_capacity
        
        # Generate all possible 3-tap sequences
        self.sequences = self._generate_sequences()
        
        # Track usage count for each tap
        self.tap_usage = {tap: 0 for tap in tap_sequence}
        self.max_runs_per_tap = 10000
    
    def _generate_sequences(self):
        """Generate all possible 3-tap sequences in FIFO fashion."""
        num_taps = len(self.tap_sequence)
        if num_taps < 3:
            raise ValueError("Need at least 3 taps in sequence")
        
        sequences = []
        for i in range(num_taps - 2):
            seq = tuple(self.tap_sequence[i:i+3])
            sequences.append(seq)
        
        return sequences
    
    def calculate_water_from_single_tap(self, v0, a0, duration):
        """
        Calculate water output from one tap running for given duration.
        
        Physics:
        - First 30 seconds: velocity=v0, acceleration=a0
        - Next 30 seconds: velocity continues, acceleration=0.9*a0
        - Tap stops after 60 seconds
        
        Formula: distance = v0*t + 0.5*a*t^2
        """
        if duration <= 0:
            return 0.0
        
        total_water = 0.0
        remaining_time = min(duration, 60)  # Cap at 60 seconds
        
        # First interval: 0-30 seconds
        t1 = min(30, remaining_time)
        if t1 > 0:
            d1 = v0 * t1 + 0.5 * a0 * t1**2
            v1 = v0 + a0 * t1  # Velocity at end of first interval
            total_water += d1
            remaining_time -= t1
        else:
            v1 = v0  # If no time in first interval
        
        # Second interval: 30-60 seconds
        if remaining_time > 0:
            t2 = min(30, remaining_time)
            if t2 > 0:
                a1 = 0.9 * a0
                d2 = v1 * t2 + 0.5 * a1 * t2**2
                total_water += d2
        
        return total_water
    
    def simulate(self, check_time):
        """
        Simulate the filling process up to check_time.
        
        Parameters:
        - check_time: time in seconds at which to check fill level
        
        Returns:
        - Percentage of bathtub filled (capped at 100%)
        """
        current_time = 0.0
        total_water = 0.0
        sequence_idx = 0
        
        while current_time < check_time:
            # Get current sequence (cycling through all sequences)
            seq = self.sequences[sequence_idx % len(self.sequences)]
            
            # Check if all taps in this sequence can still run
            can_run = all(self.tap_usage[tap] < self.max_runs_per_tap for tap in seq)
            
            if not can_run:
                # Skip this sequence
                sequence_idx += 1
                continue
            
            # Calculate how long this sequence will run
            time_for_this_run = min(60, check_time - current_time)
            
            if time_for_this_run <= 0:
                break
            
            # Calculate water from all 3 taps running simultaneously
            sequence_water = 0.0
            for tap in seq:
                v0 = self.tap_data[tap]['initial_velocity']
                a0 = self.tap_data[tap]['initial_acceleration']
                
                water = self.calculate_water_from_single_tap(v0, a0, time_for_this_run)
                sequence_water += water
            
            # Update usage count only for full 60-second runs
            if time_for_this_run == 60:
                for tap in seq:
                    self.tap_usage[tap] += 1
            
            total_water += sequence_water
            current_time += time_for_this_run
            
            # Move to next sequence
            sequence_idx += 1
        
        # Calculate percentage
        if self.bathtub_capacity <= 0:
            return 100.0
        
        percentage = (total_water / self.bathtub_capacity) * 100
        return min(percentage, 100.0)
    
    def reset(self):
        """Reset the simulator state."""
        self.tap_usage = {tap: 0 for tap in self.tap_sequence}


# ============================================================================
# Example Usage and Testing
# ============================================================================

if __name__ == "__main__":
    print("="*70)
    print("BATHTUB FILLING SIMULATOR")
    print("="*70)
    
    # Define tap parameters
    tap_data = {
        'tap1': {'initial_velocity': 1.0, 'initial_acceleration': 0.5},
        'tap2': {'initial_velocity': 1.2, 'initial_acceleration': 0.4},
        'tap3': {'initial_velocity': 0.8, 'initial_acceleration': 0.6},
        'tap4': {'initial_velocity': 1.0, 'initial_acceleration': 0.5},
        'tap5': {'initial_velocity': 1.1, 'initial_acceleration': 0.45},
    }
    
    # Define sequence order
    tap_sequence = ['tap1', 'tap2', 'tap3', 'tap4', 'tap5']
    
    # Define bathtub capacity
    bathtub_capacity = 50000
    
    # Create simulator
    sim = BathtubSimulator(tap_data, tap_sequence, bathtub_capacity)
    
    print(f"\nConfiguration:")
    print(f"  Number of taps: {len(tap_sequence)}")
    print(f"  Tap sequence: {tap_sequence}")
    print(f"  Bathtub capacity: {bathtub_capacity}")
    print(f"  Sequences generated: {sim.sequences}")
    
    print("\n" + "-"*70)
    print("Simulation Results:")
    print("-"*70)
    
    test_times = [60, 120, 180, 240, 300, 600, 1200]
    
    for t in test_times:
        sim.reset()  # Reset for each independent simulation
        pct = sim.simulate(t)
        print(f"  At t = {t:4d}s: Bathtub is {pct:6.2f}% full")
    
    print("\n" + "="*70)
    print("Test with smaller capacity (should reach 100%)")
    print("="*70)
    
    sim_small = BathtubSimulator(tap_data, tap_sequence, 5000)
    pct = sim_small.simulate(300)
    print(f"At t = 300s with capacity=5000: Bathtub is {pct:.2f}% full")
    
    print("\n" + "="*70)
    print("Interactive Mode")
    print("="*70)
    print("\nTo use this simulator with your own data:")
    print("1. Define tap_data with initial_velocity and initial_acceleration for each tap")
    print("2. Define tap_sequence as a list of tap names")
    print("3. Set bathtub_capacity")
    print("4. Call sim.simulate(check_time) to get percentage filled")