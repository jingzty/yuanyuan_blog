<template>
  <div>
    <!-- 页面头部 -->
    <div class="flex items-start justify-between gap-4 mb-6">
      <div class="min-w-0">
        <h1 class="text-2xl font-semibold tracking-tight text-[var(--foreground)]">
          {{ isEdit ? '编辑文章' : '撰写文章' }}
        </h1>
        <p class="mt-1.5 text-sm text-[var(--muted-foreground)]">
          {{ isEdit ? `正在编辑：${form.title || ''}` : '填写以下信息以创建新文章' }}
        </p>
      </div>
      <div class="flex items-center gap-2">
        <el-button @click="onCancel">取消</el-button>
        <el-button type="primary" :loading="saving" @click="onSave">
          {{ isEdit ? '保存修改' : '保存文章' }}
        </el-button>
      </div>
    </div>

    <!-- 文章信息卡片 -->
    <div class="info-card">
      <div class="metadata-toggle" :class="{ collapsed: !metadataOpen }" @click="metadataOpen = !metadataOpen">
        <span class="toggle-arrow">▼</span>
        <span>文章信息</span>
      </div>

      <transition name="metadata-slide">
        <div v-show="metadataOpen" class="metadata-body">
          <!-- 标题 + 状态 -->
          <div class="form-row">
            <div class="form-group">
              <label>文章标题</label>
              <el-input v-model="form.title" placeholder="输入文章标题..." maxlength="120" show-word-limit />
            </div>
            <div class="form-group">
              <label>状态</label>
              <el-radio-group v-model="form.status">
                <el-radio value="published">已发布</el-radio>
                <el-radio value="draft">草稿</el-radio>
              </el-radio-group>
            </div>
          </div>

          <!-- 分类 + 封面 URL -->
          <div class="form-row">
            <div class="form-group">
              <label>分类</label>
              <el-select
                v-model="form.category_ids"
                multiple
                filterable
                placeholder="请选择分类"
                style="width: 100%"
              >
                <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
              </el-select>
            </div>
            <div class="form-group">
              <label>封面 URL</label>
              <el-input v-model="form.cover_url" placeholder="https://…（OSS 地址）" />
            </div>
          </div>

          <!-- 封面预览 -->
          <div class="form-group" v-if="form.cover_url">
            <label>封面预览</label>
            <div class="cover-preview">
              <img :src="form.cover_url" alt="封面预览" />
            </div>
          </div>

          <!-- 摘要 -->
          <div class="form-group">
            <label>摘要</label>
            <el-input
              v-model="form.summary"
              type="textarea"
              :rows="3"
              placeholder="输入文章摘要..."
              maxlength="300"
              show-word-limit
            />
          </div>
        </div>
      </transition>
    </div>

    <!-- Markdown 编辑器卡片 -->
    <div class="editor-card">
      <div class="editor-container">
        <!-- 顶部：模式标签 -->
        <div class="editor-topbar">
          <div class="editor-mode-label">
            <span class="mode-badge" :class="`mode-badge--${editorMode}`">
              {{ editorMode === 'wysiwyg' ? '所见即所得' : '源码模式' }}
            </span>
            <span class="pane-hint">Ctrl+S 保存</span>
          </div>
        </div>

        <!-- 工具栏 -->
        <div class="editor-toolbar" @mousedown.prevent>
          <button type="button" @click="onToolbar('bold')" title="加粗 (Ctrl+B)"><strong>B</strong></button>
          <button type="button" @click="onToolbar('italic')" title="斜体 (Ctrl+I)"><em>I</em></button>
          <span class="toolbar-divider"></span>
          <button type="button" @click="onToolbar('heading')" title="标题">H</button>
          <button type="button" @click="onToolbar('link')" title="链接">🔗</button>
          <button type="button" @click="onToolbar('image')" title="图片">🖼</button>
          <span class="toolbar-divider"></span>
          <button type="button" @click="onToolbar('quote')" title="引用">❝</button>
          <button type="button" @click="onToolbar('code')" title="行内代码">&lt;/&gt;</button>
          <button type="button" @click="onToolbar('codeblock')" title="代码块">{ }</button>
          <span class="toolbar-divider"></span>
          <button type="button" @click="onToolbar('ul')" title="无序列表">•</button>
          <button type="button" @click="onToolbar('ol')" title="有序列表">1.</button>
          <button type="button" @click="onToolbar('hr')" title="分隔线">—</button>
          <span class="toolbar-divider"></span>
          <button type="button" class="mode-toggle" @click="toggleMode" :title="editorMode === 'wysiwyg' ? '切换到源码模式' : '切换到所见即所得'">
            {{ editorMode === 'wysiwyg' ? '源码模式' : '所见即所得' }}
          </button>
        </div>

        <!-- 源码模式 -->
        <div v-show="editorMode === 'source'" class="editor-source-pane">
          <div class="editor-wrap">
            <div class="editor-line-numbers" ref="lineNumbersRef">
              <span v-for="n in lineCount" :key="n">{{ n }}</span>
            </div>
            <textarea
              ref="textareaRef"
              v-model="form.content"
              class="editor-textarea"
              placeholder="在这里书写 Markdown..."
              @input="updateLineNumbers"
              @scroll="syncScroll"
              @keydown="handleKeydown"
            ></textarea>
          </div>
        </div>

        <!-- 所见即所得模式 -->
        <div v-show="editorMode === 'wysiwyg'" class="editor-wysiwyg-pane">
          <div
            ref="wysiwygRef"
            class="editor-wysiwyg"
            contenteditable="true"
            @blur="syncWysiwygToSource"
            @paste="onWysiwygPaste"
            @keydown="handleKeydown"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { get as getArticle, create as createArticle, update as updateArticle } from '@/api/article'
