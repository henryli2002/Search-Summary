# Search-By-Agent

高可控轻量级文献综述 Pipeline —— 全链路强类型约束与重试机制。

## 架构概览

```
用户 Query
   │
   ▼
┌─────────────────────────────────┐
│  Module 1: Entity Extractor     │  Gemini Flash + Pydantic Schema
│  提取同义词/近义词关键词组        │
└──────────────┬──────────────────┘
               │ List[str]
               ▼
┌─────────────────────────────────┐
│  Module 2: Fetch & Score Funnel │  S2AG API + 对数平滑双维加权
│  检索 → 去重 → 评分 → Top N     │
└──────────────┬──────────────────┘
               │ List[PaperData]
               ▼
┌─────────────────────────────────┐
│  Module 3: Map (Extraction)     │  Gemini Flash × N (并发)
│  隔离式结构化事实提取            │  tenacity 指数退避重试
└──────────────┬──────────────────┘
               │ List[EnrichedPaper]
               ▼
┌─────────────────────────────────┐
│  Module 4: Shuffle (Taxonomy)   │  Gemini Pro (单次全局调用)
│  3-5 个互斥穷尽技术流派分类      │  Python 逻辑接管分组
└──────────────┬──────────────────┘
               │ Dict[str, List[EnrichedPaper]]
               ▼
┌─────────────────────────────────┐
│  Module 5: Reduce (Report)      │  Gemini Pro × 组数
│  按流派生成评述 → 拼接 Markdown  │
└──────────────┬──────────────────┘
               │ Markdown Report
               ▼
          输出文件
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制模板并填入你的 API Key
cp .env.example .env
```

编辑 `.env` 文件：

```env
# [必填] Gemini API Key — https://aistudio.google.com/apikey
GOOGLE_API_KEY=your-gemini-api-key

# [可选] Semantic Scholar API Key — https://www.semanticscholar.org/product/api#api-key
# 不设置也能用（100 req/5min），设置后提升至 1 req/sec
S2AG_API_KEY=your-s2ag-api-key
```

> **关于 Semantic Scholar API Key**
>
> 论文检索使用的是 [Semantic Scholar Academic Graph API](https://api.semanticscholar.org/)。
> - **不设置** `S2AG_API_KEY`：可直接使用，但速率限制较严（100 次请求 / 5 分钟）
> - **设置** `S2AG_API_KEY`：申请免费 API Key 后可持续 1 req/sec 调用
> - 申请地址：https://www.semanticscholar.org/product/api#api-key

### 3. 运行

```bash
# 方式一：使用便捷脚本（推荐，自动检查环境）
./run.sh "大模型代码生成技术"

# 方式二：直接调用 Python
python main.py "大模型代码生成技术"

# 指定输出文件
./run.sh "Retrieval Augmented Generation" --output my_report.md
```

### 4. 断点续跑（Resume）

Pipeline 在每个模块完成后自动保存 checkpoint。如果中途因 API 限流或网络问题失败，
可以直接恢复而不必从头重跑：

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

> **Checkpoint 机制说明**
>
> - 每个模块完成后，输出被序列化到 `checkpoints/<run_id>/` 目录
> - 模块 3 (Map) 支持**增量恢复**：已成功处理的论文不会重复调用 API
> - `--resume` 自动检测最后完成的阶段，从下一阶段继续
> - Checkpoint 目录结构：
>   ```
>   checkpoints/<run_id>/
>   ├── meta.json              # 运行元信息
>   ├── m1_keywords.json       # 模块 1 输出
>   ├── m2_papers.json         # 模块 2 输出
>   ├── m3_enriched.json       # 模块 3 输出
>   ├── m3_enriched_partial.json  # 模块 3 增量保存
>   ├── m4_grouped.json        # 模块 4 输出
>   └── m5_report.md           # 最终报告
>   ```

## 全局配置

所有超参数在 `config.py` 中冻结（`MappingProxyType`），运行时不可修改：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `search.min_year` | 2020 | 文献年份下限 |
| `search.max_year` | 2026 | 文献年份上限 |
| `search.fetch_limit` | 100 | API 初始抓取量 |
| `search.process_limit` | 30 | 进入 Map 阶段的论文数 |
| `search.recency_weight` | 0.65 | 排序权重（偏向最新研究） |
| `llm.flash_model` | gemini-2.0-flash | 用于高并发 Map 提取 |
| `llm.pro_model` | gemini-2.5-pro-preview-05-06 | 用于 Taxonomy 与总结 |

## 评分公式

$$Score_{final} = w_{recency} \cdot \frac{year - year_{min}}{year_{max} - year_{min}} + (1 - w_{recency}) \cdot \frac{\log(1 + citations)}{\log(1 + citations_{max})}$$

## 模块详解

| 模块 | 输入 | 输出 | 模型 | 重试策略 | Checkpoint |
|------|------|------|------|----------|------------|
| M1 Entity Extractor | 用户 Query | `List[str]` 关键词组 | Flash | 指数退避 ×5 | `m1_keywords.json` |
| M2 Fetch & Score | 关键词组 | `List[PaperData]` Top N | — (API) | 指数退避 ×5 | `m2_papers.json` |
| M3 Map Extract | Top N 论文 | `List[EnrichedPaper]` | Flash ×N | 指数退避 ×5 + 增量保存 | `m3_enriched.json` |
| M4 Shuffle Group | 全部论文 JSON | `Dict[str, List]` 分组 | Pro ×1 | 指数退避 ×5 | `m4_grouped.json` |
| M5 Reduce Report | 分组数据 | Markdown 报告 | Pro ×组数 | 指数退避 ×5 | `m5_report.md` |

## 项目结构

```
Search-By-Agent/
├── run.sh                  # 便捷启动脚本（推荐入口）
├── main.py                 # 主编排器（支持 --resume）
├── config.py               # 全局冻结配置（支持 .env 覆盖）
├── checkpoint.py           # Checkpoint 持久化管理器
├── schemas.py              # Pydantic 强类型模型
├── m1_entity_extractor.py  # 模块 1: Query 实体提取
├── m2_fetch_score.py       # 模块 2: 文献检索与评分 (S2AG API)
├── m3_map_extract.py       # 模块 3: Map 并发要素提取（增量恢复）
├── m4_shuffle_group.py     # 模块 4: Shuffle 技术流派分类
├── m5_reduce_report.py     # 模块 5: Reduce 报告生成
├── requirements.txt        # Python 依赖
├── .env.example            # 环境变量模板
├── .gitignore              # Git 忽略规则
├── checkpoints/            # 中间状态持久化（自动创建）
└── output/                 # 生成的报告目录（自动创建）
```
