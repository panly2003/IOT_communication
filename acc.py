p = 'qhEuVlMDgPluBpuyKYFrYOiLpAOZUCCDXMXqjweSTaIwwWunPGGoAOTvbrSciepjWOeljKCBUPcfOsnAOJKQHcKQjWrQYLKCvEQVAwOEknAOWnGXPAA'
g = 'qhEuVlMDgPluBpuyKYFrYOiLAAOZUCCDXMXqjweSTaIwwWunPGGAAOTvbrSciepjWOeljKCBUPcfOsAAOJKQHcKQjWrQYLKCvEQVAwOEkAAOWnGXAAA'

corr = 0
for i in range(len(p)):
    if p[i] == g[i]:
        corr += 1
print(corr / len(p))