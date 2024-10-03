#include <stdio.h>
#define _CRT_SECURE_NO_WARNINGS

int main() {
    char name[20];
    printf("Enter your name : ");
    scanf("%s", name);
    printf("Hello %s", name);
    return 0;
}