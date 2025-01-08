***PyGMO explained implementation***
	- [DE](https://esa.github.io/pagmo2/docs/cpp/algorithms/de.html#_CPPv4N5pagmo2deE)
	- [SADE](https://esa.github.io/pagmo2/docs/cpp/algorithms/sade.html#classpagmo_1_1sade)
	- [pDE](https://esa.github.io/pagmo2/docs/cpp/algorithms/de1220.html)

## Algorithm Explained
[src](https://sci-hub.ru/10.1023/a:1008202821328) 

![DE_Crossover](/resources/DE_schema.png)

### 1-4) Mutazione
Per ogni elemento $b_i$ della popolazione $b$ viene costruito un vettore $\boldsymbol{b}_{i,mut}$ mutando il:
- **DE/best/1/bin**: membro migliore $b_0$ con la differenza di due elementi $b_j$ e $b_k$ scelti a caso, secondo la formula: $\boldsymbol{b}_{i,mut}=\boldsymbol{b}_0+\lambda(\boldsymbol{b}_j-\boldsymbol{b}_k) \hspace{30pt}\text{con }i\neq j \neq k \neq i$
- **DE/best/2/rand**: membro scelto casualmente $b_0$ con la differenza di tre elementi $b_j$, $b_k$ e $b_t$ scelti a caso, secondo la formula:$\boldsymbol{b}_{i,mut}=\boldsymbol{b}_0+\lambda(\boldsymbol{b}_j-\boldsymbol{b}_k -\boldsymbol{b}_t)  \hspace{30pt}\text{con }i\neq j \neq k \neq j$
dove $\lambda$ è detto _mutazione_.

### 4.9)Clipping
Viene poi costruito un vettore mutante $\boldsymbol{b}'_i$ verificando che ogni gene rispetta i vincoli di disuguaglianza lineare (bordi):
$$
\boldsymbol{b}'_{i}=\begin{bmatrix}
b'_{i1}=\left\{
\begin{aligned}
&b_{i,mut1} \hspace{20pt} \text{se } l_{b1} \leq b_{i,mut1} \leq u_{b1}\\
&l_{b1} \hspace{36pt} \text{se } b_{i,mut1} <l_{b1}\\
&u_{b1} \hspace{34pt} \text{se } b_{i,mut1} > u_{b1}\\
\end{aligned}
\right. \\
b'_{i2}=\left\{
\begin{aligned}
&b_{i,mut2} \hspace{20pt} \text{se } l_{b2} \leq b_{i,mut2} \leq u_{b2}\\
&l_{b2} \hspace{36pt} \text{se } b_{i,mut2} <l_{b2}\\
&u_{b2} \hspace{34pt} \text{se } b_{i,mut2} > u_{b2}\\
\end{aligned}
\right. \\
b'_{i3}=\left\{
\begin{aligned}
&b_{i,mut3} \hspace{20pt} \text{se } l_{b3} \leq b_{i,mut3} \leq u_{b3}\\
&l_{b3} \hspace{36pt} \text{se } b_{i,mut3} <l_{b3}\\
&u_{b3} \hspace{34pt} \text{se } b_{i,mut3} > u_{b3}\\
\end{aligned}
\right. \\
\end{bmatrix}
$$
> es. gene di grandezza $3$, con $l$ intendiamo il bordo inferiore e b quello superiore

### 5) Crossover
A questo punto, viene costruito un candidato $\hat{\boldsymbol{b}}_i$ scegliendo i parametri da $\boldsymbol{b}_i$ o da $\boldsymbol{b}'_i$ con la seguente strategia:

![DE_Crossover](/resources/DE_Crossover.png)

Per ogni gene viene calcolato un numero casuale
- se $rand.rand() \le CR$ il gene $i$-esimo viene preso da quello quello di $\boldsymbol{b}'_{i}$
- se $rand.rand() > CR$ il gene $i$-esimo gene rimane quello di $\boldsymbol{b}_i$

In questo modo $\hat{\boldsymbol{b}}_i$ viene formato

### 6)Selection
A questo punto viene scelto se sostituire $\boldsymbol{b}_i$ con $\hat{\boldsymbol{b}}_i$ in base al valore della funzione obiettivo:
$$
\boldsymbol{b}_{i,new} = \left\{
\begin{align*}
&\hat{\boldsymbol{b}}_i \hspace{30pt} \text{se } F(\hat{\boldsymbol{b}}_i )<F(\boldsymbol{b}_i)\\
&\boldsymbol{b}_i\hspace{30pt} \text{altrimenti}
\end{align*}
\right.
$$

## Self-Adaptive Variant
Two different variants of the Differential Evolution algorithm exploiting the idea of self-adaptation.

The original Differential Evolution algorithm can be significantly improved introducing the idea of parameter self-adaptation. 
Many different proposals have been made to self-adapt both the CR and the F parameters of the original differential evolution algorithm.
- **jDE**: Parameter control using predefined rules or distributions to change CR and F, but does not adapt parameters dynamically during DE operations. [details here](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=4016057&tag=1)
- **iDE**: True self-adaptation by using the DE operators themselves (mutation, crossover) to dynamically modify CR and F values for each individual, adapting to the problem as the algorithm evolves. [details here](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=5949732)

## PaGMO Differential Evolution
A variant of Differential evolution made by ESA that can be found in pyGMO (python) or PaGMO(C/C++)

Our variant makes use of the Differential Evolution#Self-Adaptive Variant adaptation schemes for CR and F and adds self-adaptation for the mutation variant. The only parameter left to be specified is thus population size.

Similarly to what done in Differential Evolution#Self-Adaptive Variant|SADE for F and CR, in DE 1220 each individual chromosome (index) is augmented also with an integer that specifies the mutation variant used to produce the next trial individual. 

Right before mutating the chromosome the value of $V_i$ is adapted according to the equation:
$$
	\begin{split}
  V_i =
  \left\{\begin{array}{ll}
  random & r_i < \tau \\
  V_i & \mbox{otherwise}
  \end{array}\right.
  \end{split}
$$
where $\tau$ is set to be $0.1$, selects a random mutation variant and is a random uniformly distributed number in $\[0, 1\]$

## Mutation Strategy
In order to classify the different variants and strategy, the notation **DE/x/y/z** is used:
- x = best | rand
- y = 1 | 2 | 3
- z = bin | exp

### x. Current
The **Base Individual** defines which individual in the population will be used to guide the mutation process.

| **Base Individual** | **Description**                                                                                                            |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| **best**            | The individual with the best fitness value in the current population. It is used to exploit the current optimal solutions. |
| **rand**            | A randomly chosen individual from the population. It is used to introduce diversity and explore the search space.          |

> The **current individual** refers to the candidate solution that is currently being processed or mutated in a given iteration of the Differential Evolution (DE) algorithm.

### y. Number of Random Individuals
This attribute defines how many random individuals are used to compute the difference vectors that form the mutation process. Increasing the number of random individuals allows the algorithm to explore a broader solution space, improving diversity but possibly reducing exploitation.

| Number of Random Individuals | Description                                                                                                                                                                            |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1**                        | The mutation is done using just one random individual. This is a basic mutation strategy, introducing minimal diversity.                                                               |
| **2**                        | Two random individuals are used to generate the mutation, introducing more diversity and exploration. This increases the chances of exploring different regions of the solution space. |
| **3**                        | Three random individuals are involved in the mutation process. This introduces even more exploration and variability in the mutation, enhancing global search capabilities.            |
| ...                          |                                                                                                                                                                                        |

### z. Crossover Type
The **Crossover Type** defines how the mutated individual is combined with the base individual to form the next candidate solution (or offspring). The two primary crossover methods in DE are **Exponential (exp)** and **Binomial (bin)**, and they differ in how they combine the solution vectors.

| Crossover Type   | Description                                                                                                                                                                                                                                                                                                                        |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| bin(Binomial)    | works by *independently deciding for each dimension of the individual* whether it will come from the base individual or the mutated individual. The decision is based on a fixed probability. This tends to result in **more conservative changes**, focusing on refining the solution instead of exploring drastically new areas. |
| exp(Exponential) | involves combining the base and mutated individuals across several dimensions. The offspring is created by *progressively swapping parts of the target vector with the mutant vector*. This crossover typically leads to **more aggressive changes** and is suited for exploring new areas.                                        |
