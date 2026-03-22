'use client'

import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase/client'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Upload, FileText } from 'lucide-react'

export default function DashboardPage() {
  const [user, setUser] = useState<any>(null)
  const [score, setScore] = useState<number | null>(null)
  const [reports, setReports] = useState<any[]>([])
  const [uploading, setUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState('')
  const supabase = createClient()
  const router = useRouter()
  const API_URL = process.env.NEXT_PUBLIC_API_URL

  useEffect(() => {
    const init = async () => {
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) { router.push('/login'); return }
      setUser(user)
      fetchScore(user.id)
      fetchReports(user.id)
    }
    init()
  }, [])

  const fetchScore = async (userId: string) => {
    try {
      const res = await fetch(`${API_URL}/api/score/${userId}`)
      const data = await res.json()
      if (data.score) setScore(data.score)
    } catch (e) {}
  }

  const fetchReports = async (userId: string) => {
    const { data } = await supabase
      .from('reports')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false })
    if (data) setReports(data)
  }

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file || !user) return

    setUploading(true)
    setUploadStatus('Uploading...')

    const formData = new FormData()
    formData.append('file', file)
    formData.append('user_id', user.id)

    try {
      const res = await fetch(`${API_URL}/api/reports`, {
        method: 'POST',
        body: formData,
      })
      const data = await res.json()

      setUploadStatus('Processing your report...')

      const poll = setInterval(async () => {
        const statusRes = await fetch(`${API_URL}/api/reports/${data.report_id}`)
        const statusData = await statusRes.json()

        if (statusData.status === 'processed') {
          clearInterval(poll)
          setUploadStatus('Done!')
          fetchReports(user.id)
          fetchScore(user.id)
          setTimeout(() => {
            setUploadStatus('')
            setUploading(false)
          }, 3000)
        } else if (statusData.status === 'failed') {
          clearInterval(poll)
          setUploadStatus('Failed — try another PDF')
          setUploading(false)
        }
      }, 3000)

    } catch (e) {
      setUploadStatus('Upload failed — is the backend running?')
      setUploading(false)
    }
  }

  const processedReports = reports.filter(r => r.status === 'processed')

  const getScoreColor = (score: number) => {
    if (score >= 70) return '#22c55e'
    if (score >= 50) return '#f59e0b'
    return '#ef4444'
  }

  const getScoreBadge = (score: number) => {
    if (score >= 70) return 'bg-green-100 text-green-700'
    if (score >= 50) return 'bg-yellow-100 text-yellow-700'
    return 'bg-red-100 text-red-700'
  }

  const getScoreLabel = (score: number) => {
    if (score >= 70) return 'Good'
    if (score >= 50) return 'Fair'
    return 'Needs attention'
  }

  if (!user) return (
    <div className="flex items-center justify-center h-64">
      <div className="text-gray-500">Loading...</div>
    </div>
  )

  return (
    <div className="max-w-4xl mx-auto space-y-6">

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-sm text-gray-500">Welcome back, {user.email}</p>
        </div>
      </div>

      {/* Health Score */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-6">
            <div className="relative w-28 h-28 shrink-0">
              <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
                <circle
                  cx="50" cy="50" r="40"
                  fill="none"
                  stroke="#e5e7eb"
                  strokeWidth="10"
                />
                <circle
                  cx="50" cy="50" r="40"
                  fill="none"
                  stroke={score ? getScoreColor(score) : '#e5e7eb'}
                  strokeWidth="10"
                  strokeDasharray={`${(score || 0) * 2.51} 251`}
                  strokeLinecap="round"
                  className="transition-all duration-700"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-2xl font-bold text-gray-900">
                  {score || '--'}
                </span>
              </div>
            </div>
            <div className="space-y-1">
              <h2 className="text-lg font-semibold text-gray-900">Health Score</h2>
              <p className="text-sm text-gray-500">
                {processedReports.length > 0
                  ? `Based on ${processedReports.length} report${processedReports.length !== 1 ? 's' : ''}`
                  : 'Upload a report to get your score'}
              </p>
              {score && (
                <Badge className={getScoreBadge(score)}>
                  {getScoreLabel(score)}
                </Badge>
              )}
              {!score && (
                <p className="text-xs text-gray-400">
                  Your score will appear here after your first upload
                </p>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Upload */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Upload size={18} />
            Upload Blood Test Report
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-xs text-gray-500 mb-4">
            🔒 Your data is encrypted and never sold. Delete it anytime in settings.
          </p>
          <label className={`
            flex flex-col items-center justify-center w-full h-36
            border-2 border-dashed rounded-xl cursor-pointer transition-colors
            ${uploading
              ? 'border-blue-300 bg-blue-50 cursor-not-allowed'
              : 'border-gray-300 hover:border-blue-400 hover:bg-blue-50'
            }
          `}>
            <Upload size={28} className={`mb-2 ${uploading ? 'text-blue-400' : 'text-gray-400'}`} />
            <span className={`text-sm font-medium ${uploading ? 'text-blue-600' : 'text-gray-500'}`}>
              {uploadStatus || 'Click to upload PDF'}
            </span>
            {!uploading && (
              <span className="text-xs text-gray-400 mt-1">
                Blood test, CBC, lipid panel, thyroid — any lab report
              </span>
            )}
            <input
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={handleUpload}
              disabled={uploading}
            />
          </label>
        </CardContent>
      </Card>

      {/* Reports timeline */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <FileText size={18} />
            Reports
            {reports.length > 0 && (
              <Badge className="bg-gray-100 text-gray-600 ml-auto">
                {reports.length}
              </Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {reports.length === 0 ? (
            <div className="text-center py-8">
              <FileText size={32} className="text-gray-300 mx-auto mb-2" />
              <p className="text-sm text-gray-500">
                No reports yet — upload your first blood test above
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {reports.map((report) => (
                <div
                  key={report.id}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
                >
                  <div className="space-y-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {report.file_name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {report.report_date
                        ? new Date(report.report_date).toLocaleDateString('en-IN', {
                            day: 'numeric', month: 'short', year: 'numeric'
                          })
                        : 'Date unknown'}
                      {report.source_lab && ` · ${report.source_lab}`}
                      {report.report_type && ` · ${report.report_type}`}
                    </p>
                  </div>
                  <Badge className={`shrink-0 ml-4 ${
                    report.status === 'processed'
                      ? 'bg-green-100 text-green-700'
                      : report.status === 'failed'
                      ? 'bg-red-100 text-red-700'
                      : 'bg-yellow-100 text-yellow-700'
                  }`}>
                    {report.status}
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

    </div>
  )
}