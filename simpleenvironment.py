"""
- simulates population & disease
- population starts without immunity & has certain chance of dying
- mutate -> get a few random genes (letters of the alphabet)
- when deciding if die or not, if has immunity gene (e.g. Z), then chance of survival goes up
- second step: add gene that increases death chance
- can test with certain permutations of genes too (e.g. ZA)
- only ones that survive after each wave of plague can mate
    - advance gen: kill and then mate
- randomize mating, 0-3 children per pair (0 should have very low chance)

predictions:
- survival chance too low -> extinct, too high -> no one ever dies
- should eventually all have immunity gene
"""

import random

GENES = list('AXYZ')

class Organism(object):
    
    def __init__(self, chromosome):
        self.chromosome = chromosome
    
    @classmethod
    def random_gene(self):
        global GENES
        # return str(chr(random.randrange(ord('A'), ord('Z') + 1)))
        return random.choice(GENES)
    
    @classmethod
    def random_gene_no_immunity(self, immune_gene):
        if not type(immune_gene) is str:
            raise TypeError('immune needs to be of type - str')
        z = immune_gene
        while z == immune_gene:
            z = Organism.random_gene()
        return z
    
    @classmethod
    def create_organism(self, chromosome_length):
        return Organism([Organism.random_gene() for i in range(chromosome_length)])
    
    @classmethod
    def create_organism_no_immunity(self, chromosome_length, immune_gene):
        return Organism([Organism.random_gene_no_immunity(immune_gene) for i in range(chromosome_length)])
    
    def mate(self, parent2, mutation_chance):
        child = []
        for i in range(len(self.chromosome)):
            rand = random.random()
            if rand < (1 - mutation_chance) / 2:
                child.append(self.chromosome[i])
            elif rand < 1 - mutation_chance:
                child.append(parent2.chromosome[i])
            else:
                child.append(Organism.random_gene())
        return Organism(child)
    
    def __repr__(self):
        return ''.join(self.chromosome)

class Environment(object):
    
    def __init__(self, population_size, survival_chance, immunity_increase_factor, mutation_chance, chromosome_length, immune_gene, initial_immune=False, max_displayed=50):
        if len(immune_gene) != 1:
            raise TypeError("immune gene needs to be of length 1")
        self.generation = 0
        self.chromosome_length = chromosome_length
        if initial_immune:
            self.population = [Organism.create_organism(chromosome_length) for i in range(population_size)]
        else:
            self.population = [Organism.create_organism_no_immunity(chromosome_length, immune_gene) for i in range(population_size)]
        self.survival_chance = survival_chance
        self.immunity_increase_factor = immunity_increase_factor
        self.mutation_chance = mutation_chance
        self.immune_gene = immune_gene
        self.total_immune_genes = self.count_immune()
        self.max_displayed = max_displayed
    
    
    def count_immune(self):
        sum = 0
        for org in self.population:
            sum += org.chromosome.count(self.immune_gene)
        return sum
    
    def step_gen(self, num_gens=1, population_control=False, max_size=None, purge_factor=0.5):
        if population_control and max_size is None:
            raise ValueError("max_size must be specified if population_control is True")
        for i in range(num_gens):
            self.total_immune_genes = 0
            new_pop = []
            for org in self.population:
                count_immune_genes = org.chromosome.count(self.immune_gene)
                s_chance = self.survival_chance + count_immune_genes * self.immunity_increase_factor
                rand = random.random()
                if rand < s_chance:
                    new_pop.append(org)
                    self.total_immune_genes += count_immune_genes
            parent_size = len(new_pop)
            pairs = [i for i in range(len(new_pop))]
            while len(pairs) > 1:
                parent1 = new_pop[pairs.pop(random.randrange(len(pairs)))]
                parent2 = new_pop[pairs.pop(random.randrange(len(pairs)))]
                num_children = random.randrange(1, 4)
                if random.random() < 0.1:
                    num_children = 0
                for i in range(num_children):
                    child = parent1.mate(parent2, self.mutation_chance)
                    new_pop.append(child)
                    self.total_immune_genes += child.chromosome.count(self.immune_gene)
            self.population = new_pop
        if population_control and len(self.population) >= max_size:
            self.sort()
            while len(self.population) >= max_size:
                incr = int(1 / purge_factor)
                self.purge(increment=incr if incr > 1 else 2)
        self.generation += num_gens
    
    def advance_gen(self, num_gens=1, population_control=False, max_size=None, purge_factor=0.5):
        for i in range(num_gens):
            self.step_gen(population_control=population_control, max_size=max_size, purge_factor=purge_factor)
            print(self)
            print()
    
    def sort(self):
        self.population = sorted(self.population, key=lambda x: -x.chromosome.count(self.immune_gene))
    
    def purge(self, increment=2):
        for i in range(len(self.population) - 1, -1, -increment):
            self.total_immune_genes -= self.population[i].chromosome.count(self.immune_gene)
            del self.population[i]
    
    def __repr__(self):
        self.sort()
        rev = self.population.copy()
        rev.reverse()
        num_displayed = self.max_displayed if len(self.population) >= self.max_displayed else len(self.population)
        return 'Generation {}:\nTotal Immune Genes: {} ({}%), Population Size: {}\nStrongest {}: {}\nWeakest {}: {}'.format(
            self.generation, self.total_immune_genes, 'N/A' if len(self.population) < 1 else int(self.total_immune_genes / (len(self.population) * self.chromosome_length) * 100),
            len(self.population), num_displayed, str(self.population[:num_displayed]), num_displayed, str(rev[:num_displayed])
        )
