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

import java.util.Set;
import java.util.LinkedList;

import java.io.FileWriter;

import org.jakstab.asm.AbsoluteAddress;
import org.jakstab.cfa.RTLLabel;
import org.jakstab.loader.Harness;

import java.io.IOException;
import java.io.BufferedWriter;
import java.io.OutputStreamWriter;
import java.io.DataInputStream;
import java.io.Writer;

import java.net.Socket;

/**
 * @author Thomas Peterson
 */
public class DSE {

    private static final Logger logger = Logger.getLogger(DSE.class);
    private static Socket clientSocket = null;

    public static void exportPaths(Set<LinkedList<RTLLabel>> paths){
        String out = "";

        //Format output
        boolean firstPath = true;
        for (LinkedList<RTLLabel> path : paths) {
            AbsoluteAddress prevAddr = null;

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

        sendRequest("START"+out+"END");

        logger.debug("Exported the following paths to DSE:");
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
            while((response = inFromServer.readLine()) == null);
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
