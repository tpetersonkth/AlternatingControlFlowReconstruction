/*
 * CPAAlgorithm.java - This file is part of the Jakstab project.
 * Copyright 2007-2015 Johannes Kinder <jk@jakstab.org>
 *
 * This code is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License version 2 only, as
 * published by the Free Software Foundation.
 *
 * This code is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
 * version 2 for more details (a copy is included in the LICENSE file that
 * accompanied this code).
 *
 * You should have received a copy of the GNU General Public License version
 * 2 along with this work; if not, see <http://www.gnu.org/licenses/>.
 */
package org.jakstab.analysis;

import java.util.*;

import org.jakstab.*;
import org.jakstab.analysis.composite.CompositeProgramAnalysis;
import org.jakstab.analysis.composite.CompositeState;
import org.jakstab.analysis.location.BackwardLocationAnalysis;
import org.jakstab.analysis.location.LocationAnalysis;
import org.jakstab.asm.AbsoluteAddress;
import org.jakstab.cfa.*;
import org.jakstab.loader.Harness;
import org.jakstab.rtl.statements.RTLHalt;
import org.jakstab.rtl.statements.RTLStatement;
import org.jakstab.util.*;

/**
 * The main CPA worklist algorithm.
 * 
 * @author Johannes Kinder
 */
public class CPAAlgorithm implements Algorithm {

	private static final Logger logger = Logger.getLogger(CPAAlgorithm.class);

	private final StateTransformerFactory transformerFactory;
	private final ConfigurableProgramAnalysis cpa;
	private final ReachedSet reached;
	private final AbstractReachabilityTree art;
	private final Worklist<AbstractState> worklist;	
	
	private final boolean failFast;
	private final boolean addedDSE;
	private final boolean DSEOnlyOnce;

	private long statesVisited;
	private boolean completed = false;
	private volatile boolean stop = false;

	//Stats
	private static long overApxTime = 0;
	private static long DFSTime = 0;
	private static long DSETime = 0;

	/**
	 * Instantiates a new CPA algorithm with a forward location analysis, a default
	 * forward transformer factory and worklist suitable for an analysis of a complete 
	 * and already reconstructed control flow automaton.
	 * 
	 * @param cpas The list of analyses to be performed  
	 */
	public static CPAAlgorithm createForwardAlgorithm(ControlFlowGraph cfg, ConfigurableProgramAnalysis... cpas) {
		ConfigurableProgramAnalysis cpa = new CompositeProgramAnalysis(new LocationAnalysis(), cpas);
		return new CPAAlgorithm(cpa, new CFATransformerFactory(cfg), new FastSet<AbstractState>());
	}

	/**
	 * Instantiates a new CPA algorithm with a backward location analysis, a default
	 * backward transformer factory and worklist suitable for an analysis of a complete 
	 * and already reconstructed control flow automaton.
	 * 
	 * @param cpas The list of backward analyses to be performed  
	 */
	public static CPAAlgorithm createBackwardAlgorithm(ControlFlowGraph cfg, ConfigurableProgramAnalysis... cpas) {
		ConfigurableProgramAnalysis cpa = new CompositeProgramAnalysis(new BackwardLocationAnalysis(), cpas);
		return new CPAAlgorithm(cpa, new ReverseCFATransformerFactory(cfg), new FastSet<AbstractState>());
	}

	public CPAAlgorithm(ConfigurableProgramAnalysis cpa,
			StateTransformerFactory transformerFactory, Worklist<AbstractState> worklist) {
		this(cpa, transformerFactory, worklist, false, false,false);
	}

	public CPAAlgorithm(ConfigurableProgramAnalysis cpa,
			StateTransformerFactory transformerFactory, Worklist<AbstractState> worklist, boolean failFast, boolean addedDSE, boolean DSEOnlyOnce) {
		super();
		this.cpa = cpa;
		this.transformerFactory = transformerFactory;
		this.worklist = worklist;
		this.failFast = failFast;
		this.addedDSE = addedDSE;
		this.DSEOnlyOnce = DSEOnlyOnce;//Can be set to true for increased speed at the cost of precision
		
		if (Options.errorTrace.getValue() || Options.asmTrace.getValue() || 
				AnalysisManager.getInstance().getAnalysis(
						org.jakstab.analysis.explicit.VpcTrackingAnalysis.class) != null)
			art = new AbstractReachabilityTree();
		else
			art = null;
		reached = new ReachedSet();
	}

