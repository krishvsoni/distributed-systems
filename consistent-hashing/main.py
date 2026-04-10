import bisect
import hashlib



class ConsistentHashing:
    def __init__(self,replicas=100):
        if replicas <= 0:
            raise ValueError("replicas must be a positive integer")
        self.replicas = replicas
        self.ring_keys = []
        self.ring = {}
        self.nodes = set()
        self.storage = {}

    def _hash(self,value):
        digest = hashlib.sha256(str(value).encode("utf-8")).hexdigest()
        return int(digest,16)   
    
    def add_node(self,node_id):
        if node_id in self.nodes:
            return
        self.nodes.add(node_id)
        self.storage.setdefault(node_id,{})

        for i in range(self.replicas):
            point = self._hash(f"{node_id}:{i}")

            while point in self.ring:
                point = point + 1
            self.ring[point] = node_id 
            bisect.insort(self.ring_keys,point)
        self._rebalance_data()

    def remove_node(self, node_id):
        if node_id not in self.nodes:
            return

        for i in range(self.replicas):
            point = self._hash(f"{node_id}:{i}")
            while point in self.ring and self.ring[point] != node_id:
                point += 1

            if point in self.ring and self.ring[point] == node_id:
                del self.ring[point]
                idx = bisect.bisect_left(self.ring_keys, point)
                if idx < len(self.ring_keys) and self.ring_keys[idx] == point:
                    self.ring_keys.pop(idx)

        self.nodes.remove(node_id)
        self.storage.pop(node_id, None)
        self._rebalance_data()       


    def get_node(self, key):
        if not self.ring_keys:
            return None

        point = self._hash(key)
        idx = bisect.bisect_left(self.ring_keys, point)
        if idx == len(self.ring_keys):
            idx = 0  # Wrap around the ring

        return self.ring[self.ring_keys[idx]]

    def set(self, key, value):
        node_id = self.get_node(key)
        if node_id is None:
            raise RuntimeError("No nodes in ring")
        self.storage[node_id][key] = value

    def get(self, key, default=None):
        node_id = self.get_node(key)
        if node_id is None:
            return default
        return self.storage[node_id].get(key, default)

    def _rebalance_data(self):
        # Reinsert everything according to the current ring mapping.
        all_items = []
        for node_data in self.storage.values():
            all_items.extend(node_data.items())

        for node_id in self.storage:
            self.storage[node_id].clear()

        for key, value in all_items:
            node_id = self.get_node(key)
            if node_id is not None:
                self.storage[node_id][key] = value


if __name__ == "__main__":
    ch = ConsistentHashing(replicas=100)

    ch.add_node("node-a")
    ch.add_node("node-b")
    ch.add_node("node-c")

    n = 50
    for i in range(n):
        ch.set(i, f"Value {i}")

    print("Initial distribution:")
    for node, values in ch.storage.items():
        print(node, len(values))

    ch.add_node("node-d")
    print("\nAfter adding node-d:")
    for node, values in ch.storage.items():
        print(node, len(values))

    ch.remove_node("node-b")
    print("\nAfter removing node-b:")
    for node, values in ch.storage.items():
        print(node, len(values))