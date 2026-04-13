# 文献综述报告: Vision Language Action

> 生成时间: 2026-04-13 02:50:56 CST  
> 分析论文数: 30  
> 技术流派数: 4

---

## 目录

1. [Embodied AI Applications & Systems](#embodied-ai-applications-&-systems) (8 篇)
2. [Core VLA Models & Learning Techniques](#core-vla-models-&-learning-techniques) (6 篇)
3. [Physical Robotics & Hardware Design](#physical-robotics-&-hardware-design) (4 篇)
4. [Foundations, Surveys, and Benchmarks](#foundations,-surveys,-and-benchmarks) (12 篇)

---

## 1. Embodied AI Applications & Systems

### Review of Embodied AI Applications & Systems

The research within the Embodied AI Applications & Systems school demonstrates a strong, unifying trend: the integration of large-scale AI foundation models, particularly Vision-Language Models (VLMs), to solve complex decision-making and navigation tasks. While the applications span from smart manufacturing, as discussed in "Embodied Intelligence Toward Future Smart Manufacturing in the Era of AI Foundation Model," to autonomous vehicles, the predominant focus is on Vision-and-Language Navigation (VLN).

Within the VLN-focused research, a key point of divergence is the agent's approach to memory and environmental representation. "MapNav: A Novel Memory Representation via Annotated Semantic Maps for VLM-based Vision-and-Language Navigation" and "CityNavAgent: Aerial Vision-and-Language Navigation with Hierarchical Semantic Planning and Global Memory" both advocate for structured, explicit memory systems—using annotated semantic maps and global topological graphs, respectively—to reduce computational overhead and manage long-horizon tasks. In contrast, "NaVid: Video-based VLM Plans the Next Step for Vision-and-Language Navigation" takes a minimalist approach, relying solely on a raw video stream to encode spatio-temporal context, aiming to improve generalization and bridge the sim-to-real gap. Further advancing this, "WMNav: Integrating Vision-Language Models into World Models for Object Goal Navigation" integrates VLMs into a world model to predict future states and reduce risky interactions.

Another significant trend is the enhancement of agent learning and architecture. Several papers move beyond standard supervised fine-tuning by incorporating reinforcement learning. "VLN-R1: Vision-Language Navigation via Reinforcement Fine-Tuning" employs reinforcement fine-tuning to handle continuous action spaces, while "Embodied AI-Enhanced Vehicular Networks: An Integrated Vision Language Models and Reinforcement Learning Method" uses Deep Reinforcement Learning to optimize transmission strategies. Architecturally, "DriveMoE: Mixture-of-Experts for Vision-Language-Action Model in End-to-End Autonomous Driving" introduces a novel Mixture-of-Experts framework, enabling an agent to dynamically activate specialized modules to handle diverse and complex driving scenarios.

In summary, this collection highlights a field rapidly maturing around the capabilities of foundation models. The core innovation is shifting from the base models to the specialized architectures, memory systems, and learning paradigms that enable them to operate effectively and efficiently in the physical world.

### 参考文献 — Embodied AI Applications & Systems

| # | 论文标题 | 年份 | 引用数 | 链接 |
|---|---------|------|--------|------|
| 1 | MapNav: A Novel Memory Representation via Annotated Semantic Maps for VLM-based Vision-and-Language Navigation | 2025 | 50 | [链接](https://www.semanticscholar.org/paper/6ecbf8a5e595bf0704a21b7b3b51626f72dae9cc) |
| 2 | DriveMoE: Mixture-of-Experts for Vision-Language-Action Model in End-to-End Autonomous Driving | 2025 | 57 | [链接](https://www.semanticscholar.org/paper/c25b7f5f7c86eeeba5bd897fae216f5d0ac6c62d) |
| 3 | VLN-R1: Vision-Language Navigation via Reinforcement Fine-Tuning | 2025 | 48 | [链接](https://www.semanticscholar.org/paper/c0769f42c71a091546bc1c8966e50e9b8efae476) |
| 4 | Embodied Intelligence Toward Future Smart Manufacturing in the Era of AI Foundation Model | 2025 | 61 | [链接](https://www.semanticscholar.org/paper/e4ad11ce3189456e382a8b62a178c119c64a3e1e) |
| 5 | Embodied AI-Enhanced Vehicular Networks: An Integrated Vision Language Models and Reinforcement Learning Method | 2025 | 36 | [链接](https://www.semanticscholar.org/paper/c48d5a0c375e6a735c296027776569d59cec8507) |
| 6 | WMNav: Integrating Vision-Language Models into World Models for Object Goal Navigation | 2025 | 35 | [链接](https://www.semanticscholar.org/paper/72029ba479ffdd546f92e45314515742a8ebe5b8) |
| 7 | NaVid: Video-based VLM Plans the Next Step for Vision-and-Language Navigation | 2024 | 209 | [链接](https://www.semanticscholar.org/paper/12693672913f00a32b31fe68a3d0d3d4c40cc352) |
| 8 | CityNavAgent: Aerial Vision-and-Language Navigation with Hierarchical Semantic Planning and Global Memory | 2025 | 18 | [链接](https://www.semanticscholar.org/paper/0f30f667035352220102670c5b52f5133dfc579f) |

---

## 2. Core VLA Models & Learning Techniques

### Review of Core VLA Models & Learning Techniques

The research within the **Core VLA Models & Learning Techniques** school demonstrates a concerted effort to advance Vision-Language-Action (VLA) models beyond simple imitation, focusing on enhancing reasoning, architectural innovation, and robust learning strategies. A prominent trend is the explicit integration of reasoning mechanisms to overcome the limitations of black-box decision-making. For instance, "VLA-R1: Enhancing Reasoning in Vision-Language-Action Models" introduces a post-training strategy using Reinforcement Learning from Verifiable Rewards (RLVR) and a new chain-of-thought dataset to reinforce reasoning quality. Similarly, "DualCoT-VLA: Visual-Linguistic Chain of Thought via Parallel Reasoning for Vision-Language-Action Models" proposes a novel parallel reasoning mechanism, combining visual and linguistic CoT to simultaneously handle low-level spatial understanding and high-level task planning, thereby reducing the latency and compounding errors of sequential approaches. This focus on structured reasoning is also echoed in "DM0: An Embodied-Native Vision-Language-Action Model towards Physical AI" through its Embodied Spatial Scaffolding strategy.

Architecturally, these works build upon and refine Transformer-based frameworks. "F1: A Vision-Language-Action Model Bridging Understanding and Generation to Actions" utilizes a Mixture-of-Transformer architecture to integrate visual foresight generation directly into decision-making, reformulating action generation as a foresight-guided inverse dynamics problem to mitigate short-sighted behavior. Another key approach is seen in "Multimodal Diffusion Transformer: Learning Versatile Behavior from Multimodal Goals", which presents a diffusion policy framework capable of learning from multimodal goals even with sparse language annotations. Many of these models, including "F1" and "DM0", adopt sophisticated three-stage training pipelines. "DM0" notably pioneers an "Embodied-Native" framework designed to unify manipulation and navigation by pretraining on diverse data sources.

Contrasting with these large-scale models, "Development of compositionality through interactive learning of language and action of robots" explores the foundational principles of VLA learning. It employs a brain-inspired neural network based on predictive coding and active inference to investigate how linguistic compositionality can emerge concomitantly with sensorimotor skills, highlighting a different path toward generalization that diverges from the dominant Transformer-based paradigm.

### 参考文献 — Core VLA Models & Learning Techniques

| # | 论文标题 | 年份 | 引用数 | 链接 |
|---|---------|------|--------|------|
| 1 | F1: A Vision-Language-Action Model Bridging Understanding and Generation to Actions | 2025 | 29 | [链接](https://www.semanticscholar.org/paper/5380fe9137f1ffec91b06fe4db60a083759a34fd) |
| 2 | Multimodal Diffusion Transformer: Learning Versatile Behavior from Multimodal Goals | 2024 | 137 | [链接](https://www.semanticscholar.org/paper/b46758118aef964ee41e3a8da15352a9fc6c59b8) |
| 3 | VLA-R1: Enhancing Reasoning in Vision-Language-Action Models | 2025 | 20 | [链接](https://www.semanticscholar.org/paper/084f8a422b1a58c21d1e061e8a594f9e836a960b) |
| 4 | DM0: An Embodied-Native Vision-Language-Action Model towards Physical AI | 2026 | 2 | [链接](https://www.semanticscholar.org/paper/f7937828184d3e2d704a6342bdcefa0fe516b2e8) |
| 5 | DualCoT-VLA: Visual-Linguistic Chain of Thought via Parallel Reasoning for Vision-Language-Action Models | 2026 | 2 | [链接](https://www.semanticscholar.org/paper/6ccce352ceb58e5a0ff5dab3a15e4929b8a79aee) |
| 6 | Development of compositionality through interactive learning of language and action of robots | 2025 | 18 | [链接](https://www.semanticscholar.org/paper/7b284a969eda3e5d163a2487340a9f580196810d) |

---

## 3. Physical Robotics & Hardware Design

### Review of Physical Robotics & Hardware Design

The research within the Physical Robotics & Hardware Design school demonstrates a strong focus on creating compact, adaptable robots capable of navigating complex and often extreme environments. A unifying theme across this collection is the principle of **multimodality**, which is explored both in physical locomotion and in sensory perception to overcome significant environmental challenges.

A prominent trend is the development of miniature robots with versatile movement capabilities. For instance, "A springtail-inspired multimodal walking-jumping microrobot" addresses how small-scale robots can overcome terrestrial obstacles by integrating walking and jumping behaviors using shape memory alloy actuators and a bio-inspired appendage. A similar actuation method is employed in "Miniature deep-sea morphable robot with multimodal locomotion," which tackles the extreme challenge of high hydrostatic pressure in deep-sea environments. This work uses bistable chiral metamaterials and sealed shape memory alloys to create a robust, morphable robot. Expanding on adaptability, "Dynamic Control of Multimodal Motion for Bistable Soft Millirobots in Complex Environments" presents a soft millirobot that achieves multimodal motion through reversible morphology switching, controlled by magnetic fields to navigate narrow biological cavities for medical tasks. These papers collectively showcase innovation in advanced materials and actuation to enable sophisticated locomotion at a small scale.

Shifting from actuation to perception, "Boxi: Design Decisions in the Context of Algorithmic Performance for Robotics" provides a complementary perspective. While the other papers focus on the design of novel physical mechanisms, this work addresses the critical, higher-level problem of designing robust multimodal sensor suites. It introduces the Boxi payload and provides a guideline for integrating, calibrating, and synchronizing sensors to directly improve the performance of algorithms for state estimation and mapping.

In summary, this school advances physical robotics on two fronts: pioneering novel actuators and bio-inspired mechanisms for small-scale multimodal locomotion, while simultaneously establishing foundational design principles for the integrated sensor systems that enable robots to robustly perceive their world.

### 参考文献 — Physical Robotics & Hardware Design

| # | 论文标题 | 年份 | 引用数 | 链接 |
|---|---------|------|--------|------|
| 1 | Miniature deep-sea morphable robot with multimodal locomotion | 2025 | 41 | [链接](https://www.semanticscholar.org/paper/e3c563506087a62b8530b33ed1f523ad2ead9992) |
| 2 | A springtail-inspired multimodal walking-jumping microrobot | 2025 | 26 | [链接](https://www.semanticscholar.org/paper/78c8b60a611144af3e28005d1954346f2d479f1b) |
| 3 | Dynamic Control of Multimodal Motion for Bistable Soft Millirobots in Complex Environments | 2025 | 21 | [链接](https://www.semanticscholar.org/paper/a1ca16bbea396e2a7a54099688156d798dbeef50) |
| 4 | Boxi: Design Decisions in the Context of Algorithmic Performance for Robotics | 2025 | 18 | [链接](https://www.semanticscholar.org/paper/8a75b6baf9e677c64b20c86241d9646c335bfcde) |

---

## 4. Foundations, Surveys, and Benchmarks

### Review of Foundations, Surveys, and Benchmarks

The papers in this school collectively establish the foundational groundwork for the next generation of embodied AI, primarily by mapping the current landscape, identifying critical deficiencies in Vision-Language-Action (VLA) models, and proposing rigorous methods for evaluation. A prominent trend is the proliferation of comprehensive surveys that aim to structure this rapidly evolving field. Works like "A Survey on Vision-Language-Action Models for Embodied AI" and "Large VLM-based Vision-Language-Action Models for Robotic Manipulation: A Survey" provide the first systematic taxonomies, while others such as "Towards Embodied Agentic AI" and "Large Model Empowered Embodied AI" focus on classifying agentic architectures and decision-making paradigms.

Building on this organizational effort, a significant portion of the research shifts to identifying and rectifying core limitations in existing models. A common thread is the inadequacy of current VLMs in understanding the physical world. This is directly addressed in "PhysBench: Benchmarking and Enhancing Vision-Language Models for Physical World Understanding," which introduces a benchmark to measure physical reasoning. Similarly, "Spatial Reasoning with Vision-Language Models in Ego-Centric Multi-View Scenes" and "SpatialBot: Precise Spatial Understanding with Vision Language Models" highlight and tackle the severe limitations of VLMs in 3D spatial understanding, introducing the Ego3D-Bench and SpatialBench benchmarks, respectively.

This "benchmark-and-solve" approach is a defining characteristic of the school. Beyond just identifying problems, these papers propose novel frameworks like PhysAgent and models like SpatialBot as initial solutions. This pattern extends to underexplored domains, as seen in "Openfly: A comprehensive platform for aerial vision-language navigation," which provides both a benchmark and a toolchain to spur research in aerial robotics. Critically, the school also includes introspective work. "Limited Linguistic Diversity in Embodied AI Datasets" audits the very data these models are built on, revealing foundational issues in instruction variety, while "Towards Robust and Secure Embodied AI" surveys the crucial but often overlooked aspects of system vulnerabilities. Together, these papers form a cohesive body of work dedicated to building a more robust, well-understood, and empirically-grounded future for embodied intelligence.

### 参考文献 — Foundations, Surveys, and Benchmarks

| # | 论文标题 | 年份 | 引用数 | 链接 |
|---|---------|------|--------|------|
| 1 | PhysBench: Benchmarking and Enhancing Vision-Language Models for Physical World Understanding | 2025 | 89 | [链接](https://www.semanticscholar.org/paper/5b92288640ff2288ea867e628f7d5f94065d90a9) |
| 2 | Towards Robust and Secure Embodied AI: A Survey on Vulnerabilities and Attacks | 2025 | 39 | [链接](https://www.semanticscholar.org/paper/49dac81bbac4f3604a79a9308d484b1cdbd0aaa6) |
| 3 | Scenethesis: A Language and Vision Agentic Framework for 3D Scene Generation | 2025 | 39 | [链接](https://www.semanticscholar.org/paper/e45dfb75e8c320237e06acd56687fbbabfcea05f) |
| 4 | Large VLM-based Vision-Language-Action Models for Robotic Manipulation: A Survey | 2025 | 48 | [链接](https://www.semanticscholar.org/paper/dce821cddbf6a3eb435de04d9353681925aaaecf) |
| 5 | A Survey on Vision-Language-Action Models for Embodied AI | 2024 | 215 | [链接](https://www.semanticscholar.org/paper/ae9a2bcd460354c706aaea8797b1c2c15841a6b6) |
| 6 | Spatial Reasoning with Vision-Language Models in Ego-Centric Multi-View Scenes | 2025 | 37 | [链接](https://www.semanticscholar.org/paper/4fbaf0404b00506a5b00a4d3f5b5e64816ec9f23) |
| 7 | Openfly: A comprehensive platform for aerial vision-language navigation | 2025 | 26 | [链接](https://www.semanticscholar.org/paper/4578312cad81f12bfb5e4ec93ce05782ff8caab8) |
| 8 | SpatialBot: Precise Spatial Understanding with Vision Language Models | 2024 | 161 | [链接](https://www.semanticscholar.org/paper/8a31a1db48f1776e245ee73666f327d00682fc5f) |
| 9 | Limited Linguistic Diversity in Embodied AI Datasets | 2026 | 2 | [链接](https://www.semanticscholar.org/paper/b1bafe4f1bf70db30adb58fc68ebca2518a0d50d) |
| 10 | Towards Embodied Agentic AI: Review and Classification of LLM- and VLM-Driven Robot Autonomy and Interaction | 2025 | 14 | [链接](https://www.semanticscholar.org/paper/f571b998a35c0d2d04a41d4fb62feb77ca94fbd5) |
| 11 | Large Model Empowered Embodied AI: A Survey on Decision-Making and Embodied Learning | 2025 | 15 | [链接](https://www.semanticscholar.org/paper/86abe4d4ffb239fc73e8eedadf197a6e2576a210) |
| 12 | OpenFly: A Versatile Toolchain and Large-scale Benchmark for Aerial Vision-Language Navigation | 2025 | 15 | [链接](https://www.semanticscholar.org/paper/f5204b31083259f8ff97dfc419636b3bfc54dd10) |

---

## 完整参考文献列表

以下为本报告中分析的全部 **30** 篇论文，按年份（降序）及引用数（降序）排列。

**[1]** En Yu, Haoran Lv, Jianjian Sun, Kangheng Lin, Ruitao Zhang et al.. *DM0: An Embodied-Native Vision-Language-Action Model towards Physical AI*. 2026. (引用: 2) [[链接]](https://www.semanticscholar.org/paper/f7937828184d3e2d704a6342bdcefa0fe516b2e8)

**[2]** Zhide Zhong, Junfeng Li, Junjie He, Haodong Yan, Xinlong Gong et al.. *DualCoT-VLA: Visual-Linguistic Chain of Thought via Parallel Reasoning for Vision-Language-Action Models*. 2026. (引用: 2) [[链接]](https://www.semanticscholar.org/paper/6ccce352ceb58e5a0ff5dab3a15e4929b8a79aee)

**[3]** Selma Wanna, Agnes Luhtaru, Jonathan Salfity, Ryan Barron, Juston Moore et al.. *Limited Linguistic Diversity in Embodied AI Datasets*. 2026. (引用: 2) [[链接]](https://www.semanticscholar.org/paper/b1bafe4f1bf70db30adb58fc68ebca2518a0d50d)

**[4]** Wei Chow, Jiageng Mao, Boyi Li, Daniel Seita, V. Guizilini et al.. *PhysBench: Benchmarking and Enhancing Vision-Language Models for Physical World Understanding*. 2025. (引用: 89) [[链接]](https://www.semanticscholar.org/paper/5b92288640ff2288ea867e628f7d5f94065d90a9)

**[5]** Lei Ren, Jiabao Dong, Shuai Liu, Lin Zhang, Lihui Wang. *Embodied Intelligence Toward Future Smart Manufacturing in the Era of AI Foundation Model*. 2025. (引用: 61) [[链接]](https://www.semanticscholar.org/paper/e4ad11ce3189456e382a8b62a178c119c64a3e1e)

**[6]** Zhenjie Yang, Yilin Chai, Xiaosong Jia, Qifeng Li, Yuqian Shao et al.. *DriveMoE: Mixture-of-Experts for Vision-Language-Action Model in End-to-End Autonomous Driving*. 2025. (引用: 57) [[链接]](https://www.semanticscholar.org/paper/c25b7f5f7c86eeeba5bd897fae216f5d0ac6c62d)

**[7]** Lingfeng Zhang, Xiaoshuai Hao, Qinwen Xu, Qiang Zhang, Xinyao Zhang et al.. *MapNav: A Novel Memory Representation via Annotated Semantic Maps for VLM-based Vision-and-Language Navigation*. 2025. (引用: 50) [[链接]](https://www.semanticscholar.org/paper/6ecbf8a5e595bf0704a21b7b3b51626f72dae9cc)

**[8]** Zhangyang Qi, Zhixiong Zhang, Yizhou Yu, Jiaqi Wang, Hengshuang Zhao. *VLN-R1: Vision-Language Navigation via Reinforcement Fine-Tuning*. 2025. (引用: 48) [[链接]](https://www.semanticscholar.org/paper/c0769f42c71a091546bc1c8966e50e9b8efae476)

**[9]** Rui Shao, Wei Li, Lingsen Zhang, Renshan Zhang, Zhiyang Liu et al.. *Large VLM-based Vision-Language-Action Models for Robotic Manipulation: A Survey*. 2025. (引用: 48) [[链接]](https://www.semanticscholar.org/paper/dce821cddbf6a3eb435de04d9353681925aaaecf)

**[10]** Fei Pan, Jiaqi Liu, Zonghao Zuo, Xia He, Zhuyin Shao et al.. *Miniature deep-sea morphable robot with multimodal locomotion*. 2025. (引用: 41) [[链接]](https://www.semanticscholar.org/paper/e3c563506087a62b8530b33ed1f523ad2ead9992)

**[11]** Wenpeng Xing, Minghao Li, Mohan Li, Meng Han. *Towards Robust and Secure Embodied AI: A Survey on Vulnerabilities and Attacks*. 2025. (引用: 39) [[链接]](https://www.semanticscholar.org/paper/49dac81bbac4f3604a79a9308d484b1cdbd0aaa6)

**[12]** Lu Ling, Chen-Hsuan Lin, Tsung-Yi Lin, Yifan Ding, Yuan Zeng et al.. *Scenethesis: A Language and Vision Agentic Framework for 3D Scene Generation*. 2025. (引用: 39) [[链接]](https://www.semanticscholar.org/paper/e45dfb75e8c320237e06acd56687fbbabfcea05f)

**[13]** Mohsen Gholami, Ahmad Rezaei, Weimin Zhou, Sitong Mao, Shunbo Zhou et al.. *Spatial Reasoning with Vision-Language Models in Ego-Centric Multi-View Scenes*. 2025. (引用: 37) [[链接]](https://www.semanticscholar.org/paper/4fbaf0404b00506a5b00a4d3f5b5e64816ec9f23)

**[14]** Ruichen Zhang, Changyuan Zhao, Hongyang Du, Dusit Niyato, Jiacheng Wang et al.. *Embodied AI-Enhanced Vehicular Networks: An Integrated Vision Language Models and Reinforcement Learning Method*. 2025. (引用: 36) [[链接]](https://www.semanticscholar.org/paper/c48d5a0c375e6a735c296027776569d59cec8507)

**[15]** Dujun Nie, Xianda Guo, Yiqun Duan, Ruijun Zhang, Long Chen. *WMNav: Integrating Vision-Language Models into World Models for Object Goal Navigation*. 2025. (引用: 35) [[链接]](https://www.semanticscholar.org/paper/72029ba479ffdd546f92e45314515742a8ebe5b8)

**[16]** Qi Lv, Weijie Kong, Hao Li, Jia Zeng, Zherui Qiu et al.. *F1: A Vision-Language-Action Model Bridging Understanding and Generation to Actions*. 2025. (引用: 29) [[链接]](https://www.semanticscholar.org/paper/5380fe9137f1ffec91b06fe4db60a083759a34fd)

**[17]** Francisco Ramirez Serrano, N. P. Hyun, E. Steinhardt, Pierre-Louis Lechère, Robert J. Wood. *A springtail-inspired multimodal walking-jumping microrobot*. 2025. (引用: 26) [[链接]](https://www.semanticscholar.org/paper/78c8b60a611144af3e28005d1954346f2d479f1b)

**[18]** Yunpeng Gao, Chenhui Li, Zhongrui You, Junli Liu, Zhen Li et al.. *Openfly: A comprehensive platform for aerial vision-language navigation*. 2025. (引用: 26) [[链接]](https://www.semanticscholar.org/paper/4578312cad81f12bfb5e4ec93ce05782ff8caab8)

**[19]** Zhengyuan Xin, Shihao Zhong, Anping Wu, Zhiqiang Zheng, Qing Shi et al.. *Dynamic Control of Multimodal Motion for Bistable Soft Millirobots in Complex Environments*. 2025. (引用: 21) [[链接]](https://www.semanticscholar.org/paper/a1ca16bbea396e2a7a54099688156d798dbeef50)

**[20]** Angen Ye, Zeyu Zhang, Boyuan Wang, Xiaofeng Wang, Dapeng Zhang et al.. *VLA-R1: Enhancing Reasoning in Vision-Language-Action Models*. 2025. (引用: 20) [[链接]](https://www.semanticscholar.org/paper/084f8a422b1a58c21d1e061e8a594f9e836a960b)

**[21]** Weichen Zhang, Chen Gao, Shiquan Yu, Ruiying Peng, Baining Zhao et al.. *CityNavAgent: Aerial Vision-and-Language Navigation with Hierarchical Semantic Planning and Global Memory*. 2025. (引用: 18) [[链接]](https://www.semanticscholar.org/paper/0f30f667035352220102670c5b52f5133dfc579f)

**[22]** Prasanna Vijayaraghavan, J. Queißer, Sergio Verduzco Flores, Jun Tani. *Development of compositionality through interactive learning of language and action of robots*. 2025. (引用: 18) [[链接]](https://www.semanticscholar.org/paper/7b284a969eda3e5d163a2487340a9f580196810d)

**[23]** Jonas Frey, T. Tuna, L. Fu, Cedric Weibel, Katharine Patterson et al.. *Boxi: Design Decisions in the Context of Algorithmic Performance for Robotics*. 2025. (引用: 18) [[链接]](https://www.semanticscholar.org/paper/8a75b6baf9e677c64b20c86241d9646c335bfcde)

**[24]** Wen Liang, Rui Zhou, Yang Ma, Bing Zhang, Songlin Li et al.. *Large Model Empowered Embodied AI: A Survey on Decision-Making and Embodied Learning*. 2025. (引用: 15) [[链接]](https://www.semanticscholar.org/paper/86abe4d4ffb239fc73e8eedadf197a6e2576a210)

**[25]** Yunpeng Gao, Chenhui Li, Zhongrui You, Junli Liu, Zhen Li et al.. *OpenFly: A Versatile Toolchain and Large-scale Benchmark for Aerial Vision-Language Navigation*. 2025. (引用: 15) [[链接]](https://www.semanticscholar.org/paper/f5204b31083259f8ff97dfc419636b3bfc54dd10)

**[26]** Sahar Salimpour, Leijie Fu, Farhad Keramat, L. Militano, G. T. Carughi et al.. *Towards Embodied Agentic AI: Review and Classification of LLM- and VLM-Driven Robot Autonomy and Interaction*. 2025. (引用: 14) [[链接]](https://www.semanticscholar.org/paper/f571b998a35c0d2d04a41d4fb62feb77ca94fbd5)

**[27]** Yueen Ma, Zixing Song, Yuzheng Zhuang, Jianye Hao, Irwin King. *A Survey on Vision-Language-Action Models for Embodied AI*. 2024. (引用: 215) [[链接]](https://www.semanticscholar.org/paper/ae9a2bcd460354c706aaea8797b1c2c15841a6b6)

**[28]** Jiazhao Zhang, Kunyu Wang, Rongtao Xu, Gengze Zhou, Yicong Hong et al.. *NaVid: Video-based VLM Plans the Next Step for Vision-and-Language Navigation*. 2024. (引用: 209) [[链接]](https://www.semanticscholar.org/paper/12693672913f00a32b31fe68a3d0d3d4c40cc352)

**[29]** Wenxiao Cai, Yaroslav Ponomarenko, Jianhao Yuan, Xiaoqi Li, Wankou Yang et al.. *SpatialBot: Precise Spatial Understanding with Vision Language Models*. 2024. (引用: 161) [[链接]](https://www.semanticscholar.org/paper/8a31a1db48f1776e245ee73666f327d00682fc5f)

**[30]** Moritz Reuss, Ömer Erdinç Yagmurlu, Fabian Wenzel, Rudolf Lioutikov. *Multimodal Diffusion Transformer: Learning Versatile Behavior from Multimodal Goals*. 2024. (引用: 137) [[链接]](https://www.semanticscholar.org/paper/b46758118aef964ee41e3a8da15352a9fc6c59b8)

---

*本报告由 Search-By-Agent Pipeline 自动生成，所有评述严格基于检索到的文献摘要，未引入外部知识。*
