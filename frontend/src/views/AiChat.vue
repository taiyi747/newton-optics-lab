<template>
  <div id="ai-chat-page" class="page-content h-full bg-base-200/60 p-0">
    <section class="mx-auto flex h-full max-w-[980px] flex-col overflow-hidden rounded-xl bg-base-100 shadow-[0_18px_45px_rgba(15,23,42,0.08)]">
      <header class="flex items-center justify-between gap-4 bg-base-100/95 px-5 py-4 shadow-[0_1px_0_rgba(15,23,42,0.06)]">
        <div class="flex min-w-0 items-center gap-3">
          <div class="grid h-11 w-11 shrink-0 place-items-center rounded-lg bg-primary text-primary-content shadow-sm">
            <span class="text-sm font-black">AI</span>
          </div>
          <div class="min-w-0">
            <h2 class="truncate text-base font-semibold text-base-content">{{ t('AI 物理助手') }}</h2>
            <p class="truncate text-xs text-base-content/55">{{ t('物理光学实验答疑、数据解读与误差分析') }}</p>
          </div>
        </div>
        <div class="hidden items-center gap-2 sm:flex">
          <span class="status status-success"></span>
          <span class="text-xs font-medium text-base-content/60">{{ t('在线响应') }}</span>
        </div>
      </header>

      <div id="chatArea" ref="chatAreaRef" class="min-h-0 flex-1 overflow-y-auto px-5 py-5">
        <div v-if="messages.length === 0" class="flex min-h-full items-center justify-center">
          <div class="w-full max-w-2xl text-center">
            <div class="mx-auto mb-4 grid h-14 w-14 place-items-center rounded-xl bg-primary/10 text-primary">
              <svg class="h-7 w-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.6" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 0 0-2.455 2.456Z"/>
              </svg>
            </div>
            <h1 class="mb-2 text-2xl font-semibold text-base-content">{{ t('今天想分析哪一段实验？') }}</h1>
            <p class="mx-auto mb-6 max-w-md text-sm leading-6 text-base-content/60">
              {{ t('可以直接提问，也可以上传 CSV、TXT 或实验记录，让助手结合数据回答。') }}
            </p>
            <div class="grid gap-2 sm:grid-cols-2">
              <button v-for="p in quickPrompts" :key="p.text" class="btn justify-start rounded-lg border-transparent bg-base-100 text-left shadow-sm hover:bg-primary/10 hover:text-primary" @click="sendMessage(p.prompt)">
                {{ t(p.text) }}
              </button>
            </div>
          </div>
        </div>

        <div v-else class="space-y-5">
          <article
            v-for="(msg, idx) in messages"
            :key="idx"
            :class="['message-row', msg.role === 'user' ? 'message-row-user' : 'message-row-assistant']"
          >
            <div :class="['message-avatar', msg.role === 'user' ? 'message-avatar-user' : 'message-avatar-assistant']">
              <span v-if="msg.role === 'assistant'">AI</span>
              <svg v-else class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21a8 8 0 0 0-16 0" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="12" cy="8" r="4"/>
              </svg>
            </div>

            <div class="message-stack">
              <div class="message-meta">
                <span>{{ msg.role === 'user' ? t('你') : t('AI 助手') }}</span>
              </div>
              <div :class="['message-bubble', msg.role === 'user' ? 'message-bubble-user' : 'message-bubble-assistant']">
                <div class="message-content" :data-message-index="idx" v-html="msg.content"></div>
              </div>
            </div>
          </article>
        </div>
      </div>

      <footer class="bg-base-100 px-4 py-4 shadow-[0_-10px_30px_rgba(15,23,42,0.06)]">
        <div v-if="attachments.length" class="mb-3 flex flex-wrap gap-2">
          <span v-for="(a, i) in attachments" :key="i" class="badge badge-lg gap-2 rounded-lg border-transparent bg-primary/10 text-primary">
            <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7 8.586 13.586a2 2 0 0 0 2.828 2.828l6.414-6.586a4 4 0 0 0-5.656-5.656l-6.415 6.585a6 6 0 0 0 8.486 8.486L20.5 13"/>
            </svg>
            <span class="max-w-[220px] truncate">{{ a.name }}</span>
            <button class="btn btn-ghost btn-xs h-5 min-h-5 w-5 rounded-full p-0 text-primary/60 hover:text-error" title="移除附件" @click="removeAttachment(i)">
              &times;
            </button>
          </span>
        </div>

        <div class="rounded-xl bg-base-200/70 p-2 shadow-inner ring-1 ring-primary/10">
          <textarea
            v-model="inputText"
            :placeholder="t('输入你的问题...')"
            autocomplete="off"
            rows="1"
            class="textarea min-h-12 w-full resize-none border-0 bg-transparent px-3 py-3 text-sm leading-6 shadow-none outline-none focus:outline-none"
            @keydown.enter.exact.prevent="sendMessage(inputText)"
            @input="autoResize"
          ></textarea>

          <div class="flex items-center justify-between gap-3 px-1 pb-1">
            <div class="flex items-center gap-1">
              <button class="btn btn-ghost btn-sm rounded-lg px-3" :title="t('上传实验数据附件')" @click="$refs.fileInput.click()">
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M15.172 7 8.586 13.586a2 2 0 0 0 2.828 2.828l6.414-6.586a4 4 0 0 0-5.656-5.656l-6.415 6.585a6 6 0 0 0 8.486 8.486L20.5 13"/>
                </svg>
              </button>
              <input ref="fileInput" type="file" class="hidden" multiple @change="onFileSelect">
              <button v-if="messages.length" class="btn btn-ghost btn-sm rounded-lg px-3 text-base-content/50 hover:text-error" :title="t('清空对话')" @click="clearChat">
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="m19 7-.867 12.142A2 2 0 0 1 16.138 21H7.862a2 2 0 0 1-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v3M4 7h16"/>
                </svg>
              </button>
              <span class="hidden text-xs text-base-content/40 sm:inline">{{ t('Enter 发送，Shift+Enter 换行') }}</span>
            </div>

            <div class="flex items-center gap-2">
              <button v-if="isStreaming" class="btn btn-outline btn-error btn-sm rounded-lg" @click="stopStreaming">
                <svg class="h-3.5 w-3.5" fill="currentColor" viewBox="0 0 24 24">
                  <rect x="6" y="6" width="12" height="12" rx="2"/>
                </svg>
                {{ t('停止') }}
              </button>
              <button class="btn btn-primary btn-sm rounded-lg px-4" :disabled="isStreaming || (!inputText.trim() && attachments.length === 0)" :title="t('发送')" @click="sendMessage(inputText)">
                <span>{{ t('发送') }}</span>
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14m-7-7 7 7-7 7"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </footer>
    </section>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import katex from 'katex'
