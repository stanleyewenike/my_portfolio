# Day 6 - More Exercises & Data Types
# Five-minute Daily Python Pulse - Day 6

# Discovering types
x = 42
y = 3.14
z = "Hello"

print(type(x))  # int
print(type(y))  # float
print(type(z))  # str

# String comparison
print("banana" < "cherry")  # True, because 'b' comes before 'c'

# Number compression example (integer division)
total_seconds = 5000
minutes = total_seconds // 60
seconds = total_seconds % 60
print(f"{total_seconds} seconds = {minutes} minutes and {seconds} seconds")

# Mini bot: responds to favourite language
fav_lang = "Python"
if fav_lang.lower() == "python":
    print("Great choice! ")
else:
    print("Interesting! But have you tried Python? ")
