# Day 4 - Booleans, Comparisons, and f-Strings
# Five-minute Daily Python Pulse - Day 4

# Boolean values
is_python_fun = True
is_java_fun = False

# Equality and inequality
print(5 == 5)      # True
print(5 != 3)      # True

# Greater than / less than
print(10 > 5)      # True
print(2 < 1)       # False

# Boolean negation
print(not True)    # False
print(not False)   # True

# Compound boolean with negation
x = 5
y = 10
print(not (x < y and y > 0))  # Negating a compound expression

# f-strings
name = "Stan"
age = 35
print(f"Hello, my name is {name} and I am {age} years old.")

# Advanced: f-string with a calculation
print(f"Next year, I will be {age + 1} years old")
