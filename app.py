categories = ["Rent", "Bills", "Food", "Gas", "Entertainment"]

while True:
    print("\n" + "="*50)
    print("Welcome to Team 4's Spending Tracker Application!")
    print("="*50 + "\n")
    
    # Get expense category
    valid = False
    while valid == False:
        print("Spending Categories:")
        print("1. Rent")
        print("2. Bills")
        print("3. Food")
        print("4. Gas")
        print("5. Entertainment")
        
        choice = input("\nEnter category (1-5): ")
        
        if choice == "1":
            category = "Rent"
            valid = True
        elif choice == "2":
            category = "Bills"
            valid = True
        elif choice == "3":
            category = "Food"
            valid = True
        elif choice == "4":
            category = "Gas"
            valid = True
        elif choice == "5":
            category = "Entertainment"
            valid = True
        else:
            print("Invalid choice. Please enter 1-5.\n")
    
    # Get expense amount
    valid = False
    while valid == False:
        try:
            amount = float(input("Enter expense amount (in dollars): $"))
            if amount < 0:
                print("Amount must be positive.\n")
            else:
                amount = round(amount, 2)
                valid = True
        except:
            print("Invalid amount. Please enter a number.\n")
    
    # Display the entry
    print("\n" + "-"*50)
    print("Expense Entry:")
    print("Category: " + category)
    print("Amount: $" + str(amount))
    print("-"*50 + "\n")
    
    # Ask to continue
    again = input("Add another expense? (yes/no): ")
    if again == "no" or again == "n":
        print("\nThank you for using Team 4's Spending Tracker Application!")
        break