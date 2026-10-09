def volume_in_run(v, a, t):
    """
    Volume delivered by one tap during a single run lasting t seconds (0 <= t <= 60).
    Acceleration is `a` for the first 30 s and 0.9*a for the next 30 s.
    Returns (volume, velocity_after_run, acceleration_after_run).
    """
    vol = 0.0

    # First 30-second interval: acceleration = a
    s1 = min(t, 30)
    vol += v * s1 + 0.5 * a * s1 ** 2
    v_end = v + a * s1

    # Second 30-second interval: acceleration = 0.9 * a
    if t > 30:
        a2 = 0.9 * a
        s2 = t - 30
        vol += v_end * s2 + 0.5 * a2 * s2 ** 2
        v_end += a2 * s2

    # Acceleration decays by 0.9 at each completed 30 s boundary
    if t >= 60:
        a_end = a * 0.81
    elif t >= 30:
        a_end = a * 0.9
    else:
        a_end = a

    return vol, v_end, a_end


def bathtub_fill_percentage(velocities, accelerations, capacity, query_time,
                            window=3, run_time=60, max_runs=10000):
    """
    Percentage of the bathtub filled at query_time (capped at 100).

    velocities, accelerations : initial v and a for each tap (len <= 10)
    capacity                  : bathtub capacity (same units as volume)
    query_time                : time in seconds at which to check
    window                    : number of taps running at once (3)
    run_time                  : seconds each sequence runs (60)
    max_runs                  : maximum runs per tap (10000)
    """
    n = len(velocities)
    v = list(velocities)
    a = list(accelerations)
    runs = [0] * n
    window = min(window, n)

    total = 0.0
    phase = 0
    elapsed = 0.0

    while elapsed < query_time:
        dt = min(run_time, query_time - elapsed)   # may be a partial phase
        any_active = False

        for i in range(window):
            tap = (phase + i) % n                  # FIFO sliding window
            if runs[tap] >= max_runs:
                continue
            any_active = True

            vol, v_end, a_end = volume_in_run(v[tap], a[tap], dt)
            total += vol

            # Always save the final state, including partial runs
            v[tap], a[tap] = v_end, a_end
            runs[tap] += 1

        if total >= capacity:
            return 100.0
        if not any_active:                         # every tap has hit its limit
            break

        elapsed += dt
        phase += 1

    return min(100.0, total / capacity * 100.0)


if __name__ == "__main__":
    n = int(input("Number of taps (<= 10): "))
    assert 1 <= n <= 10, "Taps must be between 1 and 10"

    velocities, accelerations = [], []
    for i in range(n):
        v = float(input(f"Tap {i + 1} initial velocity: "))
        a = float(input(f"Tap {i + 1} initial acceleration: "))
        velocities.append(v)
        accelerations.append(a)

    capacity = float(input("Bathtub capacity: "))
    t = float(input("Time (seconds) at which to check: "))

    pct = bathtub_fill_percentage(velocities, accelerations, capacity, t)
    print("Bathtub is 100% full" if pct >= 100 else f"Bathtub is {pct:.2f}% full")