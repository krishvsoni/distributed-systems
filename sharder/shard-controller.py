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
        # Add/replace group membership, then rebalance.
        new_cfg = self.configs[-1].clone()
        new_cfg.groups[gid] = list(servers)
        self._rebalance(new_cfg)
        self.configs.append(new_cfg)
        return new_cfg

    def leave(self, gid):
        # Remove group and rebalance remaining shards.
        new_cfg = self.configs[-1].clone()
        if gid in new_cfg.groups:
            del new_cfg.groups[gid]
        self._rebalance(new_cfg)
        self.configs.append(new_cfg)
        return new_cfg

    def move(self, shard, gid):
        # Move a specific shard to a specific group (manual override).
        latest = self.configs[-1]
        if shard < 0 or shard >= latest.num_shards:
            raise ValueError(f"invalid shard id: {shard}")

        if gid != 0 and gid not in latest.groups:
            raise ValueError(f"target gid does not exist: {gid}")

        new_cfg = latest.clone()
        new_cfg.shard_to_group[shard] = gid
        self.configs.append(new_cfg)
        return new_cfg

    def query(self, version=-1):
        # Return config at version (-1 = latest).
        if version == -1:
            return self.configs[-1]
        if version < 0 or version >= len(self.configs):
            raise ValueError(f"config version out of range: {version}")
        return self.configs[version]

    def _rebalance(self, config):
        # Evenly distribute shards among groups, deterministically.
        gids = sorted(config.groups.keys())
        n = config.num_shards

        if not gids:
            for s in range(n):
                config.shard_to_group[s] = 0
            return

        # Target shards per group: first remainder groups get one extra.
        g = len(gids)
        base = n // g
        rem = n % g
        target = {gid: base + (1 if i < rem else 0) for i, gid in enumerate(gids)}

        shards_by_gid = {gid: [] for gid in gids}
        pool = []

        # Collect current shard placement.
        for shard in sorted(config.shard_to_group.keys()):
            owner = config.shard_to_group[shard]
            if owner in shards_by_gid:
                shards_by_gid[owner].append(shard)
            else:
                # Unassigned or owned by removed group.
                pool.append(shard)

        # Trim overloaded groups into pool.
        for gid in gids:
            keep = target[gid]
            owned = shards_by_gid[gid]
            if len(owned) > keep:
                overflow = owned[keep:]
                shards_by_gid[gid] = owned[:keep]
                pool.extend(overflow)

        pool.sort()

        # Fill underloaded groups from pool.
        for gid in gids:
            need = target[gid] - len(shards_by_gid[gid])
            if need > 0:
                take = pool[:need]
                shards_by_gid[gid].extend(take)
                pool = pool[need:]

        # Commit assignments.
        for gid in gids:
            for shard in shards_by_gid[gid]:
                config.shard_to_group[shard] = gid

        # If anything somehow remains, mark unassigned (safety fallback).
        for shard in pool:
            config.shard_to_group[shard] = 0