/*
 * DSE.java - This file is part of the ACFR
 * Copyright 2019 Johannes Kinder <thpeter@kth.se>
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
package org.jakstab.util;

import java.util.*;

import org.jakstab.asm.AbsoluteAddress;
import org.jakstab.cfa.CFAEdge;
import org.jakstab.cfa.RTLLabel;
import org.jakstab.loader.Harness;
import org.jakstab.loader.elf.IAddress;

import java.io.IOException;
import java.io.BufferedWriter;
import java.io.OutputStreamWriter;
import java.io.DataInputStream;
import java.io.Writer;
import java.io.File;

import java.net.Socket;

/**
 * @author Thomas Peterson
 * This class contains the logic related to the directed symbolic execution. It extracts paths to unresolved
 * branches and exports these to an directed symbolic execution tool.
 */
public class DSE {

    private static final Logger logger = Logger.getLogger(DSE.class);
    private static Socket clientSocket = null;

    //Limited Depth First Search to find paths to the unresolved branches
    //Suffers from stack overflow when depth is to large
    //For large values of depth it is thus recommended to use LDFSIterative
    public static Set<LinkedList<RTLLabel>> LDFS(Set<CFAEdge>  graph, RTLLabel start, Set<RTLLabel> targets, long depth){
        Stack<RTLLabel> stack = new Stack<RTLLabel>();
        Set<LinkedList<RTLLabel>> paths = LDFSRec(graph,start,targets,depth,stack);
        return paths;
    }

    private static  Set<LinkedList<RTLLabel>> LDFSRec(Set<CFAEdge>  graph, RTLLabel start, Set<RTLLabel> targets, long depth, Stack<RTLLabel> stack) {
        Set<LinkedList<RTLLabel>> paths = new HashSet<>();
        if (depth > 0){
            stack.push(start);

            //Start is the current node
            if (targets.contains(start)){
                AbsoluteAddress lastAddress = null;
                LinkedList<RTLLabel> path = new LinkedList<RTLLabel>();
                for(RTLLabel label : stack) {
                    if (lastAddress != label.getAddress()){
                        path.add(label);//Doubly linked list => O(1) to append element
                        lastAddress = label.getAddress();
                    }
                }
                paths.add(path);
            }

            //Perform DFS on all children recursively //TODO: Store CFA in an optimized fashion
            for(CFAEdge edge : graph){
                if (edge.getSource().getLabel().equals(start)){
                    Set<LinkedList<RTLLabel>> newpaths = LDFSRec(graph, edge.getTarget().getLabel(), targets,depth-1,stack);
                    paths.addAll(newpaths);
                }
            }
            stack.pop();
        }
        return paths;
    }

    public static  Set<LinkedList<AbsoluteAddress>> LDFSIterative(ArrayList<LinkedList<Pair<Integer,AbsoluteAddress>>>  adjList, Pair<Integer,AbsoluteAddress> start, Set<AbsoluteAddress> targets, long maxDepth, Set<CFAEdge> cfa) {
        class Node {
            public int id;
            public AbsoluteAddress address;
            public Node prev;
            public long depth;
            Node(int id, AbsoluteAddress address, Node prev, long depth){
                this.id = id;
                this.address = address;
                this.prev = prev;
                this.depth = depth;
            }
        }

        Stack<Node> stack = new Stack<Node>();
        Node startNode = new Node(start.getLeft(),start.getRight(), null, maxDepth);
        stack.push(startNode);

        Set<LinkedList<AbsoluteAddress>> paths = new HashSet<>();
        long sinceLast = System.currentTimeMillis();
        while(!stack.empty()){
            Node current = stack.pop();

            if (System.currentTimeMillis()-sinceLast >= 1000){
                sinceLast = System.currentTimeMillis();

                System.out.println("Queued nodes to explore: "+stack.size()+" depth of the current elements: ");
                int max = 0;
                for(Node n : stack){
                    System.out.printf(n.depth+",");
                }
            }

            if (current.depth <= 0){
                continue;
            }

            //Extract path to this address
            if (targets.contains(current.address)){
                AbsoluteAddress lastAddress = null;
                LinkedList<AbsoluteAddress> path = new LinkedList<AbsoluteAddress>();

                Node curr = current;
                while(curr != null){
                    if (!curr.address.equals(lastAddress)){
                        path.add(0, curr.address);//Doubly linked list => O(1) to append element
                    }
                    lastAddress = curr.address;
                    curr = curr.prev;
                }
                paths.add(path);
            }

            /*
            for(CFAEdge e : cfa){
                boolean same = e.getSource().getAddress().equals(e.getTarget().getAddress());
                if (e.getSource().getAddress().equals(current.address) && !same){
                    stack.push(new Node(0,e.getTarget().getAddress(),current,current.depth-1));
                }
            }
            */

            int currId = current.id;
            for(Pair<Integer,AbsoluteAddress> target : adjList.get(currId)){
                stack.push(new Node(target.getLeft(),target.getRight(),current,current.depth-1));
            }

        }

        return paths;

    }

