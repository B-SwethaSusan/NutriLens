import { useEffect, useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import ReactMarkdown from 'react-markdown'
import {
  AlertCircle, Bot, Check, CheckCircle2, Clipboard, FileText, Loader2, MessageCircle,
  MoreHorizontal, Pencil, Plus, RefreshCw, Send, Sparkles, Trash2, UploadCloud, UserRound, X,
} from 'lucide-react'
import { api, type Citation, type Conversation, type Document } from '../lib/api'
import { formatBytes, formatDate } from '../lib/utils'
import { Badge, Button, Card, Input } from '../components/ui'
import { PageHeader } from '../components/Layout'

type LocalMessage = { role: 'user' | 'assistant'; content: string; citations?: Citation[] }
const suggestions = ['What are the key nutrients discussed in these documents?', 'Summarize the dietary recommendations.', 'What serving sizes or limits are mentioned?']

export function WorkspacePage() {
  const client = useQueryClient()
  const docs = useQuery({ queryKey: ['documents'], queryFn: async () => (await api.get<Document[]>('/documents')).data })
  const readyCount = docs.data?.filter(doc => doc.status === 'ready').length ?? 0

  const [messages, setMessages] = useState<LocalMessage[]>([])
  const [conversationId, setConversationId] = useState<string>()

  function loadConversation(item: Conversation) {
    setConversationId(item.id)
    setMessages(item.messages.map(message => ({ role: message.role as 'user' | 'assistant', content: message.content, citations: message.citations || undefined })))
  }

  return <>
    <PageHeader
      eyebrow="Document Q&A"
      title="Documents & Ask NutriLens"
      description="Upload nutrition PDFs here, then ask about them on the right — answers come only from what's uploaded and ready below, with page-level citations."
    />
    <div className="grid gap-6 xl:grid-cols-[340px_1fr]">
      <div className="space-y-6">
        <SourcesPanel docs={docs} client={client} />
        <RecentConversationsPanel onSelect={loadConversation} />
      </div>
      <ChatPanel
        hasReadyDocs={readyCount > 0}
        messages={messages}
        setMessages={setMessages}
        conversationId={conversationId}
        setConversationId={setConversationId}
      />
    </div>
  </>
}

function SourcesPanel({ docs, client }: { docs: ReturnType<typeof useQuery<Document[]>>; client: ReturnType<typeof useQueryClient> }) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [error, setError] = useState('')
  const upload = useMutation({
    mutationFn: async (file: File) => {
      const form = new FormData()
      form.append('file', file)
      return (await api.post('/upload', form, { headers: { 'Content-Type': 'multipart/form-data' }, timeout: 300000 })).data
    },
    onSuccess: () => { client.invalidateQueries({ queryKey: ['documents'] }); client.invalidateQueries({ queryKey: ['stats'] }) },
    onError: (err: any) => setError(err.response?.data?.detail || (err.code === 'ECONNABORTED' ? 'Upload timed out while parsing the PDF.' : 'Upload failed')),
  })
  function choose(file?: File) { if (file) upload.mutate(file) }
  const onChange = () => { client.invalidateQueries({ queryKey: ['documents'] }); client.invalidateQueries({ queryKey: ['stats'] }) }

  return <Card className="overflow-hidden">
    <div className="border-b border-sage-100 px-4 py-4">
      <h3 className="text-sm font-bold">Your sources</h3>
      <p className="mt-1 text-xs leading-5 text-ink/45">Chat on the right only answers from documents listed here with a "ready" status.</p>
    </div>
    <div className="p-4">
      <input ref={inputRef} type="file" accept="application/pdf" className="hidden" onChange={e => choose(e.target.files?.[0])} />
      {error && <div className="mb-3 flex items-center justify-between rounded-xl bg-red-50 px-3 py-2 text-xs text-red-700">
        <span className="flex items-center gap-2"><AlertCircle size={14} />{error}</span>
        <button onClick={() => setError('')}><X size={14} /></button>
      </div>}
      <div
        className="mb-3 rounded-xl border border-dashed border-sage-200 bg-sage-50/50 p-5 text-center"
        onDragOver={e => e.preventDefault()}
        onDrop={e => { e.preventDefault(); choose(e.dataTransfer.files[0]) }}
      >
        <UploadCloud size={20} className="mx-auto text-sage-600" />
        <p className="mt-2 text-xs text-ink/50">PDFs up to 100MB</p>
        <Button className="mt-3 w-full justify-center" onClick={() => inputRef.current?.click()} disabled={upload.isPending}>
          {upload.isPending ? 'Uploading…' : 'Upload PDF'}
        </Button>
      </div>
      {docs.isLoading ? <div className="flex justify-center py-8"><Loader2 className="animate-spin text-sage-600" /></div>
        : docs.data?.length ? <div className="space-y-2">{docs.data.map(doc => <DocumentRow key={doc.id} document={doc} onChange={onChange} />)}</div>
        : <p className="py-6 text-center text-xs leading-5 text-ink/45">No documents yet. Add a PDF above to start asking questions.</p>}
    </div>
  </Card>
}