import { list as listCategories } from '@/api/category'

const route = useRoute()
const router = useRouter()

const id = computed(() => route.params.id)
const isEdit = computed(() => !!id.value)

const form = reactive({
  title: '',
  summary: '',
  content: '',
  cover_url: '',
  status: 'draft',
  category_ids: [],
})

const categories = ref([])
const saving = ref(false)
const metadataOpen = ref(true)

const textareaRef = ref(null)
const lineNumbersRef = ref(null)
const wysiwygRef = ref(null)
const editorMode = ref('wysiwyg')

const lineCount = computed(() => {
  const lines = (form.content || '').split('\n').length
  return Math.max(lines, 1)
})

function updateLineNumbers() {
  // 由 computed lineCount 自动更新
}

function syncScroll() {
  if (lineNumbersRef.value && textareaRef.value) {
    lineNumbersRef.value.scrollTop = textareaRef.value.scrollTop
  }
}

// 工具栏：包裹选中文本（直接操作 value + 同步 v-model）
function mdWrap(before, after, placeholder) {
  const ta = textareaRef.value
  if (!ta) return
  const start = ta.selectionStart
  const end = ta.selectionEnd
  const selected = ta.value.substring(start, end)
  const insertion = selected ? before + selected + after : before + placeholder + after

  form.content = ta.value.substring(0, start) + insertion + ta.value.substring(end)

  nextTick(() => {
    ta.focus({ preventScroll: true })
    if (!selected) {
      const newStart = start + before.length
      ta.setSelectionRange(newStart, newStart + placeholder.length)
    } else {
      ta.setSelectionRange(start, start + insertion.length)
    }
  })
}

