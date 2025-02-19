"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Footprints } from "lucide-react"

export function StampedeDetectionComponent() {
  const [stampedeData, setStampedeData] = useState(null)

  useEffect(() => {
    // Simulating real-time data updates
    const interval = setInterval(() => {
      setStampedeData({
        risk: Math.random(),
        crowdDensity: Math.floor(Math.random() * 100),
        flowRate: Math.floor(Math.random() * 50),
      })
    }, 2500)

    return () => clearInterval(interval)
  }, [])

  if (!stampedeData) {
    return <div>Loading stampede detection data...</div>
  }

  const getRiskColor = (risk) => {
    if (risk < 0.3) return "bg-green-500"
    if (risk < 0.7) return "bg-yellow-500"
    return "bg-red-500"
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Footprints className="w-6 h-6 text-blue-500" />
          <span>Stampede Detection</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <p className="text-lg font-semibold">Stampede Risk</p>
            <div className="flex items-center space-x-2">
              <div className={`w-4 h-4 rounded-full ${getRiskColor(stampedeData.risk)}`}></div>
              <p className="text-xl font-bold">{(stampedeData.risk * 100).toFixed(1)}%</p>
            </div>
          </div>
          <div>
            <p className="text-lg font-semibold">Crowd Density</p>
            <p className="text-2xl font-bold text-blue-600">{stampedeData.crowdDensity} people/m²</p>
          </div>
          <div>
            <p className="text-lg font-semibold">Flow Rate</p>
            <p className="text-2xl font-bold text-blue-600">{stampedeData.flowRate} people/min</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