function DocumentRow({ document, onChange }: { document: Document; onChange: () => void }) {
  const [editing, setEditing] = useState(false)
  const [name, setName] = useState(document.filename)
  const remove = useMutation({ mutationFn: () => api.delete(`/documents/${document.id}`), onSuccess: onChange })
  const save = useMutation({ mutationFn: () => api.put(`/documents/${document.id}`, { filename: name }), onSuccess: () => { setEditing(false); onChange() } })
  const reprocess = useMutation({ mutationFn: () => api.post(`/ingest/${document.id}`), onSuccess: onChange })
  return <div className="rounded-xl border border-sage-100 p-3">
    <div className="flex items-start gap-2">
      <div className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-red-50 text-red-500"><FileText size={16} /></div>
      <div className="min-w-0 flex-1">
        {editing
          ? <div className="flex gap-1"><Input value={name} onChange={e => setName(e.target.value)} className="text-xs" /><Button onClick={() => save.mutate()} disabled={save.isPending} className="px-2 text-xs">Save</Button></div>
          : <p className="truncate text-xs font-bold">{document.filename}</p>}
        <p className="mt-0.5 text-[11px] text-ink/45">{formatDate(document.created_at)} · {formatBytes(document.file_size)} · {document.chunk_count} chunks</p>
        {document.error_message && <p className="mt-0.5 text-[11px] text-red-600">{document.error_message}</p>}
      </div>
    </div>
    <div className="mt-2 flex items-center justify-between">
      <Badge tone={document.status === 'ready' ? 'green' : document.status === 'failed' ? 'red' : 'amber'}>
        {document.status === 'ready' ? <><CheckCircle2 size={12} />ready</> : document.status === 'processing' ? <><Loader2 size={12} className="animate-spin" />processing</> : document.status}
      </Badge>
      <div className="flex items-center gap-1">
        <button title="Rename" onClick={() => setEditing(true)} className="rounded-lg p-1.5 text-ink/40 hover:bg-sage-50 hover:text-ink"><Pencil size={14} /></button>
        <button title="Reprocess" onClick={() => reprocess.mutate()} className="rounded-lg p-1.5 text-ink/40 hover:bg-sage-50 hover:text-ink"><RefreshCw size={14} className={reprocess.isPending ? 'animate-spin' : ''} /></button>
        <button title="Delete" onClick={() => { if (window.confirm('Delete this document and its indexed chunks?')) remove.mutate() }} className="rounded-lg p-1.5 text-ink/40 hover:bg-red-50 hover:text-red-700"><Trash2 size={14} /></button>
      </div>
    </div>
  </div>
}

function RecentConversationsPanel({ onSelect }: { onSelect: (item: Conversation) => void }) {
  const history = useQuery({ queryKey: ['history'], queryFn: async () => (await api.get<Conversation[]>('/history')).data })
  return <Card className="overflow-hidden">
    <div className="border-b border-sage-100 px-4 py-4"><h3 className="text-sm font-bold">Recent conversations</h3></div>
    <div className="max-h-[260px] overflow-y-auto p-2">
      {history.data?.length ? history.data.map(item => <button key={item.id} onClick={() => onSelect(item)} className="w-full rounded-xl px-3 py-3 text-left text-xs leading-5 text-ink/60 hover:bg-sage-50"><MessageCircle size={14} className="mb-1 text-sage-600" />{item.title}</button>) : <p className="p-4 text-xs leading-5 text-ink/45">Your conversations will appear here.</p>}
    </div>
  </Card>
}

