Goals

Distribute cached data across multiple servers
Maximize cache hit rate
Distribute data evenly across the servers

Metrics

Cache hit rate
Data distribution

Benefits: number of keys which need to be re-allocated, resilient with node removal, load balancing across nodes

Problem of consistent hashing
- Random node means non-uniform data and load distribution
- Oblivious to heterogeneity in node performance

Hence: virtual nodes, so if a node is unavailable the load handled by it is evenly dispersed across remaining nodes, and if you add a new node, it accepts roughly equivalent load from each of the others, and we can decide the number of virtual nodes based on the capacity of the node, accounting for heterogeneity in the physical infrastructure.

Note: load and data distribution are not the same thing. Load is the number of requests a server is handling, while data distribution is the number of keys a server is responsible for. This can cause a hotkey problem where certain keys receive a lot more requests and this can lead to performance bottlenecks.

Some keys are more popular, so our design assumes that even with skew in access distribution, there are enough keys in the popular end of the distribution that the load is spread uniformly

We can simulate a bunch of requests. Then we look at each time window. A node is in-balance if the node's request load deviates from average by less than threshold of 15%. We can plot the fraction of nodes which are out of balance across time, and also the corresponding request load by the entire system, and we se that the imbalance ratio decreases with increasing loads, since under high loads, a large number of popular keys are accessed and due to uniform distribution of keys the load is evenly distributed. However, during low loads (where load is 1/8th of the measured peak load), fewer popular keys are accessed, resulting in a higher load imbalance.


Measure the standard deviation of load across nodes, plotted against number of virtual copies per server and how that scales. Measure the 99% CI of bucket size relative to average load (total keys / servers), and what that implies for capacity planning. But then show the cost of having more virtual copies.




Ring hashing presents a solution to our initial problem. Case closed? Not quite. Ring hashing still has some problems.

First, the load distribution across the nodes can still be uneven. With 100 replicas (“vnodes”) per server, the standard deviation of load is about 10%. The 99% confidence interval for bucket sizes is 0.76 to 1.28 of the average load (i.e., total keys / number of servers). This sort of variability makes capacity planning tricky. Increasing the number of replicas to 1000 points per server reduces the standard deviation to ~3.2%, and a much smaller 99% confidence interval of 0.92 to 1.09.

This comes with significant memory cost. For 1000 nodes, this is 4MB of data, with O(log n) searches (for n=1e6) all of which are processor cache misses even with nothing else competing for the cache.




Ring hashing provides arbitrary bucket addition and removal at the cost of high memory usage to reduce load variance. Is there a way to have flexible ring resizing and low variance without the memory overhead?

Multi-Probe Consistent Hashing
Another paper from Google “Multi-Probe Consistent Hashing” (2015) attempts to address this. MPCH provides O(n) space (one entry per node), and O(1) addition and removal of nodes. The catch? Lookups get slower.

The basic idea is that instead of hashing the nodes multiple times and bloating the memory usage, the nodes are hashed only once but the key is hashed k times on lookup and the closest node over all queries is returned. The value of k is determined by the desired variance. For a peak-to-mean-ratio of 1.05 (meaning that the most heavily loaded node is at most 5% higher than the average), k is 21. With a tricky data structure you can get the total lookup cost from O(k log n) down to just O(k).

As a point of comparison, to have the equivalent peak-to-mean ratio of 1.05 for Ring Hash, you need 700 ln n replicas per node. For 100 nodes, this translates into more than a megabyte of memory.




Rendezvous Hashing
Another early attempt at solving the consistent hashing problem is called rendezvous hashing or “highest random weight hashing”. It was also first published in 1997.

The idea is that you hash the node and the key together and use the node that provides the highest hash value. The downside is that it’s hard to avoid the O(n) lookup cost of iterating over all the nodes.

Here’s an implementation taken from github.com/dgryski/go-rendezvous. My implementation optimizes the multiple hashing by pre-hashing the nodes and using an xorshift random number generator as a cheap integer hash function.

Even thought rendezvous hashing is O(n) lookups, the inner loop isn’t that expensive. Depending on the number of nodes, it can be easily be “fast enough”. See the benchmarks at the end.




Replication is picking multiple servers for a key. For ring, you just use the node afterwards. For multi probe, you use the next closest. Tradeoffs in terms of 

Consistent hashing algorithm vary in how easy and effective it is to add servers with different weights. That is, send more (or less) load to one server as to the rest. With a ring hash, you can scale the number of replicas by the desired load. This can increase memory usage quite considerably. Multi-Probe consistent hashing is trickier to use and maintain their existing performance guarantees. You can always add a second “shadow” node that refers back to an original node, but this approach fails when the load multiple is not an integer. 



Unbalanced distribution bad. Consistent hashing with bounded loads skips nodes that are too heavily loaded. 




When node stops responding, we remove and repopulate. But in data storage, we don't reshard since it is costly to move data. Instead, we use multiple replicas and only reshard if planned capacity changes, not when arbitrary node goes down.




Consistent Hashing for Bounded Loads
Mirrokni et al.


https://dev.to/endeepak/visual-simulation-of-consistent-hashing-dbd
https://blog.techlanika.com/consistent-hashing-with-bounded-loads-the-intuition-behind-it-explained-using-public-schools-44434942f71
https://research.google/blog/consistent-hashing-with-bounded-loads/
https://www.cs.princeton.edu/courses/archive/fall09/cos518/papers/chash.pdf
http://archive.dimacs.rutgers.edu/Workshops/SDNAlgorithms/Slides/Mirrokni.pdf
https://ceur-ws.org/Vol-3478/paper03.pdf
