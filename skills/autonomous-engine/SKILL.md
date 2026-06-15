---
name: autonomous-engine
description: >-
  自主决策引擎 — 调度器模式。每次激活 spawn 独立子 Agent（干净上下文），
  子 Agent 加载 decision-agent-prompt.md 进行深度研判。
  触发词：自主模式、别等我、自动继续、keep working、autonomous mode、auto-develop、
  决策引擎、继续开发、不用等我、你自己做、auto-continue。
model: sonnet
---

# Autonomous Engine — 调度器模式 v2.0

## 架构变更

**v2.0 核心改动：引擎不再内联运行，而是 spawn 独立子 Agent。**

```
v1.x (旧·内联模式):
  CronCreate 触发 → 当前会话加载 SKILL.md → 在项目对话上下文中运行
  问题: 项目对话历史污染决策 ⚠️

v2.0 (新·隔离模式):
  CronCreate 触发 → 当前会话 spawn Agent 子代理 →
  子代理加载 decision-agent-prompt.md（干净上下文）→ 只读结构化数据文件 →
  返回结构化决策 → 主会话输出摘要
  优势: 零上下文污染 ✅
```

## 你的角色

你是**调度器**，不是决策者。

当引擎被激活时（心跳/手动/内联），你的唯一职责是：
1. 读取 `decision-agent-prompt.md`（子代理的独立系统提示词）
2. 使用 **Agent 工具** spawn 一个独立子代理
3. 将当前激活上下文传递给子代理
4. 子代理完成后，输出简短摘要

**不要自己执行七阶段循环！你的工作是调度。**

---

## 执行流程

### Step 1: 确认激活模式

```
激活来源检测:
  - 如果 prompt 包含 "AUTONOMOUS_HEARTBEAT L2" → 模式 = "heartbeat_l2"
  - 如果 prompt 包含 "AUTONOMOUS_HEARTBEAT L3" → 模式 = "heartbeat_l3"
  - 如果用户主动说触发词 → 模式 = "manual"
  - 如果是回复末尾内联检查 → 模式 = "inline"
```

### Step 2: 快速预检（调度器层面，3 秒内完成）

```
1. 读 calibration.json → cooldown.current_consecutive >= 3？
   是 → 输出 "<!-- HB COOL -->"，EXIT（不 spawn 子代理）

2. 读 autonomous-state.md → GOAL_STATUS == "paused" || "achieved"？
   是 → 输出对应状态，EXIT

3. 检查 decision-agent-prompt.md 是否存在？
   否 → 输出 "<!-- ENGINE ERROR: prompt file missing -->"，EXIT
```

### Step 3: Spawn 子代理

```
使用 Agent 工具，参数如下：

subagent_type: "general-purpose"
description: "自主决策引擎子代理 - {模式}"
prompt: |
  你是 autodev-engine v2.0 的独立决策子代理。

  你的系统提示词来自文件:
  {CLAUDE_PROJECT_DIR}/.claude/skills/autonomous-engine/decision-agent-prompt.md

  ★ 在开始任何分析之前，你必须先读取上述文件作为你的完整操作手册。
  ★ 你的上下文是干净的——你没有主会话的对话历史。
  ★ 你只通过读取结构化数据文件来了解当前状态。

  本次激活信息:
  - 激活模式: {模式}
  - 激活时间: {当前ISO时间}
  - 工作区路径: {CLAUDE_PROJECT_DIR}

  执行步骤:
  1. 首先 Read decision-agent-prompt.md（完整读取）
  2. 按照其中的 §0 冷启动协议判断当前状态
  3. 如果是热运行 → 执行 §1 七阶段研判框架
  4. 如果是冷启动 → 执行 §0.2 冷启动流程
  5. 输出 MUST 包含 <decision>JSON</decision> 标签
  6. 在 <decision> 之外只输出最多 3 行自然语言摘要

  记住：你是独立子代理，你的"记忆"是文件系统，不是对话历史。
```

### Step 4: 处理子代理返回

```
子代理返回后:
  1. 检查返回中是否包含 <decision> 标签
  2. 提取 action_level 和 decision_summary
  3. 如果 action_level >= ACT_NOTIFY:
     → 执行子代理计划的具体行动（子代理不能直接调用工具修改项目文件）
     → 解释: 子代理负责"研判"，主会话负责"执行"
  4. 输出简洁摘要给用户
```

---

## 三种激活方式的具体行为

### 方式 A：心跳 L2（每 7 分钟）

```
收到 "AUTONOMOUS_HEARTBEAT L2" prompt →
  Step 2 预检 →
  Step 3 Spawn 子代理 →
  Step 4 如果子代理建议 ACT_NOTIFY 且 confidence >= 71 →
     执行建议的行动 →
     输出: "🤖 L2 @ {时间} | {行动摘要} | 信心 {分数}"
  否则:
     输出: "<!-- HB {时间} OK -->"
```

### 方式 B：心跳 L3（每 60 分钟）

```
收到 "AUTONOMOUS_HEARTBEAT L3" prompt →
  Step 2 预检 →
  Step 3 Spawn 子代理（description 设为 "L3 深度检查"）→
  子代理会执行完整研判 + 网络研究 + 模式提取 →
  Step 4 输出: "🤖 L3 @ {时间} | {发现摘要}"
```

### 方式 C：用户手动激活

```
用户说触发词 →
  Step 2 预检（跳过冷却检查——用户主动要求）→
  Step 3 Spawn 子代理 →
  Step 4 向用户展示:
    - 当前引擎状态
    - 子代理的研判结果
    - 建议的下一步行动
```

### 方式 D：内联检查（回复末尾）

```
内联检查**不需要 spawn 子代理**（太重了）：
  1. 读 decision-log.jsonl 最后 5 行
  2. 判断是否有明显未完跟进
  3. 有 → 低风险跟进直接在当前回复末尾执行
  4. 无 → 不额外输出
  5. 更新 autonomous-state.md 时间戳

内联检查阈值:
  - 刚修完 bug → 自动运行测试（信心 85，ACT_SILENT）
  - 刚改完文件 → 更新 PROGRESS.md（信心 90，ACT_SILENT）
  - 其他 → 静默
```

---

## 子代理 vs 主会话的职责边界

| 职责 | 子代理（决策者） | 主会话（执行者） |
|------|-----------------|-----------------|
| 读取结构化数据 | ✅ | ✅（仅预检） |
| 分析决策模式 | ✅ | ❌ |
| 网络研究 | ✅ | ❌ |
| 计算信心分 | ✅ | ❌ |
| 输出决策 JSON | ✅ | ❌ |
| 修改项目文件 | ❌ | ✅ |
| 运行测试 | ❌ | ✅ |
| Git 操作 | ❌ | ✅ |
| 发送通知 | ❌ | ✅ |
| 输出用户摘要 | ❌ | ✅ |

**原则：子代理用脑子，主会话用手。**

---

## 上下文污染防护清单

每次调度器激活时确认：
- [ ] 子代理通过 Agent 工具 spawn（不是 Skill 工具）
- [ ] 子代理 prompt 中不包含对话历史
- [ ] 子代理只读 structured data files，不读 audit/transcript
- [ ] 子代理返回的是 JSON，不是长文
- [ ] 主会话只输出摘要，不展开讨论
