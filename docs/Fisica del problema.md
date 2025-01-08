# Circular Restricted Three-Body Problem

[src](https://orbital-mechanics.space/the-n-body-problem/circular-restricted-three-body-problem.html#equation-eq-non-dimensional-masses-cr3bp)

In this section, we solve the three-body problem, subject to some restrictions. In particular:

1. There are two primary masses, and the mass of the tertiary object $m$ is extremely small in comparison to $m_1$ and $m_2$
2. $m_1 < m_2 << m$
3. The two primary objects orbit in a circle around their center of mass

Although these assumptions seem fairly restrictive, they actually represent several very important physical situations: the Earth-Moon system, as well as the orbits of many of the planets around the sun, with a man-made object as the third mass!
This is called the _Circular Restricted Three-Body Problem_ (CRTBP or CR3BP), because the orbits are restricted to circles and the mass of the third body is restricted to be much smaller than the other two.

>We'll see in a later section that the eccentricity of an orbit determines how close to a circle the orbit is.
>An eccentricity of 0 gives the equation for a circle, while vales up to 1.0 are ellipses.

The orbit of the moon around the earth is approximately circular, with a mean eccentricity of $0.054$, and semi-major and semi-minor axes of $384,400 km$ and $383,800 km$, respectively.
The center of mass of the system occurs at a distance of $4,600 km$ from the Earth's center, about $72\%$ of the radius of the Earth. This data comes from [Wikipedia](https://en.wikipedia.org/wiki/Orbit_of_the_Moon).

Similarly, the orbits of Venus, Earth, Jupiter, Saturn, Neptune, and Uranus around the sun all have eccentricities less than $0.06$, according to the [NASA Planetary Fact Sheet](https://nssdc.gsfc.nasa.gov/planetary/factsheet/).

Unlike the two-body problem, there is no general closed-form solution to this problem. Closed-form means an analytical equation we can solve. But we can construct the equations of motion to find some interesting parameters of the orbits.

## Orbit of Primary Masses

We first attach a _non-inertial_ coordinate system to the barycenter of the system of $m_1$ and $m_2$, such that the $x$-axis of this coordinate system points towards $m_2$. The distance from $m_1$ to $m_2$ is $r_{12}$, which is also the radius of the circular orbit, as shown in:

> ![CR3BP_img](/resources/CR3BP_img.svg)
> The system of masses for the circular restricted three body problem.

The $y$-axis of this coordinate system is in the orbital plane, and the $z$-axis is perpendicular to the orbital plane, in the same direction as the angular momentum vector. In the rotating reference frame, $m_1$ and $m_2$ appear to be stationary.

The _inertial angular velocity_ of the _reference frame_ is:
$$
 \mathbf{\Omega} = \varOmega\hat{k}
$$
where
$$
 \varOmega = \frac{2\pi}{T}
$$
$T$ is the period of the orbit, and the orbital period for a circular orbit is:
$$
 T = \frac{2\pi}{\sqrt{\mu}}r_{12}^{3/2}
$$
Plugging this in for $\varOmega$, we find:
$$\varOmega = \sqrt{\frac{\mu}{r_{12}^3}}$$
where the gravitational parameter is given by:
$$
 \mu = GM = G\left(m_1 + m_2\right)
$$

Next, we want to find the positions of the two masses relative to the barycenter.
By definition, the two masses lie in the orbital plane, so their $z$-coordinate is going to be zero. Since the line that connects $m_1$ and $m_2$ goes through the barycenter, then their $y$-coordinates must be zero as well.

In that case, we only need to find the $x$-coordinates, which we can do from the equation for the center of mass:
$$
 m_1 x_1 + m_2 x_2 = 0
$$
We need a second independent equation to solve for $x_1$ and $x_2$. Fortunately, we know the distance between the masses is $r_{12}$. Solving for $x_2$:
$$
 x_2 = x_1 + r_{12}
$$

To solve this set of equations, it's convenient to define two dimensionless ratios:
$$
\begin{aligned}
  \mu_1 &= \frac{m_1}{m_1 + m_2} & \mu_2 &= \frac{m_2}{m_1 + m_2}
\end{aligned}
$$
> You might be able to remember these by noting that $\mu_1$ has $m_1$ in the numerator, and $\mu_2$ has $m_2$ in the numerator.

Note that $\pi_2 = 1 - \pi_1$. Now we can solve for $x_1$ and $x_2$ in terms of these:
$$\begin{aligned}
  x_1 &= -\mu_2 r_{12} & x_2 &= \mu_1 r_{12}
\end{aligned}
$$

## Orbit of the Tertiary Mass

<u>Now let's add</u> the much smaller, <uertiary mass</u> $m$ into the system.
We want the equation of motion, that is, Newton's second law. For that we need the acceleration, which we will derive from the position.

### Position, Velocity, and Acceleration

The _position of the tertiary mass_ relative to the barycenter is:
$$
 \mathbf{r} = x\hat{\imath} + y\hat{\jmath} + z\hat{k}
$$
The position of the tertiary mass relative to $m_1$ is:
$$
\mathbf{r}_1 = \left(x - x_1\right)\hat{\imath} + y\hat{\jmath} + z\hat{k} = \left(x + \pi_2 r_{12}\right)\hat{\imath} + y\hat{\jmath} + z\hat{k}
$$
and finally, the position of $m$ relative to $m_2$ is:
$$
 \mathbf{r}_2 = \left(x - \pi_1 r_{12}\right)\hat{\imath} + y\hat{\jmath} + z\hat{k}
$$
Newton's second law requires the _inertial_ acceleration.
To find that, we first find the _inertial_ velocity of $m$. We need to account for the rotating frame of reference. This means that the velocity and acceleration need to include the rotation of the coordinate system:
$$\dot{\mathbf{r}} = \mathbf{v}_{COG} + \mathbf{\Omega}\times\mathbf{r} + \mathbf{v}_{\text{rel}}$$
where $\mathbf{v}_{COG}$ is the absolute velocity of the barycenter and $\mathbf{v}_{\text{rel}}$ is the velocity calculated in the moving coordinate system:
$$\mathbf{v}_{\text{rel}} = \dot{x}\hat{\imath} + \dot{y}\hat{\jmath} + \dot{z}\hat{k}
$$
Then we can find the absolute acceleration of $m$:
$$
 \ddot{\mathbf{r}} = \mathbf{a}_{COG} + \dot{\mathbf{\Omega}}\times\mathbf{r} + \mathbf{\Omega}\times\left(\mathbf{\Omega}\times\mathbf{r}\right) + 2\mathbf{\Omega}\times\mathbf{v}_{\text{rel}} + \mathbf{a}_{\text{rel}}
$$
This equation can be simplified because we showed that the acceleration of the barycenter is zero for the two-body problem, $\mathbf{a}_{COG} = 0$. In addition, the angular velocity is constant since the orbit is circular, so $\dot{\mathbf{\Omega}} = 0$. Then the equation can be simplified to:
$$\ddot{\mathbf{r}} = \mathbf{\Omega}\times\left(\mathbf{\Omega}\times\mathbf{r}\right) + 2\mathbf{\Omega}\times\mathbf{v}_{\text{rel}} + \mathbf{a}_{\text{rel}}$$
where
$$\mathbf{a}_{\text{rel}} = \ddot{x}\hat{\imath} + \ddot{y}\hat{\jmath} + \ddot{z}\hat{k}$$
Plugging everything in and simplifying:
$$\ddot{\mathbf{r}} = \left(\ddot{x} - 2\varOmega\dot{y} - \varOmega^2 x\right)\hat{\imath} + \left(\ddot{y} + 2\varOmega\dot{x} - \varOmega^2 y\right)\hat{\jmath} + \ddot{z}\hat{k}$$

### Newton's Second Law

For the tertiary body, the forces are due to both of the other masses:
$$m \ddot{\mathbf{r}} = \mathbf{F}_1 + \mathbf{F}_2$$
where $\mathbf{F}_1$ is the force from $m_1$ on $m$ and $\mathbf{F}_2$ is the force from $m_2$ on $m$.

The two forces are found by Newton's law of gravitation:
$$\begin{aligned}
 \mathbf{F}_1 &= -G\frac{m_1 m}{r_1^2} \left.\hat{u}_r\right)_1 = -\frac{\mu_1 m}{r_1^3}\mathbf{r}_1 \\
 \mathbf{F}_2 &= -G\frac{m_2 m}{r_2^2}\left.\hat{u}_r\right)_2 = -\frac{\mu_2 m}{r_2^3}\mathbf{r}_2
