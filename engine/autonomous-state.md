---
name: autonomous-state
description: 自主决策引擎运行时状态 — 目标追踪、进度、冷却计数
metadata:
  type: project
---

# 自主决策引擎状态

<!-- ENGINE_VERSION: 1.0 -->
<!-- LAST_ACTIVE: 2026-06-15T00:00:00Z -->
<!-- ACTIVE_PROJECT: infrastructure -->
<!-- CURRENT_PHASE: observe -->
<!-- CONSECUTIVE_AUTONOMOUS_ACTIONS: 0 -->

## 当前目标

<!-- GOAL_ID: none -->
<!-- GOAL_STATUS: paused -->
暂无激活目标。用户设定目标后引擎自动启动。

## 上次会话

无历史会话。

## 引擎配置

- 自主级别: moderate (OBSERVE → SUGGEST → PREPARE → ACT_NOTIFY → ACT_SILENT)
- 冷却阈值: 连续 3 次自主行动后无用户交互 → 强制冷却
- L1 内联检查: 每次回复末尾
- L2 心跳: 每 7 分钟
- L3 深度检查: 每 60 分钟
- L6 外部看门狗: 每 5 分钟 (独立进程)

## 目标历史

（暂无）
