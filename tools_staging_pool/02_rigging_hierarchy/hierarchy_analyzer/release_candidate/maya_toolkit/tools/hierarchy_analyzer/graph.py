"""Pure deterministic graph algorithms; cycles are diagnostics, never fake sorted nodes."""


def reachable(graph, start):
    pending = list(graph.get(start, ()))
    visited = set()
    while pending:
        n = pending.pop()
        if n in visited:
            continue
        visited.add(n)
        pending.extend(graph.get(n, ()))
    return visited


def project(graph, nodes):
    selected = set(nodes)
    return {n: reachable(graph, n)&selected for n in nodes}


def components(graph, nodes):
    # Iterative Kosaraju, safe for long production joint chains.
    selected = set(nodes)
    seen, order = set(), []
    for start in nodes:
        if start in seen:
            continue
        stack = [(start, False)]
        while stack:
            n, finish = stack.pop()
            if finish:
                order.append(n)
                continue
            if n in seen:
                continue
            seen.add(n)
            stack.append((n, True))
            stack.extend((c, False) for c in reversed(sorted(graph.get(n, set())&selected)) if c not in seen)
    reverse = {n: set() for n in nodes}
    for n in nodes:
        for c in graph.get(n, set())&selected:
            reverse[c].add(n)
    seen, groups = set(), []
    rank = {n: i for i, n in enumerate(nodes)}
    for start in reversed(order):
        if start in seen:
            continue
        group, pending = [], [start]
        while pending:
            n = pending.pop()
            if n in seen:
                continue
            seen.add(n)
            group.append(n)
            pending.extend(reverse[n]-seen)
        groups.append(sorted(group, key=rank.get))
    return sorted(groups, key=lambda x: min(rank[n] for n in x))


def layers(graph, nodes):
    selected = set(nodes)
    incoming = {n: 0 for n in nodes}
    for n in nodes:
        for c in graph.get(n, set())&selected:
            incoming[c] += 1
    remaining, result = set(nodes), []
    while remaining:
        layer = [n for n in nodes if n in remaining and incoming[n] == 0]
        if not layer:
            break
        result.append(layer)
        remaining.difference_update(layer)
        for n in layer:
            for c in graph.get(n, set())&selected:
                incoming[c] -= 1
    cycles = [g for g in components(graph, nodes) if len(g) > 1 or g[0] in graph.get(g[0], set())]
    return {'layers': result, 'unresolved': [n for n in nodes if n in remaining], 'cycles': cycles, 'valid': not remaining}


def verify(graph, ordered_layers, nodes):
    flattened = [n for group in ordered_layers for n in group]
    if len(flattened) != len(set(flattened)) or set(flattened) != set(nodes):
        return False
    rank = {n: i for i, group in enumerate(ordered_layers) for n in group}
    return all(rank[a] < rank[b] for a in nodes for b in graph.get(a, set()) if b in rank)
