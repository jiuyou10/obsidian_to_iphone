


## 1. margin 的本质

margin 就是 "**离失效边界还有多远**"，是一个连续量。 正负号怎么定，**完全看你怎么写公式**，没有绝对对错。

## 2. 两种常见约定

**约定 A：margin = 安全裕度（越大越安全）**

$$ m(x) = \text{读出信号} - \text{阈值} $$

例：SRAM 读操作要求差分电压超过读出放大器的灵敏度

$$ m(x) = (\text{nbl} - \text{bl}) - V_\text{sense} $$

- $m > 0$ → 差分电压超过阈值 → **正常**
- $m < 0$ → 差分电压不够 → **失效**
- $m = 0$ → 失效边界

**约定 B：margin = 失效程度（越大越糟）**

$$ m(x) = \text{阈值} - \text{读出信号} $$

符号反过来：

- $m > 0$ → 失效
- $m < 0$ → 正常

## 3. 为什么默认用 A

在结构可靠性 / FORM（first-order reliability method）里，标准约定是性能函数 $g(x)$：

$$ g(x) > 0 \Leftrightarrow \text{安全}, \quad g(x) < 0 \Leftrightarrow \text{失效} $$

失效面是 $g(x) = 0$。SRAM 良率分析沿用这套记法。

## 4. 连续性才是关键，不是符号

|样本|二值 indicator|margin (约定 A)|
|---|---|---|
|差分电压 = 0.5 V，远离失效|0（正常）|+0.45|
|差分电压 = 0.06 V，差点失效|0（正常）|+0.01|
|差分电压 = 0.04 V，刚失效|1（失效）|−0.01|
|差分电压 = −0.3 V，严重失效|1（失效）|−0.35|

- 二值视角：前两行一样、后两行一样，**信息全丢**
- margin 视角：第二行（差点失效）和第三行（刚失效）几乎挨着，在参数空间里大概率也挨着 → AIS 可以用第二行去引导下一轮采样

## 5. 落到代码里要确认两件事

仿真器返回的物理量需要满足：

1. **连续输出**（不是内部判完阈值再返回 0/1）
2. **失效条件是单边越界**（比如 `< 0` 或 `< V_sense`）

SRAM 里常用的 margin：

- 读取裕度（read margin）—— 约定 A，越大越好
- 写入裕度（write margin）—— 约定 A
- 静态噪声裕度（SNM）—— 约定 A

挑一个固定下来，整个 AIS 流程符号一致就行。

---

下面按代码执行顺序总结 `AIS_Bitcell.m` 里的主要变量。

**基础配置**

`analysis.circuitName`  
当前跑的电路名。现在是：

```matlab
analysis.circuitName = 'sram';
```

`analysis.path`  
AIS 主目录路径，用来仿真结束后切回原目录。

`analysis.hspicepath`  
HSPICE 可执行文件路径。

`analysis.circuitPath`  
当前电路目录：

```matlab
./circuits/sram
```

`analysis.model.mean`  
每个随机电路参数的均值。

`analysis.model.sigma`  
每个随机电路参数的标准差。这个是电路参数的标准差，不是 AIS proposal 的 `sigma`。

`nDim`  
随机变量维度。对当前 SRAM 来说，每个样本有 `nDim` 个参数。

`Threshold`  
失效阈值。现在是：

```matlab
Threshold = 0.09;
```

因为 `outputs = nbl - bl`，所以：

```matlab
outputs <= Threshold
```

表示失效。

`T`  
AIS 主循环迭代轮数。现在是 `8`。

`nnn_total`  
重复实验次数。现在是 `5`。

**预采样变量**

`nunit`  
每个半径上预采样的样本数。

`rad_list`  
预采样半径列表，例如：

```matlab
rad_list = (7:10)';
```

表示在标准正态空间里从 7σ 到 10σ 球面附近找边界样本。

`rad`  
当前正在跑的半径。

`sample`  
标准正态空间里的样本。每一行是一个样本，每一列是一个维度：

```matlab
sample: nunit × nDim
```

`sample_run`  
送入 HSPICE 的真实电路参数：

```matlab
sample_run = mean + sample .* sigma_parameter
```

`outputs`  
HSPICE 返回的性能指标。你现在这版返回：

```matlab
outputs = margin = nbl - bl
```

`indicator`  
失效指示函数：

```matlab
indicator = outputs <= Threshold;
```

其中：

```text
1 = 失效
0 = 非失效
```

`min_margin_list`  
每个半径下 `outputs` 的最小 margin。

`mean_margin_list`  
每个半径下 `outputs` 的平均 margin。

`fail_num_list`  
每个半径下失效样本数量。

`fail_rate_list`  
每个半径下失效比例。

`all_sample`  
所有预采样标准空间样本。

`all_margin`  
所有预采样样本对应的 margin。

`all_rad`  
每个预采样样本来自哪个半径。

