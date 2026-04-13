# Search-By-Agent

高可控轻量级学术文献综述自动化 Pipeline —— 全链路强类型约束、智能检索扩展与断点续跑。

输入一个研究主题，自动完成：关键词提取 → 文献检索 → 引用链扩展 → 结构化分析 → 技术流派分类 → Markdown 综述报告。

## 架构概览

```
用户 Query
   │
   ▼
┌─────────────────────────────────────┐
│  Module 1: Entity Extractor         │  Gemini Flash + Pydantic Schema
│  提取同义词/近义词关键词组            │
└──────────────┬──────────────────────┘
               │ List[str]
               ▼
┌─────────────────────────────────────┐
│  Module 2: Fetch & Score Funnel     │  S2AG API + Citation Snowballing
│  关键词检索 → 引用链扩展 → 去重      │  去马太效应双池选拔
│  → 过滤 → 双池选拔 → 评分 → Top N   │  LLM 智能种子筛选
└──────────────┬──────────────────────┘
               │ List[PaperData]
               ▼
┌─────────────────────────────────────┐
│  Module 3: Map (Extraction)         │  Gemini Flash × N (并发)
│  隔离式结构化事实提取                │  增量保存 + 指数退避
└──────────────┬──────────────────────┘
               │ List[EnrichedPaper]
               ▼
┌─────────────────────────────────────┐
│  Module 4: Shuffle (Taxonomy)       │  Gemini Pro (单次全局调用)
│  3-5 个互斥穷尽技术流派分类          │  多格式容错解析
└──────────────┬──────────────────────┘
               │ Dict[str, List[EnrichedPaper]]
               ▼
┌─────────────────────────────────────┐
│  Module 5: Reduce (Report)          │  Gemini Pro × 组数
│  按流派生成评述 → 拼接 Markdown      │
│  → 完整 Reference 列表              │
└──────────────┬──────────────────────┘
               │ Markdown Report
               ▼
          output/report_*.md
```

## 核心特性

- **🔍 智能检索扩展**：关键词搜索 + Citation Snowballing，LLM 筛选种子论文避免话题离散
- **⚖️ 去马太效应**：双池选拔策略，用 `log(1+citations)` 压缩引用数，防止高引论文垄断
- **🛡️ 全链路容错**：429/5xx 无限重试（指数退避 5-120s），支持断点续跑
- **🎯 灵活过滤**：学科领域限制、引用数阈值 + 近年豁免规则
- **📦 强类型约束**：全链路 Pydantic 模型，LLM 仅负责提取，逻辑判断由 Python 显式控制

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入你的 GOOGLE_API_KEY
```

**必填**：
```env
GOOGLE_API_KEY=your-gemini-api-key    # https://aistudio.google.com/apikey
```

**可选（推荐）**：
```env
S2AG_API_KEY=your-s2ag-api-key        # https://www.semanticscholar.org/product/api#api-key
```

> **Semantic Scholar API Key 说明**
>
> - **不设置**：可直接使用，但速率限制较严（100 次请求 / 5 分钟），429 会触发自动退避等待
> - **设置后**：提升至 1 req/sec，显著加快检索速度
> - 免费申请：https://www.semanticscholar.org/product/api#api-key

### 3. 运行

```bash
# 使用便捷脚本（推荐，自动检查环境和依赖）
./run.sh "Retrieval Augmented Generation"

# 或直接调用 Python
python main.py "Vision Language Action"

# 指定输出文件
./run.sh "大模型代码生成技术" --output my_report.md
```

### 4. 断点续跑

Pipeline 在每个模块完成后自动保存 checkpoint。中途因 API 限流或网络问题中断后，可直接恢复：

```bash
# 从上次中断处恢复
./run.sh "大模型代码生成技术" --resume

# 查看 checkpoint 状态
./run.sh --status "大模型代码生成技术"

# 列出所有历史运行记录
./run.sh --list

# 清理所有 checkpoint 数据
./run.sh --clean
```

## 配置参考

所有配置通过 `.env` 文件覆盖，运行时冻结（`MappingProxyType`）不可修改。

### 搜索参数

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `SEARCH_MIN_YEAR` | 2020 | 文献年份下限 |
| `SEARCH_MAX_YEAR` | 2026 | 文献年份上限 |
| `SEARCH_FETCH_LIMIT` | 50 | 每个关键词的 API 获取量 |
| `SEARCH_PROCESS_LIMIT` | 30 | 进入 Map 阶段的论文总数上限 |
| `SEARCH_RECENCY_WEIGHT` | 0.65 | 评分中时间权重（越高越偏向新论文） |

### 过滤规则

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `FILTER_FIELDS_OF_STUDY` | *(空)* | 学科领域过滤，逗号分隔（如 `Computer Science,Engineering`） |
| `FILTER_MIN_CITATIONS` | 0 | 最低引用数阈值（0=不过滤） |
| `FILTER_CITATION_EXEMPT_YEAR` | 2024 | 该年份及之后的论文不受引用数限制 |
| `FILTER_RECENT_LIMIT` | 15 | 双池选拔中新论文池的最大容量 |

### 引用链扩展（Citation Snowballing）

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `EXPAND_ENABLED` | true | 是否启用引用链扩展 |
| `EXPAND_SEED_COUNT` | 3 | 种子论文数量（由 LLM 从高引候选中筛选） |
| `EXPAND_DIRECTION` | both | 扩展方向：`references` / `citations` / `both` |
| `EXPAND_PER_SEED_LIMIT` | 20 | 每个种子每个方向的最大获取数 |

### 模型配置

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `LLM_FLASH_MODEL` | gemini-2.5-flash | 高并发提取用模型（M1/M3/种子筛选） |
| `LLM_PRO_MODEL` | gemini-2.5-pro | 全局分类与总结用模型（M4/M5） |

## 评分公式

$$Score = w_{recency} \cdot \frac{year - year_{min}}{year_{max} - year_{min}} + (1 - w_{recency}) \cdot \frac{\log(1 + citations)}{\log(1 + citations_{max})}$$

当论文总数超过 `process_limit` 时，启用**双池选拔**（去马太效应）：

```
全部论文 ─┬─ 新论文池 (year >= exempt_year)
          │    └─ 按引用数排序 → top recent_limit
          │
          └─ 经典论文池 (year < exempt_year)
               └─ 按 log(1+citations) 排序 → 填满剩余配额
                  (去马太效应：1000引用 ≈ 3x 权重于10引用，而非100x)
