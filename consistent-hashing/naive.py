class NaiveHashing:
    def __init__(self, num_servers, balance=False):
        self.num_servers = num_servers
        self.servers = [set() for _ in range(num_servers)]
        self.balance = balance
    
    def cache(self, key):
        server = hash(key) % self.num_servers
        self.servers[server].add(key)

    def lookup(self, key):
        server = hash(key) % self.num_servers
        return key in self.servers[server]
    
    def add_server(self):
        self.num_servers += 1
        self.servers.append(set())
        if self.balance:
            self.rebalance()

    def remove_server(self, server_idx):
        assert self.num_servers > 1, 'Cannot have less than one server'
        assert 0 <= server_idx < self.num_servers, 'Server index out of bounds'
        self.num_servers -= 1
        keys_removed = list(self.servers[server_idx])
        self.servers.pop(server_idx)
        if self.balance:
            self.rebalance(keys_removed)

    def rebalance(self, keys_removed=None):
        for server in self.servers:
            keys_to_move = list(server)
            for key in keys_to_move:
                new_server = hash(key) % self.num_servers
                if new_server != self.servers.index(server):
                    server.remove(key)
                    self.servers[new_server].add(key)
        if keys_removed:
            for key in keys_removed:
                new_server = hash(key) % self.num_servers
                self.servers[new_server].add(key)
    