function ChatPanel({ hasReadyDocs, messages, setMessages, conversationId, setConversationId }: {
  hasReadyDocs: boolean
  messages: LocalMessage[]
  setMessages: React.Dispatch<React.SetStateAction<LocalMessage[]>>
  conversationId: string | undefined
  setConversationId: React.Dispatch<React.SetStateAction<string | undefined>>
}) {
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState<number | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)
  const history = useQuery({ queryKey: ['history'], queryFn: async () => (await api.get<Conversation[]>('/history')).data })

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, loading])

  function newChat() { setMessages([]); setConversationId(undefined) }

  async function ask(value = question) {
    const trimmed = value.trim()
    if (!trimmed || loading) return
    setQuestion('')
    setMessages(prev => [...prev, { role: 'user', content: trimmed }])
    setLoading(true)
    try {
      const { data } = await api.post('/chat', { question: trimmed, conversation_id: conversationId, stream: false })
      setConversationId(data.conversation_id)
      setMessages(prev => [...prev, { role: 'assistant', content: data.answer, citations: data.citations }])
      history.refetch()
    } catch (err: any) {
      setMessages(prev => [...prev, { role: 'assistant', content: err.response?.data?.detail || 'Something went wrong. Please try again.' }])
    } finally {
      setLoading(false)
    }
  }

  return <Card className="flex min-h-[620px] flex-col overflow-hidden">
    <div className="flex items-center justify-between border-b border-sage-100 px-5 py-3">
      <h3 className="text-sm font-bold">Ask NutriLens</h3>
      <Button variant="secondary" onClick={newChat}><Plus size={15} />New chat</Button>
    </div>
    <div className="flex-1 overflow-y-auto p-5 sm:p-8">
      {!messages.length
        ? <div className="mx-auto flex max-w-2xl flex-col items-center py-14 text-center">
            <div className="grid h-16 w-16 place-items-center rounded-3xl bg-sage-100 text-sage-700"><Sparkles size={28} /></div>
            <h2 className="serif mt-6 text-3xl">What would you like to understand?</h2>
            {hasReadyDocs
              ? <p className="mt-3 max-w-md text-sm leading-6 text-ink/50">I'll search your uploaded nutrition documents (left panel) and show you the exact sources behind every answer.</p>
              : <p className="mt-3 max-w-md text-sm leading-6 text-ink/50">Upload a PDF on the left first — I can only answer from documents that are uploaded and show a "ready" status.</p>}
            {hasReadyDocs && <div className="mt-8 grid w-full gap-2 sm:grid-cols-3">{suggestions.map(suggestion => <button key={suggestion} onClick={() => ask(suggestion)} className="rounded-xl border border-sage-100 bg-sage-50/60 p-3 text-left text-xs leading-5 text-ink/60 transition hover:border-sage-300 hover:bg-sage-50">{suggestion}</button>)}</div>}
          </div>
        : <div className="mx-auto max-w-3xl space-y-7">
            {messages.map((message, index) => <MessageBubble key={index} message={message} index={index} onCopy={() => { navigator.clipboard.writeText(message.content); setCopied(index); setTimeout(() => setCopied(null), 1500) }} copied={copied === index} />)}
            {loading && <div className="flex gap-3"><div className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-sage-100 text-sage-700"><Bot size={16} /></div><div className="rounded-2xl rounded-tl-sm bg-sage-50 px-4 py-3"><div className="flex gap-1"><span className="h-1.5 w-1.5 animate-bounce rounded-full bg-sage-500" /><span className="h-1.5 w-1.5 animate-bounce rounded-full bg-sage-500 [animation-delay:150ms]" /><span className="h-1.5 w-1.5 animate-bounce rounded-full bg-sage-500 [animation-delay:300ms]" /></div></div></div>}
            <div ref={bottomRef} />
          </div>}
    </div>
    <div className="border-t border-sage-100 bg-sage-50/40 p-4">
      <form onSubmit={e => { e.preventDefault(); ask() }} className="mx-auto flex max-w-3xl items-end gap-2 rounded-2xl border border-sage-200 bg-white p-2 shadow-sm">
        <textarea value={question} onChange={e => setQuestion(e.target.value)} onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); ask() } }} rows={1} placeholder="Ask about your nutrition documents…" className="max-h-32 min-h-10 flex-1 resize-none bg-transparent px-3 py-2.5 text-sm outline-none placeholder:text-ink/35" />
        <Button type="submit" className="h-10 w-10 shrink-0 rounded-xl p-0" disabled={!question.trim() || loading}><Send size={17} /></Button>
      </form>
      <p className="mt-2 text-center text-[10px] text-ink/35">NutriLens answers are grounded in your files. Always use professional judgment for health decisions.</p>
    </div>
  </Card>
}

function MessageBubble({ message, index, onCopy, copied }: { message: LocalMessage; index: number; onCopy: () => void; copied: boolean }) {
  const user = message.role === 'user'
  return <div className={`flex gap-3 ${user ? 'justify-end' : ''}`}>
    <div className={`grid h-8 w-8 shrink-0 place-items-center rounded-full ${user ? 'order-2 bg-citrus text-white' : 'bg-sage-100 text-sage-700'}`}>{user ? <UserRound size={16} /> : <Bot size={16} />}</div>
    <div className={`max-w-[85%] ${user ? 'order-1' : ''}`}>
      <div className={`rounded-2xl px-4 py-3 text-sm leading-7 ${user ? 'rounded-tr-sm bg-sage-700 text-white' : 'rounded-tl-sm bg-sage-50 text-ink'}`}><ReactMarkdown>{message.content}</ReactMarkdown></div>
      {!user && <>
        <div className="mt-2 flex items-center gap-1"><button onClick={onCopy} className="inline-flex items-center gap-1 rounded-lg px-2 py-1 text-[11px] text-ink/40 hover:bg-sage-50 hover:text-ink">{copied ? <Check size={13} /> : <Clipboard size={13} />}{copied ? 'Copied' : 'Copy'}</button></div>
        {message.citations?.length ? <div className="mt-2 flex flex-wrap gap-2">{message.citations.map((citation, citationIndex) => <span key={`${citation.filename}-${citation.page_number}-${citationIndex}`} className="inline-flex items-center gap-1 rounded-lg border border-sage-100 bg-white px-2 py-1 text-[11px] text-ink/55"><FileText size={12} className="text-sage-600" />{citation.filename} · p. {citation.page_number}</span>)}</div> : null}
      </>}
    </div>
  </div>
}
