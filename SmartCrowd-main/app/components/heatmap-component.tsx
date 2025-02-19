"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export function HeatmapComponent() {
  const [heatmapData, setHeatmapData] = useState(null)

  useEffect(() => {
    // Simulating data fetch
    setTimeout(() => {
      setHeatmapData([
        [1, 2, 3, 4, 5],
        [2, 3, 4, 5, 6],
        [3, 4, 5, 6, 7],
        [4, 5, 6, 7, 8],
        [5, 6, 7, 8, 9],
      ])
    }, 1000)
  }, [])

  if (!heatmapData) {
    return <div>Loading heatmap data...</div>
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Crowd Density Heatmap</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-5 gap-1">
          {heatmapData.map((row, i) =>
            row.map((value, j) => (
              <div
                key={`${i}-${j}`}
                className="w-12 h-12 rounded"
                style={{
                  backgroundColor: `rgba(255, 0, 0, ${value / 10})`,
                  transition: "background-color 0.5s ease",
                }}
              />
            )),
          )}
        </div>
      </CardContent>
    </Card>
  )
}