    public static  Set<LinkedList<RTLLabel>> LDFSIterativeOLD(Set<CFAEdge>  graph, RTLLabel start, Set<RTLLabel> targets, long maxDepth) {
        class Node {
            public RTLLabel label;
            public Node prev;
            public long depth;
            Node(RTLLabel label, Node prev, long depth){
                this.label = label;
                this.prev = prev;
                this.depth = depth;
            }
        }

        Stack<Node> stack = new Stack<Node>();
        Node startNode = new Node(start, null, maxDepth);
        stack.push(startNode);

        Set<LinkedList<RTLLabel>> paths = new HashSet<>();

        while(!stack.empty()){
            Node current =  stack.pop();

            if (current.depth <= 0){
                continue;
            }

            //Start is the current node
            if (targets.contains(current.label)){
                AbsoluteAddress lastAddress = null;
                LinkedList<RTLLabel> path = new LinkedList<RTLLabel>();

                Node curr = current;
                while(curr != null){
                    if (curr.label.getAddress() != lastAddress){
                        path.add(0, curr.label);//Doubly linked list => O(1) to append element
                    }
                    lastAddress = curr.label.getAddress();
                    curr = curr.prev;
                }
                paths.add(path);
            }

            for(CFAEdge edge : graph){
                if (edge.getSource().getLabel().equals(current.label)){
                    stack.push(new Node(edge.getTarget().getLabel(),current,current.depth-1));
                }
            }

        }
        return paths;
    }

    public static Pair<ArrayList<LinkedList<Pair<Integer,AbsoluteAddress>>>,Map<AbsoluteAddress, Integer>> getAdjList(Set<CFAEdge> cfa){
        //Extract unique addresses
        Set<AbsoluteAddress> addresses= new HashSet<AbsoluteAddress>();
        for (CFAEdge edge : cfa) {
            addresses.add(edge.getSource().getAddress());
            addresses.add(edge.getTarget().getAddress());
        }

        //Create mapping between address and id
        Map<AbsoluteAddress, Integer> addressToId = new HashMap<AbsoluteAddress, Integer>();
        //Map<Integer, AbsoluteAddress> idToAddress = new HashMap<Integer, AbsoluteAddress>();
        int id = 0;
        for (AbsoluteAddress address : addresses){
            addressToId.put(address,id);
            //idToAddress.put(id,address);
            id = id + 1;
        }

        //Create the adjacency list using the id:s
        ArrayList<LinkedList<Pair<Integer,AbsoluteAddress>>> adjList = new ArrayList<LinkedList<Pair<Integer,AbsoluteAddress>>>(100);
        for(int i = 0; i < id + 1; i++){
            adjList.add(new LinkedList<Pair<Integer,AbsoluteAddress>>());
        }
        for (CFAEdge edge : cfa) {
            int from = addressToId.get(edge.getSource().getAddress());
            int to = addressToId.get(edge.getTarget().getAddress());

            //Corner case occurs if an instruction jumps to itself
            boolean cornerCase = edge.getTarget().getAddress().equals(edge.getSource().getAddress()) && edge.getTarget().getLabel().getIndex() == 0;

            if(from!=to){
                Pair<Integer,AbsoluteAddress> P = new Pair<Integer,AbsoluteAddress>(to,edge.getTarget().getAddress());
                adjList.get(from).add(P);
            }
        }
        return new Pair<ArrayList<LinkedList<Pair<Integer,AbsoluteAddress>>>,Map<AbsoluteAddress, Integer>>(adjList,addressToId);
    }


