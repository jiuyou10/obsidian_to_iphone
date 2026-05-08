import os

filepath = r'D:\obsidian _repo\leetcode刷题记录\java八股\redis.md'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')

# ============================================================
# Identify boundaries
# ============================================================

# Part A: lines 1 to before ## 主从复制 (index 0 to 815)
mast_replica_start = None
for i, line in enumerate(lines):
    if line.strip() == '## 主从复制':
        mast_replica_start = i
        break

# Find where 缓存雪崩 section starts
cache_start = None
for i, line in enumerate(lines):
    if line.strip() == '## 缓存雪崩 / 缓存击穿 / 缓存穿透':
        cache_start = i
        break

# Find the 哨兵 subsection boundaries within 主从复制
sentinel_start = None
sentinel_end = None
for i in range(mast_replica_start, len(lines)):
    if lines[i].strip() == '### 哨兵（Sentinel）自动故障转移':
        sentinel_start = i
    if sentinel_start is not None and i > sentinel_start:
        # The section ends at --- before next ###
        if lines[i].strip() == '---' and i > sentinel_start + 5:
            # Check if the next non-blank line is ###
            next_nonblank = None
            for j in range(i+1, min(i+10, len(lines))):
                if lines[j].strip():
                    next_nonblank = lines[j].strip()
                    break
            if next_nonblank and next_nonblank.startswith('###'):
                sentinel_end = i
                break

if not all([mast_replica_start, cache_start, sentinel_start, sentinel_end]):
    print(f"ERROR: markers not found. mast={mast_replica_start}, cache={cache_start}, sent={sentinel_start}, sent_end={sentinel_end}")
    exit(1)

print(f"mast_replica_start={mast_replica_start}")
print(f"sentinel_start={sentinel_start}")
print(f"sentinel_end={sentinel_end}")
print(f"cache_start={cache_start}")

# ============================================================
# Extract parts
# ============================================================

part_a = '\n'.join(lines[:mast_replica_start])  # before ## 主从复制
# 主从复制 section without 哨兵: from ## 主从复制 to just before 哨兵
part_b1 = '\n'.join(lines[mast_replica_start:sentinel_start])
# 哨兵 content (including the --- at the end)
sentinel_content = '\n'.join(lines[sentinel_start:sentinel_end+1])
# Rest of 主从复制 after 哨兵: from after the --- to before 缓存雪崩
part_b2 = '\n'.join(lines[sentinel_end+1:cache_start])
# 缓存雪崩 section to end
part_c = '\n'.join(lines[cache_start:])

# ============================================================
# Build new file
# ============================================================

# Cross-reference link to replace the removed 哨兵 subsection
cross_ref = """
> **哨兵（Sentinel）**：主节点挂了，从节点不会自动升级为主——哨兵负责自动故障转移，详见 [[#哨兵（Sentinel）]]。

"""

# New 哨兵 section (promoted to ##)
sentinel_section = sentinel_content.replace(
    '### 哨兵（Sentinel）自动故障转移',
    '## 哨兵（Sentinel）'
)

# New 集群 section
cluster_section = """
## 集群（Cluster）

Redis Cluster 是 Redis 的**分布式**方案，解决单机内存、吞吐量瓶颈。与哨兵（高可用）不同，集群实现的是**数据分片 + 高可用**的一体化方案。

---

### 核心思想：槽位（Slot）分配

```
整个集群有 16384 个 hash slot
  │
  ├─ 每个 key 通过 CRC16(key) % 16384 算出归属 slot
  ├─ slot 均匀分布在多个主节点上
  └─ 客户端直连任意节点，返回 MOVED 重定向或代理转发
```

**为什么是 16384？**
- 心跳包中 slot 信息用 bitmap 传输：16384 bits = 2KB，体积小
- 集群规模通常不超过 1000 节点，16384 个 slot 足够均匀分配

---

### 节点通信：Gossip 协议

节点之间通过 **Gossip 协议** 交换信息（PING/PONG），每秒随机选几个节点通信：

```
节点 A ──PING──→ 节点 B（附带 A 自己知道的集群状态）
节点 A ←─PONG─── 节点 B（附带 B 知道的集群状态）
```

- **无中心化**，每个节点都持有完整的 slot → 节点映射表
- **最终一致**，Gossip 的传播有延迟

---

### 主从架构

```
cluster node A（主）── 负责 slots [0-5000]
  └─ replica A1（从，A 挂了顶替）

cluster node B（主）── 负责 slots [5001-10000]
  └─ replica B1（从，B 挂了顶替）

cluster node C（主）── 负责 slots [10001-16383]
  └─ replica C1（从，C 挂了顶替）
```

- 每个主节点可以有多个从节点
- 主节点挂了，从节点自动提升为主（类似哨兵，但内置于集群中）

---

### 客户端访问

```
客户端请求 key "user:1001"
  │
  ├─ 计算 slot = CRC16("user:1001") % 16384
  ├─ 连接到任意节点
  │   ├─ 如果该节点负责这个 slot → 直接处理（Smart Client 模式）
  │   └─ 否则 → 返回 MOVED slot node_addr（重定向到正确节点）
  │
  └─ Smart Client（如 JedisCluster）缓存 slot→node 映射，下次直连正确节点
```

---

### 哨兵 vs 集群

| | 哨兵（Sentinel） | 集群（Cluster） |
|--|:----------------:|:--------------:|
| **解决什么问题** | 高可用（自动故障转移） | 数据分片 + 高可用 |
| **数据分布** | 所有节点存全量数据 | 数据分片到多个节点 |
| **写扩展** | ❌ 写能力受限于单主节点 | ✅ 多主节点并行写 |
| **架构复杂度** | 低（主从 + 哨兵） | 高（所有节点互联） |
| **适用场景** | 数据量不大但要求高可用 | 数据量大、需要水平扩展 |

---

### 面试一页纸

**集群的 16384 个 slot 是硬编码的吗？**
```
是的，16384 是 Redis Cluster 的固定设计。
计算方式：CRC16(key) & 16383（等同于 % 16384）。
```

**客户端如何知道 key 在哪个节点？**
```
Smart Client 缓存 slot→node 映射表。
遇到 MOVED 重定向时更新本地缓存。
```

**集群为什么至少需要 3 个主节点？**
```
因为至少 3 个主节点才能形成多数派（quorum），
挂一个节点时仍能正常工作。
```

**集群失效判定**：
```
一个主节点失联超过 cluster-node-timeout（默认 15s）：
  ├─ 如果该主节点有从节点 → 从节点自动提升为主
  └─ 如果没有从节点 → 集群进入 fail 状态，部分 slot 不可用
当 16384 个 slot 中有任意 slot 不可用（主挂了且无从节点顶替），集群就停止服务。
```

"""

output = part_a + '\n' + part_b1 + '\n' + cross_ref + part_b2 + '\n\n' + sentinel_section + '\n' + cluster_section + '\n' + part_c

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(output)

print(f'Done! Parts: a={len(part_a)}, b1={len(part_b1)}, cross_ref={len(cross_ref)}, b2={len(part_b2)}, sentinel={len(sentinel_section)}, cluster={len(cluster_section)}, c={len(part_c)}')
