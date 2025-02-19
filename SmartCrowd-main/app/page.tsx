import Link from "next/link"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { BarChart, Users, AlertTriangle, Footprints, UserMinus } from "lucide-react"

const features = [
  {
    name: "Heatmap Evaluation",
    icon: BarChart,
    href: "/heatmap",
    description: "Analyze crowd density and movement patterns",
  },
  {
    name: "Aggression Detection",
    icon: AlertTriangle,
    href: "/aggression",
    description: "Identify and monitor aggressive behavior",
  },
  {
    name: "Suspicious Behavior",
    icon: Users,
    href: "/suspicious",
    description: "Detect and analyze suspicious activities",
  },
  {
    name: "Stampede Detection",
    icon: Footprints,
    href: "/stampede",
    description: "Early warning system for potential stampedes",
  },
  {
    name: "Falls Detection",
    icon: UserMinus,
    href: "/falls",
    description: "Identify and respond to falling incidents",
  },
]

export default function Home() {
  return (
    <div className="space-y-6">
      <h1 className="text-4xl font-bold text-center mb-10">SmartCrowd Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {features.map((feature) => (
          <Link href={feature.href} key={feature.name}>
            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <feature.icon className="w-6 h-6" />
                  <span>{feature.name}</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p>{feature.description}</p>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}

