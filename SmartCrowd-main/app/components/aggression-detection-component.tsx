"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { AlertTriangle } from "lucide-react"

export function AggressionDetectionComponent() {
  const [aggressionData, setAggressionData] = useState(null)

  useEffect(() => {
    // Simulating real-time data updates
    const interval = setInterval(() => {
      setAggressionData({
        level: Math.floor(Math.random() * 100),
        incidents: Math.floor(Math.random() * 5),
      })
    }, 2000)

    return () => clearInterval(interval)
  }, [])

  if (!aggressionData) {
    return <div>Loading aggression detection data...</div>
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <AlertTriangle className="w-6 h-6 text-red-500" />
          <span>Aggression Detection</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <p className="text-lg font-semibold">Aggression Level</p>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div
                className="bg-red-600 h-2.5 rounded-full transition-all duration-500 ease-in-out"
                style={{ width: `${aggressionData.level}%` }}
              ></div>
            </div>
          </div>
          <div>
            <p className="text-lg font-semibold">Recent Incidents</p>
            <p className="text-3xl font-bold text-red-500">{aggressionData.incidents}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

