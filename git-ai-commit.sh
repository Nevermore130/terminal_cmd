#!/bin/bash
# git-ai-commit: AI-powered commit message generator
# 使用方法: git ai-commit 或直接运行此脚本
#
# 安装为全局命令:
#   1. chmod +x git-ai-commit.sh
#   2. sudo ln -s $(pwd)/git-ai-commit.sh /usr/local/bin/git-ai-commit
#   3. git config --global alias.ai '!git-ai-commit'
#
# 然后可以使用: git ai

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查是否在 git 仓库中
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo -e "${RED}Error: Not a git repository${NC}"
    exit 1
fi

# 检查是否有 staged changes
if git diff --cached --quiet; then
    echo -e "${YELLOW}No staged changes. Stage files first with 'git add'${NC}"
    exit 1
fi

# 获取 diff
DIFF=$(git diff --cached --no-color)
DIFF_LIMITED=$(echo "$DIFF" | head -c 4000)
STATS=$(git diff --cached --stat)

echo -e "${BLUE}📝 Analyzing staged changes...${NC}"
echo "$STATS"
echo ""

# 检查 API Key
if [ -z "$ANTHROPIC_API_KEY" ] && [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}Error: No API key found${NC}"
    echo "Please set ANTHROPIC_API_KEY or OPENAI_API_KEY environment variable"
    echo ""
    echo "Example:"
    echo "  export ANTHROPIC_API_KEY='your-key-here'"
    exit 1
fi

generate_with_anthropic() {
    local prompt="You are a git commit message expert. Based on the following git diff, generate a clear and concise commit message.

Rules:
1. Use conventional commits format: type(scope): description
2. Types: feat, fix, docs, style, refactor, perf, test, chore
3. Keep the first line under 72 characters
4. Be specific but concise
5. Only output the commit message, no explanation

Git diff:
$DIFF_LIMITED"

    local escaped_prompt=$(echo "$prompt" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')

    local response=$(curl -s https://api.anthropic.com/v1/messages \
        -H "Content-Type: application/json" \
        -H "x-api-key: $ANTHROPIC_API_KEY" \
        -H "anthropic-version: 2023-06-01" \
        -d "{
            \"model\": \"claude-3-5-haiku-20241022\",
            \"max_tokens\": 256,
            \"messages\": [{\"role\": \"user\", \"content\": $escaped_prompt}]
        }" 2>/dev/null)

    echo "$response" | python3 -c "import sys,json; data=json.load(sys.stdin); print(data.get('content',[{}])[0].get('text',''))" 2>/dev/null
}

generate_with_openai() {
    local prompt="Generate a git commit message for this diff. Use conventional commits format (type: description). Only output the message.\n\nDiff:\n$DIFF_LIMITED"

    local escaped_prompt=$(echo "$prompt" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')

    local response=$(curl -s https://api.openai.com/v1/chat/completions \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $OPENAI_API_KEY" \
        -d "{
            \"model\": \"gpt-4o-mini\",
            \"max_tokens\": 256,
            \"messages\": [{\"role\": \"user\", \"content\": $escaped_prompt}]
        }" 2>/dev/null)

    echo "$response" | python3 -c "import sys,json; data=json.load(sys.stdin); print(data.get('choices',[{}])[0].get('message',{}).get('content',''))" 2>/dev/null
}

# 生成 commit message
echo -e "${BLUE}🤖 Generating commit message with AI...${NC}"

if [ -n "$ANTHROPIC_API_KEY" ]; then
    MESSAGE=$(generate_with_anthropic)
elif [ -n "$OPENAI_API_KEY" ]; then
    MESSAGE=$(generate_with_openai)
fi

if [ -z "$MESSAGE" ]; then
    echo -e "${RED}Failed to generate commit message${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}Suggested commit message:${NC}"
echo "─────────────────────────────────────"
echo -e "${YELLOW}$MESSAGE${NC}"
echo "─────────────────────────────────────"
echo ""

# 询问用户
echo -e "Options:"
echo -e "  ${GREEN}[y]${NC} Accept and commit"
echo -e "  ${BLUE}[e]${NC} Edit message before commit"
echo -e "  ${YELLOW}[r]${NC} Regenerate"
echo -e "  ${RED}[n]${NC} Cancel"
echo ""

while true; do
    read -p "Your choice [y/e/r/n]: " choice
    case $choice in
        [Yy]* )
            git commit -m "$MESSAGE"
            echo -e "${GREEN}✅ Committed successfully!${NC}"
            break
            ;;
        [Ee]* )
            # 使用临时文件让用户编辑
            TMPFILE=$(mktemp)
            echo "$MESSAGE" > "$TMPFILE"
            ${EDITOR:-vim} "$TMPFILE"
            EDITED_MESSAGE=$(cat "$TMPFILE")
            rm "$TMPFILE"
            if [ -n "$EDITED_MESSAGE" ]; then
                git commit -m "$EDITED_MESSAGE"
                echo -e "${GREEN}✅ Committed successfully!${NC}"
            else
                echo -e "${RED}Empty message, commit cancelled${NC}"
            fi
            break
            ;;
        [Rr]* )
            echo -e "${BLUE}🔄 Regenerating...${NC}"
            if [ -n "$ANTHROPIC_API_KEY" ]; then
                MESSAGE=$(generate_with_anthropic)
            elif [ -n "$OPENAI_API_KEY" ]; then
                MESSAGE=$(generate_with_openai)
            fi
            echo ""
            echo -e "${GREEN}New suggestion:${NC}"
            echo "─────────────────────────────────────"
            echo -e "${YELLOW}$MESSAGE${NC}"
            echo "─────────────────────────────────────"
            echo ""
            ;;
        [Nn]* )
            echo -e "${YELLOW}Commit cancelled${NC}"
            exit 0
            ;;
        * )
            echo "Please answer y, e, r, or n"
            ;;
    esac
done