    public static void exportPaths(String mainfile, Set<LinkedList<AbsoluteAddress>> paths){
        String out = "";
        long pathCount = 0;//Avoid iterating over paths twice to obtain length

        //Format output
        boolean firstPath = true;
        for (LinkedList<AbsoluteAddress> path : paths) {
            pathCount = pathCount + 1;

            if (!firstPath) {
                out += "\n";
            }

            boolean firstAddr = true;
            for (AbsoluteAddress addr : path) {

                //Skip the initial pseudo block that only exists in the intermediate represenation
                if (addr.getValue() == Harness.PROLOGUE_BASE){
                    assert(firstAddr);//Prologue base should never be able to be anywhere else than at the start of a path
                    continue;
                }

                if (!firstAddr){
                    out += ",";
                }
                out += addr;

                firstAddr = false;
            }

            firstPath = false;

        }

        //Export to file(Deprecated)
        /*
        try{
            FileWriter fw = new FileWriter(filename);
            fw.write(out);
            fw.close();
        }
        catch(IOException e){
            logger.error("Could not export paths to file. ",e);
        }
        */

        File f = new File(mainfile);
        sendRequest("START"+f.getAbsolutePath()+"\n"+out+"END");

        logger.info("Exported " + Long.toString(pathCount) + " paths to DSE");
        logger.debug(out);
    }

    public static void exportPathsOLD(String mainfile, Set<LinkedList<RTLLabel>> paths){
        String out = "";
        long pathCount = 0;//Avoid iterating over paths twice to obtain length

        //Format output
        boolean firstPath = true;
        for (LinkedList<RTLLabel> path : paths) {
            AbsoluteAddress prevAddr = null;
            pathCount = pathCount + 1;

            if (!firstPath) {
                out += "\n";
            }

            boolean firstAddr = true;
            for (RTLLabel statement : path) {
                AbsoluteAddress addr = statement.getAddress();

                //Skip the initial pseudo block that only exists in the intermediate represenation
                if (addr.getValue() == Harness.PROLOGUE_BASE){
                    assert(firstAddr);//Prologue base should never be able to be anywhere else than at the start of a path
                    continue;
                }

                if (addr != prevAddr && addr != null){
                    if (!firstAddr){
                        out += ",";
                    }
                    out += addr;
                }

                firstAddr = false;
                prevAddr = addr;
            }

            firstPath = false;

        }

        //Export to file(Deprecated)
        /*
        try{
            FileWriter fw = new FileWriter(filename);
            fw.write(out);
            fw.close();
        }
        catch(IOException e){
            logger.error("Could not export paths to file. ",e);
        }
        */

        File f = new File(mainfile);
        sendRequest("START"+f.getAbsolutePath()+"\n"+out+"END");

        logger.info("Exported " + Long.toString(pathCount) + " paths to DSE");
        logger.debug(out);
    }

    public static void connect(int port){
        if (clientSocket == null){
            try{
                clientSocket = new Socket("localhost", port);
            }
            catch(IOException e){
                logger.error("Could not connect to DSE server.",e);
            }
        }
    }

    public static String sendRequest(String message){
        String response = "";

        try {
            Writer out = new BufferedWriter(new OutputStreamWriter(clientSocket.getOutputStream(), "UTF8"));

            //create input stream attached to socket
            DataInputStream inFromServer = new DataInputStream(clientSocket.getInputStream());

            out.append(message);
            out.flush();

            //Wait for data from DSE server
            while((response = inFromServer.readLine()) == null);//TODO: Possible to avoid polling?
        }
        catch(IOException e){
            logger.error("Could not send request to DSE server.",e);
        }

        return response;
    }

    public static void close(){
        try{
            clientSocket.close();
        }
        catch(IOException e){
            logger.error("Could not close connection to DSE server",e);
        }

    }

}
