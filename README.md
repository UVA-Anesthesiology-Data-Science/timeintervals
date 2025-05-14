![timeintervals](docs/source/_static/logo.svg "Logo")

timeintervals is a small python library useful for working with intervals and sets of time.  

## Usage
Lets look at the motivating problem to understand how to use timeintervals.  

Suppose you are managing a team of anesthesiologists. 
At least one member of the anesthesia team needs to be on call 24/7 for emergencies, and planned surgeries cannot be stopped exactly at 5pm to go home.
Therefore, anesthesiologists earn overtime pay.  

Attending anesthesiologists at teaching hospitals typically aren't doing just one case, they're supervising multiple residents or nursing anesthetists by lending aid during busy portions of the surgery and teaching residents through practical training.
Thus, their cases can often have times that look like this:  

![timeintervals](docs/source/_static/example_1.svg "Example 1")

If we were to merely count the minutes that the anesthesiologist worked, we would be double counting the minutes where two cases occured at the same time.
We need to deduplicate and use only the time they were in *any* case.  
**timeintervals** was created to solve this problem.  

### Representing Cases using TimeInterval
To create a TimeInterval, we can parse the case's start and end times from strings.
```python
from timeintervals import TimeInterval
from typing import List

cases_strs: List[str] = [
    ("2025-10-16 15:00", "2025-10-16 17:45"),
    ("2025-10-16 15:15", "2025-10-16 16:45"),
    ("2025-10-16 17:00", "2025-10-16 18:30"),
    ("2025-10-16 18:45", "2025-10-16 20:30")
]
time_format: str = "%Y-%m-%d %H:%M"
cases: List[TimeInterval] = [
    TimeInterval.from_strings(start, stop, time_format)
    for (start, stop) in cases_strs
]
for (index, case) in enumerate(cases):
    print(f"Case {index}: {case}")
```
```
Case 0: TimeInterval(start=2025-10-16 15:00:00, end=2025-10-16 17:45:00)
Case 1: TimeInterval(start=2025-10-16 15:15:00, end=2025-10-16 16:45:00)
Case 2: TimeInterval(start=2025-10-16 17:00:00, end=2025-10-16 18:30:00)
Case 3: timeInterval(start=2025-10-16 18:45:00, end=2025-10-16 20:30:00)
```

(Note: if parsing a timestamp using `datetime.strptime()` won't work for a use case, TimeIntervals can be directly constructed from datetime objects using the standard init method.) 

### Getting Ready for Set Operations using TimeSet
To perform the set-like operations, we need to create a TimeSet.  
A TimeSet is composed of a list of TimeIntervals, and exposes set operations like intersection, union, add, and subtract.  
To create one, we simply pass the list of TimeIntervals into the init method:
```python
from timeintervals import TimeSet

case_set: TimeSet = TimeSet(cases)
print(case_set)
```
```
TimeSet(time_intervals=['TimeInterval(start=2025-10-16 15:00:00, end=2025-10-16 17:45:00)', 'TimeInterval(start=2025-10-16 15:15:00, end=2025-10-16 16:45:00)', 'TimeInterval(start=2025-10-16 17:00:00, end=2025-10-16 18:30:00)', 'TimeInterval(start=2025-10-16 18:45:00, end=2025-10-16 20:30:00)'])
```

### Finding Time Spent in Cases using Union
To find out how many minutes the provider worked, we need a **union** of all the case time.  
TimeSet has a built in method called `compute_internal_union()` which will return a TimeSet containing the union of all the TimeIntervals in the TimeSet.
```python
unioned_case_set: TimeSet = case_set.compute_internal_union()
for (index, interval) in enumerate(unioned_case_set.time_intervals):
    print(f"Interval {index}: {interval}")
```
```
Interval 0: TimeInterval(start=2025-10-16 15:00:00, end=2025-10-16 18:30:00)
Interval 1: TimeInterval(start=2025-10-16 18:45:00, end=2025-10-16 20:30:00)
```

### Finding Payable Time using Intersection
Suppose the OR closes at 5:00pm, and any time over is considered overtime until the start of the next morning's cases.
To find this, we need the intersection of our unioned case time with the overtime.  

The `compute_intersection` method computes the intersection of a TimeSet with another TimeSet, and produces a new TimeSet that includes only the time which both TimeSets have in common.  
```python
from datetime import datetime
# we can also construct timeintervals from datetime objects.
overtime_start: datetime = datetime(year=2025, month=10, day=16, hour=17, minute=0)
overtime_end: datetime = datetime(year=2025, month=10, day=17, hour=6, minute=0)

overtime: TimeSet = TimeSet([TimeInterval(overtime_start, overtime_end)])
overtime_worked: TimeSet = unioned_case_set.compute_intersection(overtime)

print(overtime_worked)
```
```
TimeSet(time_intervals=['TimeInterval(start=2025-10-16 17:00:00, end=2025-10-16 18:30:00)', 'TimeInterval(start=2025-10-16 18:45:00, end=2025-10-16 20:30:00)'])
```

### Computing Payment
Finally, we can compute the payment.
```python
payment_rate_per_hour: float = 30
one_hour_in_seconds: int = 60*60
get_hours_in_time_interval = lambda ti: ti.time_elapsed().total_seconds()/(one_hour_in_seconds)
hours_worked: int = sum(get_hours_in_time_interval(ti) for ti in overtime_worked.time_intervals)
payment: float = hours_worked*payment_rate_per_hour
print(f"Hours worked: {hours_worked}")
print(f"Hourly rate: {payment_rate_per_hour}$")
print(f"Payment: {payment:.2f}$")
```
```
Hours worked: 3.25
Hourly rate: 30$
Payment: 97.50$
```

### Paying On-Call Pager Time using Subtraction
Payment computation has been completed, except there is one problem: pager payments.
When anesthesiologists are on-call, they recieve a small amount of money when they *aren't* in cases.
How do we pay for time that *isn't* present in the data?  

We can use set subtraction.  
Suppose pager shift starts at 7:00pm and goes until 4:00am the next day at a rate of 20 dollars an hour.
We can build the pager shift as a TimeInterval, wrap it in a TimeSet, and subtract the unioned case time from it to get all the payable pager time.
```python
pager_start: datetime = datetime(year=2025, month=10, day=16, hour=19, minute=0)
pager_end: datetime = datetime(year=2025, month=10, day=17, hour=4, minute=0)
pager_shift: TimeSet = TimeSet([TimeInterval(pager_start, pager_end)])

payable_timeset: TimeSet = pager_shift - unioned_case_set
print(payable_timeset)
hours_worked: int = sum(get_hours_in_time_interval(ti) for ti in payable_timeset.time_intervals)
print(f"Payment: {20}($/hr) * {hours_worked}hrs = {20*hours_worked}$")
```
```
TimeSet(time_intervals=['TimeInterval(start=2025-10-16 20:30:00, end=2025-10-17 04:00:00)'])
Payment: 20($/hr) * 7.5hrs = 150.0$
```
