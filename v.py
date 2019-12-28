#!/usr/bin/env python3
import vaex
df = vaex.example()
df.plot(df.x, df.y, show=True)
