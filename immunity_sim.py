from simpleenvironment import Environment

def main():
    genome_length = 10
    envir = Environment(
        population_size=10,
        survival_chance=0.5,
        immunity_increase_factor=0.45 / genome_length,
        mutation_chance=0.1,
        chromosome_length=genome_length,
        immune_gene='Z',
        initial_immune=True,
        max_displayed=50
    )
    print(envir)
    envir.advance_gen(
        num_gens=100,
        population_control=True,
        max_size=5000
    )

if __name__ == '__main__':
    main()
