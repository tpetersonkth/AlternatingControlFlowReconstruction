#Compile
nasm -f elf helloworld.s
ld -m elf_i386 -s -o hello helloworld.o
