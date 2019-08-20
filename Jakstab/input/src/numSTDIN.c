#include <stdio.h>
#include <stdlib.h>  // for strtol

int main(int argc, char *argv[]){
        // printf() displays the string inside quotation
        char buffer;
        read(0, &buffer, sizeof(char));

        int x = (int) (buffer-48);

        if(x > 5){
                printf("x is more than 5\n");
        }
        else{
                printf("x is less or equal to 5\n");
        }
        return 0;
}
