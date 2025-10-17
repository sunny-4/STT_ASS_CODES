// adventure.c: A simple text-based adventure game.
// All logic is contained within the main function to facilitate intraprocedural analysis.

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main() {
    int player_health = 100;
    int player_location = 0; // 0: Start, 1: Forest, 2: Cave, 3: Castle, 4: Treasure Room
    int has_sword = 0;
    int has_key = 0;
    int game_over = 0;
    int choice = 0;

    // Seed the random number generator
    srand(time(NULL));

    printf("*****************************************\n");
    printf("* WELCOME TO THE DRAGON'S LAIR     *\n");
    printf("*****************************************\n");
    printf("You are a brave adventurer seeking treasure.\n");
    printf("Your quest is to find the Dragon's gold without being defeated.\n");

    // Main game loop
    while (game_over == 0) {
        printf("\n-----------------------------------------\n");
        printf("Current Health: %d\n", player_health);
        printf("Inventory: %s %s\n", has_sword ? "[Sword]" : "", has_key ? "[Key]" : "");
        printf("-----------------------------------------\n");

        // Location-based logic using a switch statement
        switch (player_location) {
            case 0: // Starting Area: The Crossroads
                printf("You are at a crossroads. A dark forest lies to the north.\n");
                printf("To the east, you see the entrance to a damp cave.\n");
                printf("\nWhat do you do?\n");
                printf("1. Enter the forest.\n");
                printf("2. Explore the cave.\n");
                printf("3. Give up and go home.\n");
                printf("Your choice: ");
                scanf("%d", &choice);

                if (choice == 1) {
                    printf("\nYou decide to venture into the ominous forest.\n");
                    player_location = 1;
                } else if (choice == 2) {
                    printf("\nYou cautiously step into the dark, echoing cave.\n");
                    player_location = 2;
                } else if (choice == 3) {
                    printf("\nYour quest ends before it even begins. Farewell.\n");
                    game_over = 1;
                } else {
                    printf("\nInvalid choice. You stand still, confused.\n");
                }
                break;

            case 1: // The Forest
                printf("The forest is dark and full of strange noises.\n");
                printf("You stumble upon a rusty sword lying on the ground.\n");
                
                if (has_sword == 0) {
                     printf("\nWhat do you do?\n");
                     printf("1. Pick up the sword.\n");
                     printf("2. Ignore the sword and head towards a distant castle.\n");
                     printf("3. Return to the crossroads.\n");
                     printf("Your choice: ");
                     scanf("%d", &choice);
                    
                     if (choice == 1) {
                         printf("\nYou pick up the sword. It feels sturdy enough.\n");
                         has_sword = 1;
                     } else if (choice == 2) {
                         printf("\nYou leave the sword and press on towards the castle.\n");
                         player_location = 3;
                     } else if (choice == 3) {
                         printf("\nYou return to the safety of the crossroads.\n");
                         player_location = 0;
                     } else {
                         printf("\nInvalid choice. The forest's shadows play tricks on your mind.\n");
                     }
                } else {
                     printf("Having already found the sword, you see a path leading to a castle.\n");
                     printf("\nWhat do you do?\n");
                     printf("1. Follow the path to the castle.\n");
                     printf("2. Return to the crossroads.\n");
                     printf("Your choice: ");
                     scanf("%d", &choice);

                     if (choice == 1) {
                         printf("\nYou begin the long walk towards the castle.\n");
                         player_location = 3;
                     } else if (choice == 2) {
                         printf("\nYou feel the castle is too dangerous and return to the crossroads.\n");
                         player_location = 0;
                     } else {
                         printf("\nInvalid choice. You are momentarily lost.\n");
                     }
                }
                break;
            
            case 2: // The Cave
                printf("The cave is cold and wet. You hear a skittering sound.\n");
                printf("A giant spider attacks you!\n");

                if (has_sword == 1) {
                    printf("\nYou draw your sword and fight the spider!\n");
                    int fight_outcome = rand() % 2; // 50% chance of winning
                    if (fight_outcome == 1) {
                        printf("You successfully slay the spider!\n");
                        printf("Behind it, you find an old, ornate key.\n");
                        has_key = 1;
                        printf("With nothing else here, you decide to leave the cave.\n");
                        player_location = 0; // Return to crossroads
                    } else {
                        printf("The spider is too fast! It bites you before you can react.\n");
                        player_health -= 50;
                        printf("You take damage but manage to escape the cave.\n");
                        player_location = 0; // Return to crossroads
                    }
                } else {
                    printf("You are unarmed! The spider attacks and you barely escape.\n");
                    player_health -= 30;
                    printf("You stumble out of the cave, wounded.\n");
                    player_location = 0; // Return to crossroads
                }
                break;
            
            case 3: // The Castle
                printf("You have arrived at the gates of an ancient, imposing castle.\n");
                printf("A huge, locked door bars your way. It is guarded by a fearsome dragon!\n");

                printf("\nWhat do you do?\n");
                printf("1. Fight the dragon.\n");
                printf("2. Try to sneak past the dragon.\n");
                printf("3. Turn back and flee.\n");
                printf("Your choice: ");
                scanf("%d", &choice);

                if (choice == 1) {
                    if (has_sword == 1) {
                        printf("\nYou charge the dragon with your sword held high!\n");
                        int dragon_fight = rand() % 4; // 25% chance of winning
                        if (dragon_fight == 3) {
                            printf("By some miracle, you find a weak spot and defeat the dragon!\n");
                            printf("The door behind it is now unguarded.\n");
                             if (has_key == 1) {
                                printf("You use the key from the cave to unlock the door.\n");
                                player_location = 4;
                            } else {
                                printf("You defeated the dragon, but the door is locked and you have no key!\n");
                                printf("Frustrated, you leave.\n");
                                game_over = 1;
                            }
                        } else {
                            printf("The dragon breathes a torrent of fire. You are no match for it.\n");
                            player_health = 0;
                        }
                    } else {
                        printf("You try to fight the dragon with your bare hands. It is not effective.\n");
                        player_health = 0;
                    }
                } else if (choice == 2) {
                    printf("You try to sneak past the dragon...\n");
                    int sneak_outcome = rand() % 3; // 33% chance of success
                    if (sneak_outcome == 2) {
                        printf("You successfully sneak past the sleeping dragon!\n");
                        if (has_key == 1) {
                            printf("You use the key to quietly unlock the door.\n");
                            player_location = 4;
                        } else {
                            printf("You snuck past, but the door is locked and you can't open it.\n");
                            printf("You are forced to retreat.\n");
                            player_location = 0;
                        }
                    } else {
                        printf("The dragon wakes up and spots you! It attacks!\n");
                        player_health -= 70;
                        printf("You are badly burned but manage to escape the castle grounds.\n");
                        player_location = 0;
                    }
                } else if (choice == 3) {
                    printf("\nDiscretion is the better part of valor. You flee the castle.\n");
                    player_location = 1; // Flee back to the forest
                } else {
                    printf("\nParalyzed by fear, you do nothing.\n");
                }
                break;
                
            case 4: // Treasure Room
                printf("\n*****************************************\n");
                printf("You've found the treasure room! It's filled with gold and jewels.\n");
                printf("Congratulations, you have won the game!\n");
                printf("*****************************************\n");
                game_over = 1;
                break;
        }

        // Check for game over condition (player health)
        if (player_health <= 0) {
            printf("\nYour health has reached zero.\n");
            printf("You have been defeated.\n");
            printf("GAME OVER.\n");
            game_over = 1;
        }
    }

    printf("\n--- Final Stats ---\n");
    printf("Health: %d\n", player_health > 0 ? player_health : 0);
    printf("Location: %d\n", player_location);
    printf("Had Sword: %s\n", has_sword ? "Yes" : "No");
    printf("Had Key: %s\n", has_key ? "Yes" : "No");
    printf("-------------------\n");

    return 0;
}