// 工具栏：插入标题（循环 H1→H2→H3→H1）
function insertHeading() {
  const ta = textareaRef.value
  if (!ta) return
  const start = ta.selectionStart
  const lineStart = ta.value.lastIndexOf('\n', start - 1) + 1
  const lineEnd = ta.value.indexOf('\n', start)
  const end = lineEnd === -1 ? ta.value.length : lineEnd
  const currentLine = ta.value.substring(lineStart, end)

  let level = 1
  if (/^# /.test(currentLine)) level = 2
  else if (/^## /.test(currentLine)) level = 3
  else if (/^### /.test(currentLine)) level = 1

  const prefix = '#'.repeat(level) + ' '
  const newLine = prefix + currentLine.replace(/^#+ /, '')
  form.content = ta.value.substring(0, lineStart) + newLine + ta.value.substring(end)

  nextTick(() => {
    ta.focus({ preventScroll: true })
    ta.setSelectionRange(lineStart, lineStart + newLine.length)
  })
}

// 工具栏：插入代码块
function insertCodeBlock() {
  const ta = textareaRef.value
  if (!ta) return
  const start = ta.selectionStart
  const end = ta.selectionEnd
  const selected = ta.value.substring(start, end)
  const insertion = selected ? `\n\`\`\`\n${selected}\n\`\`\`\n` : '\n```\n代码块\n```\n'

  form.content = ta.value.substring(0, start) + insertion + ta.value.substring(end)

  nextTick(() => {
    ta.focus({ preventScroll: true })
    if (!selected) {
      const newStart = start + 5
      ta.setSelectionRange(newStart, newStart + 3)
    } else {
      ta.setSelectionRange(start, start + insertion.length)
    }
  })
}

// 工具栏：插入列表
function insertList(prefix) {
  const ta = textareaRef.value
  if (!ta) return
  const start = ta.selectionStart
  const end = ta.selectionEnd
  const selected = ta.value.substring(start, end)

  if (selected) {
    const items = selected.split('\n').map((l) => prefix + l).join('\n')
    form.content = ta.value.substring(0, start) + items + ta.value.substring(end)
    nextTick(() => {
      ta.focus({ preventScroll: true })
      ta.setSelectionRange(start, start + items.length)
    })
    return
  }

  const lineStart = ta.value.lastIndexOf('\n', start - 1) + 1
  let lineEnd = ta.value.indexOf('\n', start)
  if (lineEnd === -1) lineEnd = ta.value.length
  const currentLine = ta.value.substring(lineStart, lineEnd)

  const newLine = prefix + currentLine
  form.content = ta.value.substring(0, lineStart) + newLine + ta.value.substring(lineEnd)

  nextTick(() => {
    ta.focus({ preventScroll: true })
    ta.setSelectionRange(lineStart + prefix.length, lineStart + newLine.length)
  })
}

// === 模式切换 & 所见即所得 ===
function toggleMode() {
  if (editorMode.value === 'wysiwyg') {
    // 所见即所得 -> 源码：先把富文本转回 markdown
    syncWysiwygToSource()
    editorMode.value = 'source'
    nextTick(() => {
      const ta = textareaRef.value
      if (!ta) return
      // preventScroll 阻止浏览器聚焦时自动滚动到光标
      ta.focus({ preventScroll: true })
      ta.setSelectionRange(0, 0)
      // 等布局完成后再强制置顶，覆盖浏览器异步滚动行为
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          if (!textareaRef.value) return
          textareaRef.value.scrollTop = 0
          if (lineNumbersRef.value) lineNumbersRef.value.scrollTop = 0
        })
      })
    })
  } else {
    // 源码 -> 所见即所得：把 markdown 渲染成富文本
    editorMode.value = 'wysiwyg'
    nextTick(renderToWysiwyg)
  }
}

function renderToWysiwyg() {
  if (!wysiwygRef.value) return
  const html = DOMPurify.sanitize(marked.parse(form.content || '', { breaks: true }))
  wysiwygRef.value.innerHTML = html
}

function syncWysiwygToSource() {
  if (!wysiwygRef.value) return
  form.content = htmlToMarkdown(wysiwygRef.value)
}

// 所见即所得模式下粘贴：把剪贴板里的 markdown 源码即时渲染成 HTML 插入
function onWysiwygPaste(e) {
  const cd = e.clipboardData || window.clipboardData
  if (!cd) return
  const text = cd.getData('text/plain')
  if (!text) return
  e.preventDefault()
  const html = DOMPurify.sanitize(marked.parse(text, { breaks: true }))
  document.execCommand('insertHTML', false, html)
  syncWysiwygToSource()
}

