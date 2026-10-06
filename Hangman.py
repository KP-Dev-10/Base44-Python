import random

print("time to play hangman")
animals = ("rabbit", "dog", "cat", "frog", "mouse", "lizard", "horse")
secret = random.choice(animals)
guesses = 'aeiou'
turns = 5

while turns > 0:
    missed = 0
    for letter in secret:
        if letter in guesses:
            print(letter,end= " ")
        else:
            print("_",end=" ")
            missed = missed +1
    print("")

    if missed == 0:
         print("You win!")
         break

    guess = input("guess a letter:  ")
    guesses = guesses + guess


    if guess not in secret:
        turns = turns - 1
        print("Not correct")
        print(turns, "more turns")
        if turns < 5: print("  0 ")
        if turns < 4: print("\_1_/")
        if turns < 3: print("  1 ")
        if turns < 2: print(" d b")
        if turns ==0:
            print("The answer is ",secret)
