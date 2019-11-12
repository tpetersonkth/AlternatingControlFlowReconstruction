import sys, os

def main(directory, decimals):
    for filename in os.listdir(directory):
        filename = os.path.join(directory,filename)
        if filename.endswith("graph_stats.dat"):
            print("Modifying " + filename)
            f = open(filename, "r")
            lines = f.readlines()
            for l in range(len(lines)):
                line = lines[l]
                line = line.split(" ")
                for i in range(len(line)):
                    try:
                        element = line[i].strip().strip("%")
                        line[i] = str(round(float(element),decimals))+"%"
                    except ValueError: #Element is not a float, nothing to do
                        pass
                lines[l] = " ".join(line)

            f.close()
            f = open(filename, "w")
            f.write("\n".join(lines))
            f.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 generateCFA.py [directory] [decimals]")
    else:
        main(sys.argv[1],int(sys.argv[2]))