import 'katex/dist/katex.min.css'
import backendBridge from '../utils/backend-bridge.js'
import { useI18n } from '../utils/i18n.js'

const { t } = useI18n()
const inputText = ref('')
const messages = ref([])
const isStreaming = ref(false)
const attachments = ref([])
const chatHistory = ref([])
const abortController = ref(null)
const chatAreaRef = ref(null)
const fileInput = ref(null)

const quickPrompts = [
  { text: '解释牛顿环实验原理', prompt: '请解释牛顿环实验的原理。' },
  { text: '波长如何影响条纹', prompt: '牛顿环实验中，波长对条纹有什么影响？' },
  { text: '怎样测量曲率半径', prompt: '如何通过牛顿环实验测量透镜曲率半径？' },
  { text: '分析常见误差来源', prompt: '牛顿环实验的误差来源有哪些？' }
]

const chatContextPrompt = `当前前端页面是物理光学综合实验平台的 AI 助手。

请优先围绕牛顿环实验、单缝衍射、双缝干涉、双缝衍射、薄膜干涉、光学实验、实验数据处理和相关数学/物理问题回答。
如果用户上传实验数据，请结合附件内容进行解释、计算或误差分析。

排版规则：
1. 段落保持紧凑，不要在一句话中间随意换行。
2. 不要把单个变量、符号或短公式单独拆成一行，例如不要把 λ、R、r_m 单独换行。
3. 普通说明用自然段或序号列表即可，每个要点 1 到 3 句话。
4. 只有重要公式才单独成行，公式前后最多保留一个换行。

公式输出规则：
1. 行内公式使用 $...$，例如 $t=\\frac{r^2}{2R}$。
2. 重要公式单独成行时使用 $$...$$，例如 $$r_m^2=m\\lambda R$$。
3. 公式内部不要换行，不要把一个公式拆成多行。
4. 不要把公式放进代码块。`

