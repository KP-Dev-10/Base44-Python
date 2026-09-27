# Ride height program

# -------------------------
# Subprograms
# -------------------------
def valid_height(height):
    if height < 91:
        return True
    else:
        return False
    
# -------------------------
# Main program
# -------------------------
height = float(input("Enter the height of the person in cm: "))
if valid_height(height):
    print("Height OK.")
else:
    print("Sorry, you are too big.")
