# ToDo
## Prima di lanciare i notebook dei singoli metodi
- [ ] Nel problema semplice e medio fare il problema **Stock** e **Force Golomb** (ovvero con reduce_fill_if_not_optimal=True) con tutti i plot
- [ ] Su tutti fare tutti i plot, ovvero
**print_result**(show_simulated_reconstruction=True)
**plot_fitness_improvement**() dare in ingresso un *vettore con le fitness calcolate ad ogni iterazione*
- [ ] Fare che ogni algoritmo viene lanciato **8 volte** sullo stesso problema in modo da mediare i risultati, Ad ogni iterazione:
    - mettere la nuova soluzione in un vettore in modo da **ottenere un vettore di soluzioni** \[\[soluzione prima iterazione\], \[soluzione seconda iterazione\], ...\] una volta finite le iterazioni passare il vettore a print_result
    - Calcolare la **media dei 5 vettori fitness** e passarla a plot_fitness_improvement

## Notebook aumento difficolta
- [ ] runnare il robo che incrementa il numero di satelliti, **usare la variabile range increase_nSats**, farlo con il problema stock

> ci dobbiamo coordinare per chi lo esegue prima perchè si modifica lo stesso file, notebook cringe 

### Dimensione generale
- **Grandezza popolazioni**: n_dimensioni * 3 (es nel semplice 5 satelliti => (5 * 6) * 3 = 90) se si sta facendo il problema con *Force Golomb* allora le iterazioni sono moltiplicate per 1.5
- **Numero iterazioni**: n_dimensioni * 10 (es nel semplice 5 satelliti => (5 * 6) * 3 = 300)

```python
def get_n_iteration(n_sats: int, force_golomb : bool = False):
    if force_golomb :
        return int(n_sats * 6 * 10 * 1.5)
    return n_sats * 6 * 10 

def get_population_size(n_sats: int):
    return n_sats * 6 * 3
```