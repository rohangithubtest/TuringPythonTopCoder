"""
Bathtub Filling Simulator
=========================

Simulates a bathtub being filled by multiple taps with the following rules:
- Up to 10 taps, each with initial velocity and acceleration
- Exactly 3 taps run concurrently at any time
- Taps follow a FIFO sequence (circular queue)
- Each tap runs for maximum 60 seconds per activation
- After 60s, the window shifts by 1 position in the sequence
- Acceleration decreases to 90% every 30 seconds within a run
- Each tap can be activated up to 10,000 times
- When restarted, tap uses its last velocity and acceleration values
- Returns fill percentage at any given time (capped at 100%)
"""


class BathtubSimulator:
    """Simulates bathtub filling with multiple taps."""
    
    def __init__(self, taps_config, sequence, bathtub_capacity=100000):
        """
        Initialize the simulator.
        
        Parameters
        ----------
        taps_config : dict
            Dictionary mapping tap_id to {'v': initial_velocity, 'a': initial_acceleration}
            Example: {'tap1': {'v': 10, 'a': 2}, 'tap2': {'v': 8, 'a': 1.5}}
        sequence : list
            List of tap_ids in FIFO order
            Example: ['tap1', 'tap2', 'tap3', 'tap4', 'tap5']
        bathtub_capacity : float, optional
            Total capacity of the bathtub (default: 100000)
        """
        if len(taps_config) > 10:
            raise ValueError("Maximum 10 taps allowed")
        
        if len(sequence) == 0:
            raise ValueError("Sequence cannot be empty")
        
        # Validate all taps in sequence exist in config
        for tap_id in sequence:
            if tap_id not in taps_config:
                raise ValueError(f"Tap '{tap_id}' in sequence not found in taps_config")
        
        # Initialize tap states
        self.taps = {}
        for tap_id, config in taps_config.items():
            self.taps[tap_id] = {
                'current_v': float(config['v']),
                'current_a': float(config['a']),
                'run_count': 0
            }
        
        self.sequence = sequence
        self.capacity = float(bathtub_capacity)
        self.num_concurrent = 3
    
    def _calculate_tap_water(self, tap_id, duration):
        """
        Calculate water volume from a single tap running for given duration.
        
        Uses kinematic equation: s = v₀t + ½at²
        Acceleration decays to 90% every 30 seconds.
        
        Parameters
        ----------
        tap_id : str
            Identifier of the tap
        duration : float
            How long the tap runs (in seconds)
            
        Returns
        -------
        float
            Water volume contributed by this tap
        """
        # Check if tap exists and hasn't exceeded max runs
        if tap_id not in self.taps:
            return 0.0
        
        tap = self.taps[tap_id]
        if tap['run_count'] >= 10000:
            return 0.0
        
        # Increment run count
        tap['run_count'] += 1
        
        # Get current state
        current_v = tap['current_v']
        current_a = tap['current_a']
        
        total_water = 0.0
        elapsed = 0.0
        
        # Process in intervals, handling acceleration changes every 30 seconds
        while elapsed < duration:
            # Calculate time until next acceleration change or end of duration
            time_in_current_30s_block = elapsed % 30
            time_to_next_change = 30 - time_in_current_30s_block
            remaining_time = duration - elapsed
            
            dt = min(time_to_next_change, remaining_time)
            
            if dt <= 0:
                break
            
            # Calculate water flow for this interval using s = vt + ½at²
            water = current_v * dt + 0.5 * current_a * dt * dt
            total_water += water
            
            # Update velocity at end of interval: v = v₀ + at
            current_v = current_v + current_a * dt
            
            # Advance time
            elapsed += dt
            
            # Apply acceleration decay if we hit a 30-second boundary
            # and there's still time remaining in this run
            if elapsed < duration and abs(elapsed % 30) < 1e-9:
                current_a *= 0.9
        
        # Save final state for next activation
        tap['current_v'] = current_v
        tap['current_a'] = current_a
        
        return total_water
    
    def get_fill_percentage(self, query_time):
        """
        Calculate the percentage of bathtub filled at query_time.
        
        Parameters
        ----------
        query_time : float
            Time in seconds to check fill level
            
        Returns
        -------
        float
            Percentage filled (0 to 100, capped at 100)
        """
        if query_time <= 0:
            return 0.0
        
        total_water = 0.0
        seq_length = len(self.sequence)
        
        # Calculate number of batches needed
        # Each batch is 60 seconds long
        num_full_batches = int(query_time / 60)
        remaining_time = query_time % 60
        
        num_batches = num_full_batches + (1 if remaining_time > 0 else 0)
        
        # Process each batch
        for batch_num in range(num_batches):
            batch_start = batch_num * 60
            
            # Determine duration for this batch
            if batch_num < num_full_batches:
                duration = 60.0
            else:
                duration = remaining_time
            
            if duration <= 0:
                continue
            
            # Determine which 3 taps are active in this batch
            # Using circular indexing through the sequence
            for i in range(self.num_concurrent):
                idx = (batch_num + i) % seq_length
                tap_id = self.sequence[idx]
                
                # Calculate water from this tap
                water = self._calculate_tap_water(tap_id, duration)
                total_water += water
        
        # Calculate percentage and cap at 100%
        if self.capacity <= 0:
            return 100.0
        
        percentage = (total_water / self.capacity) * 100.0
        return min(percentage, 100.0)


