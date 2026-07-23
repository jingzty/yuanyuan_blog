"""
生成测试数据：分类 + 文章 + 轮播图
运行：python seed_data.py
"""

import sys
import os
from datetime import datetime, timedelta

# 添加 backend 目录到 path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, User, Category, Article, Banner


# ============ 图片资源 ============
IMG_FOREST = 'https://jingzt-image.oss-cn-shanghai.aliyuncs.com/%E6%A3%AE%E6%9E%97%20%E7%BB%BF%E8%8D%89%E5%9C%B0%20%E6%A4%85%E5%AD%90%20%E6%B2%B3%E6%B0%B4%20%E9%A3%8E%E6%99%AF%E6%A1%8C%E9%9D%A2%E5%A3%81%E7%BA%B8_%E5%BD%BC%E5%B2%B8%E5%A3%81%E7%BA%B8.jpg'
IMG_AUTUMN = 'https://jingzt-image.oss-cn-shanghai.aliyuncs.com/%E7%A7%8B%E5%A4%A9%E9%A3%8E%E6%99%AF%2C%E6%A0%91%E6%9C%A8%2C%E5%B0%8F%E8%B7%AF%2C%E9%97%B2%E9%80%B8%E9%9D%99%E8%B0%A7%2C%E9%A3%8E%E6%99%AF%E6%A1%8C%E9%9D%A2%E5%A3%81%E7%BA%B8_%E5%BD%BC%E5%B2%B8%E5%A3%81%E7%BA%B8.jpg'
IMG_A453 = 'https://jingzt-image.oss-cn-shanghai.aliyuncs.com/a453f467be07a347a1f3421a86ca8b26.jpg'
IMG_SKY = 'https://jingzt-image.oss-cn-shanghai.aliyuncs.com/%E7%94%9F%E6%88%90%E5%9B%BE%E7%89%87%EF%BC%9A%E5%A4%A9%E7%A9%BA%E4%B8%8B%E7%9A%84%E7%94%B7%E5%AD%A9%E5%A5%B3%E5%AD%A9%20(4).webp'

COVERS = [IMG_FOREST, IMG_AUTUMN, IMG_A453]


# ============ 分类 ============
CATEGORIES = [
    {'name': '前端开发', 'icon': 'code-2'},
    {'name': '后端架构', 'icon': 'server'},
    {'name': '工具效率', 'icon': 'wrench'},
    {'name': 'AI 探索', 'icon': 'sparkles'},
    {'name': '生活随笔', 'icon': 'feather'},
]


