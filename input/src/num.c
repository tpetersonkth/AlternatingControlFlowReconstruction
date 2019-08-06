#include <stdio.h>
#include <stdlib.h>  // for strtol

int main(int argc, char *argv[]){
        // printf() displays the string inside quotation
        char *p;
        int x = strtol(argv[1], &p, 10);

        printf("received argc=%d\n",argc);
        printf("received argv[0]=%s\n",argv[0]);
        printf("received x=%d\n",x);

        if(x > 10){
                printf("x is more than 10\n");
        }
        else{
                printf("x is less or equal to 10\n");
        }
        return 0;
}
