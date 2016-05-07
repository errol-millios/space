import pstats

p = pstats.Stats('prof.txt')
# p.strip_dirs().sort_stats('cumulative').print_stats()
p.print_callees()
