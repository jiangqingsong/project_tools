---
name: git-only-on-explicit-command
description: 用户只在明确说"提交""commit""推送""你懂的"时才操作 git
metadata:
  type: feedback
---

用户只在明确说出"提交""commit""推送"或"你懂的"时才进行 git 操作。不要主动 commit 或 push，即使刚完成了代码改动。

**Why:** 用户有自己的提交节奏和技能使用习惯（如"你懂的"），刚才我推送计划文档更新时超前完成了他的意图。

**How to apply:** 做完代码改动后只告知用户改了什么，等他发话再操作 git。
