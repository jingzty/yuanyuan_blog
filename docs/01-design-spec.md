# 远远的天空 — 设计规范文档

> 来源：`muban.zip` 内 4 个设计稿页面（首页、登录、文章管理、轮播图管理）
> 适配技术栈：Vue 3 + Vite + Tailwind CSS v4 + Lucide Icons（前台）+ Element Plus（后台）

---

## 1. 色彩系统

### 1.1 品牌主色
| 变量 | 值 | 用途 |
|---|---|---|
| `--color-primary` | `#0065fd` | 主按钮、链接、激活态 |
| `--color-primary-foreground` | `#ffffff` | 主色背景上的文字 |
| `--color-primary-soft` | `#e5e9ff` | 主色淡，用于 hover/装饰 |
| `--color-primary-deep` | `#00266b` | 主色按下/hover 加深 |

### 1.2 表面色
| 变量 | 值 | 用途 |
|---|---|---|
| `--background` | `#ffffff` | 页面背景 |
| `--foreground` | `#0e1115` | 主文字 |
| `--card` | `#ffffff` | 卡片背景 |
| `--card-foreground` | `#0e1115` | 卡片内文字 |
| `--popover` | `#f9f9fa` | 浮层背景 |
| `--popover-foreground` | `#0e1115` | 浮层文字 |

### 1.3 语义色
| 变量 | 值 | 用途 |
|---|---|---|
| `--secondary` | `#eff1f4` | 次要背景 |
| `--secondary-foreground` | `#333942` | 次要文字 |
| `--muted` | `#eff1f4` | 静默背景 |
| `--muted-foreground` | `#7f8d9f` | 次级文字、占位符 |
| `--accent` | `#e5e9ff` | 强调背景（标签、徽章） |
| `--accent-foreground` | `#00266b` | 强调背景上的文字 |
| `--destructive` | `#ef4444` | 危险/删除 |
| `--destructive-foreground` | `#ffffff` | 危险按钮文字 |
| `--border` | `#e7eaef` | 边框 |
| `--input` | `#e7eaef` | 输入框边框 |
| `--ring` | `#557fff` | focus ring |

### 1.4 图表色（轮播卡片左边条等）
`--chart-1: #557fff` · `--chart-2: #0065fd` · `--chart-3: #0057da` · `--chart-4: #0043ad` · `--chart-5: #002e7d`

---

## 2. 字体系统

### 2.1 字体族
- **sans（默认）**：`"PingFang SC", "Microsoft YaHei", "Stack Sans Text", ui-sans-serif, sans-serif, system-ui`
- **serif**：`"Source Serif 4", "Songti SC", serif`
- **mono**：`"JetBrains Mono", ui-monospace, monospace`

### 2.2 字号层级
| 用途 | 类 | 字号 |
|---|---|---|
| Hero 大标题 | `text-4xl md:text-5xl lg:text-6xl font-semibold` | 36-60px |
| 页面 H1 | `text-2xl font-semibold tracking-tight` | 24px |
| 卡片 H3 | `text-lg font-semibold` | 18px |
| 正文 | `text-sm` / `text-base` | 14-16px |
| 辅助/Tag | `text-xs` | 12px |
| 统计大数字 | `text-3xl font-semibold tabular-nums` | 30px |

### 2.3 行高
- 默认 `leading-relaxed`（1.625）
- 标题 `tracking-tight`（-0.025em）

---

## 3. 间距与栅格

### 3.1 容器
- 前台容器宽度：`max-w-[1200px] mx-auto px-6`
- 后台容器宽度：`max-w-[1440px] mx-auto`

### 3.2 栅格
- 首页主区域：`grid grid-cols-1 lg:grid-cols-12 gap-8`
  - 文章列表：`lg:col-span-8`
  - 侧边栏：`lg:col-span-4`
- 后台统计卡：`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4`

### 3.3 常用间距
- 卡片内边距：`p-4` / `p-5`
- 区块间距：`space-y-5` / `space-y-6`
- 按钮高度：`h-9`（小）/ `h-10`（中）/ `h-11`（大）/ `h-12`（登录）
- 输入框：`h-10` / `h-12`

---

## 4. 圆角与阴影

### 4.1 圆角
| 变量 | 值 | 用途 |
|---|---|---|
| `--radius` / `--radius-lg` | `1.2rem` (19.2px) | 卡片、登录卡 |
| `--radius-md` | `0.8rem` (12.8px) | 按钮、输入框、导航项 |
| `--radius-sm` | `0.4rem` (6.4px) | tag、小元件 |
| `--radius-full` | `9999px` | 头像、圆点 |

### 4.2 阴影
| 变量 | 值 |
|---|---|
| `--shadow-sm` | `0 1px 0px 0px rgb(14 17 21 / 0), 0 1px 2px -1px rgb(14 17 21 / 0)` |
| `--shadow-md` | `0 1px 0px 0px rgb(14 17 21 / 0), 0 2px 4px -1px rgb(14 17 21 / 0)` |
| `--shadow-lg` | `0 4px 12px -2px rgb(14 17 21 / 0.06), 0 2px 6px -2px rgb(14 17 21 / 0.04)` |

整体风格：**柔和、低对比**，避免硬阴影。

---

## 5. 响应式断点

设计稿使用 Tailwind 默认断点：
- `sm`：640px
- `md`：768px（导航菜单显隐切换点）
- `lg`：1024px（侧边栏显隐、grid 切换点）
- `xl`：1280px

