import sys
from manticore.native import Manticore

def main():
    program = sys.argv[1]
    address = int(sys.argv[2],16)
    print("Running with program="+program+" address="+hex(address))
    run(program,address)

def run(program, address):
    m = Manticore(program)
    with m.locked_context() as context:
        context['flag'] = ""

    @m.hook(address)
    def hook(state):
        print("Reached address " + hex(address))
        m.generate_testcase(state,address)
        m.kill()

    m.run()


if __name__ == "__main__":
    main()
