import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { ChatbotIcon } from "./components/chatbot-icon"
import { Sidebar } from "./components/sidebar"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "SmartCrowd | Advanced Crowd Management",
  description: "Intelligent crowd monitoring and management system",
    generator: 'v0.dev'
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="flex h-screen bg-gradient-to-br from-blue-100 to-indigo-100">
          <Sidebar />
          <main className="flex-1 p-8 overflow-auto">{children}</main>
        </div>
        <ChatbotIcon />
      </body>
    </html>
  )
}



import './globals.css'