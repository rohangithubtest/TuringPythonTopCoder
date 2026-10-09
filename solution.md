## Steps to the solution

Each tap has an initial velocity and acceleration. The solution calculates the volume of water contributed by each active tap using the formula:

Volume = velocity × time + 0.5 × acceleration × time²

Each tap runs for up to 60 seconds. After every 30 seconds, its acceleration is reduced to 90% of its previous value. The velocity is updated as the tap runs, and the final velocity and   acceleration are carried forward to subsequent activations.

The solution uses a sliding-window approach to determine which taps are active. For example, with four taps and a sequence size of three, the active groups are taps 1, 2, and 3, followed by   taps 2, 3, and 4. The implementation uses circular indexing, allowing the sequence to wrap around to the beginning of the tap list.

The simulation advances in time intervals until the requested query time is reached. It accumulates the water contributed by the active taps and calculates the bathtub's fill percentage   based on its capacity. The returned percentage is capped at 100%.

The implementation also tracks the number of times each tap runs, subject to the configured maximum run count. However, input validation and the handling of exhausted taps require additional    attention to ensure that all problem constraints are enforced correctly.



## The edge cases are not implemented

Limitations: the edge cases are documented in the test cases, but not implemented in the code

