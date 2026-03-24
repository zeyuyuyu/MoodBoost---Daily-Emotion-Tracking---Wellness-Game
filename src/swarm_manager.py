import time
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from threading import Lock

@dataclass
class SwarmNode:
    id: str
    status: str  # 'active', 'degraded', 'offline'
    last_heartbeat: float
    load: float  # 0.0 to 1.0
    tasks: List[str]

class SwarmManager:
    def __init__(self):
        self._nodes: Dict[str, SwarmNode] = {}
        self._lock = Lock()
        self.heartbeat_timeout = 30.0  # seconds
        self._setup_logging()

    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('SwarmManager')

    def register_node(self, node_id: str) -> bool:
        with self._lock:
            if node_id in self._nodes:
                self.logger.warning(f'Node {node_id} already registered')
                return False
            
            self._nodes[node_id] = SwarmNode(
                id=node_id,
                status='active',
                last_heartbeat=time.time(),
                load=0.0,
                tasks=[]
            )
            self.logger.info(f'Registered new node {node_id}')
            return True

    def heartbeat(self, node_id: str, load: float) -> bool:
        with self._lock:
            if node_id not in self._nodes:
                return False
            
            node = self._nodes[node_id]
            node.last_heartbeat = time.time()
            node.load = load
            
            # Update status based on load
            if load >= 0.9:
                node.status = 'degraded'
            else:
                node.status = 'active'
            
            return True

    def assign_task(self, task_id: str) -> Optional[str]:
        with self._lock:
            # Find least loaded active node
            available_nodes = [
                node for node in self._nodes.values()
                if node.status == 'active' and node.load < 0.8
            ]
            
            if not available_nodes:
                self.logger.warning('No available nodes for task assignment')
                return None
            
            target_node = min(available_nodes, key=lambda x: x.load)
            target_node.tasks.append(task_id)
            target_node.load += 0.1  # Approximate load increase
            
            self.logger.info(f'Assigned task {task_id} to node {target_node.id}')
            return target_node.id

    def check_health(self) -> Dict[str, List[str]]:
        unhealthy_nodes = []
        overloaded_nodes = []
        offline_nodes = []
        
        current_time = time.time()
        
        with self._lock:
            for node_id, node in self._nodes.items():
                if current_time - node.last_heartbeat > self.heartbeat_timeout:
                    node.status = 'offline'
                    offline_nodes.append(node_id)
                elif node.load >= 0.9:
                    overloaded_nodes.append(node_id)
                elif node.status == 'degraded':
                    unhealthy_nodes.append(node_id)
        
        return {
            'unhealthy': unhealthy_nodes,
            'overloaded': overloaded_nodes,
            'offline': offline_nodes
        }

    def rebalance_tasks(self) -> int:
        tasks_rebalanced = 0
        with self._lock:
            overloaded_nodes = [
                node for node in self._nodes.values()
                if node.load > 0.8 and node.tasks
            ]
            
            available_nodes = [
                node for node in self._nodes.values()
                if node.status == 'active' and node.load < 0.5
            ]
            
            for overloaded in overloaded_nodes:
                while overloaded.tasks and overloaded.load > 0.8 and available_nodes:
                    task = overloaded.tasks.pop()
                    target = min(available_nodes, key=lambda x: x.load)
                    
                    target.tasks.append(task)
                    target.load += 0.1
                    overloaded.load -= 0.1
                    
                    tasks_rebalanced += 1
                    self.logger.info(f'Rebalanced task {task} from {overloaded.id} to {target.id}')
        
        return tasks_rebalanced

    def get_swarm_status(self) -> Dict:
        with self._lock:
            return {
                'total_nodes': len(self._nodes),
                'active_nodes': sum(1 for n in self._nodes.values() if n.status == 'active'),
                'total_tasks': sum(len(n.tasks) for n in self._nodes.values()),
                'average_load': sum(n.load for n in self._nodes.values()) / len(self._nodes) if self._nodes else 0
            }