"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { UserMinus } from "lucide-react"

export function FallsDetectionComponent() {
  const [fallsData, setFallsData] = useState(null)

  useEffect(() => {
    // Simulating real-time data updates
    const interval = setInterval(() => {
      setFallsData({
        fallsDetected: Math.floor(Math.random() * 3),
        locations: ["Main Hall", "Entrance", "Staircase"].slice(0, Math.floor(Math.random() * 3) + 1),
        lastDetection: new Date().toLocaleTimeString(),
      })
    }, 4000)

    return () => clearInterval(interval)
  }, [])

  if (!fallsData) {
    return <div>Loading falls detection data...</div>
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <UserMinus className="w-6 h-6 text-purple-500" />
          <span>Falls Detection</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <p className="text-lg font-semibold">Falls Detected</p>
            <p className="text-3xl font-bold text-purple-500">{fallsData.fallsDetected}</p>
          </div>
          <div>
            <p className="text-lg font-semibold">Locations</p>
            <ul className="list-disc list-inside">
              {fallsData.locations.map((location, index) => (
                <li key={index} className="text-purple-600">
                  {location}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <p className="text-lg font-semibold">Last Detection</p>
            <p className="text-xl font-bold text-purple-500">{fallsData.lastDetection}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