// 统一工具栏入口：按当前模式分发
function onToolbar(action) {
  if (editorMode.value === 'source') {
    switch (action) {
      case 'bold': return mdWrap('**', '**', '加粗文字')
      case 'italic': return mdWrap('*', '*', '斜体文字')
      case 'heading': return insertHeading()
      case 'link': return mdWrap('[', '](url)', '链接文字')
      case 'image': return mdWrap('![', '](url)', '图片描述')
      case 'quote': return mdWrap('> ', '', '引用文字')
      case 'code': return mdWrap('`', '`', '代码')
      case 'codeblock': return insertCodeBlock()
      case 'ul': return insertList('- ')
      case 'ol': return insertList('1. ')
      case 'hr': return mdWrap('\n---\n', '', '')
    }
  } else {
    switch (action) {
      case 'bold': return document.execCommand('bold')
      case 'italic': return document.execCommand('italic')
      case 'heading': return richHeading()
      case 'link': return richLink()
      case 'image': return richImage()
      case 'quote': return document.execCommand('formatBlock', false, 'BLOCKQUOTE')
      case 'code': return wrapInline('<code>', '</code>')
      case 'codeblock': return richCodeBlock()
      case 'ul': return document.execCommand('insertUnorderedList')
      case 'ol': return document.execCommand('insertOrderedList')
      case 'hr': return document.execCommand('insertHorizontalRule')
    }
  }
}

// 富文本：标题循环 P -> H2 -> H3 -> H4 -> P
function richHeading() {
  const sel = window.getSelection()
  let node = sel.anchorNode
  while (node && node.parentElement && node.parentElement !== wysiwygRef.value) {
    node = node.parentElement
  }
  const cur = node && node.tagName ? node.tagName.toLowerCase() : 'p'
  let next = 'H2'
  if (cur === 'h2') next = 'H3'
  else if (cur === 'h3') next = 'H4'
  else if (cur === 'h4') next = 'P'
  document.execCommand('formatBlock', false, next)
}

function richLink() {
  const url = window.prompt('输入链接地址')
  if (url) document.execCommand('createLink', false, url)
}

function richImage() {
  const url = window.prompt('输入图片地址')
  if (url) document.execCommand('insertImage', false, url)
}

function richCodeBlock() {
  const sel = window.getSelection()
  const text = sel.toString() || '代码块'
  document.execCommand('insertHTML', false, `<pre><code>${escapeHtml(text)}</code></pre><p><br></p>`)
}

// 富文本：行内包裹（用于行内代码，execCommand 无对应命令）
function wrapInline(open, close) {
  const sel = window.getSelection()
  if (!sel.rangeCount) return
  const range = sel.getRangeAt(0)
  const text = range.toString() || '代码'
  const wrapper = document.createElement('span')
  wrapper.innerHTML = open + escapeHtml(text) + close
  const node = wrapper.firstChild
  range.deleteContents()
  range.insertNode(node)
}

