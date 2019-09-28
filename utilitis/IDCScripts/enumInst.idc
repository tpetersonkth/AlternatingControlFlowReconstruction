#include <idc.idc>

/*
 * This is an ida plugin which extracts a control flow automata from the IDA analysis
 * Author: Thomas Peterson
 * Year: 2019
 */

extern outputFile;
extern TRUE;
extern FALSE;

static main() {
    auto name, addr, prev, first, end, inst, wid, pid, size, target;
    TRUE = 0;
    FALSE = 1;

    name = get_root_filename();

    auto nodes = "";
    auto edges = "";

    auto filename = name+"_IDA_CFA.dot";
    outputFile = fopen(filename, "w");
    fprintf(outputFile,"digraph G {\nnode[shape=rectangle,style=filled,fillcolor=lightsteelblue,color=lightsteelblue]\nbgcolor=\"transparent\"graph [label=\"label\", labelloc=t, fontsize=35, pad=30]\n");

    first = GetFunctionAttr(ScreenEA(), FUNCATTR_START);//TODO: Check if there is a better way to get first instruction

    //Create the worklist stack
    auto worklist = Stack(name);

    //Add first instruction to the stack
    worklist.push(first);

    while (worklist.getSize() > 0) {
        //pop inst of the stack
        inst = worklist.pop();

        nodes = nodes + sprintf("\"%x\"[label=\"%x\"];\n",inst,inst);

        //For all successors of inst
        for (target=Rfirst(inst) ; target!=BADADDR ; target=Rnext(inst,target)) {
            edges = edges + sprintf("\"%x\" -> \"%x\" [color=\"#000000\",label=\"%s\"];\n",inst,target,GetDisasm(inst));
            worklist.push(target);
        }
    }

    fprintf(outputFile,nodes+edges+"}");

    Message("\nThe CFA was exported to "+filename)+"\n";
}

class Stack{
    Stack(name){
        this.name = name;
        this.size = 0;
        this.unique = 0;

        auto oldwid = GetArrayId(name);
        DeleteArray(oldwid);
        this.wid = CreateArray(name);

        auto oldVisited = GetArrayId(name+"visited");
        DeleteArray(oldVisited);
        this.visited = CreateArray(name+"visited");

    }
    ~Stack(){
    }
    push(inst){
        if (this.visited(inst)==FALSE){
            SetArrayLong(this.wid,this.size,inst);
            this.size = this.size + 1;

            SetArrayLong(this.visited,this.unique,inst);
            this.unique = this.unique + 1;
        }
    }
    pop(){
        this.size = this.size - 1;
        return GetArrayElement(AR_LONG,this.wid,this.size);
    }
    visited(inst){
        //Returns TRUE if the inst has ever been pushed to the stack. FALSE otherwise
        auto curr, count;
        for (count=0; count<this.unique ; count=count+1) {
            curr = GetArrayElement(AR_LONG,this.visited,count);
            if (curr == inst){
                return TRUE;
            }
        }
        //Message("%x!=%x\n",inst,curr);
        return FALSE;
    }
    getSize(){
        return this.size;
    }
};