"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Users } from "lucide-react"

export function SuspiciousBehaviorComponent() {
  const [suspiciousData, setSuspiciousData] = useState(null)

  useEffect(() => {
    // Simulating real-time data updates
    const interval = setInterval(() => {
      setSuspiciousData({
        count: Math.floor(Math.random() * 10),
        locations: ["North Gate", "South Entrance", "Main Hall"].slice(0, Math.floor(Math.random() * 3) + 1),
      })
    }, 3000)

    return () => clearInterval(interval)
  }, [])

  if (!suspiciousData) {
    return <div>Loading suspicious behavior data...</div>
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Users className="w-6 h-6 text-yellow-500" />
          <span>Suspicious Behavior</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <p className="text-lg font-semibold">Suspicious Activities Detected</p>
            <p className="text-3xl font-bold text-yellow-500">{suspiciousData.count}</p>
          </div>
          <div>
            <p className="text-lg font-semibold">Locations</p>
            <ul className="list-disc list-inside">
              {suspiciousData.locations.map((location, index) => (
                <li key={index} className="text-yellow-600">
                  {location}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