# ============ 文章 ============
ARTICLES = [
    {
        'title': '从 100ms 到 30ms：前端首屏性能优化的实战路径',
        'summary': '基于真实项目数据，拆解从资源加载、代码分割、渲染管线到运行时优化的全链路改造过程。',
        'cover': IMG_FOREST,
        'categories': ['前端开发'],
        'views': 1284,
        'content': '''# 从 100ms 到 30ms：前端首屏性能优化的实战路径

> 性能优化不是一次性的工程，而是贯穿研发全流程的持续实践。

## 一、问题背景

在最近一次大型电商项目重构中，我们面临着这样的指标：

- **首屏 FCP**：1.8s（目标 < 1s）
- **LCP**：3.2s（目标 < 2s）
- **TBT**：580ms（目标 < 200ms）

这些数字背后是真实的用户流失：每增加 100ms 延迟，转化率下降约 1%。

## 二、资源加载优化

### 1. 关键资源预加载

```html
<link rel="preload" href="/fonts/main.woff2" as="font" type="font/woff2" crossorigin>
<link rel="modulepreload" href="/assets/app.js">
```

### 2. 图片优化

使用 `webp` 格式 + 响应式 `srcset`：

```html
<img src="hero.webp"
     srcset="hero-480.webp 480w, hero-800.webp 800w, hero-1200.webp 1200w"
     sizes="(max-width: 600px) 480px, 800px" />
```

## 三、代码分割

```js
// 路由级分割
const Home = () => import('./views/Home.vue')

// 组件级分割
const Chart = defineAsyncComponent(() => import('./Chart.vue'))
```

## 四、渲染管线优化

### 1. 避免 Layout Thrashing

```js
// ❌ 错误：强制同步布局
for (let i = 0; i < els.length; i++) {
  els[i].style.left = els[i].offsetLeft + 10 + 'px'
}

// ✅ 正确：先读后写
const lefts = els.map(el => el.offsetLeft + 10)
els.forEach((el, i) => el.style.left = lefts[i] + 'px')
```

### 2. 使用 will-change

```css
.animated-element {
  will-change: transform, opacity;
}
```

## 五、运行时优化

### 1. 虚拟列表

对于 1000+ 条数据：

```js
import { useVirtualList } from '@vueuse/core'

const { list, containerProps, wrapperProps } = useVirtualList(
  hugeList,
  { itemHeight: 60 }
)
```

### 2. 防抖与节流

```js
// 搜索框防抖
const onSearch = useDebounceFn((q) => fetchResults(q), 300)

// 滚动节流
const onScroll = useThrottleFn(updatePosition, 100)
```

## 六、结果对比

| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| FCP  | 1.8s   | 0.6s   | 67%  |
| LCP  | 3.2s   | 1.4s   | 56%  |
| TBT  | 580ms  | 120ms  | 79%  |

## 七、持续监控

部署后不是终点。我们使用 Lighthouse CI 持续监控：

```yaml
name: Lighthouse CI
on: [push]
jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: treosh/lighthouse-ci-action@v9
        with:
          urls: |
            https://example.com
            https://example.com/about
```

## 总结

性能优化是一场马拉松。从资源加载到运行时，每一步的微小改进累积起来就是质的飞跃。希望本文对你有所帮助。

---

*本文首发于「远远的天空」，转载请注明出处。*
''',
    },
    {
        'title': '用 Rust 重写 Node.js 网关：性能与开发体验的权衡',
        'summary': '半年时间把核心网关从 Node.js 迁移到 Rust，记录下在编译时间、生态成熟度与运行性能之间的真实取舍。',
        'cover': IMG_AUTUMN,
        'categories': ['后端架构'],
        'views': 982,
        'content': '''# 用 Rust 重写 Node.js 网关：性能与开发体验的权衡

> 这不是一篇「Rust 优于 Node.js」的宣战书，而是一次真实迁移的复盘。

## 一、为什么是 Rust？

我们的 Node.js 网关在 QPS 8000 时开始出现：
- GC 暂停导致 P99 抖动到 200ms+
- 内存占用持续增长至 4GB
- Express 中间件链难以维护

Rust 的吸引力在于：
- **零成本抽象**：性能接近 C++
- **无 GC**：内存可预测
- **强类型系统**：编译期捕获错误

## 二、Tokio + Axum 技术栈

```toml
[dependencies]
tokio = { version = "1", features = ["full"] }
axum = "0.7"
tower = "0.4"
serde = { version = "1", features = ["derive"] }
```

### 一个简单的中间件

```rust
async fn auth_middleware(
    State(state): State<AppState>,
    mut req: Request,
    next: Next,
) -> Result<Response, StatusCode> {
    let token = req
        .headers()
        .get("authorization")
        .and_then(|v| v.to_str().ok())
        .ok_or(StatusCode::UNAUTHORIZED)?;

    let user = state.auth.verify(token).await
        .map_err(|_| StatusCode::UNAUTHORIZED)?;

    req.extensions_mut().insert(user);
    Ok(next.run(req).await)
}
```

## 三、性能对比

在同等硬件、同等业务逻辑下：

| 指标 | Node.js | Rust | 提升 |
|------|---------|------|------|
| QPS  | 8,000   | 32,000 | 4x |
| P99  | 220ms   | 45ms  | 5x |
| 内存 | 4GB     | 380MB | 10x |

## 四、迁移中的坑

### 1. 编译时间

首次编译耗时 6 分钟，CI 流水线压力倍增。解决方案：
- 启用 `sccache` 缓存
- 使用 `cargo nextest` 并行测试
- 增量构建 + Docker 层缓存

### 2. 异步生态

`tokio` 生态强大但学习曲线陡峭：
- `Arc<Mutex<T>>` vs `Arc<RwLock<T>>`
- `Pin<Box<dyn Future>>` 的生命周期
- `Send + Sync` bound 错误

### 3. JSON Schema

Node.js 用 Zod 即可，Rust 需要 `serde` + `validator`：

```rust
#[derive(Deserialize, Validate)]
struct CreateUser {
    #[validate(length(min = 3, max = 20))]
    username: String,
    #[validate(email)]
    email: String,
}
```

## 五、开发体验对比

### 优势
- **类型安全**：编译期捕获 80% 错误
- **重构信心**：编译器辅助重构
- **文档生成**：`cargo doc` 一键生成

### 劣势
- **学习曲线**：团队需要 2-3 个月适应
- **生态年轻**：某些库还处于 0.x 阶段
- **调试体验**：`gdb` 比 `chrome devtools` 难用

## 六、最终结论

| 维度 | Node.js | Rust |
|------|---------|------|
| 启动速度 | 快 | 慢 |
| 运行性能 | 中 | 极快 |
| 团队上手 | 易 | 难 |
| 长期维护 | 中 | 易 |

如果你的服务满足以下任一条件，可以考虑 Rust：
- QPS > 10,000
- P99 < 50ms
- 内存敏感场景

否则，Node.js 依然是高性价比的选择。

## 写在最后

迁移完成后，团队最大的收获不是性能数字，而是对系统边界的重新认知。Rust 让我们学会了用「拥有权」的视角思考数据流，这种思维模型反过来也让我们的 Node.js 代码变得更清晰。

**技术选型没有银弹，只有适合的权衡。**

---

*本文首发于「远远的天空」，转载请注明出处。*
''',
    },
    {
        'title': '我的 2026 年开发环境：从编辑器到终端的全套配置',
        'summary': '每年更新一次的开发环境清单，今年包括 Neovim 的 Lua 配置、Zellij 替代 tmux 以及一些效率工具的迭代。',
        'cover': IMG_A453,
        'categories': ['工具效率'],
        'views': 2156,
        'content': '''# 我的 2026 年开发环境：从编辑器到终端的全套配置

> 工欲善其事，必先利其器。这是我 2026 年的开发环境全清单。

## 一、硬件

- **主机**：MacBook Pro 16" M3 Max / 64GB RAM / 2TB SSD
- **显示器**：LG 32UN880 32" 4K + Dell U2723QE 27" 4K
- **键盘**：HHKB Professional Hybrid Type-S
- **鼠标**：Logitech MX Master 3S
- **音箱**：Audioengine A2+

## 二、终端

### Shell: Fish + Starship

```fish
# ~/.config/fish/config.fish
set -g fish_greeting ""

# 别名
alias g="git"
alias gs="git status"
alias ll="eza -la --git --icons"
alias cat="bat"
```

```toml
# ~/.config/starship.toml
add_newline = true
format = """$directory$git_branch$git_status$character"""

[character]
success_symbol = "[➜](bold green)"
error_symbol = "[➜](bold red)"
```

### Multiplexer: Zellij

替代 tmux，开箱即用：

```kdl
// ~/.config/zellij/config.kdl
default_layout "compact"
theme "catppuccin-mocha"
pane_frames false
```

## 三、编辑器

### 主力：Neovim

```lua
-- ~/.config/nvim/init.lua
require("core.options")
require("core.keymaps")
require("core.plugins")
require("core.lsp")
require("core.cmp")
require("core.telescope")
require("core.treesitter")
```

```lua
-- ~/.config/nvim/lua/core/options.lua
local options = {
  number = true,
  relativenumber = true,
  shiftwidth = 2,
  tabstop = 2,
  expandtab = true,
  wrap = false,
  termguicolors = true,
  scrolloff = 8,
  sidescrolloff = 8,
  cursorline = true,
}
for k, v in pairs(options) do
  vim.opt[k] = v
end
```

### LSP 配置

```lua
-- ~/.config/nvim/lua/core/lsp.lua
local lsp = require("lspconfig")

lsp.lua_ls.setup({})
lsp.ts_ls.setup({})
lsp.pyright.setup({})
lsp.rust_analyzer.setup({
  settings = {
    ["rust-analyzer"] = {
      cargo = { allFeatures = true },
      checkOnSave = { command = "clippy" },
    }
  }
})
```

### 辅助：VS Code

仅在 Pair Programming 或调试复杂 TypeScript 时使用。

## 四、Git 工作流

### 全局配置

```ini
# ~/.gitconfig
[user]
  name = Yuanyuan
  email = yuanyuan@example.com

[init]
  defaultBranch = main

[pull]
  rebase = true

[push]
  autoSetupRemote = true

[core]
  editor = nvim
  pager = delta

[interactive]
  diffFilter = delta --color-only

[delta]
  navigate = true
  side-by-side = true
```

### 提交规范

使用 Conventional Commits：

```
feat(auth): add JWT refresh token
fix(api): handle null user in /me
docs: update README
refactor: simplify response helper
```

## 五、效率工具

| 类别 | 工具 | 说明 |
|------|------|------|
| 启动器 | Raycast | 替代 Spotlight |
| 剪贴板 | Maccy | 开源轻量 |
| 窗口管理 | Aerospace | 替代 Yabai |
| 截图 | CleanShot X | 截图 + 录屏 |
| 密码 | 1Password | 跨平台 |
| 笔记 | Obsidian | Zettelkasten |

## 六、Docker

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:16
    ports: ["5432:5432"]
    environment:
      POSTGRES_PASSWORD: dev
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

volumes:
  pgdata:
```

## 七、总结

这套配置不是一蹴而就的，而是经过无数次迭代后沉淀下来的。每年我都会做一次复盘，淘汰不再使用的工具，引入新的尝试。

如果你也在搭建自己的开发环境，记住一句话：

> **最好的工具，是你用得最熟练的那一个。**

---

*本文首发于「远远的天空」，转载请注明出处。*
''',
    },
    {
        'title': '单体仓库 vs 多仓库：中型团队的工程化选择',
        'summary': '在 50 人规模的工程团队中，我们在一年内尝试了三种代码组织方式，最终的选择和背后的考量。',
        'cover': IMG_FOREST,
        'categories': ['后端架构'],
        'views': 743,
        'content': '''# 单体仓库 vs 多仓库：中型团队的工程化选择

> 代码组织方式从来不是技术问题，而是组织问题。

## 一、三种模式

### 1. Polyrepo（多仓库）

每个服务一个仓库：

```
├── auth-service/
├── payment-service/
├── user-service/
└── shared-utils/
```

**优点**：
- 边界清晰
- 团队独立
- 构建快

**缺点**：
- 代码复用难
- 跨服务改动繁琐
- 依赖版本碎片化

### 2. Monorepo（单体仓库）

所有代码在一个仓库：

```
├── packages/
│   ├── auth/
│   ├── payment/
│   ├── user/
│   └── shared/
└── apps/
    ├── web/
    └── admin/
```

**优点**：
- 代码共享容易
- 原子化提交
- 统一工具链

**缺点**：
- 仓库膨胀
- 权限管理粗粒度
- CI 复杂

### 3. Hybrid（混合）

核心系统 monorepo，边缘服务 polyrepo。

## 二、我们的实践

### 阶段 1：Polyrepo（2023 年）

5 个团队，每个团队 8-10 人，共 15 个服务。

**痛点**：
- 改一个接口要改 3 个仓库
- `shared-utils` 仓库成为瓶颈
- 依赖版本不一致导致 bug

### 阶段 2：Monorepo（2024 年）

迁移到 Turborepo + pnpm workspace。

**痛点**：
- 首次 clone 耗时 8 分钟
- CI 跑全量测试需要 40 分钟
- 新人 onboarding 困难

### 阶段 3：Hybrid（2025 年）

**最终架构**：
- 核心 monorepo：`apps/web`, `apps/admin`, `packages/ui`, `packages/utils`
- 边缘 polyrepo：每个微服务独立仓库

## 三、关键决策点

### 1. 团队规模

- **< 10 人**：Monorepo 简单直接
- **10-50 人**：Hybrid 平衡
- **> 50 人**：需要考虑 Bazel 等工具

### 2. 服务耦合度

高耦合 → Monorepo
低耦合 → Polyrepo

### 3. 工具链成熟度

| 工具 | 适合规模 | 语言 |
|------|---------|------|
| Turborepo | 中小型 | JS/TS |
| Nx | 中大型 | JS/TS |
| Bazel | 大型 | 多语言 |
| Pants | 中大型 | 多语言 |

## 四、Monorepo 最佳实践

### 1. 任务编排

```json
// turbo.json
{
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**"]
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": []
    }
  }
}
```

### 2. 变更检测

```bash
# 只测试受影响的包
turbo run test --filter=...[origin/main]
```

### 3. 远程缓存

```bash
turbo login
turbo link
# CI 配置 TURBO_TOKEN
```

## 五、Polyrepo 最佳实践

### 1. 版本管理

使用 Changesets：

```bash
npx changeset
npx changeset version
npx changeset publish
```

### 2. 依赖同步

```yaml
# .github/workflows/sync-deps.yml
name: Sync Dependencies
on:
  schedule:
    - cron: '0 0 * * 1'
jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: tibdex/github-app-token@v1
      - run: npx syncpack fix-mismatches
```

## 六、最终结论

经过一年的实践，我们得出以下公式：

```
最佳架构 = f(团队规模, 服务耦合度, 工具链成熟度)
```

**没有银弹**，只有权衡。希望我们的实践能给你一些参考。

---

*本文首发于「远远的天空」，转载请注明出处。*
''',
    },
    {
        'title': '在编辑器里集成 LLM：一个端侧推理实验',
        'summary': '尝试在本地编辑器中运行小型语言模型作为辅助，对比云端 API 在延迟、隐私和上下文质量上的差异。',
        'cover': IMG_AUTUMN,
        'categories': ['AI 探索'],
        'views': 1847,
        'content': '''# 在编辑器里集成 LLM：一个端侧推理实验

> 当 LLM 真的跑在你的笔记本里，体验会和云端 API 有何不同？

## 一、动机

云端 LLM API 有三个痛点：
1. **延迟**：网络往返 500ms+
2. **隐私**：代码上传到第三方
3. **成本**：按 token 计费，月费 $20+

如果能在本地运行一个 7B 级别模型，是否能解决这些问题？

## 二、技术选型

### 模型：Qwen2.5-Coder-7B

选择理由：
- 中文友好
- 代码能力强
- 7B 参数量可在 16GB Mac 上流畅运行

### 推理框架：llama.cpp

```bash
# 下载 GGUF 量化版本
huggingface-cli download Qwen/Qwen2.5-Coder-7B-Instruct-GGUF \\
  qwen2.5-coder-7b-instruct-q5_k_m.gguf

# 启动服务器
llama-server \\
  -m qwen2.5-coder-7b-instruct-q5_k_m.gguf \\
  --port 8080 \\
  -c 8192 \\
  -ngl 33
```

### 编辑器集成：Neovim + CodeCompanion

```lua
-- ~/.config/nvim/lua/plugins/codecompanion.lua
return {
  "olimorris/codecompanion.nvim",
  opts = {
    adapters = {
      llama = function()
        return require("codecompanion.adapters").extend("ollama", {
          schema = {
            model = { default = "qwen2.5-coder:7b" },
            num_ctx = { default = 8192 },
          },
        })
      end,
    },
    strategies = {
      chat = { adapter = "llama" },
      inline = { adapter = "llama" },
    },
  },
}
```

## 三、性能对比

### 1. 延迟

| 方式 | 首 token | 完整响应 |
|------|---------|---------|
| 云端 GPT-4 | 800ms | 3-5s |
| 云端 Claude | 600ms | 2-4s |
| 本地 Qwen 7B | 200ms | 1-2s |

本地首 token 延迟更低，因为没有网络往返。

### 2. 上下文质量

| 方式 | 上下文长度 | 代码理解 |
|------|----------|---------|
| 云端 | 128k+ | 极强 |
| 本地 | 8k | 中等 |

本地模型的上下文窗口是硬伤。8k tokens 大概只能容纳 2-3 个文件。

### 3. 隐私

| 方式 | 代码是否上传 |
|------|------------|
| 云端 | 是 |
| 本地 | 否 |

这是本地模型最大的优势。

### 4. 成本

| 方式 | 月费 |
|------|------|
| 云端 GPT-4 | $20 |
| 云端 Claude | $20 |
| 本地 Qwen 7B | $0（电费） |

## 四、体验细节

### 1. 离线工作

本地模型最大的优势是离线工作。在飞机上、咖啡馆里，没有网络也能继续 coding。

### 2. 代码补全

```lua
-- ~/.config/nvim/lua/plugins/copilot.lua
return {
  "zbirenbaum/copilot.lua",
  opts = {
    suggestion = {
      enabled = true,
      auto_trigger = true,
    },
  },
}
```

### 3. Chat 对话

```
User: 解释一下这段 Lua 代码

Assistant: 这段代码定义了一个 Neovim 插件，使用 CodeCompanion.nvim 集成本地 LLM...
```

## 五、踩过的坑

### 1. 内存占用

7B 模型量化后约 5GB，但推理时实际占用 8-10GB。16GB Mac 上其他应用会卡顿。

### 2. 上下文丢失

超过 8k 上下文后，模型开始「忘记」前面的内容。解决方案：
- 分段对话
- 使用 RAG 检索相关代码

### 3. 中文输出

Qwen2.5 中文输出质量不错，但有时会夹杂英文。Prompt 工程很重要。

## 六、最终方案

经过一个月的实验，我最终采用的方案是：

1. **日常补全**：GitHub Copilot（云端，质量高）
2. **Chat 对话**：本地 Qwen 7B（隐私敏感）
3. **复杂任务**：Claude（云端，能力强）

混合使用，各取所长。

## 七、未来展望

端侧 LLM 的未来值得期待：
- Apple Intelligence 集成系统级 LLM
- Qualcomm Snapdragon X Elite 的 NPU 算力
- MLX 框架在 Apple Silicon 上的优化

**未来已来，只是分布不均。**

---

*本文首发于「远远的天空」，转载请注明出处。*
''',
    },
    {
        'title': '一次线上 P0 事故复盘：从数据库死锁到分布式锁',
        'summary': '高峰期订单服务突然全部超时，根因是数据库死锁。从事故响应到根因分析再到长期改进的完整复盘。',
        'cover': IMG_A453,
        'categories': ['后端架构'],
        'views': 3201,
        'content': '''# 一次线上 P0 事故复盘：从数据库死锁到分布式锁

> 事故不可怕，可怕的是同样的错误犯第二次。

## 一、事故概要

| 项目 | 内容 |
|------|------|
| 事故等级 | P0 |
| 影响时长 | 42 分钟 |
| 影响范围 | 全站订单服务不可用 |
| 损失 | 约 1.2 万订单，GMV 约 380 万 |

## 二、事故时间线

### T+0 11:30:00

监控告警：订单服务 P99 突增至 5s+，错误率从 0.1% 升至 15%。

### T+1min 11:31:00

值班工程师小李收到电话告警，立即登入 Grafana 查看：

- QPS 正常，无明显流量突增
- 数据库 CPU 100%
- 大量 `Lock wait timeout exceeded` 错误

### T+3min 11:33:00

小李判断为数据库死锁，立即执行：
1. `SHOW PROCESSLIST` 查看活跃连接
2. 找到 3 条相互等待的 transaction
3. `KILL` 掉这 3 条 transaction

服务恢复。

### T+5min 11:35:00

服务再次出现相同问题。小李意识到不是简单的偶发死锁，开始升级响应：
1. 通知 DBA 介入
2. 通知架构组介入
3. 启动 P0 事故响应流程

### T+15min 11:45:00

DBA 通过 `information_schema.INNODB_TRX` 发现大量长事务，手动 kill 后服务恢复。但根因仍未定位。

### T+30min 12:00:00

架构组通过日志分析定位到一次 30 分钟前发布的代码变更：新增了「批量优惠券发放」功能，使用了不当的事务范围。

### T+42min 12:12:00

回滚代码，服务完全恢复。

## 三、根因分析

### 1. 直接原因

新功能的伪代码：

```python
def batch_issue_coupons(user_ids, coupon_id):
    with transaction():
        for user_id in user_ids:
            coupon = Coupon.lock(coupon_id)  # 行锁
            user = User.lock(user_id)        # 行锁
            IssueCoupon.create(user, coupon)
```

问题：
- 一个事务内对多行加锁
- 不同请求的加锁顺序不一致（coupon_id 顺序 vs user_id 顺序）
- 高并发下必然死锁

### 2. 深层原因

#### a. 代码审查流于形式

PR 评审时，3 位 reviewer 都关注了「业务逻辑是否正确」，没人关注「事务范围是否合理」「加锁顺序是否一致」。

#### b. 缺乏并发测试

测试环境 QPS 只有 10，根本无法触发死锁。生产环境 QPS 2000+，死锁概率指数级上升。

#### c. 监控告警滞后

死锁从发生到影响 P99，中间有 30 秒的窗口期。但我们的告警是 1 分钟一次，错过了最佳干预时机。

#### d. 应急预案不完善

小李的第一反应是 kill transaction，这是对的。但 kill 之后没有立即排查根因，导致死锁反复发生。

## 四、改进措施

### 1. 短期（1 周内）

- [x] 修复批量发放优惠券的事务范围
- [x] 把 `SELECT ... FOR UPDATE` 改为先查后更，缩小锁粒度
- [x] 增加死锁监控告警（10 秒级）
- [x] 编写《死锁排查 SOP》

### 2. 中期（1 个月内）

- [x] 引入分布式锁（Redisson）替代数据库行锁
- [x] 完善并发测试框架
- [x] 代码审查 checklist 增加「事务」「锁」「并发」检查项
- [x] 演练 P0 事故响应流程

### 3. 长期（3 个月内）

- [x] 全量代码扫描，识别类似事务范围问题
- [x] 引入 OpenTelemetry 全链路追踪
- [x] 建设 Chaos Engineering 平台
- [x] 推广「防御性编程」文化

## 五、分布式锁方案

```python
from redis import Redis
from redis.lock import Lock

redis = Redis.from_url('redis://localhost:6379')

def batch_issue_coupons(user_ids, coupon_id):
    lock_key = f"coupon:{coupon_id}"
    lock = Lock(redis, lock_key, timeout=10, blocking_timeout=5)

    if not lock.acquire():
        raise BusinessException('系统繁忙，请稍后再试')

    try:
        for user_id in user_ids:
            issue_coupon(user_id, coupon_id)
    finally:
        lock.release()
```

**关键设计点**：
1. 锁的粒度：按 coupon_id 加锁，而非全局锁
2. 锁的超时：10s 自动释放，防止死锁
3. 阻塞超时：5s 内获取不到锁则失败
4. 失败处理：返回友好错误，而非抛出异常

## 六、复盘感悟

### 1. 技术层面

- 数据库行锁是把双刃剑，用好了简单高效，用不好就是定时炸弹
- 分布式锁虽然引入了 Redis 依赖，但大大降低了死锁风险
- 监控告警的延迟，直接决定了事故的影响时长

### 2. 流程层面

- 代码审查不能只看业务逻辑，还要看并发、事务、异常处理
- 测试环境要尽量模拟生产环境的并发量
- 应急预案要定期演练，不能只停留在文档上

### 3. 文化层面

- 事故复盘要「对事不对人」，避免推卸责任
- 要鼓励「主动暴露问题」，而非「掩盖问题」
- 要把事故转化为组织学习的机会

## 七、结语

这次事故给我们上了深刻的一课。技术架构的演进，往往不是主动的选择，而是被动地被事故推着走。

但正如飞行员的座右铭：

> **一切事故都是礼物，只要你愿意从中学习。**

---

*本文首发于「远远的天空」，转载请注明出处。*
''',
    },
    {
        'title': '周末徒步记：从城市到山野的 48 小时',
        'summary': '繁忙的编码工作之外，也需要走进自然。这是一次从周六清晨到周日傍晚的山野徒步记录。',
        'cover': IMG_FOREST,
        'categories': ['生活随笔'],
        'views': 654,
        'content': '''# 周末徒步记：从城市到山野的 48 小时

> 代码之外，还有山野。

## 周六 05:30 — 出发

闹钟在 5 点响起。天还没亮，城市的灯光稀疏。背上 30L 的徒步包，里面装着：

- 单层冲锋衣 + 抓绒
- 2L 水 + 能量棒
- 急救包
- 充电宝 + 离线地图
- 一本薄薄的诗集

地铁第一班 5:30，我赶上了。

## 周六 07:30 — 山脚

抵达山脚的小镇。空气里有柴火和露水的味道。早餐是镇上小店的豆浆油条，老板娘说：

> 「你们这些城里来的娃娃，周末不在家歇着，跑山里来干啥？」

我笑笑，没回答。**因为山在那里。**

## 周六 08:00 — 开始攀登

山径蜿蜒向上，先是石阶，然后是土路，最后是乱石。海拔从 800 米到 1500 米，垂直爬升 700 米。

前两个小时，身体在抗拒。大腿酸，呼吸急，汗流浃背。

第三个小时，身体开始顺从。步伐变得有节奏，呼吸变得均匀，思绪变得清晰。

**这大概就是徒步的魔法——它让身体回到身体本身。**

## 周六 12:00 — 半山腰的午餐

在半山腰的一块大石头上坐下。午餐是面包 + 火腿 + 一杯速溶咖啡。

眼前是层叠的山峦，云在山间流动。风吹过松林，发出沙沙的声音。

我翻开诗集，读到里尔克的句子：

> 「如果日常的喧嚣使你心疲，那就让山间的风告诉你：你是自由的。」

## 周六 15:00 — 登顶

登顶的那一刻，没有想象中的激动。只是平静。

山顶的风很大，我裹紧冲锋衣。远处的城市在云层之下，看不清楚。

**突然意识到，那些让我焦虑的代码 bug、deadline、KPI，在山面前都不值一提。**

## 周六 18:00 — 下撤到营地

下撤比攀登更难。膝盖承受着巨大的压力，每一步都要小心。

抵达营地时，天色已暗。搭好帐篷，生起炉子，煮一锅热汤。

夜里，躺在帐篷里，听外面的风声和虫鸣。**久违的、没有屏幕的夜晚。**

## 周日 06:00 — 山间的清晨

清晨被鸟叫醒。拉开帐篷，山谷里雾气弥漫，阳光从山顶洒下，形成丁达尔效应。

煮一壶咖啡，坐在帐篷前发呆。**这是这 48 小时里，最奢侈的时刻。**

## 周日 10:00 — 下山

下山选择了另一条路线，经过一片原始森林。树木参天，阳光透过树叶斑驳地洒在地上。

路上遇到一位 70 岁的老大爷，独自一人徒步。他说：

> 「小伙子，我每周都来。山不嫌老，人也不该嫌老。」

## 周日 16:00 — 回到城市

地铁里依然是疲惫的上班族。但我感觉不一样了。

**山没有改变什么，但它让我有力量面对不变的生活。**

## 徒步装备清单

| 类别 | 装备 | 备注 |
|------|------|------|
| 服装 | 冲锋衣 + 抓绒 | 防风保暖 |
| 鞋子 | 中帮徒步鞋 | 防滑护踝 |
| 背包 | 30L 徒步包 | 带防雨罩 |
| 水具 | 2L 水袋 | 随时补水 |
| 食物 | 能量棒 + 面包 | 轻便高能 |
| 安全 | 急救包 + 头灯 | 应急必备 |
| 导航 | 离线地图 + 指南针 | 信号盲区 |

## 写在最后

作为程序员，我们习惯了虚拟世界的无限可能。但偶尔走进真实的山野，会让我们的脚重新踩在地上。

**山在那里，我也在那里。**

---

*本文首发于「远远的天空」，转载请注明出处。*
''',
    },
    {
        'title': 'Vue 3.5 响应式系统深度解析：从 ref 到 signal',
        'summary': 'Vue 3.5 对响应式系统做了重大重构，性能提升 10 倍。本文深入解析新系统的实现原理。',
        'cover': IMG_AUTUMN,
        'categories': ['前端开发'],
        'views': 1872,
        'content': '''# Vue 3.5 响应式系统深度解析：从 ref 到 signal

> Vue 3.5 对响应式系统做了重大重构，性能提升 10 倍。本文深入解析新系统的实现原理。

## 一、响应式系统的演进

### Vue 2：Object.defineProperty

```js
Object.defineProperty(obj, 'key', {
  get() { /* 收集依赖 */ },
  set() { /* 触发更新 */ }
})
```

**局限**：
- 无法监听属性新增/删除
- 无法监听数组索引修改
- 需要递归遍历所有属性

### Vue 3.0-3.4：Proxy

```js
new Proxy(obj, {
  get(target, key, receiver) {
    track(target, key)
    return Reflect.get(target, key, receiver)
  },
  set(target, key, value, receiver) {
    trigger(target, key)
    return Reflect.set(target, key, value, receiver)
  }
})
```

**改进**：
- 监听属性新增/删除
- 监听数组操作
- 惰性响应式（只有访问时才转换）

**遗留问题**：
- 依赖收集使用 Map + Set，内存占用高
- 大型应用中，响应式对象创建耗时显著

### Vue 3.5：重构响应式系统

**核心改进**：
1. **版本计数**：替代 Map<key, Set> 结构
2. **双向链表**：管理依赖关系
3. **惰性计算**：computed 延迟到访问时

## 二、版本计数（Version Counting）

### 旧系统的依赖结构

```
targetMap: Map<target, Map<key, Set<dep>>>
```

每个属性都维护一个 Set，存储所有依赖该属性的 effect。

**问题**：即使属性值没变，effect 也会被触发。

### 新系统的版本计数

```ts
interface Dep {
  version: number  // 版本号
  // ...
}

interface Subscriber {
  deps: Dep[]
  // ...
}
```

**工作流程**：

1. **首次访问**：记录 dep 的 version
2. **再次访问**：对比 version
   - version 没变 → 跳过
   - version 变了 → 执行 effect

```ts
function checkDirty(dep: Dep, subscriber: Subscriber): boolean {
  if (dep.version !== subscriber.trackedVersion[dep.id]) {
    return true  // dirty，需要重新计算
  }
  return false
}
```

**性能提升**：
- 不变的数据不再触发 effect
- 大型 list 渲染性能提升 5-10 倍

## 三、双向链表管理依赖

### 旧系统的问题

每个 dep 维护一个 Set<Subscriber>，每个 Subscriber 维护一个 Set<Dep>。

**问题**：
- 内存占用高
- 删除依赖时需要遍历

### 新系统的双向链表

```ts
interface Link {
  dep: Dep
  sub: Subscriber
  prevDep: Link | undefined
  nextDep: Link | undefined
  prevSub: Link | undefined
  nextSub: Link | undefined
}
```

**优势**：
- 内存占用降低 50%
- 依赖删除 O(1)

## 四、新 computed 实现

### 旧 computed

```ts
class ComputedRefImpl {
  _value: any
  _dirty: boolean = true

  get value() {
    if (this._dirty) {
      this._value = this._fn()
      this._dirty = false
    }
    return this._value
  }
}
```

**问题**：每次访问都要检查 dirty，即使依赖没变。

### 新 computed

```ts
class ComputedRefImpl {
  _value: any
  _version: number = 0

  get value() {
    // 只有依赖的 dep.version 变了才会重新计算
    if (this.dep.version !== this._version) {
      this._value = this._fn()
      this._version = this.dep.version
    }
    return this._value
  }
}
```

**性能提升**：computed 在大型应用中性能提升 3-5 倍。

## 五、signal 与 ref 的未来

### Solid 的 signal

```ts
const [count, setCount] = createSignal(0)

// 精确依赖追踪
createEffect(() => {
  console.log(count())  // 只依赖 count
})
```

### Vue 3.5 的 ref

```ts
const count = ref(0)

// 同样精确
watchEffect(() => {
  console.log(count.value)
})
```

### 共同趋势

1. **细粒度更新**：不再依赖虚拟 DOM diff
2. **惰性计算**：只有访问时才计算
3. **版本追踪**：避免不必要的重新计算

## 六、性能对比

在 10,000 个响应式对象的场景下：

| 操作 | Vue 3.4 | Vue 3.5 | 提升 |
|------|---------|---------|------|
| 创建 | 120ms | 35ms | 3.4x |
| 读取 | 45ms | 12ms | 3.8x |
| 修改 | 80ms | 20ms | 4.0x |
| 内存 | 18MB | 9MB | 2.0x |

## 七、最佳实践

### 1. 大型列表使用 shallowRef

```ts
const list = shallowRef<Item[]>([])

// 修改时重新赋值
list.value = [...list.value, newItem]
```

### 2. 避免在模板中解构 props

```vue
<!-- ❌ 失去响应式 -->
<script setup>
const { count } = defineProps<{ count: number }>()
</script>

<!-- ✅ 保持响应式 -->
<script setup>
const props = defineProps<{ count: number }>()
</script>
```

### 3. 使用 computed 缓存计算结果

```ts
const filtered = computed(() =>
  list.value.filter(item => item.active)
)
```

### 4. 大对象使用 markRaw

```ts
const map = markRaw(new HeavyMapClass())
```

## 八、调试技巧

### 1. 查看响应式依赖

```ts
import { getDep } from '@vue/reactivity'

const dep = getDep(obj, 'key')
console.log(dep.subs)  // 查看所有订阅者
```

### 2. 追踪 effect 触发

```ts
import { effectScope } from 'vue'

const scope = effectScope()
scope.run(() => {
  watchEffect(() => {
    console.log('triggered')
  })
})
scope.stop()  // 清理所有 effect
```

## 九、总结

Vue 3.5 的响应式系统是一次重要的架构升级。从 Map/Set 到双向链表，从 dirty flag 到 version counting，每一处改进都体现了 Vue 团队对性能和开发体验的极致追求。

**响应式系统的本质，是数据与视图的契约。** Vue 3.5 让这份契约更高效、更可靠。

---

*本文首发于「远远的天空」，转载请注明出处。*
''',
    },
]


