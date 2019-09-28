#include <idc.idc>

extern logfile;

static main() {
    auto name, addr, prev, first, end, inst, wid, pid, size, target;
    name = get_root_filename();

    logInit(name);
    logWrite("digraph G {\nnode[shape=rectangle,style=filled,fillcolor=lightsteelblue,color=lightsteelblue]\nbgcolor=\"transparent\"graph [label=\"label\", labelloc=t, fontsize=35, pad=30]\n");
    //logWrite("----------CFA of "+name+"----------\n");

    Message("%s\n",name);
    first = GetFunctionAttr(ScreenEA(), FUNCATTR_START);
    prev = -1; //-1 = Not set

    //Create an array that will be used as a worklist stack
    wid = GetArrayId(name);
    DeleteArray(wid);
    wid = CreateArray(name);

    //Create a stack of previous labels
    pid = GetArrayId(name+"prev");
    DeleteArray(pid);
    pid = CreateArray(name+"prev");

    //Add first instruction to the stack
    SetArrayLong(wid,0,first);
    SetArrayLong(pid,0,prev);
    size = 1;

    while (size > 0) {
        //pop inst of the stack
        size = size - 1;
        inst = GetArrayElement(AR_LONG,wid,size);
        prev = GetArrayElement(AR_LONG,pid,size);

        Message("Current instruction: %x \n",inst);
        fprintf(logfile,"\"%x\"[label=\"%x\"];\n",inst,inst);
        //For all successors of inst
        for (target=Rfirst(inst) ; target!=BADADDR ; target=Rnext(inst,target)) {
            Message("RNext: %x -> %x\n", inst, target);
            fprintf(logfile,"\"%x\" -> \"%x\" [color=\"#000000\",label=\"%s\"];\n",inst,target,GetDisasm(inst));
            SetArrayLong(wid,size,target);
            SetArrayLong(pid,size,inst);
            size = size + 1;
        }
    }

    logWrite("}");
}

static logInit(n){
  logfile = fopen(n+"_IDA_CFA.dot", "w");
  if (logfile == 0)
    return 0;
  return -1;
}

static logWrite(str){
  if (logfile != 0)
    return fprintf(logfile, "%s", str);
  return -1;
}