function escapeHtml(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

// === HTML -> Markdown 转换 ===
function htmlToMarkdown(root) {
  const md = serializeBlock(root)
  return md.replace(/\n{3,}/g, '\n\n').trim() + '\n'
}

function serializeInline(node) {
  let out = ''
  node.childNodes.forEach((child) => {
    if (child.nodeType === Node.TEXT_NODE) {
      out += child.textContent.replace(/\s+/g, ' ')
    } else if (child.nodeType === Node.ELEMENT_NODE) {
      const tag = child.tagName.toLowerCase()
      const inner = serializeInline(child)
      switch (tag) {
        case 'strong': case 'b': out += '**' + inner + '**'; break
        case 'em': case 'i': out += '*' + inner + '*'; break
        case 'del': case 's': out += '~~' + inner + '~~'; break
        case 'code': out += '`' + child.textContent + '`'; break
        case 'a': out += '[' + inner + '](' + (child.getAttribute('href') || '') + ')'; break
        case 'img': out += '![' + (child.getAttribute('alt') || '') + '](' + (child.getAttribute('src') || '') + ')'; break
        case 'br': out += '\n'; break
        default: out += inner
      }
    }
  })
  return out
}

function serializeBlock(root) {
  let out = ''
  root.childNodes.forEach((node) => {
    if (node.nodeType === Node.TEXT_NODE) {
      const t = node.textContent.replace(/\s+/g, ' ').trim()
      if (t) out += t + '\n\n'
      return
    }
    if (node.nodeType !== Node.ELEMENT_NODE) return
    const tag = node.tagName.toLowerCase()
    switch (tag) {
      case 'h1': case 'h2': case 'h3': case 'h4': case 'h5': case 'h6': {
        const level = parseInt(tag[1])
        out += '#'.repeat(level) + ' ' + serializeInline(node).trim() + '\n\n'
        break
      }
      case 'p': case 'div':
        out += serializeInline(node).trim() + '\n\n'; break
      case 'br': out += '\n'; break
      case 'hr': out += '---\n\n'; break
      case 'blockquote': {
        const inner = serializeBlock(node).trim()
        out += inner.split('\n').map((l) => '> ' + l).join('\n') + '\n\n'
        break
      }
      case 'pre': {
        const codeEl = node.querySelector('code')
        const lang = codeEl ? (codeEl.className.match(/language-(\w+)/) || [])[1] : ''
        const text = (codeEl || node).textContent.replace(/\n$/, '')
        out += '```' + (lang || '') + '\n' + text + '\n```\n\n'
        break
      }
      case 'ul': case 'ol': {
        const items = Array.from(node.children).filter((c) => c.tagName.toLowerCase() === 'li')
        items.forEach((li, i) => {
          const prefix = tag === 'ol' ? `${i + 1}. ` : '- '
          out += prefix + serializeInline(li).trim() + '\n'
        })
        out += '\n'
        break
      }
      case 'table':
        out += serializeTable(node) + '\n\n'; break
      default: out += serializeBlock(node)
    }
  })
  return out
}

function serializeTable(table) {
  const rows = Array.from(table.querySelectorAll('tr'))
  if (!rows.length) return ''
  const header = Array.from(rows[0].children).map((td) => serializeInline(td).trim())
  let md = '| ' + header.join(' | ') + ' |\n'
  md += '| ' + header.map(() => '---').join(' | ') + ' |\n'
  rows.slice(1).forEach((tr) => {
    const cells = Array.from(tr.children).map((td) => serializeInline(td).trim())
    md += '| ' + cells.join(' | ') + ' |\n'
  })
  return md
}

// 快捷键
function handleKeydown(e) {
  // Ctrl+S / Cmd+S 保存（两种模式通用）
  if ((e.ctrlKey || e.metaKey) && e.key === 's') {
    e.preventDefault()
    onSave()
    return
  }
  if (editorMode.value === 'source') {
    // Ctrl+B 加粗
    if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
      e.preventDefault()
      mdWrap('**', '**', '加粗文字')
      return
    }
    // Ctrl+I 斜体
    if ((e.ctrlKey || e.metaKey) && e.key === 'i') {
      e.preventDefault()
      mdWrap('*', '*', '斜体文字')
      return
    }
    // Tab 插入两个空格
    if (e.key === 'Tab') {
      e.preventDefault()
      const ta = textareaRef.value
      const start = ta.selectionStart
      const end = ta.selectionEnd
      ta.value = ta.value.substring(0, start) + '  ' + ta.value.substring(end)
      ta.selectionStart = ta.selectionEnd = start + 2
      form.content = ta.value
    }
  }
  // 所见即所得模式下 Ctrl+B/I 由浏览器原生 contenteditable 命令处理
}

async function loadArticle() {
  if (!id.value) return
  try {
    const data = await getArticle(id.value)
    Object.assign(form, {
      title: data.title ?? '',
      summary: data.summary ?? '',
      content: data.content ?? '',
      cover_url: data.cover_url ?? '',
      status: data.status ?? 'draft',
      category_ids: Array.isArray(data.category_ids) && data.category_ids.length
        ? data.category_ids
        : Array.isArray(data.categories)
          ? data.categories.map((c) => c.id)
          : [],
    })
  } catch (e) {
    // ignore
  }
}

async function loadCategories() {
  try {
    const data = await listCategories({ include_count: true })
    categories.value = data?.items || data?.list || data || []
  } catch (e) {
    categories.value = []
  }
}

function onCancel() {
  router.back()
  if (!window.history.length) router.push('/admin/articles')
}

