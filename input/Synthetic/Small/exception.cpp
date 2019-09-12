/*
A file containing a minimalistic exception in cpp.
cpa c: Gets stuck at ret instruction at address 0x000005d5
cpa cs: Can resolve the ret instruction c couldn't resolve but gets stuck at call 550 located at address 0x000005cc (? I don't know why..)
cpa b/i/x: Can resolve all
*/

int main()
{
   try {
        int x = 0;
        throw x;
   }
   catch (int x) {
   }
   return 0;
}

