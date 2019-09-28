#include <idc.idc>

/*
 * This is an ida plugin which extracts a control flow automata from the IDA analysis
 * Author: Thomas Peterson
 * Year: 2019
 */

extern outputFile;

static main() {
    auto name, addr, prev, first, end, inst, wid, pid, size, target;
    name = get_root_filename();

    auto nodes = "";
    auto edges = "";

    outputFile = fopen(name+"_IDA_CFA.dot", "w");
    fprintf(outputFile,"digraph G {\nnode[shape=rectangle,style=filled,fillcolor=lightsteelblue,color=lightsteelblue]\nbgcolor=\"transparent\"graph [label=\"label\", labelloc=t, fontsize=35, pad=30]\n");
    //logWrite("----------CFA of "+name+"----------\n");

    first = GetFunctionAttr(ScreenEA(), FUNCATTR_START);//TODO: Check if there is a better way to get first instruction
    Message("First: %x\n",first);

    //Create the worklist stack
    auto worklist = Stack(name);

    //Add first instruction to the stack
    worklist.push(first);

    while (worklist.getSize() > 0) {
        //pop inst of the stack
        inst = worklist.pop();

        Message("Current instruction: %x: \n",inst);
        nodes = nodes + sprintf("\"%x\"[label=\"%x\"];\n",inst,inst);

        //For all successors of inst
        for (target=Rfirst(inst) ; target!=BADADDR ; target=Rnext(inst,target)) {
            Message("RNext: %x -> %x\n", inst, target);
            edges = edges + sprintf("\"%x\" -> \"%x\" [color=\"#000000\",label=\"%s\"];\n",inst,target,GetDisasm(inst));
            worklist.push(target);
        }
    }


    fprintf(outputFile,nodes+edges+"}");
}

class Stack{
    Stack(name){
        Message("Stack constructor has been called with %s ", name);
        this.name = name;
        this.size = 0;

        auto oldwid = GetArrayId(name);
        DeleteArray(oldwid);
        this.wid = CreateArray(name);

    }
    ~Stack(){
        print("Destructor of stack called");
    }
    push(inst){
        SetArrayLong(this.wid,this.size,inst);
        this.size = this.size + 1;
    }
    pop(){
        this.size = this.size - 1;
        return GetArrayElement(AR_LONG,this.wid,this.size);
    }
    getSize(){
        return this.size;
    }
};