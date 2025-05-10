from collections import defaultdict
import time

class LoadBalancer:
    def __init__(self, nodes: List[str]):
        self.nodes = nodes
        self.node_loads = defaultdict(int)
        self.node_health = {node: True for node in nodes}
        
    def get_optimal_node(self) -> str:
        """Select least loaded healthy node"""
        available_nodes = [n for n in self.nodes if self.node_health[n]]
        return min(available_nodes, key=lambda x: self.node_loads[x])
        
    def distribute_load(self, task: Dict) -> str:
        """Distribute tasks across nodes"""
        selected_node = self.get_optimal_node()
        self.node_loads[selected_node] += 1
        return selected_node