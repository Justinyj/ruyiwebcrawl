#include<stdio.h>
int *check(){
    int a[10];
    int i;
    for (i=0;i<10;i++) a[i]=0;
    return a;
}
int main(){
    int *a;
    a = check();
}