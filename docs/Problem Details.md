# Simple/Medium Problem Details
>
> Note all units are normalized with respect to something:
>
> * positions $LU = 389703km$
> * speed $SU = 382981km/s$.
> * Earth-Moon orbital period $TU = 27.3days$

```python
def init_simple_problem() -> orbital_golomb_array :
    ic = [
     0.896508460944940632764,
     0.,
     0.,
     0.000000000000013951082,
     0.474817948848534454598,
     0.
    ]
    period = 2.6905181697222775
    N = 5 # Number of satellites
    grid_size = 11 # Grid size

    ############### Constants
    M = 3 # Number of observations
    T = period*(M-1) # Each observation is made after each period
    mu = 0.01215058560962404  # M_L/(M_T + M_L)
    scaling_factor = 1e-4
    inflation_factor = 1.23
    ###############
 [...]
```

#### Initial Conditions of the Mother Satellite

```python
ic = [
    0.896508460944940632764,   # x
    0.,                        # y
    0.,                        # z
    0.000000000000013951082,   # v_x
    0.474817948848534454598,   # v_y
    0.                         # v_z
]
```

These are the initial conditions of the trajectory of the mother satellite $m$ in the reference system:

* Initial position: $(x=0.896508460944940632764, y=0, z=0)$
* Initial velocity: $(v_x=0.000000000000013951082, v_y=0.474817948848534454598, v_z=0)$

#### Orbital Period

```python
period = 2.6905181697222775
```

This is the period, normalized with respect to that of the Earth-Moon system, of the orbit of the mother satellite's trajectory in the CR3BP reference system.

#### Mass Parameter ($\mu_2$)

```python
mu = 0.01215058560962404
```

This value represents the mass ratio between masses $m_1$ and $m_2$, specifically between the Earth and the Moon:
$$
\mu_2 = \frac{M_{2}}{M_{1} + M_{2}}
\quad \text{where}\quad
\left\{
 \begin{aligned}
 M_1&=5,9721 \times 10^{24}kg \\
 M_2&=7,3477 \times 10^{22}kg \\
 \end{aligned}
\right.$$
A value of $0.01215058560962404$ means that the mass of the Moon is $1.22\%$ of the total mass involved, while that of the Earth is the remaining $98.78\%$

#### Total Mission Time (T)
```python
T = period * (M - 1)
```
Where M is the number of measurements. This formula ensures that each measurement is taken after a complete orbital period.

#### Distance Between the Planets
In the standard CR3BP system, the distance between the two main bodies is normalized and thus corresponds to $1$ unit in the normalized coordinate system.
#### Scaling Factor
```python
scaling_factor = 1.23
```
Used to resize (scale) the initial positions and velocities of the satellites. It is applied during initialization to reduce the magnitude of the variables.
#### Inflation Factor
```python
n_factor = 1.23
```
"Spreads" the dispersion of the satellites in some cases...?
