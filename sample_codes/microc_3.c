int main() {
    int a, b, c, d;
    a = 0;
    d = 1;
    b = 17;
    c = 8;
    if(a == c)
        c = 15;
    else
        c = 62;
    d = a + b;
    a = b - c;
    c = a * b;
    return c;
}