\end{aligned}
\qquad \text{where} \qquad
\left\{
 \begin{aligned}
 \mu_1 &= G m_1 \\
 \mu_2 &= G m_2
 \end{aligned}
\right.
\qquad \text{and} \qquad
\left\{
 \begin{aligned}
  \left.\hat{u}_r\right)_1 &= \frac{\mathbf{r}_1}{r_1}\\
  \left.\hat{u}_r\right)_2 &= \frac{\mathbf{r}_2}{r_2}
 \end{aligned}
\right.
$$
Combining the first and the second equation, and dividing through by $m$, we find:
$$\ddot{\mathbf{r}} = -\frac{\mu_1}{r_1^3}\mathbf{r}_1 - \frac{\mu_2}{r_2^3}\mathbf{r}_2$$
Now we substitute for $\ddot{\mathbf{r}}$ from equation $\ddot{\mathbf{r}} = \mathbf{a}_{COG} + \dot{\mathbf{\Omega}}\times\mathbf{r} + \mathbf{\Omega}\times\left(\mathbf{\Omega}\times\mathbf{r}\right) + 2\mathbf{\Omega}\times\mathbf{v}_{\text{rel}} + \mathbf{a}_{\text{rel}}$
and split out by components to have three scalar equations of motion for the CR3BP:
$$
\begin{aligned}
  \ddot{x} - 2\varOmega\dot{y} - \varOmega^2 x &= -\frac{\mu_1}{r_1^3}\left(x + \pi_2 r_{12}\right) - \frac{\mu_2}{r_2^3}\left(x - \pi_1 r_{12}\right) \\
  \ddot{y} + 2\varOmega\dot{x} - \varOmega^2 y &= -\frac{\mu_1}{r_1^3}y - \frac{\mu_2}{r_2^3}y \\
  \ddot{z} &= -\frac{\mu_1}{r_1^3}z - \frac{\mu_2}{r_2^3}z
