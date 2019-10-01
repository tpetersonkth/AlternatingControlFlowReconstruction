package org.jakstab.cfa;

import org.jakstab.asm.AbsoluteAddress;
import org.jakstab.util.Logger;

import java.util.Collections;
import java.util.HashSet;
import java.util.Set;

public class ConcreteControlFlowGraph {

    private static final Logger logger = Logger.getLogger(ConcreteControlFlowGraph.class);
    ;
    private Set<AbsoluteAddress> locations;
    private Set<ConcreteCFAEdge> edges;

    protected ConcreteControlFlowGraph() {
        locations = new HashSet<AbsoluteAddress>();
        edges = new HashSet<ConcreteCFAEdge>();
    }

    public ConcreteControlFlowGraph(Set<CFAEdge> edges) {
        this();
        buildFromEdgeSet(edges);
    }

    public Set<ConcreteCFAEdge> getEdges() {
        return Collections.unmodifiableSet(
                new HashSet<ConcreteCFAEdge>(edges));
    }

    public Set<AbsoluteAddress> getNodes() {
        return Collections.unmodifiableSet(locations);
    }

    protected final void buildFromEdgeSet(Set<CFAEdge> edges) {
        for (CFAEdge e : edges) {
            if (e.getSource().getAddress().equals(e.getTarget().getAddress())){
                continue;//Skip edges that go from the same node to itself
            }
            addEdge(new ConcreteCFAEdge(e.getSource().getAddress(),e.getTarget().getAddress()));
        }
    }

    protected void addEdge(ConcreteCFAEdge e) {
        // Check if edge already exists (equality on edges uses not only source & target)
        /*
        for (ConcreteCFAEdge existing : edges) {
            if (existing.getSource().equals(e.getSource()) && existing.getTarget().equals(e.getTarget()))
                return;
        }
        */

        edges.add(e);
        locations.add(e.getSource());
        locations.add(e.getTarget());
    }
}