	public static long getOverApxTime() {
		return overApxTime;
	}

	public static long getDFSTime() {
		return DFSTime;
	}

	public static long getDSETime() {
		return DSETime;
	}

	public static void setOverApxTime(long overApxTime) {
		CPAAlgorithm.overApxTime = overApxTime;
	}

	public static void setDFSTime(long DFSTime) {
		CPAAlgorithm.DFSTime = DFSTime;
	}

	public static void setDSETime(long DSETime) {
		CPAAlgorithm.DSETime = DSETime;
	}

	/**
	 * After a run of the algorithm, returns the set of reached states.
	 * 
	 * @return the set of reached (and kept) states.
	 */
	public ReachedSet getReachedStates() {
		return reached;
	}
	
	public AbstractReachabilityTree getART() {
		return art;
	}
	
	public long getNumberOfStatesVisited() {
		return statesVisited;
	}

	/**
	 * Returns whether the algorithm terminated normally.
	 */
	public boolean isCompleted() {
		return completed;
	}

	/**
	 * Returns whether the algorithm had to make unsound assumptions. Alwaysoptions
	 * true for analyses on complete CFAs.
	 * 
	 * @return true if the analysis required unsound assumptions. 
	 */
	public boolean isSound() {
		if (transformerFactory instanceof ResolvingTransformerFactory) {
			return ((ResolvingTransformerFactory)transformerFactory).isSound();
		} else {
			return true;
		}
	}

