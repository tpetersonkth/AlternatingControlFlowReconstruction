package org.jakstab.cfa;

import org.jakstab.asm.AbsoluteAddress;
import org.jakstab.util.Logger;

public class ConcreteCFAEdge implements Comparable<ConcreteCFAEdge> {

    @SuppressWarnings("unused")
    private static final Logger logger = Logger.getLogger(CFAEdge.class);

    private AbsoluteAddress source;
    private AbsoluteAddress target;

    public ConcreteCFAEdge(AbsoluteAddress source, AbsoluteAddress target) {
        super();
        assert (source != null && target != null) : "Cannot create edge with dangling edges: " + source + " -> " + target;
        this.source = source;
        this.target = target;
    }

    public AbsoluteAddress getSource() {
        return source;
    }

    public AbsoluteAddress getTarget() {
        return target;
    }

    public void setSource(AbsoluteAddress source) {
        this.source = source;
    }

    public void setTarget(AbsoluteAddress target) {
        this.target = target;
    }

    @Override
    public String toString() {
        return source + " -> " + target;
    }

    @Override
    public int compareTo(ConcreteCFAEdge o) {
        int c = source.compareTo(o.source);
        if (c != 0) return c;
        c = target.compareTo(o.target);
        if (c != 0) return c;

        //If target and source is the same, return 0
        return 0;
    }

}