\end{aligned}
$$

There are a few things we can note from these equations.

1. the $x$ and $y$ equations are coupled;
2. the $x$ equation depends on $y$, and the $y$ equation depends on $x$.
However, the $z$ equation is decoupled from the other two, so if $m$ starts in planar motion, it will remain there.

## Extra: Non-dimensional Equations of Motion

Next, let's make these equations non-dimensional. This offers the advantage of being general for any system we want to study and removing the dependence on the rate of rotation of the coordinate system.

To make the equations of motion non-dimensional, we need to define characteristic parameters for all of the dimensions in our problem. Typically, the characteristic parameters are chosen so that they are representative of some physical quantity in the system. We need the same number of characteristic parameters as dimensions in the problem.

In this problem, we have 3 dimensions:

1. Mass
2. Length
3. Time

The characteristic mass is the sum of the primary and secondary masses, $m_1 + m_2$. To create the non-dimensional masses, we divide $m_1$ and $m_2$ by the characteristic mass, which gives the definitions of $\pi_1$ and $\pi_2$ from Equation $\pi_1 = \frac{m_1}{m_1 + m_2}$ and  $\pi_2 = \frac{m_2}{m_1 + m_2}$

The characteristic length is the circular orbit radius, $r_{12}$. Using this, we define the non-dimensional position vectors by dividing the dimensional position vectors, $\mathbf{r}_1$, $\mathbf{r}_2$, and $\mathbf{r}$ by $r_{12}$:
$$
\begin{aligned}
  \mathbf{\rho} &= \frac{\mathbf{r}}{r_{12}} = x^*\hat{\imath} + y^*\hat{\jmath} + z^*\hat{k} \\
  \mathbf{\sigma} &= \frac{\mathbf{r}_1}{r_{12}} = \left(x^* + \pi_2\right)\hat{\imath} + y^*\hat{\jmath} + z^*\hat{k} \\
  \mathbf{\psi} &= \frac{\mathbf{r}_2}{r_{12}} = \left(x^* - 1 + \pi_2\right)\hat{\imath} + y^*\hat{\jmath} + z^*uvec{k}