	@Override
	public void run() {
		logger.debug("Starting CPA algorithm.");
		
		Runtime runtime = Runtime.getRuntime();
		Program program = Program.getProgram();

		AbstractState start = cpa.initStartState(transformerFactory.getInitialLocation()); 
		worklist.add(start);
		reached.add(start);
		if (art != null) art.setRoot(start);

		// Set up precisions
		Precision precision = cpa.initPrecision(transformerFactory.getInitialLocation(), null);
		Map<Location, Precision> precisionMap = new HashMap<Location, Precision>();
		precisionMap.put(start.getLocation(), precision);

		int steps = 0;
		statesVisited = 0;
		final int stepThreshold = 50;
		long startTime = System.currentTimeMillis();
		long outputTime = System.currentTimeMillis();//Last time the CFA and stats were outputted
		long outputDelta = 60000;//CFA and stats are outputted once every outputDelta milliseconds
		long lastSteps = 0;
		long lastTime = 0;
		LinkedList<AbstractState> unresolvedStates = new LinkedList<>();
		LinkedList<AbstractState> tops = new LinkedList<>();
		Set<CFAEdge> DSEedges = new HashSet<>();
		long startTimeOverApx = System.currentTimeMillis();
		while ((!worklist.isEmpty()) && !stop && (!failFast || isSound())) {
			statesVisited++;
			if (++steps == stepThreshold) {

				// Helps limit memory usage
				long now = System.currentTimeMillis();
				System.gc();
				long gcTime = System.currentTimeMillis() - now;
				logger.debug("Time for GC: " + gcTime + "ms");

				now = System.currentTimeMillis();
				long duration = Math.max(1, now - lastTime);
				long speed = (1000L*(statesVisited - lastSteps) / duration);
				//speed = Math.min(speed, 1000);

				logger.warn("*** Reached " + reached.size() + " states, processed " +
						statesVisited + " states after " + (now - startTime) + "ms, at " +
						speed + " states/second" +
						(transformerFactory instanceof ResolvingTransformerFactory ?
								", " + program.getInstructionCount() + " instructions."
								: "."));

				logger.info(String.format("    Allocated heap memory: %.2f MByte", (runtime.totalMemory() - runtime.freeMemory())/(1024.0*1024.0)));

				steps = 0;

				StatsPlotter.plot((now - startTime) + "\t" + statesVisited  +"\t" + program.getInstructionCount() + "\t" + gcTime + "\t" + speed);

				lastSteps = statesVisited;
				lastTime = now;

				if (Options.timeout.getValue() > 0 && (System.currentTimeMillis() - startTime > Options.timeout.getValue() * 1000)) {
					logger.error("Timeout after " + Options.timeout.getValue() + "s!");
					stop = true;
				}
			}

			if (System.currentTimeMillis() - outputTime > outputDelta){
				//Ensure that time is correct before performing output
				long now = System.currentTimeMillis();
				Main.setOverallEndTime(now);
				overApxTime += now - startTimeOverApx;
				startTimeOverApx = now;

				//Update CFA nodes and edges
				Main.updateCFA();

				//Output stats and CFA
				Main.outputStats();
				Main.outputGraphs(new ProgramGraphWriter(program));

				//Update outputime to delay next output by outputDelta
				outputTime = System.currentTimeMillis();
			}

			// We need the state before precision refinement for building the ART
			AbstractState unadjustedState = worklist.pick();

			// Prefix everything by current location for easier debugging
			//Logger.setGlobalPrefix(unadjustedState.getLocation().toString());

			precision = precisionMap.get(unadjustedState.getLocation());

			Pair<AbstractState, Precision> pair = cpa.prec(unadjustedState, precision, reached);

			// Warning: The refined a is not stored in "reached", only used for successor calculation
			AbstractState a = pair.getLeft();
			precision = pair.getRight();
			precisionMap.put(a.getLocation(), precision);

			//logger.debug("Picked from worklist: " + a.getIdentifier());

			// transformerFactory.getTransformers() might throw exceptions
			try {
				Set<CFAEdge> transformers = new HashSet<>();
				transformers.addAll(transformerFactory.getTransformers(a));
				transformers.addAll(DSE.getTransformers(DSEedges,a));
				if (transformers.isEmpty()){
					RTLStatement stmt = Program.getProgram().getStatement((RTLLabel)a.getLocation());
					if (!(stmt instanceof RTLHalt)){//Halt statements don't have any successors
						unresolvedStates.add(a);
					}
				}
				// For each outgoing edge
				for (CFAEdge cfaEdge : transformers) {
					Precision targetPrecision = precisionMap.get(cfaEdge.getTarget());
					if (targetPrecision == null) {
						targetPrecision = cpa.initPrecision(cfaEdge.getTarget(), cfaEdge.getTransformer());
						precisionMap.put(cfaEdge.getTarget(), targetPrecision);
					}

					// Calculate the set of abstract successors
					// post() might throw exceptions
					Set<AbstractState> successors;
					try {
						successors = cpa.post(a, cfaEdge, targetPrecision);
					} catch (StateException e) {
						if (e.getState() == null) {
							e.setState(a);
						}
						if (art != null && !unadjustedState.equals(e.getState()))
							art.addChild(unadjustedState, cfaEdge, e.getState());
						throw e;
					}

					if (successors.isEmpty()) {
						logger.debug("No successors along edge " + cfaEdge);
						continue;
					}

					//logger.debug("via edge " + cfaEdge.toString() + " " + successors.size() + " successors.");

					// Process every successor
					for (AbstractState succ : successors) {
						//logger.debug("Processing new post state: " + succ.getIdentifier());

						// Try to merge the new state with an existing one
						Set<AbstractState> statesToRemove = new FastSet<AbstractState>();
						Set<AbstractState> statesToAdd = new FastSet<AbstractState>();

						for (AbstractState r : reached.where(0, ((CompositeState)succ).getComponent(0))) {
							AbstractState merged = cpa.merge(succ, r, targetPrecision);
							if (!merged.equals(r)) {
								//logger.debug("Merge of new successor:\n" + succ + "\n and reached state:\n" + r + "\n produced new state \n" + merged);
								statesToRemove.add(r);
								statesToAdd.add(merged);
							}
						}

						// replace the old state in worklist and reached with the merged version
						for (AbstractState r : statesToRemove) {
							reached.remove(r);
							worklist.remove(r);
							//art.remove(r);
						}

						for (AbstractState r : statesToAdd) {
							// Only add r to the worklist if it hasn't been reached yet
							if (reached.add(r)) {
								worklist.add(r);
								if (art != null) art.addChild(unadjustedState, cfaEdge, r);
							}
						}

						// if not stopped add to worklist
						if (!cpa.stop(succ, reached, targetPrecision)) {

							/*if (!statesToAdd.isEmpty()) {
								logger.verbose("Merged successor with " + statesToAdd.size() + " states, but still adding it to reached and worklist:");
								logger.warn(succ);
							}*/

							worklist.add(succ);
							reached.add(succ);
							if (art != null) art.addChild(unadjustedState, cfaEdge, succ);
						}
					}
					// end for each outgoing edge
				}
				if (worklist.isEmpty()){
					//Log time taken to empty the worklist
					long now = System.currentTimeMillis();
					overApxTime += now - startTimeOverApx;
				}
			} catch (StateException e) {
				// Fill in state for disassembly and unknownpointer exceptions
				if (e.getState() == null) {
					e.setState(a);
				}
				throw e;
			}
			if(worklist.isEmpty() && addedDSE){
				//Export the paths to the unresolved branches to DSE
				logger.info("Formatting graph for efficient path extraction");
				ResolvingTransformerFactory transformerFactory = (ResolvingTransformerFactory) this.transformerFactory;
				Set<CFAEdge> cfa = transformerFactory.getCFA();
				Pair<ArrayList<LinkedList<Pair<Integer, AbsoluteAddress>>>,Map<AbsoluteAddress, Integer>> out = DSE.getAdjList(cfa);
				ArrayList<LinkedList<Pair<Integer,AbsoluteAddress>>> adjList = out.getLeft();
				Map<AbsoluteAddress, Integer> addressToId = out.getRight();

				LinkedList<AbstractState> unresolvedStatesToSend = new LinkedList<>();

				Set<AbsoluteAddress> unresolved = new HashSet<AbsoluteAddress>();
				for(AbstractState as : unresolvedStates){
					unresolved.add(as.getLocation().getAddress());
				}

				unresolvedStatesToSend.addAll(unresolvedStates);

				if (!this.DSEOnlyOnce){
					for(AbstractState as : tops){
						unresolved.add(as.getLocation().getAddress());
					}
					unresolvedStatesToSend.addAll(tops);
				}

				//Search for paths towards the locations of the unresolved states
				logger.info("Searching for paths to the unresolved locations");
				Pair<Integer, AbsoluteAddress> startPair = new Pair<Integer, AbsoluteAddress>(addressToId.get(Harness.prologueAddress),Harness.prologueAddress);
				long startTimeDFS = System.currentTimeMillis();
				Set<LinkedList<AbsoluteAddress>> paths = DSE.LDFSIterative(adjList, startPair, unresolved, 200);
				long diffDFS = System.currentTimeMillis() - startTimeDFS;
				DFSTime += diffDFS;
				logger.info("Iterative path search took: "+Long.toString(diffDFS)+" milliseconds and found " + paths.size() + " paths");

				//Create an empty list and pass them by reference to DSE.execute to have it filled by this function
				logger.info("Sending request for Directed Symbolic Execution");
				LinkedList<AbstractState> toExploreAgain = new LinkedList<AbstractState>();
				DSEedges = DSE.execute(program, unresolvedStatesToSend, Options.mainFilename, paths, toExploreAgain);
				logger.info("DSE resulted in "+DSEedges.size()+" new edges");
				//For statistics
				Set<RTLLabel> resolvedTops = program.getResolvedTops();
				for (AbstractState as: toExploreAgain){
					resolvedTops.add(as.getLocation().getLabel());
				}
				program.setResolvedTops(resolvedTops);

				int oldCFASize = transformerFactory.getCFA().size();
				transformerFactory.saveDSEEdges(DSEedges);

				boolean reachedFixpoint = (oldCFASize == transformerFactory.getCFA().size());
				if (!reachedFixpoint){
					//Re add abstract states to worklist
					if (!this.DSEOnlyOnce){
						tops.addAll(unresolvedStates);
						for (AbstractState as : tops){
							worklist.add(as);
						}
					}
					else{
						for (AbstractState as : toExploreAgain){
							worklist.add(as);
						}
					}
				}

				unresolvedStates = new LinkedList<>();

				//Benchmark the time of emptying the worklist
				startTimeOverApx = System.currentTimeMillis();
			}
		}
		long endTime = System.currentTimeMillis();
		if (endTime - startTime > 0) {
			logger.info("Processed " + statesVisited + " states at " + (1000L*statesVisited / (endTime - startTime)) + " states/second");
			logger.info(String.format("Allocated heap memory: %.2f MByte", (runtime.totalMemory() - runtime.freeMemory())/(1024.0*1024.0)));
		}

		completed = worklist.isEmpty(); 
	}

	public void stop() {
		logger.fatal(Characters.starredBox("Interrupt! Stopping CPA Algorithm!"));
		stop = true;
	}

}