def example_usage():
    """Demonstrate usage with examples."""
    
    print("=" * 70)
    print("BATHTUB FILLING SIMULATOR - EXAMPLE USAGE")
    print("=" * 70)
    
    # Example 1: Standard configuration
    print("\n--- Example 1: 5 Taps ---")
    taps_config = {
        'tap1': {'v': 10, 'a': 2},
        'tap2': {'v': 8, 'a': 1.5},
        'tap3': {'v': 12, 'a': 2.5},
        'tap4': {'v': 9, 'a': 1.8},
        'tap5': {'v': 11, 'a': 2.2}
    }
    sequence = ['tap1', 'tap2', 'tap3', 'tap4', 'tap5']
    
    sim = BathtubSimulator(taps_config, sequence, bathtub_capacity=100000)
    
    test_times = [0, 30, 60, 90, 120, 180, 300]
    print(f"{'Time (s)':<12} {'Fill %':<12}")
    print("-" * 30)
    for t in test_times:
        pct = sim.get_fill_percentage(t)
        print(f"{t:<12} {pct:<12.2f}")
    
    # Example 2: Small capacity (tests 100% cap)
    print("\n--- Example 2: Small Capacity (should cap at 100%) ---")
    sim2 = BathtubSimulator(taps_config, sequence, bathtub_capacity=5000)
    for t in [60, 120]:
        pct = sim2.get_fill_percentage(t)
        print(f"t = {t}s: {pct:.2f}%")
    
    # Example 3: Single tap
    print("\n--- Example 3: Single Tap ---")
    single_tap_config = {'tap1': {'v': 5, 'a': 1}}
    single_seq = ['tap1']
    sim3 = BathtubSimulator(single_tap_config, single_seq, bathtub_capacity=50000)
    for t in [60, 120, 180]:
        pct = sim3.get_fill_percentage(t)
        print(f"t = {t}s: {pct:.2f}%")
    
    # Example 4: Two taps
    print("\n--- Example 4: Two Taps ---")
    two_tap_config = {
        'A': {'v': 15, 'a': 3},
        'B': {'v': 10, 'a': 2}
    }
    two_seq = ['A', 'B']
    sim4 = BathtubSimulator(two_tap_config, two_seq, bathtub_capacity=200000)
    for t in [60, 120, 180, 240]:
        pct = sim4.get_fill_percentage(t)
        print(f"t = {t}s: {pct:.2f}%")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    example_usage()