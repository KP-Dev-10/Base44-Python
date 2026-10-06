# Get age from user
age = int(input("Enter the age of the person: "))

# Calculate price based on conditions
if age >= 60:
    price = 9
elif 13 <= age <= 17:
    price = 6
elif age < 12:
    price = 4
else:
    price = 12

# Output the result
print(f"The ticket price is: £{price}")
