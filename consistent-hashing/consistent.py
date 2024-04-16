from sortedcontainers import SortedDict

class ConsistentHashing:
    def __init__(self, num_servers, balance=False, virtual=1):
        self.num_servers = num_servers
        self.servers = SortedDict()
        for i in range(num_servers):
            for j in range(virtual):
                self.servers[hash(f"server{i}_copy{j}")] = i
        self.cache = {}
        for i in range(num_servers):
            self.servers[i] = set()
        self.balance = balance
        self.virtual_copies = [virtual] * num_servers

    def cache(self, key):
        key_hash = hash(key)
        server_idx = self.servers.bisect_left(key_hash)
        if server_idx >= len(self.num_servers):
            server_idx = 0
        server = self.servers.peekitem(server_idx)[1]
        self.cache[server].add(key)
    
    def lookup(self, key):
        key_hash = hash(key)
        server_idx = self.servers.bisect_left(key_hash)
        if server_idx >= len(self.num_servers):
            server_idx = 0
        server = self.servers.peekitem(server_idx)[1]
        return key in self.cache[server]
    
    def add_server(self, virtual=1):
        self.num_servers += 1
        for j in range(virtual):
            self.servers[hash(f"server{self.num_servers-1}_copy{j}")] = self.num_servers-1
        self.virtual_copies.append(virtual)
        self.cache[self.num_servers-1] = set()
        if self.balance:
            self.rebalance()
    
    def remove_server(self):
        assert self.num_servers > 1, 'Cannot have less than one server'
        self.num_servers -= 1
        for j in range(self.virtual):
            del self.servers[hash(f"server{self.num_servers}_copy{j}")]
        self.cache.pop(self.num_servers)
        if self.balance:
            self.rebalance()