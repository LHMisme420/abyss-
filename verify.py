import sympy

def analyze_gaps(limit=1_000_000):
    primes = list(sympy.primerange(2, limit))
    gaps = [primes[i+1] - primes[i] for i in range(len(primes)-1)]
    
    count10 = gaps.count(10)
    count12 = gaps.count(12)
    print(f"gap 10: {count10}   gap 12: {count12}   surplus: {100*(count10/count12-1):.2f}%")
    
    start10 = [primes[i] % 3 for i in range(len(gaps)) if gaps[i]==10]
    start12 = [primes[i] % 3 for i in range(len(gaps)) if gaps[i]==12]
    print(f"g=10 starters ≡1 mod3: {100*start10.count(1)/len(start10):.2f}%")
    print(f"g=12 starters ≡2 mod3: {100*start12.count(2)/len(start12):.2f}%")
    
    multiples_of_6 = [g for g in set(gaps) if g % 6 == 0 and g > 0]
    counts = [gaps.count(g) for g in multiples_of_6]
    rho = [c/g for c,g in zip(counts, multiples_of_6)]
    print(f"Decay 6→12: {rho[0]/rho[1]:.4f}")
    print(f"Decay 12→18: {rho[1]/rho[2]:.4f}")

analyze_gaps()