```

## 引用链扩展工作流

```
关键词检索 → 发现 N 篇论文
     │
     ▼
取引用数前 3×seed_count 篇作为候选
     │
     ▼
LLM (Flash) 评估候选与查询的相关性
     │  ← 避免离题高引论文带偏扩展方向
     ▼
选出 seed_count 篇种子
     │
     ├─→ 获取 references (种子引用了哪些论文)
     └─→ 获取 citations  (哪些论文引用了种子)
     │
     ▼
合并去重 → 扩展后的论文池
     │
     ▼
引用过滤 → 双池选拔 → 评分排序 → Top N
```

## 模块详解

| 模块 | 输入 | 输出 | 模型 | 重试策略 | Checkpoint |
|------|------|------|------|----------|------------|
| **M1** Entity Extractor | 用户 Query | `List[str]` 关键词组 | Flash | 指数退避 ×5 | `m1_keywords.json` |
| **M2** Fetch & Score | 关键词组 | `List[PaperData]` Top N | S2AG API + Flash | 无限重试（429/5xx） | `m2_papers.json` |
| **M3** Map Extract | Top N 论文 | `List[EnrichedPaper]` | Flash ×N 并发 | 指数退避 ×5 + 增量保存 | `m3_enriched.json` |
| **M4** Shuffle Group | 全部论文 | `Dict[str, List]` 分组 | Pro ×1 | 指数退避 ×5 | `m4_grouped.json` |
| **M5** Reduce Report | 分组数据 | Markdown 报告 + References | Pro ×组数 | 指数退避 ×5 | `m5_report.md` |

### Checkpoint 机制

- 每个模块完成后，输出被序列化到 `checkpoints/<run_id>/` 目录
- M3 (Map) 支持**增量恢复**：已成功处理的论文不会重复调用 API
- `--resume` 自动检测最后完成的阶段，从下一阶段继续
- 429/5xx 错误会无限重试（指数退避 5-120s），可放心挂后台过夜运行

```
checkpoints/<run_id>/
├── meta.json                # 运行元信息（query, 时间戳）
├── m1_keywords.json         # 模块 1 输出
├── m2_papers.json           # 模块 2 输出
├── m3_enriched.json         # 模块 3 输出
├── m3_enriched_partial.json # 模块 3 增量保存
├── m4_grouped.json          # 模块 4 输出
└── m5_report.md             # 最终报告
```

## 项目结构

```
Search-By-Agent/
├── run.sh                  # 便捷启动脚本（推荐入口）
├── main.py                 # 主编排器（支持 --resume/--status/--list）
├── config.py               # 全局冻结配置（MappingProxyType，支持 .env 覆盖）
├── checkpoint.py           # Checkpoint 持久化管理器
├── schemas.py              # Pydantic 强类型模型定义
├── m1_entity_extractor.py  # 模块 1: Query → 同义词关键词组
├── m2_fetch_score.py       # 模块 2: S2AG 检索 + 引用链扩展 + 双池评分
├── m3_map_extract.py       # 模块 3: 并发结构化要素提取（增量恢复）
├── m4_shuffle_group.py     # 模块 4: 技术流派分类（多格式容错）
├── m5_reduce_report.py     # 模块 5: 按流派生成综述 + Reference 列表
├── requirements.txt        # Python 依赖
├── .env.example            # 环境变量模板（含完整参数说明）
├── .gitignore              # Git 忽略规则
├── checkpoints/            # 中间状态持久化（自动创建）
└── output/                 # 生成的报告目录（自动创建）
```

## 设计原则

1. **LLM 职责分离**：LLM 仅负责提取和分类，逻辑判断（分组、过滤、排序）均由 Python 显式控制
2. **强类型约束**：全链路 Pydantic 模型，确保模块间数据交换的严谨性
3. **优雅降级**：LLM 种子筛选失败自动回退到引用数排序；M4 兼容多种 JSON 输出格式
4. **全链路容错**：429/5xx 无限重试 + 关键词间冷却延迟 + 增量 checkpoint

## License

MIT
