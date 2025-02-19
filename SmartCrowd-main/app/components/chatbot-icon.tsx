"use client"

import { useState } from "react"
import { MessageCircle } from "lucide-react"
import { Button } from "@/components/ui/button"

export function ChatbotIcon() {
  const [isOpen, setIsOpen] = useState(false)

  const toggleChatbot = () => {
    setIsOpen(!isOpen)
  }

  return (
    <div className="fixed bottom-4 right-4">
      <Button
        onClick={toggleChatbot}
        className="rounded-full w-12 h-12 flex items-center justify-center bg-primary text-primary-foreground"
      >
        <MessageCircle className="w-6 h-6" />
      </Button>
      {isOpen && (
        <div className="absolute bottom-16 right-0 w-80 h-96 bg-white rounded-lg shadow-lg p-4">
          {/* Add your chatbot interface here */}
          <p>Chatbot interface goes here</p>
        </div>
      )}
    </div>
  )
}