# ============ 轮播图 ============
BANNERS = [
    {
        'title': '远远的天空',
        'subtitle': '探索技术与生活的无限可能',
        'image_url': IMG_SKY,
        'link_url': '/',
        'sort_order': 1,
        'status': 'enabled',
    },
    {
        'title': '记录技术与生活的远方',
        'subtitle': '每一行代码都是一次冒险',
        'image_url': IMG_FOREST,
        'link_url': '/',
        'sort_order': 2,
        'status': 'enabled',
    },
    {
        'title': '在代码里寻找秩序',
        'subtitle': '从混乱到优雅的编程之旅',
        'image_url': IMG_AUTUMN,
        'link_url': '/',
        'sort_order': 3,
        'status': 'enabled',
    },
    {
        'title': '也记录风吹过的日子',
        'subtitle': '生活不止眼前的屏幕',
        'image_url': IMG_A453,
        'link_url': '/',
        'sort_order': 4,
        'status': 'enabled',
    },
    {
        'title': '思考与远方',
        'subtitle': '保持好奇，持续成长',
        'image_url': IMG_FOREST,
        'link_url': '/',
        'sort_order': 5,
        'status': 'enabled',
    },
]


def seed():
    """生成测试数据"""
    app = create_app('default')

    with app.app_context():
        # ============ 清空已有数据（保留 admin 用户）============
        print('=== 清理旧数据 ===')
        # 先清理中间表（SQLite 不会自动级联）
        db.session.execute(db.text('DELETE FROM article_category'))
        # 删除所有文章
        Article.query.delete()
        # 删除所有轮播图
        Banner.query.delete()
        # 删除所有分类（稍后重新创建）
        Category.query.delete()
        db.session.commit()
        print('旧数据已清理')

        # ============ 创建分类 ============
        print('\n=== 创建分类 ===')
        cat_map = {}
        for c in CATEGORIES:
            cat = Category(name=c['name'])
            db.session.add(cat)
            db.session.commit()
            cat_map[c['name']] = cat
            print(f'  分类: {c["name"]} (id={cat.id})')

        # ============ 创建文章 ============
        print('\n=== 创建文章 ===')
        now = datetime.utcnow()
        for i, a in enumerate(ARTICLES):
            article = Article(
                title=a['title'],
                summary=a['summary'],
                content=a['content'],
                cover_url=a['cover'],
                view_count=a['views'],
                status='published',
                published_at=now - timedelta(days=i * 3, hours=i),
                created_at=now - timedelta(days=i * 3, hours=i),
                updated_at=now - timedelta(days=i * 3, hours=i),
            )
            db.session.add(article)
            db.session.commit()

            # 关联分类
            for cat_name in a['categories']:
                cat = cat_map.get(cat_name)
                if cat:
                    article.categories.append(cat)

            db.session.commit()
            print(f'  文章: {a["title"][:30]}... (id={article.id}, views={a["views"]})')

        # ============ 创建轮播图 ============
        print('\n=== 创建轮播图 ===')
        for b in BANNERS:
            banner = Banner(
                title=b['title'],
                subtitle=b.get('subtitle'),
                image_url=b['image_url'],
                link_url=b['link_url'],
                sort_order=b['sort_order'],
                status=b['status'],
            )
            db.session.add(banner)
            db.session.commit()
            print(f'  轮播图: {b["title"]} (id={banner.id}, sort={b["sort_order"]})')

        # ============ 统计 ============
        print('\n=== 数据统计 ===')
        print(f'  分类总数: {Category.query.count()}')
        print(f'  文章总数: {Article.query.count()}')
        print(f'  轮播图总数: {Banner.query.count()}')
        print(f'  用户总数: {User.query.count()}')

        print('\n✅ 测试数据生成完成！')
        print(f'   默认管理员: admin / admin123')
        print(f'   前端地址: http://localhost:5173')
        print(f'   后端地址: http://localhost:5000')


if __name__ == '__main__':
    seed()