async function onSave() {
  if (!form.title.trim()) {
    ElMessage.warning('请输入文章标题')
    return
  }
  // 所见即所得模式下，保存前先把富文本同步回 markdown
  if (editorMode.value === 'wysiwyg') syncWysiwygToSource()
  saving.value = true
  try {
    const payload = { ...form }
    if (isEdit.value) {
      await updateArticle(id.value, payload)
      ElMessage.success('保存成功')
    } else {
      await createArticle(payload)
      ElMessage.success('创建成功')
    }
    router.push('/admin/articles')
  } catch (e) {
    // 错误已提示
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  loadCategories()
  await loadArticle()
  nextTick(() => {
    syncScroll()
    if (editorMode.value === 'wysiwyg') renderToWysiwyg()
  })
})

// 全局快捷键
onMounted(() => {
  const onGlobalKeydown = (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
      e.preventDefault()
      onSave()
    }
  }
  document.addEventListener('keydown', onGlobalKeydown)
})
</script>

<style scoped>
/* === 文章信息卡片 === */
.info-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.25rem;
  margin-bottom: 1.5rem;
}

.metadata-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: var(--muted-foreground);
  cursor: pointer;
  padding: 0.25rem 0;
  user-select: none;
  transition: color 0.2s ease;
}
.metadata-toggle:hover {
  color: var(--foreground);
}
.metadata-toggle .toggle-arrow {
  display: inline-block;
  transition: transform 0.2s ease;
  font-size: 0.7rem;
}
.metadata-toggle.collapsed .toggle-arrow {
  transform: rotate(-90deg);
}

.metadata-body {
  margin-top: 1rem;
}

.metadata-slide-enter-active,
.metadata-slide-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}
.metadata-slide-enter-from,
.metadata-slide-leave-to {
  max-height: 0;
  opacity: 0;
}
.metadata-slide-enter-to,
.metadata-slide-leave-from {
  max-height: 1000px;
  opacity: 1;
}

/* === 表单 === */
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
  margin-bottom: 1.25rem;
}
.form-group {
  margin-bottom: 1.25rem;
}
.form-group:last-child {
  margin-bottom: 0;
}
.form-group label {
  display: block;
  font-size: 0.85rem;
  font-weight: 500;
  margin-bottom: 0.25rem;
  color: var(--foreground);
}

/* === 封面预览 === */
.cover-preview {
  border-radius: var(--radius-md);
  overflow: hidden;
  border: 1px solid var(--border);
  max-width: 400px;
}
.cover-preview img {
  width: 100%;
  max-height: 240px;
  object-fit: cover;
  display: block;
}

/* === 编辑器卡片 === */
.editor-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.editor-container {
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 220px);
  background: var(--background);
}

.editor-topbar {
  padding: 0.625rem 1rem;
  background: var(--secondary);
  border-bottom: 1px solid var(--border);
}
.editor-mode-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-family: var(--font-mono);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--muted-foreground);
}
.mode-badge {
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.05em;
}
.mode-badge--wysiwyg {
  background: rgba(0, 101, 253, 0.12);
  color: var(--color-primary);
}
.mode-badge--source {
  background: var(--card);
  color: var(--foreground);
  border: 1px solid var(--border);
}
.editor-mode-label .pane-hint {
  font-size: 0.7rem;
  color: var(--muted-foreground);
}

