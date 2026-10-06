# Carpet cost program

# -------------------------
# Subprograms
# -------------------------
def carpet_cost(width, length, price):
    carpet = width * length * price
    grippers = width + length
    fitting = 50
    underlay = width * length * 2
    return carpet + grippers + fitting + underlay

# -------------------------
# Main program
# -------------------------

width = int(input("Enter the width of the room to nearest meter: "))
length = int(input("Enter the length of the room to nearest meter: "))
price = float(input("Enter the price of the carpet per m2 in £: "))
print("The total cost is: £" +  str(carpet_cost(width, length, price)))
