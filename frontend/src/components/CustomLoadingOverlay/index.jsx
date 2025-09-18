import { useEffect, useState } from 'react'

export default function CustomLoadingOverlay({ visible, initial=5, onDone }) {
  const [progress, setProgress] = useState(initial)
  const [stage, setStage] = useState('Analyzing Your Document')

  useEffect(() => {
    if (!visible) return
    let mounted = true
    let timer
    const tick = () => {
      setProgress(prev => {
        const next = Math.min(prev + Math.random() * 8, 95)
        return next
      })
      timer = setTimeout(tick, 300)
    }
    tick()
    return () => { mounted = false; clearTimeout(timer) }
  }, [visible])

  useEffect(() => {
    if (progress > 70) setStage('Finalizing analysis report...')
  }, [progress])

  if (!visible) return null

  return (
    <div style={styles.backdrop}>
      <div style={styles.card}>
        <div style={styles.circleWrap}>
          <div style={{...styles.circle, background: `conic-gradient(#667eea ${progress*3.6}deg, #e5e7eb 0deg)`}} />
          <div style={styles.circleInner}>
            <div style={styles.percent}>{Math.round(progress)}%</div>
          </div>
        </div>
        <h2 style={styles.title}>Analyzing Your Document</h2>
        <p style={styles.subtitle}>{stage}</p>
        <div style={styles.hint}><i className="fas fa-clock" style={{marginRight:8}}></i> This usually takes 30-60 seconds</div>
      </div>
    </div>
  )
}

const styles = {
  backdrop: {
    position: 'fixed', inset: 0, background: 'rgba(250,253,255,0.8)', backdropFilter: 'blur(2px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999
  },
  card: {
    width: 420, maxWidth: '90%', background: '#fff', borderRadius: 16, boxShadow: '0 10px 40px rgba(0,0,0,0.1)', padding: 32, textAlign: 'center'
  },
  circleWrap: { position: 'relative', width: 120, height: 120, margin: '0 auto 20px' },
  circle: { width: '100%', height: '100%', borderRadius: '50%' },
  circleInner: { position: 'absolute', inset: 10, background: '#fff', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: 'inset 0 0 0 1px #eee' },
  percent: { fontSize: 22, fontWeight: 700, color: '#111' },
  title: { margin: '12px 0 6px', fontSize: 20 },
  subtitle: { margin: 0, color: '#666' },
  hint: { marginTop: 12, color: '#888', fontSize: 12 }
}


