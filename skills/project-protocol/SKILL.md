---
name: project-protocol
description: >-
  项目协议系统 — 确保任何项目都有 CLAUDE.md + PROGRESS.md + GATES.md 三件套。
  当进入一个项目目录时自动生效，缺失文件则自举生成。
  触发词：初始化项目、创建项目规范、补齐三件套、project setup、init project。
  这是工作区基础设施 Skill，所有项目自动受其约束。
model: haiku
---

# Project Protocol — 项目协议自举系统

## 这是基础设施 Skill

**所有 x-tool 工作区项目自动受本协议约束。** 不是可选功能。

## 核心机制

```
  Agent 进入项目目录
       ↓
  检查三件套是否存在
   ↙              ↘
 全部存在          缺失文件
   ↓                 ↓
 按规范工作      自动从模板生成
                   ↓
                Agent 继续工作
```

## 三件套定义

| 文件 | 内容 | 谁来写 |
|------|------|--------|
| `CLAUDE.md` | 项目身份、技术栈、入口命令、项目规则 | 模板生成后人工补充 |
| `PROGRESS.md` | 进度追踪、状态标记、变更历史 | 模板生成 + Agent 自动更新 |
| `GATES.md` | 🔴🟡🟢 三级质量门禁 | 模板生成后按项目调整 |

## 触发条件

用户说以下任一句时触发：
- "初始化项目规范"
- "创建三件套"
- "给 XXX 加协议"
- "protocol setup"
- "补齐项目文件"

**更重要的是**：任何 Agent 进入缺少三件套的项目目录时，本 Skill 的 Hook (`protocol-check.py`) 自动触发自举生成。

## 工作流

### Step 1: 探测项目信息

从项目目录已有内容推断：
- 项目名：从目录名或 package.json / README 提取
- 技术栈：从 package.json / requirements.txt / go.mod 等推断
- 入口命令：从 package.json scripts / Makefile / Dockerfile 提取

**推断不到的不猜测**，留空标记 `<!-- TODO -->`。

### Step 2: 从模板生成三件套

使用 `templates/` 下的模板，填充探测到的信息。

### Step 3: 注册到工作区

生成后自动：
1. 更新 `PROJECTS.md` 项目索引
2. 写入 `project-index` memory
3. 不再需要人工操作

## 模板变量

生成时替换：
- `{{PROJECT_NAME}}` → 项目名
- `{{PROJECT_DIR}}` → 项目目录路径
- `{{TECH_STACK}}` → 推断的技术栈
- `{{ENTRY_CMD}}` → 推断的入口命令
- `{{TIMESTAMP}}` → 当前 ISO 时间戳

## 和 PROTOCOL.md 的关系

```
PROTOCOL.md (工作区宪法)
    ↓ 定义规则
project-protocol Skill (本 Skill)
    ↓ 执行规则
protocol-check.py Hook
    ↓ 自动检查 + 自举
每个项目的 CLAUDE.md + PROGRESS.md + GATES.md
```

## 不可跳过的规则

1. 项目目录必须有三件套 — Hook 自动检查
2. 缺失时自动生成 — 不阻塞工作
3. 生成后 Agent 必须按规范工作 — BEFORE → CHANGE → AFTER
