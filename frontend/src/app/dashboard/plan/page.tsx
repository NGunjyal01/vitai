'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ClipboardList } from 'lucide-react'

export default function PlanPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">My Plan</h1>
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <ClipboardList size={18} />
            Your Health Plan
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12">
            <ClipboardList size={40} className="text-gray-300 mx-auto mb-3" />
            <p className="text-sm font-medium text-gray-600">No plan yet</p>
            <p className="text-xs text-gray-400 mt-1">
              Upload a report and ask your coach to "make my plan"
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}