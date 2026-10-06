student = input("What is the student's name?")
Mark = int(input("What is their mark?"))
PassorFail = input("Enter p for pass and f for fail for the student.")
Effort = input("What was their effort enter 1 for most and 4 for least and any number in the middle.")


if PassorFail == "p" and Effort == "1":
    print("Give them a praise and Commendation.")

elif PassorFail == "p" or Effort == "1":
    print("Give them a Praise.")
else:
    print(student,"must work harder")
