# Git Hooks

本目录包含项目共享的 Git hooks。

## 安装方法

### 方法 1: 配置 Git 使用此目录（推荐）

```bash
# 仅对当前项目生效
git config core.hooksPath hooks

# 或全局生效（所有项目）
git config --global core.hooksPath hooks
```

### 方法 2: 创建符号链接

```bash
ln -sf ../../hooks/prepare-commit-msg .git/hooks/prepare-commit-msg
```

## 包含的 Hooks

### prepare-commit-msg

AI 自动生成 commit message，支持三种 API：

| 优先级 | API | 环境变量 | 模型 |
|--------|-----|----------|------|
| 1 | Gemini | `GEMINI_API_KEY` | gemini-2.0-flash |
| 2 | Anthropic | `ANTHROPIC_API_KEY` | claude-3-5-haiku |
| 3 | OpenAI | `OPENAI_API_KEY` | gpt-4o-mini |

**配置示例** (添加到 `~/.zshrc` 或 `~/.bashrc`):

```bash
export GEMINI_API_KEY='your-key-here'
```

**跳过 AI 生成**:

```bash
git commit -m "manual message"  # 直接指定 message
GIT_AI_SKIP=1 git commit        # 环境变量跳过
```
