---
题号: LCP 68
题目: "美观的花束"
url: https://leetcode.cn/problems/1GxJYY/
难度: Medium
标签:
  - 数组
  - 滑动窗口
专题: "01-滑动窗口与双指针"
关键词: "滑动窗口统计合法子数组数"
掌握程度: 5
耗时: 4
提交日期: 2026-05-04
---

# LCP 68. 美观的花束

🔗 [题目链接](https://leetcode.cn/problems/1GxJYY/)   ⏱️ 耗时 **4 分钟**

> 💡 **关键词**:滑动窗口统计合法子数组数

## 思路
题目要求统计所有子数组中每个元素出现次数不超过cnt的区间数。使用滑动窗口维护一个合法窗口，当右指针移动导致某个元素超限时，左指针右移直到恢复合法。对于每个右端点，以它为结尾的合法子数组数等于窗口长度，累加即可得到总数。

## 关键点
- 滑动窗口保证窗口内始终满足“每个品种数量≤cnt”
- 每次右移后，以当前右端点为结尾的合法子数组数为r-l+1

## 复杂度
- 时间:O(n)
- 空间:O(n)

## 我的代码

```python
class Solution:
    def beautifulBouquet(self, flowers: List[int], cnt: int) -> int:
    
        n=len(flowers)
        l=ans=0
        count=defaultdict(int)
        for r in range(n):
            count[flowers[r]]+=1

            while count[flowers[r]]>cnt:
                count[flowers[l]]-=1
                l+=1
            
            #当前r能找到对应的l，那么l-r这段区间都可以作为左端点
            ans+=r-l+1
        
        return ans
```