function stripMarkdown(text) {
  if (!text) return ''
  return text
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/\*(.*?)\*/g, '$1')
    .replace(/###\s*/g, '')
    .replace(/##\s*/g, '')
    .replace(/#\s*/g, '')
    .replace(/```/g, '')
    .replace(/`(.*?)`/g, '$1')
    .replace(/\[(.*?)\]\(.*?\)/g, '$1')
    .replace(/!\[(.*?)\]\(.*?\)/g, '$1')
    .replace(/---/g, '')
}

function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function formatMessage(text) {
  return renderLatex(stripMarkdown(text).replace(/\r\n/g, '\n'))
}

function renderFormula(source, displayMode) {
  try {
    return katex.renderToString(source.trim(), {
      displayMode,
      throwOnError: false,
      strict: 'ignore',
      trust: false,
      output: 'html'
    })
  } catch {
    return escapeHtml(source)
  }
}

function renderLatex(text) {
  const tokens = []
  const pattern = /(\$\$[\s\S]+?\$\$|\\\[[\s\S]+?\\\]|\\\([\s\S]+?\\\)|\$[^$\n]+?\$)/g
  let cursor = 0
  let match

  while ((match = pattern.exec(text)) !== null) {
    if (match.index > cursor) {
      tokens.push({ type: 'text', value: text.slice(cursor, match.index) })
    }

    const raw = match[0]
    if (raw.startsWith('$$')) {
      tokens.push({ type: 'math', display: true, value: raw.slice(2, -2) })
    } else if (raw.startsWith('\\[')) {
      tokens.push({ type: 'math', display: true, value: raw.slice(2, -2) })
    } else if (raw.startsWith('\\(')) {
      tokens.push({ type: 'math', display: false, value: raw.slice(2, -2) })
    } else {
      tokens.push({ type: 'math', display: false, value: raw.slice(1, -1) })
    }
    cursor = pattern.lastIndex
  }

  if (cursor < text.length) {
    tokens.push({ type: 'text', value: text.slice(cursor) })
  }

  return tokens.map((token) => {
    if (token.type === 'math') return renderFormula(token.value, token.display)
    return escapeHtml(token.value).replace(/\n/g, '<br>')
  }).join('')
}

function readSseData(frame) {
  const dataLines = []
  for (const rawLine of frame.split(/\r?\n/)) {
    const line = rawLine.trimEnd()
    if (!line || line.startsWith(':')) continue
    if (line.startsWith('data:')) {
      dataLines.push(line.slice(5).replace(/^ /, ''))
    }
  }
  return dataLines.length ? dataLines.join('\n') : ''
}

function extractSseContent(parsed) {
  return parsed?.choices?.[0]?.delta?.content
    ?? parsed?.choices?.[0]?.message?.content
    ?? parsed?.delta?.content
    ?? parsed?.content
    ?? ''
}

function extractSseError(parsed) {
  const error = parsed?.error
  if (!error) return ''
  return typeof error === 'string' ? error : (error.message || JSON.stringify(error))
}

async function readFileAsBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result.split(',')[1])
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

async function onFileSelect(e) {
  const files = Array.from(e.target.files || [])
  for (const file of files) {
    attachments.value.push({
      name: file.name,
      type: file.type,
      size: file.size,
      data: await readFileAsBase64(file)
    })
  }
  e.target.value = ''
}

function removeAttachment(index) {
  attachments.value.splice(index, 1)
}

async function sendMessage(text) {
  if (!text?.trim() && attachments.value.length === 0) return
  if (isStreaming.value) return

  let actualMessage = text?.trim() || ''
  let displayMessage = actualMessage

  if (attachments.value.length > 0) {
    const fileNames = attachments.value.map(a => a.name).join('、')
    actualMessage = (actualMessage || '请分析我上传的实验数据')
      + `\n\n[用户上传了附件：${fileNames}，这是物理光学综合实验平台的相关实验数据，请结合附件内容进行分析回答。]`
    displayMessage = actualMessage || `上传了 ${fileNames}`
  }

  const historyForApi = chatHistory.value.map(item => ({
    role: item.role === 'ai' ? 'assistant' : item.role,
    content: item.content
  }))

  messages.value.push({ role: 'user', content: formatMessage(displayMessage) })
  chatHistory.value.push({ role: 'user', content: displayMessage })
  inputText.value = ''
  resetTextarea()

  const attachmentsToSend = attachments.value.length > 0 ? [...attachments.value] : null
  attachments.value = []

  await nextTick()
  scrollToBottom()

  isStreaming.value = true

  const aiMsgIndex = messages.value.length
  messages.value.push({ role: 'assistant', content: '<span class="chat-loading" aria-label="正在生成"><span></span><span></span><span></span></span>' })

  let fullResponse = ''
  let streamClosed = false

  const finishStream = (hasError = false) => {
    if (streamClosed) return
    streamClosed = true
    isStreaming.value = false
    abortController.value = null
    if (hasError) {
      messages.value[aiMsgIndex].content = formatMessage(fullResponse || '抱歉，响应出现了错误')
    } else if (fullResponse) {
      messages.value[aiMsgIndex].content = formatMessage(fullResponse)
      chatHistory.value.push({ role: 'ai', content: fullResponse })
    } else {
      messages.value[aiMsgIndex].content = '（无响应）'
    }
  }

  try {
    const response = await backendBridge.sseChat({
      message: actualMessage,
      attachments: attachmentsToSend,
      chat_history: historyForApi,
      context_prompt: chatContextPrompt
    })

    const reader = response.body.getReader()
    abortController.value = { abort: () => reader.cancel() }

    const decoder = new TextDecoder()
    let buffer = ''

    const applyContent = async (content) => {
      if (!content) return
      fullResponse += content
      messages.value[aiMsgIndex].content = formatMessage(fullResponse) + '<span class="streaming-cursor"></span>'
      await nextTick()
      scrollToBottom()
    }

    const processSseFrame = async (frame) => {
      const data = readSseData(frame)
      if (!data) return false
      if (data === '[DONE]') {
        finishStream(false)
        return true
      }

      try {
        const parsed = JSON.parse(data)
        const content = extractSseContent(parsed)
        const error = extractSseError(parsed)
        await applyContent(content || error)
      } catch (e) {
        console.debug('忽略无法解析的 SSE 片段', e)
      }
      return false
    }

    while (true) {
      const { done, value } = await reader.read()
      if (done) {
        const remaining = buffer.trim()
        if (remaining) {
          await processSseFrame(remaining)
        }
        finishStream(false)
        break
      }

      buffer += decoder.decode(value, { stream: true })
      const frames = buffer.split(/\r?\n\r?\n/)
      buffer = frames.pop()

      for (const frame of frames) {
        const didFinish = await processSseFrame(frame)
        if (didFinish) {
          return
        }
      }
    }
  } catch (error) {
    if (error.name !== 'AbortError') {
      console.error('流式对话失败:', error)
      const healthy = await backendBridge.checkHealth().catch(() => false)
      if (!healthy) {
        fullResponse = '后端服务未启动。请在项目根目录运行 python server.py，或使用 npm run dev 同时启动前端和后端。'
      } else {
        fullResponse = '对话失败，请稍后重试。'
      }
    }
    finishStream(true)
  }
}

function stopStreaming() {
  if (isStreaming.value && abortController.value) {
    abortController.value.abort()
  }
}

function clearChat() {
  if (isStreaming.value && abortController.value) {
    abortController.value.abort()
  }
  isStreaming.value = false
  abortController.value = null
  messages.value = []
  chatHistory.value = []
  attachments.value = []
}

function autoResize(e) {
  const el = e.target
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 132) + 'px'
}

function resetTextarea() {
  const el = document.querySelector('#ai-chat-page textarea')
  if (el) {
    el.style.height = 'auto'
  }
}

function scrollToBottom() {
  if (chatAreaRef.value) {
    chatAreaRef.value.scrollTop = chatAreaRef.value.scrollHeight
  }
}
</script>

<style scoped>
.message-row {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  animation: chatFadeIn 0.24s ease;
}

.message-row-user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 2.25rem;
  height: 2.25rem;
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  border-radius: 0.75rem;
  font-size: 0.6875rem;
  font-weight: 900;
  margin-top: 1.35rem;
  box-shadow: 0 1px 2px rgb(15 23 42 / 0.08);
}

.message-avatar-assistant {
  color: color-mix(in oklab, var(--color-primary) 82%, #0f172a);
  background: color-mix(in oklab, var(--color-primary) 13%, white);
}

.message-avatar-user {
  color: color-mix(in oklab, var(--color-base-content) 72%, transparent);
  background: var(--color-base-200);
}

.message-stack {
  display: flex;
  max-width: min(76%, 720px);
  flex-direction: column;
  gap: 0.25rem;
}

.message-row-user .message-stack {
  align-items: flex-end;
}

.message-meta {
  padding: 0 0.25rem;
  font-size: 0.75rem;
  line-height: 1rem;
  color: color-mix(in oklab, var(--color-base-content) 45%, transparent);
}

.message-bubble {
  position: relative;
  border-radius: 1rem;
  padding: 0.68rem 0.9rem;
  font-size: 0.9375rem;
  line-height: 1.65;
  overflow-wrap: break-word;
  word-break: normal;
  white-space: normal;
}

.message-bubble-assistant {
  color: color-mix(in oklab, var(--color-base-content) 78%, transparent);
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid color-mix(in oklab, var(--color-base-content) 10%, transparent);
  border-bottom-left-radius: 0.35rem;
  box-shadow: 0 8px 20px rgb(15 23 42 / 0.06);
}

.message-bubble-user {
  color: #ffffff;
  background: #0ea5e9;
  border-bottom-right-radius: 0.35rem;
  box-shadow: 0 10px 24px rgb(14 165 233 / 0.22);
}

.message-content :deep(br) {
  line-height: 1.9;
}

.message-content :deep(.katex) {
  font-size: 1.02em;
  white-space: nowrap;
}

.message-content :deep(.katex-display) {
  margin: 0.65rem 0;
  max-width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  padding: 0.15rem 0;
}

.message-content :deep(.chat-loading) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.28rem;
  min-width: 2.5rem;
  min-height: 1.4rem;
  padding: 0.05rem 0;
}

.message-content :deep(.chat-loading span) {
  width: 0.42rem;
  height: 0.42rem;
  border-radius: 999px;
  background: #94a3b8;
  animation: chatLoadingPulse 1s infinite ease-in-out both;
}

.message-content :deep(.chat-loading span:nth-child(2)) {
  animation-delay: 0.14s;
}

.message-content :deep(.chat-loading span:nth-child(3)) {
  animation-delay: 0.28s;
}

@keyframes chatLoadingPulse {
  0%, 80%, 100% { opacity: 0.35; transform: translateY(0); }
  40% { opacity: 1; transform: translateY(-2px); }
}

@media (max-width: 640px) {
  .message-stack {
    max-width: calc(100% - 3rem);
  }

  .message-avatar {
    width: 2rem;
    height: 2rem;
    border-radius: 0.65rem;
    margin-top: 1.3rem;
  }

  .message-bubble {
    padding: 0.72rem 0.82rem;
    font-size: 0.875rem;
  }
}
</style>
