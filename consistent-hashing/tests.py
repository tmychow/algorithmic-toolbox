from naive import NaiveHashing
from consistent import ConsistentHashing

def test_naive_imbalanced():
    cache_obj = NaiveHashing(3)
    for i in range(10):
        cache_obj.cache(f'key{i}')
    for i in range(10):
        assert cache_obj.lookup(f'key{i}')
    assert not cache_obj.lookup('key10')
    keys_in_server1 = cache_obj.servers[1]
    cache_obj.remove_server(1)
    for key in keys_in_server1:
        assert not cache_obj.lookup(key)
    cache_obj.add_server()
    assert cache_obj.servers[2] == set()
    print('NaiveHashing imbalanced test passed')

def test_naive_balanced():
    cache_obj = NaiveHashing(3, balance=True)
    for i in range(10):
        cache_obj.cache(f'key{i}')
    for i in range(10):
        assert cache_obj.lookup(f'key{i}')
    assert not cache_obj.lookup('key10')
    keys_in_server1 = cache_obj.servers[1]
    cache_obj.remove_server(1)
    for key in keys_in_server1:
        assert cache_obj.lookup(key)
    cache_obj.add_server()
    assert cache_obj.servers[2] != set()
    print('NaiveHashing balanced test passed')

def simulate_variable_servers(cache_obj):
    pass

def test_benchmarks():
    cache_obj1 = NaiveHashing(num_servers = 10, balance = True)
    cache_obj2 = ConsistentHashing(num_servers = 10, balance = True, virtual = 5)
    cache_obj3 = MultiProbeHashing(num_servers = 10, balance = True, copies = 5)
    possible_keys = set()
    for _ in range(num_periods):
        # pick random number of loads in that period
        # sample from distribution of possible keys
        # add request function i.e. lookup, if untrue cache

def main():
    test_naive_imbalanced()
    test_naive_balanced()

if __name__ == '__main__':
    main()