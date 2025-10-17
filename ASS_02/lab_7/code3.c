// grades.c: A program to calculate and analyze student grades.
// All logic is contained within the main function for single-function analysis.

#include <stdio.h>
#include <string.h>

#define MAX_STUDENTS 50
#define NUM_SUBJECTS 5
#define PASS_MARK 40.0

int main() {
    int num_students = 0;
    
    // Data storage arrays
    int student_ids[MAX_STUDENTS];
    char student_names[MAX_STUDENTS][100];
    float scores[MAX_STUDENTS][NUM_SUBJECTS];
    float total_scores[MAX_STUDENTS];
    float average_scores[MAX_STUDENTS];
    char grades[MAX_STUDENTS]; // A, B, C, D, F
    
    char subject_names[NUM_SUBJECTS][20] = {"Math", "Science", "History", "English", "Art"};
    int i, j; // Loop counters

    printf("======================================\n");
    printf(" Student Grade Calculation System \n");
    printf("======================================\n");

    // --- Part 1: Data Entry ---
    printf("\nEnter the total number of students to process (max %d): ", MAX_STUDENTS);
    int input_status = scanf("%d", &num_students);

    // Input validation
    if (input_status != 1 || num_students <= 0 || num_students > MAX_STUDENTS) {
        printf("Invalid input. Please enter a number between 1 and %d.\n", MAX_STUDENTS);
        printf("Exiting program.\n");
        return 1; // Indicate error
    }

    printf("\n--- Begin Data Entry for %d Students ---\n", num_students);
    for (i = 0; i < num_students; i++) {
        printf("\n---\n");
        printf("Enter details for Student #%d:\n", i + 1);
        student_ids[i] = 1001 + i; // Assign a unique ID

        printf("  Enter name: ");
        scanf("%s", student_names[i]);

        printf("  Enter scores for %s:\n", student_names[i]);
        total_scores[i] = 0; // Initialize total score for the student
        
        for (j = 0; j < NUM_SUBJECTS; j++) {
            printf("    -> Score for %s: ", subject_names[j]);
            float temp_score;
            if (scanf("%f", &temp_score) != 1) {
                printf("    Invalid score format. Defaulting to 0.\n");
                temp_score = 0;
                while(getchar() != '\n'); // Clear buffer
            }

            // Score validation
            if (temp_score < 0.0) {
                printf("    Score cannot be negative. Setting to 0.\n");
                scores[i][j] = 0.0;
            } else if (temp_score > 100.0) {
                printf("    Score cannot be over 100. Setting to 100.\n");
                scores[i][j] = 100.0;
            } else {
                scores[i][j] = temp_score;
            }
            total_scores[i] += scores[i][j];
        }
    }

    // --- Part 2: Calculations ---
    printf("\n--- Processing all student data... ---\n");
    for (i = 0; i < num_students; i++) {
        // Calculate average score
        average_scores[i] = total_scores[i] / NUM_SUBJECTS;
        
        // Determine grade using an if-else-if ladder
        if (average_scores[i] >= 90.0) {
            grades[i] = 'A';
        } else if (average_scores[i] >= 80.0) {
            grades[i] = 'B';
        } else if (average_scores[i] >= 70.0) {
            grades[i] = 'C';
        } else if (average_scores[i] >= 60.0) {
            grades[i] = 'D';
        } else {
            grades[i] = 'F';
        }
    }
    printf("Calculations complete.\n");

    // --- Part 3: Display Results Table ---
    printf("\n=========================================================================================\n");
    printf("                             STUDENT PERFORMANCE REPORT\n");
    printf("=========================================================================================\n");
    printf("%-5s | %-15s |", "ID", "Name");
    // Print subject headers dynamically
    for (j = 0; j < NUM_SUBJECTS; j++) {
        printf(" %-7s |", subject_names[j]);
    }
    printf(" %-8s | %-8s | %-5s\n", "Total", "Average", "Grade");
    printf("-----------------------------------------------------------------------------------------\n");

    for (i = 0; i < num_students; i++) {
        printf("%-5d | %-15s |", student_ids[i], student_names[i]);
        for (j = 0; j < NUM_SUBJECTS; j++) {
            printf(" %-7.2f |", scores[i][j]);
        }
        printf(" %-8.2f | %-8.2f | %-5c\n", total_scores[i], average_scores[i], grades[i]);
    }
    printf("=========================================================================================\n");


    // --- Part 4: Class Analytics ---
    printf("\n--- CLASS ANALYTICS ---\n");
    float class_total_score = 0.0;
    int pass_count = 0;
    int fail_count = 0;
    float highest_avg = 0.0;
    float lowest_avg = 100.0;
    char top_student[100] = "N/A";
    char bottom_student[100] = "N/A";
    int grade_counts[5] = {0, 0, 0, 0, 0}; // A, B, C, D, F

    if (num_students > 0) {
        // Loop to perform analytics
        for (i = 0; i < num_students; i++) {
            class_total_score += average_scores[i];

            // Check pass/fail status
            int failed_subjects = 0;
            for (j = 0; j < NUM_SUBJECTS; j++) {
                if (scores[i][j] < PASS_MARK) {
                    failed_subjects++;
                }
            }
            // A student fails if they fail in more than 2 subjects OR their grade is F
            if (failed_subjects > 2 || grades[i] == 'F') {
                fail_count++;
            } else {
                pass_count++;
            }
            
            // Find highest and lowest scores
            if (average_scores[i] > highest_avg) {
                highest_avg = average_scores[i];
                strcpy(top_student, student_names[i]);
            }
            if (average_scores[i] < lowest_avg) {
                lowest_avg = average_scores[i];
                strcpy(bottom_student, student_names[i]);
            }
            
            // Count grades
            if (grades[i] == 'A') {
                grade_counts[0]++;
            } else if (grades[i] == 'B') {
                grade_counts[1]++;
            } else if (grades[i] == 'C') {
                grade_counts[2]++;
            } else if (grades[i] == 'D') {
                grade_counts[3]++;
            } else if (grades[i] == 'F') {
                grade_counts[4]++;
            }
        }
        
        float class_average = class_total_score / num_students;
        printf("Class Average Score: %.2f\n", class_average);
        printf("Number of Students Passed: %d\n", pass_count);
        printf("Number of Students Failed: %d\n", fail_count);
        printf("Highest Average Score: %.2f (Achieved by %s)\n", highest_avg, top_student);
        printf("Lowest Average Score:  %.2f (Achieved by %s)\n", lowest_avg, bottom_student);

        printf("\nGrade Distribution:\n");
        printf("  'A' Grades: %d\n", grade_counts[0]);
        printf("  'B' Grades: %d\n", grade_counts[1]);
        printf("  'C' Grades: %d\n", grade_counts[2]);
        printf("  'D' Grades: %d\n", grade_counts[3]);
        printf("  'F' Grades: %d\n", grade_counts[4]);

    } else {
        printf("No student data to analyze.\n");
    }

    printf("\n--- End of Report ---\n\n");

    return 0;
}