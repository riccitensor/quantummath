import z3
import itertools

def find_directed_graph(n, enforce_axiom1=True, enforce_axiom2_prime=True, enforce_axiom_anti1483=True, k_default=2):
    s = z3.Solver()
    elements = list(range(n))

    is_high = [z3.Bool(f'is_high_{x}') for x in elements]
    is_low = [z3.Not(is_high[x]) for x in elements]

    edge = [[z3.Bool(f'edge_{x}_{y}') for y in elements] for x in elements]

    if enforce_axiom1:
        for a, b, c, d, e in itertools.product(elements, repeat=5):
            cond = z3.And(
                is_high[a],
                is_low[b],
                is_low[c],
                is_low[d],
                is_high[e],
                edge[a][b],
                edge[b][c],
                edge[c][d],
                edge[d][e],
                edge[e][a]
            )
            s.add(z3.Not(cond))

    if enforce_axiom2_prime:
        for x, y in itertools.product(elements, repeat=2):
            if x == y:
                continue
            possible_z = []
            for z in elements:
                path = z3.And(edge[x][z], edge[z][y])
                not_all_low = z3.Or(is_high[x], is_high[z], is_high[y])
                possible_z.append(z3.And(path, not_all_low))
            s.add(z3.Or(possible_z))

    if enforce_axiom_anti1483:
        modified_cycles = []
        for a, b, c, d, e in itertools.product(elements, repeat=5):
            cond = z3.And(
                is_high[a],
                is_low[b],
                is_low[c],
                is_low[d],
                is_high[e],
                edge[a][b],
                edge[b][c],
                edge[c][d],
                edge[e][d],
                edge[e][a]
            )
            modified_cycles.append(cond)
        if modified_cycles:
            s.add(z3.Or(modified_cycles))
        else:
            s.add(z3.BoolVal(False))

    high_high_edges = [z3.And(edge[x][y], is_high[x], is_high[y])
                       for x, y in itertools.product(elements, repeat=2) if x != y]
    s.add(z3.Or(high_high_edges))

    low_low_low_paths = []
    for x, y, z in itertools.product(elements, repeat=3):
        low_low_low_paths.append(z3.And(edge[x][y], edge[y][z], is_low[x], is_low[y], is_low[z]))
    s.add(z3.Or(low_low_low_paths))

    for x in elements:
        pass

    s.add(z3.Or(is_high))
    s.add(z3.Or(is_low))

    if k_default is not None:
        s.add(z3.Sum([z3.If(is_high[x], 1, 0) for x in elements]) <= k_default)

    return s, is_high, edge

def print_graph(model, is_high, edge, n):
    high_vertices = [x for x in range(n) if z3.is_true(model.evaluate(is_high[x]))]
    low_vertices = [x for x in range(n) if not z3.is_true(model.evaluate(is_high[x]))]

    print("\nVertex Classification:")
    print(f"High vertices: {high_vertices}")
    print(f"Low vertices: {low_vertices}")

    print("\nEdge List:")
    for x in range(n):
        for y in range(n):
            if x != y and z3.is_true(model.evaluate(edge[x][y])):
                print(f"{x} → {y}")

    print("\nAdjacency Matrix:")
    header = "   " + " ".join(f"{y:2}" for y in range(n))
    print(header)
    for x in range(n):
        row = " ".join(['1 ' if z3.is_true(model.evaluate(edge[x][y])) else '0 ' for y in range(n)])
        print(f"{x}: {row}")

def main():
    n_values = range(5, 10)
    for n in n_values:
        print(f"\n{'='*60}\nSearching for directed graphs of size {n} with the given constraints:")
        try:
            s, is_high, edge = find_directed_graph(
                n,
                enforce_axiom1=True,
                enforce_axiom2_prime=True,
                enforce_axiom_anti1483=True,
                k_default=min(2, n-1)
            )
        except ValueError as ve:
            print(f"Error for n={n}: {ve}")
            continue

        if s.check() == z3.sat:
            model = s.model()
            print(f"\nFound a satisfying directed graph for n={n}:")
            print_graph(model, is_high, edge, n)
        else:
            print(f"\nNo satisfying directed graph found for n={n} with the given constraints.")

if __name__ == "__main__":
    main()
