---
name: ralph-bridge
description: >-
  桥接 SDD 规划产物到 ralph-v2。读完 SDD 的 spec.md / tasks.json 后自动生成 prd.json，
  然后启动 ralph-v2 自主执行。当用户完成规划后说"用 ralph 执行"或"自动构建"时触发。
  不要用于没有规划产物的项目——先用 SDD 或 flow 做出 spec。
model: sonnet
---

# Ralph Bridge — SDD → ralph-v2 桥接

## 触发条件

用户完成 SDD 规划后说：
- "用 ralph 执行"
- "交给 ralph"
- "自动构建"
- "让 ralph 来做"
- "/ralph"

## 工作流

### Step 1: 收集规划产物

按优先级查找：
1. `.sdd/spec.md` + `.sdd/tasks.json`（SDD 标准输出）
2. `.agents/specs/` 下的 spec 文件（Flow 输出）
3. `.dev/` 下的 PRD 文件（dev-workflow 输出）
4. 当前 CLAUDE.md 中的目标描述（最后手段）

**找不到任何产物？** → 告诉用户先跑 SDD：用 `/sdd:specify` 写出规格。

### Step 2: 生成 prd.json

把收集到的规划信息转换为 ralph-v2 的 `prd.json` 格式：

```json
{
  "project": "从 spec 提取项目名",
  "description": "1 行描述",
  "platform": "1d-platform",
  "tech_stack": ["从 spec/design 提取"],
  "env_vars": ["需要的环境变量"],
  "branchName": "feat/功能名",
  "userStories": [
    {
      "id": "US-001",
      "title": "从 tasks.json 或 spec 转换",
      "description": "As a user, I want X so that Y",
      "priority": "P0",
      "effort_hours": 4,
      "dependencies": [],
      "acceptance_criteria": [
        "从 spec 的 Given/When/Then 提取"
      ],
      "spec_hints": {
        "operation_type": "CRUD | text_generate | data_query | ui_build",
        "data_flow": "数据流向",
        "pages": ["涉及的页面路径"],
        "server_routes": ["API 路由"]
      },
      "state": "pending"
    }
  ],
  "implementation_order": ["US-001"],
  "total_effort_hours": 0,
  "notes": "由 ralph-bridge 从 SDD 规划自动生成"
}
```

### Step 3: 展示 prd.json 并启动

生成后简要展示：
- 几个故事、总预估工时
- P0/P1/P2 分布

然后直接启动 ralph-v2 skill 开始执行。ralph-v2 会接管后续的 Plan → Implement → Review → Commit 循环。

## 和 ralph-v2 的关系

```
SDD 规划产物 → ralph-bridge（这个 skill）→ 生成 prd.json → ralph-v2（执行引擎）
```

- **ralph-bridge** = 翻译层：把 SDD 的输出"翻译"成 ralph-v2 能读的 prd.json
- **ralph-v2** = 执行引擎：读 prd.json，跑 Plan → Implement → Review → Commit

如果你已经有 prd.json，直接用 ralph-v2，不需要 bridge。
