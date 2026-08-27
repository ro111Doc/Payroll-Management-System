# Payroll-Management-System
工资查询和工资相关政策查询

## 1. 核心功能

### 1.1 工资查询

- 按用户姓名查询个人工资明细
- 按指定月份/月份范围/年份限制个人工资明细查询范围
- 支持计算相同工资对应的合计值

### 1.2 政策查询

基于《国办发2015_18号机关事业单位职业年金办法》《中华人民共和国社会保险法2018修正》《住房公积金管理条例_司法部行政法规库》三份文档，提供工资相关政策查询功能。

- 按关键词/标签检索（如“职业年金”“基本养老保险”“社会保险基金”）

- 政策原文 + 智能解读（重点提炼）

  

## 2. 核心技术

| 模块                       | 技术选型                          | 职责                                                         |
| :------------------------- | :-------------------------------- | :----------------------------------------------------------- |
| **意图识别与分类**         | LLM                               | 将用户问题分为四类：工资查询、其他薪资查询、非相关问题、政策查询 |
| **提取工资查询所需的参数** | LLM                               | 提取用户姓名、查询月份、查询年份、查询关键词，并以 JSON 格式输出提取结果 |
| **工资回答生成**           | LLM                               | 依据查询到的工资数据回答用户问题                             |
| **政策回答生成**           | LLM                               | 基于检索到的政策片段，结合问题生成清晰、权威的解读           |
| **工资数据获取**           | HTTP 请求模块                     | 构造请求体调用内部工资接口，获取原始结构化数据               |
| **政策知识检索**           | Chroma 向量数据库                 | 存储政策文档切片，支持语义检索                               |
| **知识库分段策略**         | 父子分段（Parent-Child Chunking） | 父段保留完整上下文，子段用于精准匹配，兼顾召回率与准确性     |

## 3. 项目目录结构

```yaml
train/                          # 项目根目录
├─ .claude/                     # Claude Code本地缓存目录
├─ config/                      # 系统固定配置模块
│  ├─ __init__.py
│  └─ settings.py               # 读取.env
├─ docx/                        # 原始政策文档
├─ handlers/                    # 接口请求处理器
│  ├─ __init__.py
│  └─ chat.py                   # 接收用户输入，调用工作流
├─ knowledge/                   # RAG知识库模块
│  ├─ chroma_db/                # Chroma向量数据库持久化存储文件夹
│  ├─ __init__.py
│  ├─ build_knowledge.py        # 构建知识库
│  ├─ parent_child_mapping      # 文档层级映射，记录政策段落父子关系
│  └─ query_knowledge.py        # 知识库检索
├─ llm/                         # 大模型相关封装
│  ├─ __init__.py
│  ├─ classifier.py             # 问题分类器，区分：工资查询/其他薪资/政策/无关问题
│  ├─ model.py                  # LLM 统一配置与创建模块
│  ├─ policy_qa.py              # 政策问答：传入检索到的知识库片段，生成政策回答
│  ├─ salary_answer.py          # 工资业务回答组装，拼接接口返回数据生成自然语言
│  └─ salary_params.py          # 工资查询：把用户问题转成调用工资接口的请求参数
├─ models/                      # 用户请求数据模型
│  ├─ __init__.py
│  └─ user_request.py           # UserRequest模型，带校验
├─ services/                    # 外部业务服务调用
│  ├─ __init__.py
│  ├─ salary_http.py            # HTTP请求，调用内部工资业务接口
│  └─ salary_parser.py          # 解析工资接口返回的原始响应数据
├─ workflow/                    # 业务工作流，路由分发
│  ├─ __init__.py
│  └─ router.py                 # 根据分类器结果，将用户请求分发到对应的处理分支
├─ .env                         # 环境变量，存放API_KEY、接口密钥等敏感配置
├─ .gitignore                   # git忽略清单
├─ ce.py / ce2.py / ce3.py      # 临时测试脚本，调试用
├─ main.py                      # 项目主入口
├─ README.md                    # 项目说明文档
└─ train.py                     # 调试用
```

.env内部说明：存放DeepSeek API_KEY、工资接口。

- DeepSeek API_KEY：

  ```
  DEEPSEEK_API_KEY= （我的api key）
  DEEPSEEK_BASE_URL=https://api.deepseek.com/anthropic
  DEEPSEEK_MODEL=deepseek-v4-flash
  DEEPSEEK_TEMPERATURE=0
  DEEPSEEK_TIMEOUT=60
  DEEPSEEK_MAX_TOKENS=1024
  ```

- 工资接口：

  ```
  SALARY_AUTHORIZATION=（不可告知的）
  SALARY_AUTHORIZATION_CODE=（不可告知的）
  SALARY_AUTHORIZATION_ID=（不可告知的）
  SALARY_AUTHORIZATION_ROLEID=（不可告知的）
  SALARY_BASE_URL=（不可告知的）
  ```

