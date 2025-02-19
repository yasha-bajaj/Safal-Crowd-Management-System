import Link from "next/link"
import { BarChart, Users, AlertTriangle, Footprints, UserMinus, Home } from "lucide-react"

const navItems = [
  { name: "Dashboard", icon: Home, href: "/" },
  { name: "Heatmap", icon: BarChart, href: "/heatmap" },
  { name: "Aggression", icon: AlertTriangle, href: "/aggression" },
  { name: "Suspicious", icon: Users, href: "/suspicious" },
  { name: "Stampede", icon: Footprints, href: "/stampede" },
  { name: "Falls", icon: UserMinus, href: "/falls" },
]

export function Sidebar() {
  return (
    <nav className="w-64 bg-white shadow-lg">
      <div className="p-4">
        <h1 className="text-2xl font-bold text-indigo-600">SmartCrowd</h1>
      </div>
      <ul className="space-y-2 p-4">
        {navItems.map((item) => (
          <li key={item.name}>
            <Link
              href={item.href}
              className="flex items-center space-x-2 text-gray-700 hover:text-indigo-600 hover:bg-indigo-50 rounded p-2 transition-colors"
            >
              <item.icon className="w-5 h-5" />
              <span>{item.name}</span>
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  )
}

