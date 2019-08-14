import sys
from manticore.native import Manticore

def main():
    program = sys.argv[1]
    address = int(sys.argv[2],16)
    print("Running with program="+program+" address="+hex(address))
    run(program,address)

def run(program, address):
    #m = Manticore(program, pure_symbolic=True)
    m = Manticore(program, pure_symbolic=False)
    with m.locked_context() as context:
        context['flag'] = ""

    m.add_hook(None, print_ip)

    @m.hook(address)
    def hook(state):
        print("Reached address " + hex(address))
        print(state.cpu)
        print(state.mem)
        m.generate_testcase(state,address)
        m.kill()

    m.run()

def print_ip(state):
    print(hex(state.cpu.RIP))

if __name__ == "__main__":
    main()
