import { useState } from 'react'
import './App.css'

export default function App() {
  const [repository, setRepository] = useState('')
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function submit(event) {
    event.preventDefault()
    if (loading) return
    setError('')
    if (!/^https:\/\/github\.com\/[\w.-]+\/[\w.-]+\/?$/.test(repository.trim())) {
      setError('https://github.com/owner/repo の形式で入力してください。')
      return
    }
    if (!question.trim()) { setError('質問を入力してください。'); return }
    const message = `リポジトリ: ${repository.trim()}\n質問: ${question.trim()}`
    if (message.length > 4000) { setError('URLと質問は合計4,000文字以内で入力してください。'); return }
    setLoading(true)
    setAnswer('')
    const controller = new AbortController()
    const timeout = setTimeout(() => controller.abort(), 310000)
    try {
      const response = await fetch('/api/chat', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }), signal: controller.signal,
      })
      const data = await response.json().catch(() => null)
      if (!response.ok) throw new Error(typeof data?.detail === 'string' ? data.detail : `送信に失敗しました（HTTP ${response.status}）。`)
      if (typeof data?.answer !== 'string' || !data.answer.trim()) throw new Error('回答を受け取れませんでした。もう一度お試しください。')
      setAnswer(data.answer)
    } catch (err) {
      setError(err.name === 'AbortError' ? '回答までに時間がかかっています。しばらくしてから再度お試しください。' : err instanceof TypeError ? 'サーバーに接続できません。接続先の起動状態を確認してください。' : err.message)
    } finally { clearTimeout(timeout); setLoading(false) }
  }

  return (
    <div className="app-shell">
      <header className="site-header">
        <a className="brand" href="./"><span className="brand-mark" aria-hidden="true">g.</span>GitLearn</a>
        <span className="badge">プロトタイプ</span>
      </header>
      <main>
        <section className="intro">
          <p className="eyebrow">コードを読む、最初の一歩。</p>
          <h1>リポジトリを、<br className="mobile-break" />一緒に読み解く。</h1>
          <p className="description">公開 GitHub リポジトリの URL と、知りたいことを入力してください。</p>
        </section>
        <form onSubmit={submit}>
          <label htmlFor="repository">GitHub リポジトリ URL</label>
          <input id="repository" type="url" placeholder="https://github.com/google/adk-python" value={repository} onChange={e => setRepository(e.target.value)} required disabled={loading} />
          <label htmlFor="question">知りたいこと</label>
          <textarea id="question" rows={4} placeholder="例：このリポジトリの構成と、最初に読むとよいファイルを教えてください。" value={question} onChange={e => setQuestion(e.target.value)} required disabled={loading} />
          <div className="form-footer"><p>質問ごとに新しい調査を行います。</p><button disabled={loading || !repository.trim() || !question.trim()}>{loading ? '調査中…' : '質問する'}<span aria-hidden="true">↗</span></button></div>
          {error && <p className="error" role="alert">{error}</p>}
        </form>
        <section className="answer-section" aria-labelledby="answer-title" aria-busy={loading}>
          <div className="answer-heading"><h2 id="answer-title">回答</h2><span>{loading ? '調査中' : answer ? '調査完了' : '入力待ち'}</span></div>
          <div aria-live="polite" aria-atomic="true">
            {loading ? <p className="empty"><span className="dot" aria-hidden="true" />リポジトリを調べています。回答まで数分かかる場合があります。</p> : answer ? <div className="answer-text">{answer}</div> : <p className="empty">ここに調査結果が表示されます。</p>}
          </div>
        </section>
      </main>
      <footer>AI の回答には誤りが含まれる場合があります。大切な内容は元のコードでも確認してください。</footer>
    </div>
  )
}