\end{aligned}
$$

where $x^* = x/r_{12}$, and similar for $y^*$ and $z^*$.

The natural unit of time in this problem is the period of the circular orbit, Equation $T = \frac{2\pi}{\sqrt{\mu}}r_{12}^{3/2}$. We will ignore the constant factor of $2\pi$ because it doesn't change the dimensions available in the equation. Therefore, the characteristic time is:
$$t_C = \sqrt{\frac{r_{12}^3}{\mu}}$$

To make Equation $\ddot{\mathbf{r}} = \mathbf{a}_{COG} + \dot{\mathbf{\Omega}}\times\mathbf{r} + \mathbf{\Omega}\times\left(\mathbf{\Omega}\times\mathbf{r}\right) + 2\mathbf{\Omega}\times\mathbf{v}_{\text{rel}} + \mathbf{a}_{\text{rel}}$ non-dimensional, we need to multiply both sides of the equation by $t_C^2/r_{12}$.
For the left of the equation, side this makes:
$$\ddot{\mathbf{\rho}} = \frac{d^2\mathbf{r}}{dt^2}\frac{t_C^2}{r_{12}} = \frac{d^2\mathbf{\rho}}{d\tau^2}$$

where $\tau = t/t_C$. Making the terms on the right hand side of the equation non-dimensional is also the result of multiplying by $t_C^2/r_{12}$. Note that the dimensions of $\varOmega$ are $t^{-1}$:
$$\ddot{\mathbf{\rho}} = \left(\ddot{x}^* - 2\dot{y}^* - x^*\right)\hat{\imath} + \left(\ddot{y}^* + 2\dot{x}^* - y^*\right)\hat{\jmath} + \ddot{z}^*\hat{k}$$

Now we have the non-dimensional inertial acceleration, we need to make Equation $\ddot{\mathbf{r}} = -\frac{\mu_1}{r_1^3}\mathbf{r}_1 - \frac{\mu_2}{r_2^3}\mathbf{r}_2$, the equation of motion, non-dimensional. After a bunch of algebra, not shown here, we end up with:
$$\ddot{\mathbf{\rho}} = -\frac{1 - \pi_2}{\sigma^3}\mathbf{\sigma} - \frac{\pi_2}{\psi^3}\mathbf{\psi}$$

where $\sigma = \|\mathbf{\sigma}\|$ and $\psi = \|\mathbf{\psi}\|$. Now we can break this into the three scalar components as before:
$$\begin{aligned}
  \ddot{x}^* - 2\dot{y}^* - x^* &= -\frac{1 - \pi_2}{\sigma^3}\left(x^* + \pi_2\right) - \frac{\pi_2}{\psi^3}\left(x^* - 1 + \pi_2\right) \\
  \ddot{y}^* + 2\dot{x}^* - y^* &= -\frac{1 - \pi_2}{\sigma^3} y^* - \frac{\pi_2}{\psi^3}y^* \\
  \ddot{z}^* &= -\frac{1 - \pi_2}{\sigma^3}z^* - \frac{\pi_2}{\psi^3}z^*
\end{aligned}$$

There are three main advantages of this formulation of the equations of motion:
1. The equations are independent of the two masses $m_1$ and $m_2$, depending only on their relative sizes via $\pi_2 = m_2 / (m_1 + m_2)$
2. The equations are independent of the rate of rotation of the reference frame, $\varOmega$
3. The equations are independent of the separation distance between $m_1$ and $m_2$, $r_{12}$, so can be used to represent any system

With the equations of motion, we can determine solutions by integrating them in time. As we will see, this can be a little bit tricky, depending on the situation. We also cannot solve the equations analytically, either in the dimensional or non-dimensional case.

Nonetheless, this system represents a number of physical systems, as mentioned previously, so we will continue to analyze its properties with these non-dimensional equations.
