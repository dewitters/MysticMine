#!/usr/bin/env python

import cProfile
import pstats
import monorail

cProfile.run('monorail.main()', 'profile.txt')

p = pstats.Stats('profile.txt')
p.strip_dirs()

p.sort_stats("cumulative")
p.print_stats(50)

p.sort_stats("time")
p.print_stats(20)



