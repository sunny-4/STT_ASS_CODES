// inventory.c: A simple command-line inventory management system.
// All logic is contained within the main function for intraprocedural analysis.

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define MAX_ITEMS 100
#define MAX_NAME_LENGTH 50

// Structure to define an inventory item
struct InventoryItem
{
    int id;
    char name[MAX_NAME_LENGTH];
    int quantity;
    double price;
    int in_stock; // 0 for no, 1 for yes
};

int main()
{
    struct InventoryItem inventory[MAX_ITEMS];
    int itemCount = 0;
    int nextId = 1;
    int choice = 0;

    // Pre-populate with some data for demonstration
    inventory[0].id = nextId++;
    strcpy(inventory[0].name, "Laptop");
    inventory[0].quantity = 15;
    inventory[0].price = 1200.50;
    inventory[0].in_stock = 1;
    itemCount++;

    inventory[1].id = nextId++;
    strcpy(inventory[1].name, "Mouse");
    inventory[1].quantity = 150;
    inventory[1].price = 25.00;
    inventory[1].in_stock = 1;
    itemCount++;

    inventory[2].id = nextId++;
    strcpy(inventory[2].name, "Keyboard");
    inventory[2].quantity = 0;
    inventory[2].price = 75.75;
    inventory[2].in_stock = 0;
    itemCount++;

    printf("============================================\n");
    printf(" Simple Inventory Management System \n");
    printf("============================================\n");

    // Main program loop
    while (choice != 5)
    {
        printf("\n--- Main Menu ---\n");
        printf("1. Add New Item\n");
        printf("2. Display All Items\n");
        printf("3. Search for an Item by ID\n");
        printf("4. Update Item Stock\n");
        printf("5. Exit\n");
        printf("-------------------\n");
        printf("Enter your choice: ");

        // Input validation
        if (scanf("%d", &choice) != 1)
        {
            printf("\nError: Invalid input. Please enter a number.\n");
            // Clear the input buffer to prevent an infinite loop
            while (getchar() != '\n')
                ;
            choice = 0; // Reset choice to continue loop
            continue;
        }

        // Switch statement to handle menu choices
        switch (choice)
        {
        case 1:
            // --- Add a new item ---
            printf("\n--- Add New Item ---\n");
            if (itemCount >= MAX_ITEMS)
            {
                printf("Error: Inventory is full. Cannot add more items.\n");
            }
            else
            {
                struct InventoryItem newItem;
                newItem.id = nextId++;

                printf("Enter item name: ");
                scanf("%s", newItem.name);

                printf("Enter quantity: ");
                if (scanf("%d", &newItem.quantity) != 1)
                {
                    printf("Invalid quantity input. Setting to 0.\n");
                    newItem.quantity = 0;
                    while (getchar() != '\n')
                        ;
                }

                printf("Enter price: ");
                if (scanf("%lf", &newItem.price) != 1)
                {
                    printf("Invalid price input. Setting to 0.0.\n");
                    newItem.price = 0.0;
                    while (getchar() != '\n')
                        ;
                }

                if (newItem.quantity > 0)
                {
                    newItem.in_stock = 1;
                }
                else
                {
                    newItem.in_stock = 0;
                }

                inventory[itemCount] = newItem;
                itemCount++;
                printf("Success: Item '%s' added to inventory.\n", newItem.name);
            }
            break;

        case 2:
            // --- Display all items ---
            printf("\n--- Full Inventory List ---\n");
            if (itemCount == 0)
            {
                printf("Inventory is empty.\n");
            }
            else
            {
                printf("------------------------------------------------------------------\n");
                printf("%-5s | %-20s | %-10s | %-10s | %-10s\n", "ID", "Name", "Quantity", "Price", "In Stock");
                printf("------------------------------------------------------------------\n");
                for (int i = 0; i < itemCount; i++)
                {
                    printf("%-5d | %-20s | %-10d | %-10.2f | %-10s\n",
                           inventory[i].id,
                           inventory[i].name,
                           inventory[i].quantity,
                           inventory[i].price,
                           inventory[i].in_stock ? "Yes" : "No");
                }
                printf("------------------------------------------------------------------\n");
            }
            break;

        case 3:
            // --- Search for an item ---
            printf("\n--- Search for Item by ID ---\n");
            if (itemCount == 0)
            {
                printf("Inventory is empty. Cannot search.\n");
            }
            else
            {
                int searchId;
                printf("Enter Item ID to search for: ");
                if (scanf("%d", &searchId) != 1)
                {
                    printf("Invalid ID format.\n");
                    while (getchar() != '\n')
                        ;
                    break;
                }

                int found = 0;
                for (int i = 0; i < itemCount; i++)
                {
                    if (inventory[i].id == searchId)
                    {
                        printf("\n--- Item Found ---\n");
                        printf("ID       : %d\n", inventory[i].id);
                        printf("Name     : %s\n", inventory[i].name);
                        printf("Quantity : %d\n", inventory[i].quantity);
                        printf("Price    : %.2f\n", inventory[i].price);
                        printf("In Stock : %s\n", inventory[i].in_stock ? "Yes" : "No");
                        printf("--------------------\n");
                        found = 1;
                        break;
                    }
                }

                if (!found)
                {
                    printf("Error: Item with ID %d not found.\n", searchId);
                }
            }
            break;

        case 4:
            // --- Update item stock ---
            printf("\n--- Update Item Stock ---\n");
            if (itemCount == 0)
            {
                printf("Inventory is empty. Cannot update.\n");
            }
            else
            {
                int updateId;
                printf("Enter Item ID to update: ");
                if (scanf("%d", &updateId) != 1)
                {
                    printf("Invalid ID format.\n");
                    while (getchar() != '\n')
                        ;
                    break;
                }

                int itemIndex = -1;
                for (int i = 0; i < itemCount; i++)
                {
                    if (inventory[i].id == updateId)
                    {
                        itemIndex = i;
                        break;
                    }
                }

                if (itemIndex != -1)
                {
                    int newQuantity;
                    printf("Current quantity for '%s' is %d. Enter new quantity: ", inventory[itemIndex].name, inventory[itemIndex].quantity);
                    if (scanf("%d", &newQuantity) != 1)
                    {
                        printf("Invalid quantity input. Update failed.\n");
                        while (getchar() != '\n')
                            ;
                        break;
                    }

                    if (newQuantity < 0)
                    {
                        printf("Error: Quantity cannot be negative. Update failed.\n");
                    }
                    else
                    {
                        inventory[itemIndex].quantity = newQuantity;
                        if (newQuantity > 0)
                        {
                            inventory[itemIndex].in_stock = 1;
                        }
                        else
                        {
                            inventory[itemIndex].in_stock = 0;
                        }
                        printf("Success: Stock for item ID %d updated to %d.\n", updateId, newQuantity);
                    }
                }
                else
                {
                    printf("Error: Item with ID %d not found.\n", updateId);
                }
            }
            break;

        case 5:
            // --- Exit ---
            printf("\nExiting the inventory system. Goodbye!\n\n");
            break;

        default:
            // --- Invalid choice ---
            printf("\nError: Invalid choice. Please select an option from 1 to 5.\n");
            break;
        }
    }

    return 0;
}