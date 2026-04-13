# Search-By-Agent

高可控轻量级学术文献综述自动化 Pipeline —— 全链路强类型约束、智能的大模型相关性初筛与断点续跑。

输入一个研究主题，自动完成：关键词提取 → 文献检索 → 引用链扩展 → **大模型并发批量初筛** → 双池选拔 → 结构化事实提取 → 技术流派分类 → Markdown 综述报告。

无论是搜索什么语言，中间所有检索和提取过程均已强制英语化以适配顶级学术文献库，生成最终报告时再随心切换为你想要的语言（中/英等）。

## 架构概览

```
用户 Query (如: "LLM记忆管理")
               │
               ▼
┌─────────────────────────────────────┐
│  Module 1: Entity Extractor         │  Gemini Flash 
│  严格提取学术标准的[英文]近义关键词      │
└──────────────┬──────────────────────┘
               │ List[str] (e.g., ["Agent memory optimization", ...])
               ▼
┌─────────────────────────────────────┐
│  Module 2: Fetch & Score Funnel     │  S2AG API + LLM Batch Screening
│  关键词检索 → 引用链扩展(Snowballing) │  
│  → LLM大模型并发批量把关(剔除偏题文献)  │  ← [关键! 避免高引水分论文污染]
│  → 去马太效应双池选拔 → 评分排序       │
└──────────────┬──────────────────────┘
               │ List[PaperData] (仅保留高度相关的 Top N 精英论文)
               ▼
┌─────────────────────────────────────┐
│  Module 3: Map (Extraction)         │  Gemini Flash × N (并发)
│  隔离式结构化事实提取 (强制英文输出)      │  增量保存 + 指数退避 + 单篇相关性双重校验
└──────────────┬──────────────────────┘
               │ List[EnrichedPaper]
               ▼
┌─────────────────────────────────────┐
│  Module 4: Shuffle (Taxonomy)       │  Gemini Pro (单次全局调用)
│  1-5 个互斥穷尽的技术流派分类(英文命名)  │  多格式容错解析
└──────────────┬──────────────────────┘
               │ Dict[str, List[EnrichedPaper]]
               ▼
┌─────────────────────────────────────┐
│  Module 5: Reduce (Report)          │  Gemini Pro × 组数
│  按最终设定的报告语言动态翻译并生成评述  │  支持: REPORT_LANGUAGE=(中文|English|Auto)
│  → 拼接包含引用和链接的 Markdown       │
└──────────────┬──────────────────────┘
               │ Markdown Report
               ▼
          output/report_*.md
```

## 核心特性

- **🚀 零极偏题 (LLM Batch Screening)**：在引用数打分前，系统会将上百篇搜索到的庞大文献库切分为多个小块并发喂给大模型进行“初筛诊断”，利用最低的 Token 成本拦截所有“偏题凑字数”的高引论文。
- **🌐 语言无边界 (Cross-Lingual Flow)**：你可以用中文查询，流水线中段会全栈使用纯粹的 Academic English（学术英语）同各种 API 及模型进行沟通，最后再在 M5 的组装阶段把成果毫无断层地翻译回中文或其他语言排版生成，消除信息差。
- **🔍 智能检索扩展**：关键词搜索 + Citation Snowballing（文献滚雪球追踪），LLM 筛选种子论文避免发散。
- **⚖️ 去马太效应**：经过大模型“初筛存活”下来的论文池，采用“双池选拔策略”，用 `log(1+citations)` 压缩引用数防垄断，同时设定特定配额保护近期零引用的最新文献。
- **🛡️ 全链路容错**：哪怕面临 429 或 5xx 限流报错，系统也会采用无休止的指数退避（5s-120s）配合增量保存。你甚至可以中断进程并在几天后跑 `./run.sh --resume` 进行挂后台续跑！

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入你的 GOOGLE_API_KEY （可自由选择其他大模型）
```

**必填**：
```env
GOOGLE_API_KEY=your-gemini-api-key    # https://aistudio.google.com/apikey
```

### 3. 运行

```bash
# 使用便捷脚本（推荐，自动检查环境和依赖）
./run.sh "Agent长记忆压缩"

# 或直接调用 Python
python main.py "Agent长记忆压缩"
```

### 4. 断点续跑与状态管理

Pipeline 中途因网络或不可抗力中断？它已经存好了 Checkpoint！

```bash
# 从上次中断处（比如刚做完信息提取的 M3）恢复接着做流派分类
./run.sh "Agent长记忆压缩" --resume

# 查看当前运行任务的具体进度状态
./run.sh --status "Agent长记忆压缩"

# 临时想换个语言？更改 .env 后直接用 --resume，它会秒拉之前的 M4 缓存并用新语言生报告！

# 清理所有的缓存（如果你想彻底重新跑一边）
./run.sh --clean
```

## 配置参考 (.env)

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `REPORT_LANGUAGE` | 中文 | [**🆕 新增**] 最终报告的母语 (Auto, 中文, English)，中间全部流程走英文不受影响检索 |
| `SEARCH_MIN_YEAR` | 2020 | 文献年份下限 |
| `SEARCH_MAX_YEAR` | 2026 | 文献年份上限 |
| `SEARCH_PROCESS_LIMIT` | 30 | 经过大模型筛选和去马太效应双池过滤后，最终能进入 M3 精读的精英论文数量 |
| `FILTER_MIN_CITATIONS` | 3 | 最低引用数阈值（会被 Exempt Year 豁免） |
| `FILTER_CITATION_EXEMPT_YEAR` | 2024 | 该年份及之后的最新论文**不受**被引数限制 |
| `EXPAND_ENABLED` | true | 是否开启引用追踪（Citation Snowballing），挖出最对路的核心引用文献 |

## 去马太效应工作流 (Anti-Matthew Selection)

当通过了 LLM 严格的批量主题相关性初筛后，如果存活论文仍然超过 `process_limit`，系统启用双池选拔：

```text
存活的精英论文 ─┬─ 新论文池 (year >= exempt_year) 
            │    └─ 按绝对引用数排序 → 选拔不超过 recent_limit
            │
            └─ 经典论文池 (year < exempt_year)
                 └─ 按 log(1+citations) 曲线排序 → 填满剩余坑位
                    (防止动辄几万引的综述常青树永远霸榜，给 100 引用甚至 50 引用的精对口小论文机会)
```

## 项目目录结构

```text
Search-By-Agent/
├── run.sh                  # 便捷启动脚本（核心入口）
├── main.py                 # 流程主编排与界面绘制
├── config.py               # 安全配置中心（剥离纯环境变量导致的引号/注释解析错误）
├── checkpoint.py           # 容错续跑核心模块
├── schemas.py              # Pydantic 强结构化类型定义
├── m1_entity_extractor.py  # M1: Query → 学科标准英语关键词
├── m2_fetch_score.py       # M2: 学术检索 → 大批量并行初筛 → 去马太排序
├── m3_map_extract.py       # M3: 提取结构化事实 (增量并发提取)
├── m4_shuffle_group.py     # M4: 上帝视角流派技术栈分类定义
├── m5_reduce_report.py     # M5: 按配置母语翻译拼接最终的精美报告
└── checkpoints/            # 临时生成的数据状态夹
```

## License

MIT
