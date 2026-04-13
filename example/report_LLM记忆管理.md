# 文献综述报告: LLM记忆管理

> 生成时间: 2026-04-13 19:49:54 CST  
> 分析论文数: 86  
> 技术流派数: 4

---

## 目录

1. [System-Level & Hardware Optimization](#system-level-&-hardware-optimization) (31)
2. [Agentic Memory Architectures & Frameworks](#agentic-memory-architectures-&-frameworks) (24)
3. [Core Model Architecture & Context Extension](#core-model-architecture-&-context-extension) (12)
4. [Surveys, Benchmarks, and Foundational Analysis](#surveys,-benchmarks,-and-foundational-analysis) (19)

---

## 1. System-Level & Hardware Optimization

### 系统层面与硬件优化

该研究领域的论文集中探讨了大型语言模型（LLM）所面临的严峻计算与内存挑战，通过系统和硬件层面的创新来提升其效率。一个贯穿多数研究的核心主题是**键值缓存（KV Cache）的优化**，尤其是在处理长上下文推理时，KV缓存已成为主要的性能瓶颈。

为解决此问题，研究者们提出了多种策略。一类方法聚焦于**压缩与量化**，旨在直接减小KV缓存的内存占用。例如，《KVQuant: Towards 10 Million Context Length LLM Inference with KV Cache Quantization》和《PQCache: Product Quantization-based KVCache for Long Context LLM Inference》分别利用新颖的量化方案来达成高压缩率。另一类方法则通过**稀疏化与智能选择**来减少不必要的数据访问和计算，如《Quest: Query-Aware Sparsity for Efficient Long-Context LLM Inference》提出的查询感知缓存选择算法。此外，**分层存储与计算卸载**成为一个重要趋势，如《InstAttention: In-Storage Attention Offloading for Cost-Effective Long-Context LLM Inference》将部分计算和缓存卸载到计算存储驱动器，而《FlashGen: Accelerating LLM Serving for Multi-turn Dialogues with Efficient Resource Management》则设计了跨GPU、CPU和SSD的多级缓存系统。

除了针对KV缓存的优化，该领域的研究也延伸至更广泛的模型压缩与硬件协同设计。在模型层面，《SliceGPT: Compress Large Language Models by Deleting Rows and Columns》通过结构化稀疏来压缩模型，而《Efficient Mixed-Precision Large Language Model Inference with TurboMind》则系统性地应用混合精度技术。在硬件层面，《20.5 C-Transformer》等工作探索了专为LLM设计的处理器架构，以提升端侧设备的能效。

一个值得注意的差异点在于，虽然大多数研究致力于提升性能，但部分工作开始关注这些优化技术带来的**安全风险**。例如，《I Know What You Asked: Prompt Leakage via KV-Cache Sharing in Multi-Tenant LLM Serving》揭示了KV缓存共享可能导致旁路攻击，造成用户隐私泄露。作为应对，《Selective KV-Cache Sharing to Mitigate Timing Side-Channels in LLM Inference》则探索如何在保障安全的前提下，平衡性能增益与隐私风险。

总体而言，该研究方向展现了从算法、系统软件到硬件架构的多维度协同创新，共同致力于使大型语言模型在实际部署中更加高效、经济和安全。

### 参考文献 — System-Level & Hardware Optimization

| # | 论文标题 | 年份 | 引用数 | 链接 |
|---|---------|------|--------|------|
| 1 | I Know What You Asked: Prompt Leakage via KV-Cache Sharing in Multi-Tenant LLM Serving | 2025 | 41 | [链接](https://www.semanticscholar.org/paper/79538f4bd1fabc0ac7aa28f743462c3fc31d7c35) |
| 2 | InstAttention: In-Storage Attention Offloading for Cost-Effective Long-Context LLM Inference | 2025 | 18 | [链接](https://www.semanticscholar.org/paper/35b5137a1ce1475c421ce2b04c7343a6f24b6959) |
| 3 | Accelerating LLM Serving for Multi-turn Dialogues with Efficient Resource Management | 2025 | 17 | [链接](https://www.semanticscholar.org/paper/cb19a679394ffb464785ca289ccfbd13c926046d) |
| 4 | Efficient Mixed-Precision Large Language Model Inference with TurboMind | 2025 | 13 | [链接](https://www.semanticscholar.org/paper/b29e9bbe560c5f96e7fddc9f7ba1cf667252cd37) |
| 5 | Selective KV-Cache Sharing to Mitigate Timing Side-Channels in LLM Inference | 2025 | 12 | [链接](https://www.semanticscholar.org/paper/370ea3e5e8f544c9d34dc8bb153bbce5c6811665) |
| 6 | SliceGPT: Compress Large Language Models by Deleting Rows and Columns | 2024 | 332 | [链接](https://www.semanticscholar.org/paper/7754ac3e8ff1286f17593159781487543cdddaba) |
| 7 | KVQuant: Towards 10 Million Context Length LLM Inference with KV Cache Quantization | 2024 | 449 | [链接](https://www.semanticscholar.org/paper/b085968c4362fb286ad6c5ef71a5db9630da0498) |
| 8 | Quest: Query-Aware Sparsity for Efficient Long-Context LLM Inference | 2024 | 290 | [链接](https://www.semanticscholar.org/paper/1c7db9fb18246787fbe3de6e0eaa370ae749e795) |
| 9 | vAttention: Dynamic Memory Management for Serving LLMs without PagedAttention | 2024 | 86 | [链接](https://www.semanticscholar.org/paper/e03827ea5638ae9f9f987b73b2017fd115f9f79b) |
| 10 | PQCache: Product Quantization-based KVCache for Long Context LLM Inference | 2024 | 83 | [链接](https://www.semanticscholar.org/paper/022f386eb66fc5532dd6f439e7a356fd33ebb9a2) |
| 11 | WKVQuant: Quantizing Weight and Key/Value Cache for Large Language Models Gains More | 2024 | 75 | [链接](https://www.semanticscholar.org/paper/f608011b0f50a14bb2949c186a7c632a099aa75b) |
| 12 | Long Context Compression with Activation Beacon | 2024 | 77 | [链接](https://www.semanticscholar.org/paper/f69f494ab691481ec353da4be480b334fada6607) |
| 13 | Infinite-LLM: Efficient LLM Service for Long Context with DistAttention and Distributed KVCache | 2024 | 82 | [链接](https://www.semanticscholar.org/paper/ee802ccb7fc3a322b824310ae6f29fc6a1e4314b) |
| 14 | LOOK-M: Look-Once Optimization in KV Cache for Efficient Multimodal Long-Context Inference | 2024 | 81 | [链接](https://www.semanticscholar.org/paper/6c5e09cef64fe7fbeab9a6f3f062363bffba917d) |
| 15 | Compressing Large Language Models using Low Rank and Low Precision Decomposition | 2024 | 58 | [链接](https://www.semanticscholar.org/paper/5de1ce5b5954d86cf7a990533600ca0c8168ac25) |
| 16 | DéjàVu: KV-cache Streaming for Fast, Fault-tolerant Generative LLM Serving | 2024 | 56 | [链接](https://www.semanticscholar.org/paper/37ffdf2c97a846d20418201d22604004ed1a98ba) |
| 17 | VPTQ: Extreme Low-bit Vector Post-Training Quantization for Large Language Models | 2024 | 39 | [链接](https://www.semanticscholar.org/paper/e8735aa9bc89f25619fe4f6e5465ade7ec8fc344) |
| 18 | InstInfer: In-Storage Attention Offloading for Cost-Effective Long-Context LLM Inference | 2024 | 25 | [链接](https://www.semanticscholar.org/paper/23a3c4d49c3fc652f464da4b482deb739bd63351) |
| 19 | 20.5 C-Transformer: A 2.6-18.1μJ/Token Homogeneous DNN-Transformer/Spiking-Transformer Processor with Big-Little Network and Implicit Weight Generation for Large Language Models | 2024 | 24 | [链接](https://www.semanticscholar.org/paper/bd7831ca2ee267a179491f97517077b53d433689) |
| 20 | vTensor: Flexible Virtual Tensor Management for Efficient LLM Serving | 2024 | 17 | [链接](https://www.semanticscholar.org/paper/c974d12ded9d1e6a3acb744ba737e0d2646e268d) |
| 21 | GRASS: Compute Efficient Low-Memory LLM Training with Structured Sparse Gradients | 2024 | 20 | [链接](https://www.semanticscholar.org/paper/0c909ef8b889dcf751fde42aa9ef97ff7a619232) |
| 22 | Bandwidth Characterization of DeepSpeed on Distributed Large Language Model Training | 2024 | 9 | [链接](https://www.semanticscholar.org/paper/fa941495588d9b846a3b86f70155a8d237d6fa05) |
| 23 | Compressing KV Cache for Long-Context LLM Inference with Inter-Layer Attention Similarity | 2024 | 9 | [链接](https://www.semanticscholar.org/paper/a7ebfd44de6eb3d9df4a2954c348ff1e17349a66) |
| 24 | LCM: LLM-focused Hybrid SPM-cache Architecture with Cache Management for Multi-Core AI Accelerators | 2024 | 11 | [链接](https://www.semanticscholar.org/paper/55b601400d2cf4b7994c7df62dd864c8141a5679) |
| 25 | CORM: Cache Optimization with Recent Message for Large Language Model Inference | 2024 | 7 | [链接](https://www.semanticscholar.org/paper/39835c99ded942f08dd6e8355f1a8681a58b0be6) |
| 26 | MEMO: Fine-grained Tensor Management For Ultra-long Context LLM Training | 2024 | 5 | [链接](https://www.semanticscholar.org/paper/1fe8ac2dba28b523a868b44bb82b6155b04766d3) |
| 27 | ProTrain: Efficient LLM Training via Memory-Aware Techniques | 2024 | 5 | [链接](https://www.semanticscholar.org/paper/e7c318d1044309bfe69865ab1db9db870b153b4a) |
| 28 | PIMphony: Overcoming Bandwidth and Capacity Inefficiency in PIM-Based Long-Context LLM Inference System | 2024 | 5 | [链接](https://www.semanticscholar.org/paper/cf2205a1c198be91ac53ffd120c3602b5b5661ec) |
| 29 | SYMPHONY: Improving Memory Management for LLM Inference Workloads | 2024 | 3 | [链接](https://www.semanticscholar.org/paper/b0a8cf33c94ba3d951ce599ac4760a2eded16997) |
| 30 | KunServe: Parameter-centric Memory Management for Efficient Memory Overloading Handling in LLM Serving | 2024 | 4 | [链接](https://www.semanticscholar.org/paper/c8d1f0f4dfba6980bf563527ab17351fcd1e2f5c) |
| 31 | Tokenization and Memory Optimization for Reducing GPU Load in NLP Deep Learning Models | 2024 | 3 | [链接](https://www.semanticscholar.org/paper/09c46a8c602b0ec9282a898ee2ec7a5d8734cbe0) |

---

## 2. Agentic Memory Architectures & Frameworks

### 智能体记忆架构与框架 (Agentic Memory Architectures & Frameworks)

“智能体记忆架构与框架”这一研究方向的核心，在于解决大型语言模型（LLM）因固定上下文窗口限制而在长时程推理和持续交互中面临的根本挑战。该领域的论文普遍致力于构建持久、可扩展且高效的记忆系统，以赋予智能体超越其原生上下文限制的能力。

一个显著的趋势是从扁平化的记忆存储转向更复杂的结构化表示。多项研究探索了分层或图结构记忆。例如，《HiAgent》和《Memory OS of AI Agent》提出了层级化架构来区分不同时效性的信息，而《From Isolated Conversations to Hierarchical Schemas》则引入了动态树状结构。同时，基于图的方法也备受关注，如《Mem0》的图变体、《AriGraph》的记忆图以及《HippoRAG》中的知识图谱，这些方法旨在捕捉信息之间更丰富的关系。

另一个重要的发展方向是将记忆管理视为智能体自身的一项能动性技能（agentic skill）。与传统的被动检索不同，《Agentic Memory》、《Memory as Action》和《Scaling Long-Horizon LLM Agent via Context-Folding》等工作将记忆操作（如信息整合、提炼或遗忘）定义为智能体策略的一部分，并利用强化学习进行端到端优化。这一思路进一步催生了“记忆操作系统”的概念，如《EverMemOS》和《MemOS》所提出的框架，它们旨在为智能体提供统一、标准化的记忆管理服务，涵盖从信息组织、生命周期管理到检索的全过程。

值得注意的是，许多框架从认知科学中汲取灵感，试图模拟人类记忆机制，例如《LightMem》借鉴了Atkinson-Shiffrin模型，《EverMemOS》和《Nemori》则分别受到印痕生命周期和事件分割理论的启发。

总体而言，该研究学派的工作标志着从简单的检索增强生成（RAG）向构建复杂、自主且结构化的智能体记忆系统的深刻转变。通过引入层次化、图结构、可学习的策略以及系统级的管理框架，这些研究为开发能够在长时程任务中保持连贯性和适应性的高级人工智能代理铺平了道路。

### 参考文献 — Agentic Memory Architectures & Frameworks

| # | 论文标题 | 年份 | 引用数 | 链接 |
|---|---------|------|--------|------|
| 1 | Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory | 2025 | 233 | [链接](https://www.semanticscholar.org/paper/1d9c21a0fdb1cc16a32c5d490ebaf98436a23382) |
| 2 | Agentic Memory: Learning Unified Long-Term and Short-Term Memory Management for Large Language Model Agents | 2026 | 11 | [链接](https://www.semanticscholar.org/paper/fddca50008a46c925b288bae079e43ead0bbeb6e) |
| 3 | Scaling Long-Horizon LLM Agent via Context-Folding | 2025 | 44 | [链接](https://www.semanticscholar.org/paper/6ca29e9438224626cafa50f121c22244f35575c0) |
| 4 | EverMemOS: A Self-Organizing Memory Operating System for Structured Long-Horizon Reasoning | 2026 | 12 | [链接](https://www.semanticscholar.org/paper/db97b0581b1d60c1ad41428fe9950398bf987b60) |
| 5 | From RAG to Memory: Non-Parametric Continual Learning for Large Language Models | 2025 | 117 | [链接](https://www.semanticscholar.org/paper/b79b3a401119bc610b6e2db738aeee531b40aaf0) |
| 6 | In Prospect and Retrospect: Reflective Memory Management for Long-term Personalized Dialogue Agents | 2025 | 43 | [链接](https://www.semanticscholar.org/paper/fc669d9b8460d21a1a1d2bff6cef7270c4e2dee3) |
| 7 | LightMem: Lightweight and Efficient Memory-Augmented Generation | 2025 | 40 | [链接](https://www.semanticscholar.org/paper/5e86097153a19e5656ab6a310e6f36b2679b70e8) |
| 8 | Nemori: Self-Organizing Agent Memory Inspired by Cognitive Science | 2025 | 38 | [链接](https://www.semanticscholar.org/paper/54e0b0223b0d0e48286a40204608b159d3577b18) |
| 9 | SagaLLM: Context Management, Validation, and Transaction Guarantees for Multi-Agent LLM Planning | 2025 | 28 | [链接](https://www.semanticscholar.org/paper/356b85ae926b2a8b4cd794e10fe8f37891ebf8d7) |
| 10 | Memory OS of AI Agent | 2025 | 37 | [链接](https://www.semanticscholar.org/paper/680ce7341b47e2979073142e4a7388b34257cdbc) |
| 11 | MemOS: An Operating System for Memory-Augmented Generation (MAG) in Large Language Models | 2025 | 28 | [链接](https://www.semanticscholar.org/paper/a739c14146ec40d8e08eb945d457a1f72258f3f9) |
| 12 | 3DLLM-Mem: Long-Term Spatial-Temporal Memory for Embodied 3D Large Language Model | 2025 | 17 | [链接](https://www.semanticscholar.org/paper/3d78432d20f0f285abce701b713b7ede54d0cd9c) |
| 13 | SGMem: Sentence Graph Memory for Long-Term Conversational Agents | 2025 | 15 | [链接](https://www.semanticscholar.org/paper/6721171b3d6c84336c9450dfb01f40887ccbd872) |
| 14 | Memory as Action: Autonomous Context Curation for Long-Horizon Agentic Tasks | 2025 | 12 | [链接](https://www.semanticscholar.org/paper/5f0f0c762c094bb6e1deba3222331ee51b98d1fc) |
| 15 | HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models | 2024 | 169 | [链接](https://www.semanticscholar.org/paper/4308208fac24626e0c927ee728038aadc4e87266) |
| 16 | AriGraph: Learning Knowledge Graph World Models with Episodic Memory for LLM Agents | 2024 | 56 | [链接](https://www.semanticscholar.org/paper/e2687f80077e8466918e4aeb2ea52e591bfe7e81) |
| 17 | From Isolated Conversations to Hierarchical Schemas: Dynamic Tree Memory Representation for LLMs | 2024 | 46 | [链接](https://www.semanticscholar.org/paper/86aea18148fa67c6fd0eecdc0ee68137fe16a75d) |
| 18 | HiAgent: Hierarchical Working Memory Management for Solving Long-Horizon Agent Tasks with Large Language Model | 2024 | 49 | [链接](https://www.semanticscholar.org/paper/a7fb4245b412f0e54ec26d5973f041d52c83c0ad) |
| 19 | Online Adaptation of Language Models with a Memory of Amortized Contexts | 2024 | 37 | [链接](https://www.semanticscholar.org/paper/366441034ec03b2fd72e29c246c49389a50b8ad8) |
| 20 | Long Term Memory: The Foundation of AI Self-Evolution | 2024 | 30 | [链接](https://www.semanticscholar.org/paper/5007fb901de5e32adf27e6ca129b38f878c5b4af) |
| 21 | Towards Lifelong Dialogue Agents via Timeline-based Memory Management | 2024 | 21 | [链接](https://www.semanticscholar.org/paper/a7645ac747cfde0a6dcf865c5279b891f303bdc4) |
| 22 | Robots Can Multitask Too: Integrating a Memory Architecture and LLMs for Enhanced Cross-Task Robot Action Generation | 2024 | 8 | [链接](https://www.semanticscholar.org/paper/86e6a0d8e36fcccaf13b4dd8c24433999d1d7bae) |
| 23 | THEANINE: Revisiting Memory Management in Long-term Conversations with Timeline-augmented Response Generation | 2024 | 5 | [链接](https://www.semanticscholar.org/paper/373b56dd4f6861e5e0622f7eb2959f05aac2edc1) |
| 24 | Enhancing Long-Term Memory using Hierarchical Aggregate Tree for Retrieval Augmented Generation | 2024 | 3 | [链接](https://www.semanticscholar.org/paper/070c3c063a80bbcf81d927d6d3351a882153e962) |

---

## 3. Core Model Architecture & Context Extension

### 核心模型架构与上下文扩展

该研究方向的论文致力于解决大型语言模型（LLM）在处理长序列时面临的核心挑战，主要聚焦于两大方向：一是直接扩展模型的有效上下文窗口，二是提升长上下文处理的架构效率与内存管理能力。

在上下文窗口扩展方面，一个显著的趋势是通过改进位置编码机制来实现。例如，《LongRoPE: Extending LLM Context Window Beyond 2 Million Tokens》及其后续工作《LongRoPE2: Near-Lossless LLM Context Window Scaling》通过对旋转位置嵌入（RoPE）进行非均匀插值和渐进式扩展，在少量微调的情况下显著延长了预训练模型的上下文处理能力，同时努力保持其在原始短上下文上的性能。与这种需要微调的方法不同，《LLM Maybe LongLM: Self-Extend LLM Context Window Without Tuning》提出了一种创新方案，在推理阶段通过构建双层注意力机制，无需任何额外训练即可扩展现有模型的上下文窗口。

在提升效率和优化内存管理方面，研究者们探索了多种路径。一种主流方法是改革注意力机制本身。《SampleAttention》引入了自适应的结构化稀疏注意力，而《Mixture of Attention Spans》则为不同注意力头自动定制异构的滑动窗口长度，两者都旨在降低长上下文推理的延迟和内存开销。另一大趋势是引入显式或外部记忆系统。《M+: Extending MemoryLLM with Scalable Long-Term Memory》通过协同训练的检索器整合了长期记忆机制；《Memory3: Language Modeling with Explicit Memory》利用显式记忆降低训练与推理成本；而《WISE》则设计了双参数记忆方案来解决终身模型编辑中的难题。此外，还有一些研究从更根本的架构层面入手，如《Falcon-H1》提出的结合Transformer和状态空间模型（SSM）的混合架构，旨在同时优化长上下文记忆的性能与效率。

总体而言，该领域的研究呈现出多元化的创新路径，从调整位置编码和注意力等核心组件，到集成外部记忆系统，再到设计全新的混合模型架构，共同推动着大型语言模型突破长上下文处理的瓶颈。

### 参考文献 — Core Model Architecture & Context Extension

| # | 论文标题 | 年份 | 引用数 | 链接 |
|---|---------|------|--------|------|
| 1 | Falcon-H1: A Family of Hybrid-Head Language Models Redefining Efficiency and Performance | 2025 | 31 | [链接](https://www.semanticscholar.org/paper/0b25979bf487cbc9334e0e94031cdac83d4f28dd) |
| 2 | M+: Extending MemoryLLM with Scalable Long-Term Memory | 2025 | 26 | [链接](https://www.semanticscholar.org/paper/8a85ef6b1063972f873d99ce19fe31a0c02657bf) |
| 3 | LongRoPE2: Near-Lossless LLM Context Window Scaling | 2025 | 16 | [链接](https://www.semanticscholar.org/paper/929ac69abb84bb8e6cb0e0a6fe1ed8b8e7924a2d) |
| 4 | LongRoPE: Extending LLM Context Window Beyond 2 Million Tokens | 2024 | 306 | [链接](https://www.semanticscholar.org/paper/c9603ec967879c24973b5bd48861df2e5555932e) |
| 5 | LLM Maybe LongLM: Self-Extend LLM Context Window Without Tuning | 2024 | 164 | [链接](https://www.semanticscholar.org/paper/a9468d8bfa6bd016dfd3128c4e8408e30eb8549b) |
| 6 | WISE: Rethinking the Knowledge Memory for Lifelong Model Editing of Large Language Models | 2024 | 68 | [链接](https://www.semanticscholar.org/paper/8ce5f6e28d49e1bc00804fa2fa3e917deb203388) |
| 7 | SampleAttention: Near-Lossless Acceleration of Long Context LLM Inference with Adaptive Structured Sparse Attention | 2024 | 40 | [链接](https://www.semanticscholar.org/paper/5b2c04e082a56c0eb70ed62bc36148919f665e1c) |
| 8 | Memory3: Language Modeling with Explicit Memory | 2024 | 38 | [链接](https://www.semanticscholar.org/paper/2c4f702a4bbb733e1abfb722c5c74fa15aa85ee5) |
| 9 | Mixture of Attention Spans: Optimizing LLM Inference Efficiency with Heterogeneous Sliding-Window Lengths | 2024 | 37 | [链接](https://www.semanticscholar.org/paper/966a36fdc59702889a2fe44f47631fd0065ed5ef) |
| 10 | Search for Efficient Large Language Models | 2024 | 14 | [链接](https://www.semanticscholar.org/paper/18465f8ecb733960c17b22c468a196440a59cf0f) |
| 11 | Recurrent Context Compression: Efficiently Expanding the Context Window of LLM | 2024 | 7 | [链接](https://www.semanticscholar.org/paper/1102088716730adc1dea06cfa1741f91bb6fa0e9) |
| 12 | An Evolved Universal Transformer Memory | 2024 | 5 | [链接](https://www.semanticscholar.org/paper/9505c9ec941a22788d3a80ce794620e24ded0e90) |

---

## 4. Surveys, Benchmarks, and Foundational Analysis

### 调查、基准与基础分析

本研究方向的论文集主要围绕两大核心主题展开：提升大型语言模型（LLM）智能体的记忆能力，以及优化模型的计算效率。这些研究通过全面的文献综述、创新的基准测试和深入的基础分析，共同推动了对LLM能力边界和实际部署挑战的理解。

一个显著的趋势是对LLM智能体记忆机制的深入探索。多篇综述性文章，如《A Survey on the Memory Mechanism of Large Language Model-based Agents》和《Cognitive Memory in Large Language Models》，系统地梳理了现有记忆机制。同时，研究者们开始倡导更高级的记忆形式，如《Position: Episodic Memory is the Missing Piece for Long-Term LLM Agents》所主张的情景记忆。为了评估这些能力，一系列新的基准被提出，包括用于评估动态记忆演化的《Evo-Memory: Benchmarking LLM Agent Test-time Learning with Self-Evolving Memory》和评估长期对话记忆的《Evaluating Very Long-Term Conversational Memory of LLM Agents》。这些基准与《RULER: What's the Real Context Size of Your Long-Context Language Models?》等研究共同揭示了当前模型在处理长程依赖和复杂任务时的局限性。此外，《How Memory Management Impacts LLM Agents: An Empirical Study of Experience-Following Behavior》等实证研究进一步剖析了记忆管理决策对智能体长期性能的关键影响。

另一个核心研究方向是应对LLM日益增长的计算和内存需求，正如《AI and Memory Wall》所指出的，内存带宽已成为主要性能瓶颈。多篇综述，例如《A Survey on Efficient Inference for Large Language Models》和《Efficient Compressing and Tuning Methods for Large Language Models: A Systematic Literature Review》，对知识蒸馏、量化、剪枝和KV缓存管理等压缩与优化技术进行了系统性总结。超越单纯的效率提升，《Token Reduction Should Go Beyond Efficiency in Generative Models - From Vision, Language to Multimodality》提出，令牌缩减应被视为一种基础性设计原则。这些优化技术在《Cognitive Edge Computing: A Comprehensive Survey on Optimizing Large Models and AI Agents for Pervasive Deployment》中找到了在资源受限设备上部署的实际应用场景。

### 参考文献 — Surveys, Benchmarks, and Foundational Analysis

| # | 论文标题 | 年份 | 引用数 | 链接 |
|---|---------|------|--------|------|
| 1 | How Memory Management Impacts LLM Agents: An Empirical Study of Experience-Following Behavior | 2025 | 39 | [链接](https://www.semanticscholar.org/paper/7a40273098359b3f25989768bb2555ebb79ec3be) |
| 2 | Evo-Memory: Benchmarking LLM Agent Test-time Learning with Self-Evolving Memory | 2025 | 37 | [链接](https://www.semanticscholar.org/paper/87dc9cf7adf0a6446c07231c6ff2ae71d48235d3) |
| 3 | Position: Episodic Memory is the Missing Piece for Long-Term LLM Agents | 2025 | 33 | [链接](https://www.semanticscholar.org/paper/f85004321e43370535088042ebac96b958880c5d) |
| 4 | Cognitive Memory in Large Language Models | 2025 | 28 | [链接](https://www.semanticscholar.org/paper/d1958a7fc89303cad736884bd52c7d1dfd4469b5) |
| 5 | Cognitive Edge Computing: A Comprehensive Survey on Optimizing Large Models and AI Agents for Pervasive Deployment | 2025 | 25 | [链接](https://www.semanticscholar.org/paper/6e4ac103b4a76bee2d1c436b23c47eff9f6bdd90) |
| 6 | Token Reduction Should Go Beyond Efficiency in Generative Models - From Vision, Language to Multimodality | 2025 | 18 | [链接](https://www.semanticscholar.org/paper/399b9877c80802f3bc942163973b03d8a9c321bf) |
| 7 | Efficient Compressing and Tuning Methods for Large Language Models: A Systematic Literature Review | 2025 | 16 | [链接](https://www.semanticscholar.org/paper/b073de891287423915b1709c4cc90f40756c38b9) |
| 8 | RULER: What's the Real Context Size of Your Long-Context Language Models? | 2024 | 770 | [链接](https://www.semanticscholar.org/paper/ac5824e9ff924a937d9eef379d0b581de2417678) |
| 9 | A Survey on the Memory Mechanism of Large Language Model-based Agents | 2024 | 434 | [链接](https://www.semanticscholar.org/paper/b6ab16c8eade03a39830493071d99fc48a736fac) |
| 10 | Evaluating Very Long-Term Conversational Memory of LLM Agents | 2024 | 346 | [链接](https://www.semanticscholar.org/paper/0bf3a1867f7245b8a702093901c66b08b518eafc) |
| 11 | A Survey on Efficient Inference for Large Language Models | 2024 | 212 | [链接](https://www.semanticscholar.org/paper/5be7e6b04c5a240cff340034aae2b57c677e211f) |
| 12 | LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory | 2024 | 203 | [链接](https://www.semanticscholar.org/paper/fd48dc6b433cfcd220b6e769c6179d8ef6fcf862) |
| 13 | AI and Memory Wall | 2024 | 306 | [链接](https://www.semanticscholar.org/paper/4c14b1c41cb0aaa68f5d3f4a432f55e7199657ea) |
| 14 | A Survey on Large Language Model Acceleration based on KV Cache Management | 2024 | 99 | [链接](https://www.semanticscholar.org/paper/6bcd708d2e49b34f34f157daa6bf1c3e062f57c5) |
| 15 | Memory Matters: The Need to Improve Long-Term Memory in LLM-Agents | 2024 | 85 | [链接](https://www.semanticscholar.org/paper/a0ca8fff30c8d13c32a8da839e3adf335db86b32) |
| 16 | A Survey on Transformer Compression | 2024 | 73 | [链接](https://www.semanticscholar.org/paper/a74a20be53e5767648b5970e30b2d81a9ba8293f) |
| 17 | Understanding the Impact of Long-Term Memory on Self-Disclosure with Large Language Model-Driven Chatbots for Public Health Intervention | 2024 | 50 | [链接](https://www.semanticscholar.org/paper/8474164eda27baede5da93d8b73b3b77301374ee) |
| 18 | Assessing Episodic Memory in LLMs with Sequence Order Recall Tasks | 2024 | 9 | [链接](https://www.semanticscholar.org/paper/cfba39bc6adee8b99c1ced4ba150b9e3099ee34e) |
| 19 | Understanding Multi-Dimensional Efficiency of Fine-Tuning Large Language Models Using SpeedUp, MemoryUp, and EnergyUp | 2024 | 3 | [链接](https://www.semanticscholar.org/paper/2d578d0ab26d4506f615adf0a1b811015e21265f) |

---

## 完整参考文献列表

以下为本报告中分析的全部 **86** 篇论文，按年份（降序）及引用数（降序）排列。

**[1]** Chuanrui Hu, Xingze Gao, Zuyi Zhou, Dannong Xu, Yi Bai et al.. *EverMemOS: A Self-Organizing Memory Operating System for Structured Long-Horizon Reasoning*. 2026. (引用: 12) [[链接]](https://www.semanticscholar.org/paper/db97b0581b1d60c1ad41428fe9950398bf987b60)

**[2]** Yi Yu, Liuyi Yao, Yuexiang Xie, Q. Tan, Jiaqi Feng et al.. *Agentic Memory: Learning Unified Long-Term and Short-Term Memory Management for Large Language Model Agents*. 2026. (引用: 11) [[链接]](https://www.semanticscholar.org/paper/fddca50008a46c925b288bae079e43ead0bbeb6e)

**[3]** P. Chhikara, Dev Khant, Saket Aryan, Taranjeet Singh, Deshraj Yadav. *Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory*. 2025. (引用: 233) [[链接]](https://www.semanticscholar.org/paper/1d9c21a0fdb1cc16a32c5d490ebaf98436a23382)

**[4]** Bernal Jim'enez Guti'errez, Yiheng Shu, Weijian Qi, Sizhe Zhou, Yu Su. *From RAG to Memory: Non-Parametric Continual Learning for Large Language Models*. 2025. (引用: 117) [[链接]](https://www.semanticscholar.org/paper/b79b3a401119bc610b6e2db738aeee531b40aaf0)

**[5]** Weiwei Sun, Miao Lu, Zhan Ling, Kang Liu, Xuesong Yao et al.. *Scaling Long-Horizon LLM Agent via Context-Folding*. 2025. (引用: 44) [[链接]](https://www.semanticscholar.org/paper/6ca29e9438224626cafa50f121c22244f35575c0)

**[6]** Zhen Tan, Jun Yan, I-Hung Hsu, Rujun Han, Zifeng Wang et al.. *In Prospect and Retrospect: Reflective Memory Management for Long-term Personalized Dialogue Agents*. 2025. (引用: 43) [[链接]](https://www.semanticscholar.org/paper/fc669d9b8460d21a1a1d2bff6cef7270c4e2dee3)

**[7]** Guanlong Wu, Zheng Zhang, Yao Zhang, Weili Wang, Jianyu Niu et al.. *I Know What You Asked: Prompt Leakage via KV-Cache Sharing in Multi-Tenant LLM Serving*. 2025. (引用: 41) [[链接]](https://www.semanticscholar.org/paper/79538f4bd1fabc0ac7aa28f743462c3fc31d7c35)

**[8]** Jizhan Fang, Xinle Deng, Haoming Xu, Ziyan Jiang, Yuqi Tang et al.. *LightMem: Lightweight and Efficient Memory-Augmented Generation*. 2025. (引用: 40) [[链接]](https://www.semanticscholar.org/paper/5e86097153a19e5656ab6a310e6f36b2679b70e8)

**[9]** Zidi Xiong, Yuping Lin, Wenya Xie, Pengfei He, Jiliang Tang et al.. *How Memory Management Impacts LLM Agents: An Empirical Study of Experience-Following Behavior*. 2025. (引用: 39) [[链接]](https://www.semanticscholar.org/paper/7a40273098359b3f25989768bb2555ebb79ec3be)

**[10]** Jiayan Nan, Wenquan Ma, Wenlong Wu, Yize Chen. *Nemori: Self-Organizing Agent Memory Inspired by Cognitive Science*. 2025. (引用: 38) [[链接]](https://www.semanticscholar.org/paper/54e0b0223b0d0e48286a40204608b159d3577b18)

**[11]** Jiazheng Kang, Mingming Ji, Zhe Zhao, Ting Bai. *Memory OS of AI Agent*. 2025. (引用: 37) [[链接]](https://www.semanticscholar.org/paper/680ce7341b47e2979073142e4a7388b34257cdbc)

**[12]** Tianxin Wei, Noveen Sachdeva, Benjamin Coleman, Zhankui He, Yuanchen Bei et al.. *Evo-Memory: Benchmarking LLM Agent Test-time Learning with Self-Evolving Memory*. 2025. (引用: 37) [[链接]](https://www.semanticscholar.org/paper/87dc9cf7adf0a6446c07231c6ff2ae71d48235d3)

**[13]** Mathis Pink, Qinyuan Wu, Vy A. Vo, Javier Turek, Jianing Mu et al.. *Position: Episodic Memory is the Missing Piece for Long-Term LLM Agents*. 2025. (引用: 33) [[链接]](https://www.semanticscholar.org/paper/f85004321e43370535088042ebac96b958880c5d)

**[14]** Jingwei Zuo, Maksim Velikanov, Ilyas Chahed, Younes Belkada, Dhia Eddine Rhayem et al.. *Falcon-H1: A Family of Hybrid-Head Language Models Redefining Efficiency and Performance*. 2025. (引用: 31) [[链接]](https://www.semanticscholar.org/paper/0b25979bf487cbc9334e0e94031cdac83d4f28dd)

**[15]** Edward Y. Chang, Longling Geng. *SagaLLM: Context Management, Validation, and Transaction Guarantees for Multi-Agent LLM Planning*. 2025. (引用: 28) [[链接]](https://www.semanticscholar.org/paper/356b85ae926b2a8b4cd794e10fe8f37891ebf8d7)

**[16]** Zhiyu Li, Shichao Song, Hanyu Wang, Simin Niu, Ding Chen et al.. *MemOS: An Operating System for Memory-Augmented Generation (MAG) in Large Language Models*. 2025. (引用: 28) [[链接]](https://www.semanticscholar.org/paper/a739c14146ec40d8e08eb945d457a1f72258f3f9)

**[17]** Lianlei Shan, Shixian Luo, Zezhou Zhu, Yu Yuan, Yong Wu. *Cognitive Memory in Large Language Models*. 2025. (引用: 28) [[链接]](https://www.semanticscholar.org/paper/d1958a7fc89303cad736884bd52c7d1dfd4469b5)

**[18]** Yu Wang, Dmitry Krotov, Yuanzhe Hu, Yifan Gao, Wangchunshu Zhou et al.. *M+: Extending MemoryLLM with Scalable Long-Term Memory*. 2025. (引用: 26) [[链接]](https://www.semanticscholar.org/paper/8a85ef6b1063972f873d99ce19fe31a0c02657bf)

**[19]** Xubin Wang, Qing Li, Weijia Jia. *Cognitive Edge Computing: A Comprehensive Survey on Optimizing Large Models and AI Agents for Pervasive Deployment*. 2025. (引用: 25) [[链接]](https://www.semanticscholar.org/paper/6e4ac103b4a76bee2d1c436b23c47eff9f6bdd90)

**[20]** Xiurui Pan, Endian Li, Qiao Li, Shengwen Liang, Yizhou Shan et al.. *InstAttention: In-Storage Attention Offloading for Cost-Effective Long-Context LLM Inference*. 2025. (引用: 18) [[链接]](https://www.semanticscholar.org/paper/35b5137a1ce1475c421ce2b04c7343a6f24b6959)

**[21]** Zhenglun Kong, Yize Li, Fanhu Zeng, Lei Xin, Shvat Messica et al.. *Token Reduction Should Go Beyond Efficiency in Generative Models - From Vision, Language to Multimodality*. 2025. (引用: 18) [[链接]](https://www.semanticscholar.org/paper/399b9877c80802f3bc942163973b03d8a9c321bf)

**[22]** Jinwoo Jeong, Jeongseob Ahn. *Accelerating LLM Serving for Multi-turn Dialogues with Efficient Resource Management*. 2025. (引用: 17) [[链接]](https://www.semanticscholar.org/paper/cb19a679394ffb464785ca289ccfbd13c926046d)

**[23]** Wenbo Hu, Yining Hong, Yanjun Wang, Le Gao, Zibu Wei et al.. *3DLLM-Mem: Long-Term Spatial-Temporal Memory for Embodied 3D Large Language Model*. 2025. (引用: 17) [[链接]](https://www.semanticscholar.org/paper/3d78432d20f0f285abce701b713b7ede54d0cd9c)

**[24]** Ning Shang, L. Zhang, Siyuan Wang, Gaokai Zhang, Gilsinia Lopez et al.. *LongRoPE2: Near-Lossless LLM Context Window Scaling*. 2025. (引用: 16) [[链接]](https://www.semanticscholar.org/paper/929ac69abb84bb8e6cb0e0a6fe1ed8b8e7924a2d)

**[25]** Gun Il Kim, Sunga Hwang, Beakcheol Jang. *Efficient Compressing and Tuning Methods for Large Language Models: A Systematic Literature Review*. 2025. (引用: 16) [[链接]](https://www.semanticscholar.org/paper/b073de891287423915b1709c4cc90f40756c38b9)

**[26]** Yaxiong Wu, Yongyue Zhang, Sheng Liang, Yong Liu. *SGMem: Sentence Graph Memory for Long-Term Conversational Agents*. 2025. (引用: 15) [[链接]](https://www.semanticscholar.org/paper/6721171b3d6c84336c9450dfb01f40887ccbd872)

**[27]** Li Zhang, Youhe Jiang, Guoliang He, Xin Chen, Han Lv et al.. *Efficient Mixed-Precision Large Language Model Inference with TurboMind*. 2025. (引用: 13) [[链接]](https://www.semanticscholar.org/paper/b29e9bbe560c5f96e7fddc9f7ba1cf667252cd37)

**[28]** Kexin Chu, Zecheng Lin, Dawei Xiang, Zixu Shen, Jianchang Su et al.. *Selective KV-Cache Sharing to Mitigate Timing Side-Channels in LLM Inference*. 2025. (引用: 12) [[链接]](https://www.semanticscholar.org/paper/370ea3e5e8f544c9d34dc8bb153bbce5c6811665)

**[29]** Yuxiang Zhang, Jiangming Shu, Ye Ma, Xueyuan Lin, Shangxi Wu et al.. *Memory as Action: Autonomous Context Curation for Long-Horizon Agentic Tasks*. 2025. (引用: 12) [[链接]](https://www.semanticscholar.org/paper/5f0f0c762c094bb6e1deba3222331ee51b98d1fc)

**[30]** Cheng-Ping Hsieh, Simeng Sun, Samuel Kriman, Shantanu Acharya, Dima Rekesh et al.. *RULER: What's the Real Context Size of Your Long-Context Language Models?*. 2024. (引用: 770) [[链接]](https://www.semanticscholar.org/paper/ac5824e9ff924a937d9eef379d0b581de2417678)

**[31]** Coleman Hooper, Sehoon Kim, Hiva Mohammadzadeh, Michael W. Mahoney, Y. Shao et al.. *KVQuant: Towards 10 Million Context Length LLM Inference with KV Cache Quantization*. 2024. (引用: 449) [[链接]](https://www.semanticscholar.org/paper/b085968c4362fb286ad6c5ef71a5db9630da0498)

**[32]** Zeyu Zhang, Quanyu Dai, Xiaohe Bo, Chen Ma, Rui Li et al.. *A Survey on the Memory Mechanism of Large Language Model-based Agents*. 2024. (引用: 434) [[链接]](https://www.semanticscholar.org/paper/b6ab16c8eade03a39830493071d99fc48a736fac)

**[33]** Adyasha Maharana, Dong-Ho Lee, S. Tulyakov, Mohit Bansal, Francesco Barbieri et al.. *Evaluating Very Long-Term Conversational Memory of LLM Agents*. 2024. (引用: 346) [[链接]](https://www.semanticscholar.org/paper/0bf3a1867f7245b8a702093901c66b08b518eafc)

**[34]** Saleh Ashkboos, Maximilian L. Croci, Marcelo Gennari Do Nascimento, Torsten Hoefler, James Hensman. *SliceGPT: Compress Large Language Models by Deleting Rows and Columns*. 2024. (引用: 332) [[链接]](https://www.semanticscholar.org/paper/7754ac3e8ff1286f17593159781487543cdddaba)

**[35]** Yiran Ding, L. Zhang, Chengruidong Zhang, Yuanyuan Xu, Ning Shang et al.. *LongRoPE: Extending LLM Context Window Beyond 2 Million Tokens*. 2024. (引用: 306) [[链接]](https://www.semanticscholar.org/paper/c9603ec967879c24973b5bd48861df2e5555932e)

**[36]** A. Gholami, Z. Yao, Sehoon Kim, Coleman Hooper, Michael W. Mahoney et al.. *AI and Memory Wall*. 2024. (引用: 306) [[链接]](https://www.semanticscholar.org/paper/4c14b1c41cb0aaa68f5d3f4a432f55e7199657ea)

**[37]** Jiaming Tang, Yilong Zhao, Kan Zhu, Guangxuan Xiao, Baris Kasikci et al.. *Quest: Query-Aware Sparsity for Efficient Long-Context LLM Inference*. 2024. (引用: 290) [[链接]](https://www.semanticscholar.org/paper/1c7db9fb18246787fbe3de6e0eaa370ae749e795)

**[38]** Zixuan Zhou, Xuefei Ning, Ke Hong, Tianyu Fu, Jiaming Xu et al.. *A Survey on Efficient Inference for Large Language Models*. 2024. (引用: 212) [[链接]](https://www.semanticscholar.org/paper/5be7e6b04c5a240cff340034aae2b57c677e211f)

**[39]** Di Wu, Hongwei Wang, Wenhao Yu, Yuwei Zhang, Kai-Wei Chang et al.. *LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory*. 2024. (引用: 203) [[链接]](https://www.semanticscholar.org/paper/fd48dc6b433cfcd220b6e769c6179d8ef6fcf862)

**[40]** Bernal Jimenez Gutierrez, Yiheng Shu, Yu Gu, Michihiro Yasunaga, Yu Su. *HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models*. 2024. (引用: 169) [[链接]](https://www.semanticscholar.org/paper/4308208fac24626e0c927ee728038aadc4e87266)

**[41]** Hongye Jin, Xiaotian Han, Jingfeng Yang, Zhimeng Jiang, Zirui Liu et al.. *LLM Maybe LongLM: Self-Extend LLM Context Window Without Tuning*. 2024. (引用: 164) [[链接]](https://www.semanticscholar.org/paper/a9468d8bfa6bd016dfd3128c4e8408e30eb8549b)

**[42]** Haoyang Li, Yiming Li, Anxin Tian, Tianhao Tang, Zhanchao Xu et al.. *A Survey on Large Language Model Acceleration based on KV Cache Management*. 2024. (引用: 99) [[链接]](https://www.semanticscholar.org/paper/6bcd708d2e49b34f34f157daa6bf1c3e062f57c5)

**[43]** Ramya Prabhu, Ajay Nayak, Jayashree Mohan, R. Ramjee, Ashish Panwar. *vAttention: Dynamic Memory Management for Serving LLMs without PagedAttention*. 2024. (引用: 86) [[链接]](https://www.semanticscholar.org/paper/e03827ea5638ae9f9f987b73b2017fd115f9f79b)

**[44]** Kostas Hatalis, Despina Christou, Joshua Myers, Steven Jones, Keith A. Lambert et al.. *Memory Matters: The Need to Improve Long-Term Memory in LLM-Agents*. 2024. (引用: 85) [[链接]](https://www.semanticscholar.org/paper/a0ca8fff30c8d13c32a8da839e3adf335db86b32)

**[45]** Hailin Zhang, Xiaodong Ji, Yiling Chen, Fangcheng Fu, Xupeng Miao et al.. *PQCache: Product Quantization-based KVCache for Long Context LLM Inference*. 2024. (引用: 83) [[链接]](https://www.semanticscholar.org/paper/022f386eb66fc5532dd6f439e7a356fd33ebb9a2)

**[46]** Bin Lin, Tao Peng, Chen Zhang, Minmin Sun, Lanbo Li et al.. *Infinite-LLM: Efficient LLM Service for Long Context with DistAttention and Distributed KVCache*. 2024. (引用: 82) [[链接]](https://www.semanticscholar.org/paper/ee802ccb7fc3a322b824310ae6f29fc6a1e4314b)

**[47]** Zhongwei Wan, Ziang Wu, Che Liu, Jinfa Huang, Zhihong Zhu et al.. *LOOK-M: Look-Once Optimization in KV Cache for Efficient Multimodal Long-Context Inference*. 2024. (引用: 81) [[链接]](https://www.semanticscholar.org/paper/6c5e09cef64fe7fbeab9a6f3f062363bffba917d)

**[48]** Peitian Zhang, Zheng Liu, Shitao Xiao, Ninglu Shao, Qiwei Ye et al.. *Long Context Compression with Activation Beacon*. 2024. (引用: 77) [[链接]](https://www.semanticscholar.org/paper/f69f494ab691481ec353da4be480b334fada6607)

**[49]** Yuxuan Yue, Zhihang Yuan, Haojie Duanmu, Sifan Zhou, Jianlong Wu et al.. *WKVQuant: Quantizing Weight and Key/Value Cache for Large Language Models Gains More*. 2024. (引用: 75) [[链接]](https://www.semanticscholar.org/paper/f608011b0f50a14bb2949c186a7c632a099aa75b)

**[50]** Yehui Tang, Yunhe Wang, Jianyuan Guo, Zhijun Tu, Kai Han et al.. *A Survey on Transformer Compression*. 2024. (引用: 73) [[链接]](https://www.semanticscholar.org/paper/a74a20be53e5767648b5970e30b2d81a9ba8293f)

**[51]** Peng Wang, Zexi Li, Ningyu Zhang, Ziwen Xu, Yunzhi Yao et al.. *WISE: Rethinking the Knowledge Memory for Lifelong Model Editing of Large Language Models*. 2024. (引用: 68) [[链接]](https://www.semanticscholar.org/paper/8ce5f6e28d49e1bc00804fa2fa3e917deb203388)

**[52]** R. Saha, Naomi Sagan, Varun Srivastava, Andrea J. Goldsmith, Mert Pilanci. *Compressing Large Language Models using Low Rank and Low Precision Decomposition*. 2024. (引用: 58) [[链接]](https://www.semanticscholar.org/paper/5de1ce5b5954d86cf7a990533600ca0c8168ac25)

**[53]** F. Strati, Sara McAllister, Amar Phanishayee, Jakub Tarnawski, Ana Klimovic. *DéjàVu: KV-cache Streaming for Fast, Fault-tolerant Generative LLM Serving*. 2024. (引用: 56) [[链接]](https://www.semanticscholar.org/paper/37ffdf2c97a846d20418201d22604004ed1a98ba)

**[54]** Petr Anokhin, Nikita Semenov, Artyom Y. Sorokin, Dmitry Evseev, M. Burtsev et al.. *AriGraph: Learning Knowledge Graph World Models with Episodic Memory for LLM Agents*. 2024. (引用: 56) [[链接]](https://www.semanticscholar.org/paper/e2687f80077e8466918e4aeb2ea52e591bfe7e81)

**[55]** Eunkyung Jo, Yuin Jeong, Sohyun Park, Daniel A. Epstein, Young-Ho Kim. *Understanding the Impact of Long-Term Memory on Self-Disclosure with Large Language Model-Driven Chatbots for Public Health Intervention*. 2024. (引用: 50) [[链接]](https://www.semanticscholar.org/paper/8474164eda27baede5da93d8b73b3b77301374ee)

**[56]** Mengkang Hu, Tianxing Chen, Qiguang Chen, Yao Mu, Wenqi Shao et al.. *HiAgent: Hierarchical Working Memory Management for Solving Long-Horizon Agent Tasks with Large Language Model*. 2024. (引用: 49) [[链接]](https://www.semanticscholar.org/paper/a7fb4245b412f0e54ec26d5973f041d52c83c0ad)

**[57]** Alireza Rezazadeh, Zichao Li, Wei Wei, Yujia Bao. *From Isolated Conversations to Hierarchical Schemas: Dynamic Tree Memory Representation for LLMs*. 2024. (引用: 46) [[链接]](https://www.semanticscholar.org/paper/86aea18148fa67c6fd0eecdc0ee68137fe16a75d)

**[58]** Qianchao Zhu, Jiangfei Duan, Chang Chen, Siran Liu, Xiuhong Li et al.. *SampleAttention: Near-Lossless Acceleration of Long Context LLM Inference with Adaptive Structured Sparse Attention*. 2024. (引用: 40) [[链接]](https://www.semanticscholar.org/paper/5b2c04e082a56c0eb70ed62bc36148919f665e1c)

**[59]** Yifei Liu, Jicheng Wen, Yang Wang, Shengyu Ye, L. Zhang et al.. *VPTQ: Extreme Low-bit Vector Post-Training Quantization for Large Language Models*. 2024. (引用: 39) [[链接]](https://www.semanticscholar.org/paper/e8735aa9bc89f25619fe4f6e5465ade7ec8fc344)

**[60]** Hongkang Yang, Zehao Lin, Wenjin Wang, Hao Wu, Zhiyu Li et al.. *Memory3: Language Modeling with Explicit Memory*. 2024. (引用: 38) [[链接]](https://www.semanticscholar.org/paper/2c4f702a4bbb733e1abfb722c5c74fa15aa85ee5)

**[61]** Jihoon Tack, Jaehyung Kim, Eric Mitchell, Jinwoo Shin, Yee Whye Teh et al.. *Online Adaptation of Language Models with a Memory of Amortized Contexts*. 2024. (引用: 37) [[链接]](https://www.semanticscholar.org/paper/366441034ec03b2fd72e29c246c49389a50b8ad8)

**[62]** Tianyu Fu, Haofeng Huang, Xuefei Ning, Genghan Zhang, Boju Chen et al.. *Mixture of Attention Spans: Optimizing LLM Inference Efficiency with Heterogeneous Sliding-Window Lengths*. 2024. (引用: 37) [[链接]](https://www.semanticscholar.org/paper/966a36fdc59702889a2fe44f47631fd0065ed5ef)

**[63]** Xun Jiang, Feng Li, Han Zhao, Jiayin Wang, Jun Shao et al.. *Long Term Memory: The Foundation of AI Self-Evolution*. 2024. (引用: 30) [[链接]](https://www.semanticscholar.org/paper/5007fb901de5e32adf27e6ca129b38f878c5b4af)

**[64]** Xiurui Pan, Endian Li, Qiao Li, Shengwen Liang, Yizhou Shan et al.. *InstInfer: In-Storage Attention Offloading for Cost-Effective Long-Context LLM Inference*. 2024. (引用: 25) [[链接]](https://www.semanticscholar.org/paper/23a3c4d49c3fc652f464da4b482deb739bd63351)

**[65]** Sangyeob Kim, Sangjin Kim, Wooyoung Jo, Soyeon Kim, Seongyon Hong et al.. *20.5 C-Transformer: A 2.6-18.1μJ/Token Homogeneous DNN-Transformer/Spiking-Transformer Processor with Big-Little Network and Implicit Weight Generation for Large Language Models*. 2024. (引用: 24) [[链接]](https://www.semanticscholar.org/paper/bd7831ca2ee267a179491f97517077b53d433689)

**[66]** Seo Hyun Kim, Kai Tzu-iunn Ong, Taeyoon Kwon, Namyoung Kim, Keummin Ka et al.. *Towards Lifelong Dialogue Agents via Timeline-based Memory Management*. 2024. (引用: 21) [[链接]](https://www.semanticscholar.org/paper/a7645ac747cfde0a6dcf865c5279b891f303bdc4)

**[67]** Aashiq Muhamed, Oscar Li, David P. Woodruff, Mona T. Diab, Virginia Smith. *GRASS: Compute Efficient Low-Memory LLM Training with Structured Sparse Gradients*. 2024. (引用: 20) [[链接]](https://www.semanticscholar.org/paper/0c909ef8b889dcf751fde42aa9ef97ff7a619232)

**[68]** Jiale Xu, Rui Zhang, Cong Guo, Weiming Hu, Zihan Liu et al.. *vTensor: Flexible Virtual Tensor Management for Efficient LLM Serving*. 2024. (引用: 17) [[链接]](https://www.semanticscholar.org/paper/c974d12ded9d1e6a3acb744ba737e0d2646e268d)

**[69]** Xuan Shen, Pu Zhao, Yifan Gong, Zhenglun Kong, Zheng Zhan et al.. *Search for Efficient Large Language Models*. 2024. (引用: 14) [[链接]](https://www.semanticscholar.org/paper/18465f8ecb733960c17b22c468a196440a59cf0f)

**[70]** Chengtao Lai, Zhongchun Zhou, Akash Poptani, Wei Zhang. *LCM: LLM-focused Hybrid SPM-cache Architecture with Cache Management for Multi-Core AI Accelerators*. 2024. (引用: 11) [[链接]](https://www.semanticscholar.org/paper/55b601400d2cf4b7994c7df62dd864c8141a5679)

**[71]** Bagus Hanindhito, Bhavesh Patel, L. John. *Bandwidth Characterization of DeepSpeed on Distributed Large Language Model Training*. 2024. (引用: 9) [[链接]](https://www.semanticscholar.org/paper/fa941495588d9b846a3b86f70155a8d237d6fa05)

**[72]** Da Ma, Lu Chen, Situo Zhang, Yuxun Miao, Su Zhu et al.. *Compressing KV Cache for Long-Context LLM Inference with Inter-Layer Attention Similarity*. 2024. (引用: 9) [[链接]](https://www.semanticscholar.org/paper/a7ebfd44de6eb3d9df4a2954c348ff1e17349a66)

**[73]** Mathis Pink, Vy A. Vo, Qinyuan Wu, Jianing Mu, Javier Turek et al.. *Assessing Episodic Memory in LLMs with Sequence Order Recall Tasks*. 2024. (引用: 9) [[链接]](https://www.semanticscholar.org/paper/cfba39bc6adee8b99c1ced4ba150b9e3099ee34e)

**[74]** Hassan Ali, Philipp Allgeuer, Carlo Mazzola, G. Belgiovine, Burak Can Kaplan et al.. *Robots Can Multitask Too: Integrating a Memory Architecture and LLMs for Enhanced Cross-Task Robot Action Generation*. 2024. (引用: 8) [[链接]](https://www.semanticscholar.org/paper/86e6a0d8e36fcccaf13b4dd8c24433999d1d7bae)

**[75]** Jincheng Dai, Zhuo Huang, Haiyun Jiang, Chen Chen, Deng Cai et al.. *CORM: Cache Optimization with Recent Message for Large Language Model Inference*. 2024. (引用: 7) [[链接]](https://www.semanticscholar.org/paper/39835c99ded942f08dd6e8355f1a8681a58b0be6)

**[76]** Chensen Huang, Guibo Zhu, Xuepeng Wang, Yifei Luo, Guojing Ge et al.. *Recurrent Context Compression: Efficiently Expanding the Context Window of LLM*. 2024. (引用: 7) [[链接]](https://www.semanticscholar.org/paper/1102088716730adc1dea06cfa1741f91bb6fa0e9)

**[77]** Pinxue Zhao, Hailin Zhang, Fangcheng Fu, Xiaonan Nie, Qibin Liu et al.. *MEMO: Fine-grained Tensor Management For Ultra-long Context LLM Training*. 2024. (引用: 5) [[链接]](https://www.semanticscholar.org/paper/1fe8ac2dba28b523a868b44bb82b6155b04766d3)

**[78]** Hanmei Yang, Jin Zhou, Yao Fu, Xiaoqun Wang, Ramine Roane et al.. *ProTrain: Efficient LLM Training via Memory-Aware Techniques*. 2024. (引用: 5) [[链接]](https://www.semanticscholar.org/paper/e7c318d1044309bfe69865ab1db9db870b153b4a)

**[79]** Hyucksung Kwon, K. Koo, Janghyeon Kim, Woongkyu Lee, Minjae Lee et al.. *PIMphony: Overcoming Bandwidth and Capacity Inefficiency in PIM-Based Long-Context LLM Inference System*. 2024. (引用: 5) [[链接]](https://www.semanticscholar.org/paper/cf2205a1c198be91ac53ffd120c3602b5b5661ec)

**[80]** Seo Hyun Kim, Kai Tzu-iunn Ong, Taeyoon Kwon, Namyoung Kim, Keummin Ka et al.. *THEANINE: Revisiting Memory Management in Long-term Conversations with Timeline-augmented Response Generation*. 2024. (引用: 5) [[链接]](https://www.semanticscholar.org/paper/373b56dd4f6861e5e0622f7eb2959f05aac2edc1)

**[81]** Edoardo Cetin, Qi Sun, Tianyu Zhao, Yujin Tang. *An Evolved Universal Transformer Memory*. 2024. (引用: 5) [[链接]](https://www.semanticscholar.org/paper/9505c9ec941a22788d3a80ce794620e24ded0e90)

**[82]** Rongxin Cheng, Yuxin Lai, Xingda Wei, Rong Chen, Haibo Chen. *KunServe: Parameter-centric Memory Management for Efficient Memory Overloading Handling in LLM Serving*. 2024. (引用: 4) [[链接]](https://www.semanticscholar.org/paper/c8d1f0f4dfba6980bf563527ab17351fcd1e2f5c)

**[83]** Saurabh Agarwal, Anyong Mao, Aditya Akella, Shivaram Venkataraman. *SYMPHONY: Improving Memory Management for LLM Inference Workloads*. 2024. (引用: 3) [[链接]](https://www.semanticscholar.org/paper/b0a8cf33c94ba3d951ce599ac4760a2eded16997)

**[84]** Dejan Dodi, Ć. DušanREGODI. *Tokenization and Memory Optimization for Reducing GPU Load in NLP Deep Learning Models*. 2024. (引用: 3) [[链接]](https://www.semanticscholar.org/paper/09c46a8c602b0ec9282a898ee2ec7a5d8734cbe0)

**[85]** A. AadharshAadhithya, S. SachinKumar, Soman K.p.. *Enhancing Long-Term Memory using Hierarchical Aggregate Tree for Retrieval Augmented Generation*. 2024. (引用: 3) [[链接]](https://www.semanticscholar.org/paper/070c3c063a80bbcf81d927d6d3351a882153e962)

**[86]** Dayuan Chen, Noe Soto, Jonas F. Tuttle, Ziliang Zong. *Understanding Multi-Dimensional Efficiency of Fine-Tuning Large Language Models Using SpeedUp, MemoryUp, and EnergyUp*. 2024. (引用: 3) [[链接]](https://www.semanticscholar.org/paper/2d578d0ab26d4506f615adf0a1b811015e21265f)

---

*本报告由 Search-By-Agent Pipeline 自动生成，所有评述严格基于检索到的文献摘要，未引入外部知识。*
