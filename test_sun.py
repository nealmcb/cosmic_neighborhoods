from astropy.coordinates import get_sun
from astropy.time import Time
import astropy.units as u

# Test winter solstice
date = Time('1957-12-21')
sun = get_sun(date)
ra = sun.ra.to_value(u.deg)
print(f'Sun RA: {ra:.6f}°')
print(f'Assigned RA: {(ra + 180.0) % 360.0:.6f}°')

