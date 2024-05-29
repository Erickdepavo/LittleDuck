from .vm import VirtualMachine
from .vm_types import GeneratedCode


class VirtualMachineRunner:
    def __init__(self,
                 debug: bool = False):
        self.debug = debug

    def run_from_code(self, code: GeneratedCode):
        func_dir, mem_list, constants, quadruples = code

        const_list = [t[1] for t in constants]

        virtual_machine = VirtualMachine(function_directory=func_dir,
                                         memory_scope_templates=mem_list,
                                         constants=const_list,
                                         instructions=quadruples,
                                         debug=self.debug)

        virtual_machine.run()

