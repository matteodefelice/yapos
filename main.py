import yapos
import sys

sim = yapos.problem(sys.argv[1], sys.argv[2])

sim.solve()
