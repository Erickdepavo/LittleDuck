from typing import Dict, List, Set

from .errors import CompileError


class DependencyGraph:
    def __init__(self):
        self.graph: Dict[str, Set[str]] = {}
        self.visited: Set[str] = set()
        self.stack: Set[str] = set()
        self.sorted_modules: List[str] = []

    def add_module(self, module_name: str):
        if module_name not in self.graph:
            self.graph[module_name] = set()

    def add_dependency(self, module_name: str, dependency_name: str):
        if module_name not in self.graph:
            self.graph[module_name] = set()
        if dependency_name not in self.graph:
            self.graph[dependency_name] = set()
        self.graph[module_name].add(dependency_name)

    def build_graph(self, modules: Dict[str, List[str]]):
        for module_name, dependencies in modules.items():
            self.add_module(module_name)
            for dependency in dependencies:
                self.add_dependency(module_name, dependency)

    def remove_unused_modules(self, main_module: str) -> Set[str]:
        modules_used: Set[str] = set([main_module])
        for module, dependencies in self.graph.items():
            modules_used = modules_used.union(dependencies)

        unused_modules = set(self.graph.keys()).difference(modules_used)
        for module in unused_modules:
            del self.graph[module]

        return unused_modules

    def detect_cycles(self):
        def visit(node):
            if node in self.stack:
                raise CompileError(f"Circular dependency detected: {node}")
            if node not in self.visited:
                self.stack.add(node)
                for neighbor in self.graph.get(node, []):
                    visit(neighbor)
                self.stack.remove(node)
                self.visited.add(node)

        for module in self.graph:
            if module not in self.visited:
                visit(module)

    def topological_sort(self):
        def visit(node: str):
            if node not in self.visited:
                self.visited.add(node)
                for neighbor in self.graph.get(node, set()):
                    visit(neighbor)
                self.sorted_modules.append(node)

        self.visited.clear()
        for module in self.graph:
            if module not in self.visited:
                visit(module)

        return self.sorted_modules[::-1]

if __name__ == "__main__":
    modules: Dict[str, List[str]] = {
        'module1': ['module2', 'module3'],
        'module2': ['module3'],
        'module3': [],
        'module5': [],
        'module4': ['module1'],
    }

    dependency_graph = DependencyGraph()
    dependency_graph.build_graph(modules)
    unused_modules = dependency_graph.remove_unused_modules('module1')
    print(f"Unused modules: {unused_modules}")
    dependency_graph.detect_cycles()
    sorted_modules = dependency_graph.topological_sort()
    print(f"Topologically sorted modules: {sorted_modules}")