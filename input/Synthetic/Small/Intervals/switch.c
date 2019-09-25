
int calculate(int a, int b)
{
    switch(a) {
        case 0:
            b = b * b;
            break;
        case 1:
            b = b * -1;
            break;
        case 2:
            b = b + 128;
            break;
        case 3:
            b = b - 1;
            break;
        case 4:
            b = b + 1;
            break;
        case 5:
            b = b + a;
            break;
    }
    return b;
}

int main(){
    calculate(1,2);
}
