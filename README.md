![timeintervals](docs/source/_static/logo.svg "Logo")

timeintervals is a small python library useful for working with intervals (or sets) of time.  

## Usage
Lets look at the motivating problem to understand how to use timeintervals.  

Suppose you are managing a team of anesthesiologists. 
They need to be available 24/7 to repond to patient emergencies, and even routine, planned procedures can go longer than intended, so overtime pay is necessary.
Attending anesthesiologists at teaching hospitals, however, typically aren't doing just one case, they're supervising multiple residents or nursing anesthetists and responding to their calls for assistance when necessary.
Thus, their cases can often look like this:  

![timeintervals](docs/source/_static/example_1.svg, "Example 1")

If we just count the minutes that the anesthesiologist worked, we would be double counting the minutes where two cases were occuring at the same time.
We need to deduplicate and use only the time the anesthesiologist was in *any* case.  
Lets use **timeintervals** to solve this problem.  
### TimeInterval
To create these timeintervals, we can parse the case's start and end times from strings.
```python
from timeintervals import TimeInterval
from typing import List

cases_strs: List[str] = [
    ("2025-10-16 15:00", "2025-10-16 17:45"),
    ("2025-10-16 15:15", "2025-10-16 16:45"),
    ("2025-10-16 17:00", "2025-10-16 18:30"),
    ("2025-10-16 17:45", "2025-10-16 20:30")
]
time_format: str = "%Y-%m-%d %H:%M"
cases: List[TimeInterval] = [
    TimeInterval.from_strings(start, stop, time_format) for (start, stop) in cases_strs
]
for (index, case) in enumerate(cases):
    print(f"Case {index}: {case}")
```
```
Case 0: TimeInterval(start=2025-10-16 15:00:00, end=2025-10-16 17:45:00)
Case 1: TimeInterval(start=2025-10-16 15:15:00, end=2025-10-16 16:45:00)
Case 2: TimeInterval(start=2025-10-16 17:00:00, end=2025-10-16 18:30:00)
Case 3: TimeInterval(start=2025-10-16 17:45:00, end=2025-10-16 20:30:00)
```

