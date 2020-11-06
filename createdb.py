#!/usr/bin/python3

import sqlite3

conn = sqlite3.connect('flightevents.db')

c = conn.cursor()

# Create table
c.execute('''CREATE TABLE observations
             (
             tstamp numeric,
             radioid text,
             aircraft_type int,
             lat double,
             lon double,
             relative_north int,
             relative_east int,
             relative_vertical int,
             track int,
             speed int,
             climb_rate double,
             PRIMARY KEY (tstamp, radioid)
             )''')


# Save (commit) the changes
conn.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()