### 5.1 关键响应式行为
- 顶部导航：`hidden md:flex`（< 768px 隐藏菜单）
- 首页栅格：`grid-cols-1 lg:grid-cols-12`（< 1024px 单列）
- Hero 高度：`min-h-[560px] md:min-h-[640px]`
- 文章卡封面：`w-full sm:w-[200px]`（< 640px 全宽）
- 统计卡片：`grid-cols-1 sm:grid-cols-2 lg:grid-cols-4`

---

## 6. 交互与过渡

### 6.1 通用 transition
- `transition-colors`：用于 hover 颜色切换
- `transition-all duration-150/200`：输入框聚焦
- `transition-transform`：图标缩放

### 6.2 hover 效果
- 文章卡片：`hover:translate-y-[-3px] + hover:shadow` + `hover:border-primary`
- 按钮：`hover:bg-primary-deep`
- 导航项：`hover:bg-secondary`
- 侧边栏卡片：`hover:translate-y-[-2px] + hover:shadow`

### 6.3 轮播动画（首页 Hero）
- 切换间隔：`5000ms`
- 进入动画：`opacity 700ms ease, transform 700ms ease`
- 文案分层进入：title 80ms / subtitle 160ms / actions 240ms
- 圆点：未激活 `width: 0.5rem`，激活 `width: 1.75rem`
- 支持 `prefers-reduced-motion`

### 6.4 Scroll Reveal
- 文章卡：`translateY(28px) → 0`，`opacity 0 → 1`，`0.6s cubic-bezier(0.22, 1, 0.36, 1)`
- 侧边栏：`translateX(24px) → 0`
- 触发：`IntersectionObserver`，`threshold: 0.08`

### 6.5 登录页加载动画
- Logo：`fadeInDown 0.6s ease-out 0.1s both`
- 卡片：`fadeInUp 0.6s ease-out 0.3s both`
- 页脚：`fadeIn 0.6s ease-out 0.5s both`

---

## 7. 组件清单

### 7.1 前台组件
| 组件 | 说明 |
|---|---|
| `TopNav` | 顶部导航：Logo + 菜单 + 搜索 + 管理后台按钮 |
| `HeroCarousel` | 首页大轮播：3 张幻灯片、左右切换、圆点 |
| `ArticleCard` | 文章卡片：封面 + 标签 + 日期 + 标题 + 摘要 + 阅读量 + 标签 |
| `Sidebar` | 侧边栏容器 |
| `SidebarSearch` | 搜索卡片 |
| `SidebarTags` | 热门标签云 |
| `SidebarCategories` | 分类列表 |
| `SidebarAbout` | 关于博主卡 |
| `Footer` | 页脚版权 |

### 7.2 后台组件
| 组件 | 说明 |
|---|---|
| `AdminHeader` | 顶部：Logo + 返回前台 + 头像 |
| `AdminSidebar` | 左侧导航：内容管理 / 系统设置 / 个人中心 |
| `StatCard` | 统计卡片：左边色条 + 大数字 + 标签 |
| `FilterBar` | 筛选 + 搜索 + 批量操作栏 |
| `DataTable` | 通用表格 |
| `Pagination` | 分页 |

### 7.3 登录页
| 组件 | 说明 |
|---|---|
| `BrandLogo` | 品牌圆形 logo |
| `LoginInput` | 带左侧图标的输入框 |
| `CaptchaBox` | 验证码图片容器 |
| `LoginButton` | 全宽登录按钮 |

---

## 8. 关键页面结构

### 8.1 首页
```
<main>
  <nav> 顶部导航 </nav>
  <section> Hero 轮播 </section>
  <section>
    <div grid-cols-12>
      <div col-span-8> 文章列表（5篇） </div>
      <aside col-span-4>
        搜索 / 热门标签 / 分类 / 关于
      </aside>
    </div>
  </section>
  <footer> 页脚 </footer>
</main>
```

### 8.2 登录页
```
背景：多层渐变 + 模糊光晕 + SVG 云朵
<main min-h-screen flex-col>
  <返回首页链接>
  <品牌 Logo>
  <LoginCard>
    用户名 / 密码 / 验证码 / 登录按钮
  </LoginCard>
</main>
```

### 8.3 文章管理 / 轮播图管理（共用后台布局）
```
<header sticky> 顶部 </header>
<div flex>
  <aside w-60> 左侧导航 </aside>
  <section flex-1>
    <页面头部>
    <统计卡片行 grid-cols-4>
    <筛选 + 搜索 + 批量操作>
    <表格>
    <分页>
  </section>
</div>
```

---

## 9. 图标系统

- **库**：Lucide Icons（`lucide@1.8.0`）
- **常用图标**：
  - `cloud-sun` — 品牌 logo
  - `search` / `arrow-right` — 搜索
  - `eye` / `tag` — 文章元信息
  - `book-open` — CTA
  - `chevron-left/right` — 轮播控制
  - `user` / `lock` / `shield-check` — 登录
  - `layout-dashboard` / `file-text` / `images` / `tags` — 后台导航
  - `trash-2` / `plus` / `pencil` — 操作

---

## 10. 注意事项

1. **设计稿用 Tailwind Browser 版**，正式项目用 Vite + Tailwind v4 PostCSS 插件
2. **Lucide 在 Vue 中** 使用 `lucide-vue-next`
3. **Element Plus** 仅用于后台，主题需覆盖为主色 `#0065fd`
4. **登录页背景** 使用多层渐变 + 模糊光晕，必须保留
5. **首页轮播** 自动播放 + 手动切换 + 圆点 + 左右按钮，必须保留
6. **所有 hover/transition** 必须还原
