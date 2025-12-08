"""
Day 2 — Variables
Goal: create variables, follow naming conventions, peek at constants.
"""

# Basic string variables
city = "Miami"
device_type = "apple"      # just a string label, not the company 
movie_quote = "Winter is coming."

# Naming: use snake_case for regular variables
preferred_language = "Python"

# Constants: by convention, UPPER_CASE (not enforced by Python)
PI_APPROX = 3.14
APP_NAME = "Five-Minute Daily Python Pulse"

# Using variables
print(city)                        # -> Miami
print(f"My device is an {device_type}")
print(f"Quote of the day: {movie_quote}")

# A tiny (optional) step further: check the type
print(type(city))                  # -> <class 'str'>

# Comments explain *why* not just *what*
# Next micro-step: add more examples with numbers, booleans, and inline comments.
