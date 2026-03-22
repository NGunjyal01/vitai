'use client'

import { useState, useEffect } from 'react'
import { createClient } from '@/lib/supabase/client'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { BookOpen, Check } from 'lucide-react'

const SYMPTOMS = ['Fatigue', 'Headache', 'Brain fog', 'Bloating', 'Poor sleep', 'Joint pain']

export default function JournalPage() {
  const [user, setUser] = useState<any>(null)
  const [energy, setEnergy] = useState(3)
  const [mood, setMood] = useState(3)
  const [selectedSymptoms, setSelectedSymptoms] = useState<string[]>([])
  const [notes, setNotes] = useState('')
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [todayLog, setTodayLog] = useState<any>(null)
  const [pastLogs, setPastLogs] = useState<any[]>([])
  const supabase = createClient()
  const router = useRouter()

  useEffect(() => {
    const init = async () => {
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) { router.push('/login'); return }
      setUser(user)
      fetchLogs(user.id)
    }
    init()
  }, [])

  const fetchLogs = async (userId: string) => {
    const { data } = await supabase
      .from('symptom_logs')
      .select('*')
      .eq('user_id', userId)
      .order('logged_date', { ascending: false })
      .limit(7)

    if (data && data.length > 0) {
      setPastLogs(data)
      const today = new Date().toISOString().split('T')[0]
      const todayEntry = data.find(d => d.logged_date === today)
      if (todayEntry) {
        setTodayLog(todayEntry)
        setEnergy(todayEntry.energy_level)
        setMood(todayEntry.mood)
        setSelectedSymptoms(todayEntry.symptoms || [])
        setNotes(todayEntry.notes || '')
      }
    }
  }

  const toggleSymptom = (symptom: string) => {
    setSelectedSymptoms(prev =>
      prev.includes(symptom)
        ? prev.filter(s => s !== symptom)
        : [...prev, symptom]
    )
  }

  const handleSave = async () => {
    if (!user) return
    setSaving(true)

    const today = new Date().toISOString().split('T')[0]
    const payload = {
      user_id: user.id,
      logged_date: today,
      energy_level: energy,
      mood: mood,
      symptoms: selectedSymptoms,
      notes: notes,
    }

    const { error } = await supabase
      .from('symptom_logs')
      .upsert(payload, { onConflict: 'user_id,logged_date' })

    setSaving(false)
    if (!error) {
      setSaved(true)
      fetchLogs(user.id)
      setTimeout(() => setSaved(false), 2000)
    }
  }

  const getEnergyLabel = (val: number) => {
    return ['', 'Exhausted', 'Tired', 'Okay', 'Good', 'Energized'][val]
  }

  const getMoodLabel = (val: number) => {
    return ['', 'Very low', 'Low', 'Okay', 'Good', 'Great'][val]
  }

  if (!user) return <div>Loading...</div>

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Journal</h1>

      {/* Today's check-in */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <BookOpen size={18} />
            Today's Check-in
            {todayLog && (
              <span className="ml-auto text-xs text-green-600 font-normal flex items-center gap-1">
                <Check size={12} /> Already logged today
              </span>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">

          {/* Energy */}
          <div>
            <div className="flex justify-between mb-2">
              <label className="text-sm font-medium text-gray-700">Energy level</label>
              <span className="text-sm text-blue-600 font-medium">{getEnergyLabel(energy)}</span>
            </div>
            <input
              type="range" min={1} max={5} value={energy}
              onChange={e => setEnergy(Number(e.target.value))}
              className="w-full accent-blue-600"
            />
            <div className="flex justify-between text-xs text-gray-400 mt-1">
              <span>1</span><span>2</span><span>3</span><span>4</span><span>5</span>
            </div>
          </div>

          {/* Mood */}
          <div>
            <div className="flex justify-between mb-2">
              <label className="text-sm font-medium text-gray-700">Mood</label>
              <span className="text-sm text-blue-600 font-medium">{getMoodLabel(mood)}</span>
            </div>
            <input
              type="range" min={1} max={5} value={mood}
              onChange={e => setMood(Number(e.target.value))}
              className="w-full accent-blue-600"
            />
            <div className="flex justify-between text-xs text-gray-400 mt-1">
              <span>1</span><span>2</span><span>3</span><span>4</span><span>5</span>
            </div>
          </div>

          {/* Symptoms */}
          <div>
            <label className="text-sm font-medium text-gray-700 block mb-2">
              Symptoms today
            </label>
            <div className="flex flex-wrap gap-2">
              {SYMPTOMS.map(s => (
                <button
                  key={s}
                  onClick={() => toggleSymptom(s)}
                  className={`px-3 py-1 text-xs rounded-full border transition-colors ${
                    selectedSymptoms.includes(s)
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-gray-300 text-gray-600 hover:border-blue-400'
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          {/* Notes */}
          <div>
            <label className="text-sm font-medium text-gray-700 block mb-2">
              Notes
            </label>
            <textarea
              value={notes}
              onChange={e => setNotes(e.target.value)}
              placeholder="How are you feeling today?"
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:border-blue-400 resize-none"
              rows={3}
            />
          </div>

          <button
            onClick={handleSave}
            disabled={saving}
            className="w-full py-2.5 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {saving ? 'Saving...' : saved ? '✓ Saved!' : 'Save check-in'}
          </button>
        </CardContent>
      </Card>

      {/* Past logs */}
      {pastLogs.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Past 7 days</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {pastLogs.map(log => (
                <div key={log.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {new Date(log.logged_date).toLocaleDateString('en-IN', {
                        weekday: 'short', day: 'numeric', month: 'short'
                      })}
                    </p>
                    {log.symptoms?.length > 0 && (
                      <p className="text-xs text-gray-500 mt-0.5">
                        {log.symptoms.join(', ')}
                      </p>
                    )}
                  </div>
                  <div className="flex gap-3 text-xs text-gray-500">
                    <span>⚡ {log.energy_level}/5</span>
                    <span>😊 {log.mood}/5</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}