`diagnose_table`  
预采样诊断表，会写到：

```text
data_18/presample_diagnose.csv
```

`rad_upper`  
用于筛选初始化候选样本的最大半径。

`Kcand`  
最多选多少个靠近边界的候选样本。

`candidate_sample`  
满足半径条件的候选标准空间样本。

`candidate_margin`  
候选样本对应的 margin。

`candidate_rad`  
候选样本对应的半径。

`order`  
按 `abs(candidate_margin - Threshold)` 从小到大排序的索引。

`selected`  
最终选中的边界附近样本索引。

`fail_sample`  
名字叫 fail sample，但你现在这版实际含义是“边界附近初始化样本”，不一定全是失效样本。

**AIS proposal 变量**

`K0`  
初始中心数量。

`center(:,:,t)`  
第 `t` 轮 proposal 的中心集合。每一行是一个高斯分量中心：

```matlab
center(:,:,t): K × nDim
```

`K`  
当前轮中心数量，也就是混合高斯分量数量。

`sigma_list`  
每轮 proposal 的扩散宽度。现在是：

```matlab
sigma_list = linspace(1.5, 0.8, T);
```

`AIS sigma`  
当前轮使用的 proposal 宽度：

```matlab
sigma = sigma_list(t);
```

它控制从 `center` 周围采样时扩散多大，不是电路参数标准差。

`M`  
当前轮主采样数量。现在是：

```matlab
M = 50 * K;
```

`comp`  
每个样本选择哪个 center 作为生成中心：

```matlab
comp = randi(K, M, 1);
```

`sample`  
当前轮从 proposal 采出来的标准空间样本：

```matlab
sample = center(comp,:,t) + sigma * randn(M,nDim);
```

**密度和权重变量**

`p0`  
样本在原始标准正态分布下的相对密度：

```matlab
p0 = exp(-sum(sample.^2,2)/2);
```

这里：

```matlab
sum(sample.^2,2)
```

表示每个样本所有维度平方后求和，也就是：

```text
||z||² = z1² + z2² + ... + zd²
```

完整标准正态密度中的常数 `1/(2π)^(d/2)` 被省略了，因为后面和 proposal 密度相除时会抵消。

`fenmu`  
样本在当前 proposal 混合高斯分布下的相对密度：

```matlab
q(z) = 1/K * Σ N(z | center_k, sigma²I)
```

代码里：

```matlab
a = (repmat(sample(i,:),K,1) - center(:,:,t)).^2;
fenmu(i) = 1/sigma^nDim * mean(exp(-sum(a,2)/(2*sigma*sigma)));
```

其中 `1/sigma^nDim` 是多维高斯里的尺度项，公共常数同样省略。

`fenzi`  
重要采样分子：

```matlab
fenzi = p0 .* indicator;
```

`w`  
重要采样权重：

```matlab
w = fenzi ./ fenmu;
```

也就是：

```text
w = I(z) * p(z) / q(z)
```

`w_save`  
累计保存所有轮的权重。

`w_norm`  
归一化权重，用来重采样更新下一轮 center：

```matlab
w_norm = w / sum(w);
```

`p`  
失效概率收敛曲线：

```matlab
p(index) = mean(w_save(1:index));
```

**自适应更新变量**

`new_idx`  
按 `w_norm` 抽中的样本索引。高权重样本更容易被选中。

`new_part`  
被选中的高权重样本，用来作为下一轮新的 center。

`keep_idx`  
从旧 center 中随机保留的索引。

`keep_part`  
保留下来的旧 center。

`center(:,:,t+1)`  
下一轮 proposal 中心：

```matlab
center(:,:,t+1) = [new_part; keep_part];
```

这就是当前代码里的自适应更新：  
proposal 的中心会向高贡献失效区域移动。

**保存结果变量**

`samples_total{nnn}`  
第 `nnn` 次重复实验的所有主采样标准空间样本。

`indicator_total{nnn}`  
这些样本是否失效。

`outputs_total{nnn}`  
这些样本的 margin。

`p_fail_total{nnn}`  
第 `nnn` 次重复实验的失效概率收敛曲线。

`w_total{nnn}`  
第 `nnn` 次重复实验的所有重要采样权重。

`simulationNum_save`  
每次重复实验调用的 HSPICE 样本数量。

`ais_summary`  
最终汇总表，保存到：

```text
D:\yield_analysis\AIS\data_18\AIS_summary.csv
```

里面主要字段：

`final_pfail`：最后的失效概率估计。  
`fail_count`：主采样阶段采到的失效样本数。  
`sample_count`：主采样总样本数。  
`min_margin`：最小 `nbl - bl`。  
`mean_margin`：平均 `nbl - bl`。  
`simulation_num`：HSPICE 总仿真样本数。  
`weight_sum`：权重总和。  
`ess`：有效样本数，越大说明权重越不集中、结果越稳定。