#!/usr/bin/env python3
import sys
import json

class ShardConfig:
    def __init__(self, num_shards=10):
        self.num_shards = num_shards
        self.version = 0
        self.shard_to_group = {s: 0 for s in range(num_shards)}  # 0 = unassigned
        self.groups = {}  # gid -> [server_ids]
    
    def clone(self):
        c = ShardConfig(self.num_shards)
        c.version = self.version + 1
        c.shard_to_group = dict(self.shard_to_group)
        c.groups = {gid: list(servers) for gid, servers in self.groups.items()}
        return c

class ShardController:
    def __init__(self, raft_node):
        self.raft = raft_node
        self.configs = [ShardConfig()]
    
    def join(self, gid, servers):
        # TODO: Add group, rebalance shards
        self.configs[-1] = self.configs[-1].clone()
        self.configs[-1].groups[gid] = servers

        
    
    def leave(self, gid):
        # TODO: Remove group, reassign its shards
        self.configs[-1] = self.configs[-1].clone()
        del self.configs[-1].groups[gid]
        
           


            
    
    def move(self, shard, gid):
        # TODO: Move specific shard to group
        pass
    
    def query(self, version=-1):
        # TODO: Return config at version (-1 = latest)
        pass
    
    def _rebalance(self, config):
        # TODO: Distribute shards evenly
        pass
