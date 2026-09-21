"""Prereg §5.1: exact, geometry-preserving, non-identity null populations by predicate relabeling.

A relabeling is a permutation sigma of the predicate vocabulary applied to every family: F_i' = sigma[F_i]. Family sizes,
total membership multiplicity and the full pairwise-overlap structure are identical by construction. The domain-structured
null restricts sigma to permute predicates only within relational-domain blocks. Two permutations that induce the same
cover (they differ only on predicates with identical membership signature) are the same null member: covers are
canonicalized and deduplicated, and the identity cover is excluded. If the unique non-identity population is at or below
the requested count it is enumerated exhaustively; otherwise it is sampled uniformly (a uniformly random permutation
induces a uniform distribution over distinct covers, because every distinct cover corresponds to the same number of
permutations)."""
from __future__ import annotations
import random
from collections import Counter
from math import factorial
from typing import Any, Dict, Iterator, List, Tuple
from .models import Assignment, Family

Canon = Tuple[Tuple[str, ...], ...]


def canonical(assignment: Assignment) -> Canon:
    return tuple(tuple(sorted(f.predicates)) for f in assignment.families)


def relabel(assignment: Assignment, sigma: Dict[str, str]) -> Assignment:
    return Assignment([Family(name=f.name, predicates=frozenset(sigma[p] for p in f.predicates), boundary=frozenset(), criterion=f.criterion) for f in assignment.families])


def signatures(assignment: Assignment, vocab: List[str]) -> Dict[str, frozenset]:
    return {p: frozenset(f.name for f in assignment.families if p in f.predicates) for p in vocab}


def blocks_for(vocab: List[str], pred_domain: Dict[str, str] | None) -> List[List[str]]:
    if pred_domain is None:
        return [sorted(vocab)]
    doms = sorted(set(pred_domain[p] for p in vocab))
    return [sorted(p for p in vocab if pred_domain[p] == d) for d in doms]


def population_size(assignment: Assignment, vocab: List[str], pred_domain: Dict[str, str] | None) -> int:
    """Number of distinct covers reachable by (block-restricted) relabeling, including the identity."""
    sig = signatures(assignment, vocab)
    total = 1
    for block in blocks_for(vocab, pred_domain):
        mult = Counter(sig[p] for p in block)
        n = factorial(len(block))
        for m in mult.values():
            n //= factorial(m)
        total *= n
    return total


def _multiset_permutations(items: List[Any]) -> Iterator[Tuple[Any, ...]]:
    items = sorted(items, key=repr)
    n = len(items)
    def rec(prefix, remaining):
        if not remaining:
            yield tuple(prefix)
            return
        seen = set()
        for i, x in enumerate(remaining):
            key = repr(x)
            if key in seen:
                continue
            seen.add(key)
            yield from rec(prefix + [x], remaining[:i] + remaining[i + 1:])
    yield from rec([], items)


def enumerate_population(assignment: Assignment, vocab: List[str], pred_domain: Dict[str, str] | None) -> List[Assignment]:
    """Exhaustive enumeration of distinct non-identity covers (only used when the population is small)."""
    sig = signatures(assignment, vocab)
    blocks = blocks_for(vocab, pred_domain)
    identity = canonical(assignment)
    per_block = []
    for block in blocks:
        sigs = [sig[p] for p in block]
        per_block.append([dict(zip(block, arrangement)) for arrangement in _multiset_permutations(sigs)])
    out, seen = [], set()
    def rec(i, sig_map):
        if i == len(per_block):
            fams = [Family(name=f.name, predicates=frozenset(p for p, s in sig_map.items() if f.name in s), boundary=frozenset(), criterion=f.criterion) for f in assignment.families]
            a = Assignment(fams)
            c = canonical(a)
            if c != identity and c not in seen:
                seen.add(c); out.append(a)
            return
        for arrangement in per_block[i]:
            rec(i + 1, {**sig_map, **arrangement})
    rec(0, {})
    return out


def sample_population(assignment: Assignment, vocab: List[str], pred_domain: Dict[str, str] | None, n: int, seed: int, max_draws: int = 10_000_000) -> List[Assignment]:
    rng = random.Random(seed)
    blocks = blocks_for(vocab, pred_domain)
    identity = canonical(assignment)
    out, seen, draws = [], set(), 0
    while len(out) < n and draws < max_draws:
        draws += 1
        sigma = {}
        for block in blocks:
            perm = list(block)
            rng.shuffle(perm)
            sigma.update(dict(zip(block, perm)))
        a = relabel(assignment, sigma)
        c = canonical(a)
        if c == identity or c in seen:
            continue
        seen.add(c); out.append(a)
    if len(out) < n:
        raise RuntimeError(f"could not draw {n} unique non-identity covers in {max_draws} draws")
    return out


def build_null(assignment: Assignment, vocab: List[str], pred_domain: Dict[str, str] | None, n_requested: int, seed: int) -> Dict[str, Any]:
    pop = population_size(assignment, vocab, pred_domain)
    non_identity = pop - 1
    if non_identity <= n_requested:
        covers = enumerate_population(assignment, vocab, pred_domain)
        mode = "exhaustive"
    else:
        covers = sample_population(assignment, vocab, pred_domain, n_requested, seed)
        mode = "sampled"
    return {"mode": mode, "population_size_including_identity": pop, "population_size_non_identity": non_identity, "n_used": len(covers), "seed": seed, "covers": covers}