/* === 工具栏 === */
.editor-toolbar {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid var(--border);
  background: var(--card);
}
.editor-toolbar button {
  min-width: 32px;
  height: 32px;
  padding: 0 6px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  color: var(--muted-foreground);
  transition: all 0.2s ease;
  background: transparent;
  border: none;
  cursor: pointer;
}
.editor-toolbar button:hover {
  background: var(--secondary);
  color: var(--foreground);
}
.editor-toolbar button:active {
  background: var(--border);
}
.editor-toolbar .toolbar-divider {
  width: 1px;
  height: 20px;
  background: var(--border);
  margin: 0 4px;
}
.editor-toolbar .mode-toggle {
  margin-left: auto;
  padding: 0 12px;
  font-size: 0.78rem;
  font-weight: 500;
  color: var(--color-primary);
  border: 1px solid var(--border);
}
.editor-toolbar .mode-toggle:hover {
  background: rgba(0, 101, 253, 0.08);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

/* === 编辑区主体 === */
.editor-wrap {
  position: relative;
  flex: 1;
  display: flex;
  overflow: hidden;
}
.editor-source-pane,
.editor-wysiwyg-pane {
  flex: 1;
  display: flex;
  overflow: hidden;
}
.editor-line-numbers {
  width: 48px;
  flex-shrink: 0;
  padding: 1rem 0;
  text-align: right;
  font-family: var(--font-mono);
  font-size: 0.9rem;
  line-height: 1.8;
  color: var(--muted-foreground);
  background: var(--secondary);
  border-right: 1px solid var(--border);
  user-select: none;
  overflow: hidden;
}
.editor-line-numbers span {
  display: block;
  padding-right: 0.5rem;
}
.editor-textarea {
  flex: 1;
  padding: 1rem;
  border: none;
  outline: none;
  resize: none;
  font-family: var(--font-mono);
  font-size: 0.9rem;
  line-height: 1.8;
  color: var(--foreground);
  background: var(--background);
  tab-size: 2;
  white-space: pre-wrap;
  word-wrap: break-word;
}

/* === 所见即所得编辑区 === */
.editor-wysiwyg {
  flex: 1;
  padding: 1.5rem 2rem;
  overflow-y: auto;
  line-height: 1.9;
  outline: none;
  font-size: 0.95rem;
  color: var(--foreground);
}
.editor-wysiwyg:focus {
  outline: none;
}
.editor-wysiwyg :deep(h1) { font-size: 1.75rem; margin-bottom: 0.75rem; }
.editor-wysiwyg :deep(h2) { font-size: 1.4rem; margin-bottom: 0.75rem; margin-top: 1.5rem; }
.editor-wysiwyg :deep(h3) { font-size: 1.15rem; margin-bottom: 0.5rem; margin-top: 1.25rem; }
.editor-wysiwyg :deep(p) { margin-bottom: 0.75rem; }
.editor-wysiwyg :deep(ul),
.editor-wysiwyg :deep(ol) { margin-bottom: 0.75rem; padding-left: 1.5rem; }
.editor-wysiwyg :deep(li) { margin-bottom: 0.25rem; }
.editor-wysiwyg :deep(blockquote) {
  border-left: 3px solid var(--color-primary);
  padding: 0.5rem 1rem;
  margin: 1rem 0;
  background: var(--secondary);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  color: var(--muted-foreground);
}
.editor-wysiwyg :deep(code) {
  font-family: var(--font-mono);
  font-size: 0.85em;
  background: var(--secondary);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
}
.editor-wysiwyg :deep(pre) {
  background: #1a1a1c;
  color: #e7eaef;
  padding: 1rem;
  border-radius: var(--radius-md);
  overflow-x: auto;
  margin-bottom: 1rem;
  font-family: "Fira Code", "JetBrains Mono", "Cascadia Code", ui-monospace, monospace;
  font-size: 0.875rem;
  line-height: 1.7;
  font-variant-ligatures: contextual;
  font-feature-settings: "calt" 1;
}
.editor-wysiwyg :deep(pre code) {
  background: none;
  padding: 0;
  color: inherit;
}
.editor-wysiwyg :deep(img) {
  max-width: 100%;
  border-radius: var(--radius-md);
  margin: 1rem 0;
}
.editor-wysiwyg :deep(hr) {
  border: none;
  border-top: 1px solid var(--border);
  margin: 2rem 0;
}
.editor-wysiwyg :deep(a) {
  color: var(--color-primary);
  text-decoration: underline;
  text-underline-offset: 2px;
}
.editor-wysiwyg :deep(a:hover) {
  color: var(--color-primary-deep);
}
.editor-wysiwyg :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1rem;
}
.editor-wysiwyg :deep(th),
.editor-wysiwyg :deep(td) {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border);
  text-align: left;
}
.editor-wysiwyg :deep(th) {
  background: var(--secondary);
  font-weight: 600;
}

/* === 响应式 === */
@media (max-width: 900px) {
  .editor-container {
    min-height: auto;
  }
  .editor-source-pane,
  .editor-wysiwyg-pane {
    min-height: 400px;
  }
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
