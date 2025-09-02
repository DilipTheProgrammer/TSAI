import type React from "react"
import type { Metadata } from "next"
import { DM_Sans } from "next/font/google"
import { Space_Grotesk } from "next/font/google"
import { GeistMono } from "geist/font/mono"
import "./globals.css"

const dmSans = DM_Sans({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-dm-sans",
})

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-space-grotesk",
})

export const metadata: Metadata = {
  title: "ClinicalBERT AI Dashboard",
  description:
    "Healthcare AI Dashboard for ClinicalBERT API - Readmission Prediction, Entity Extraction, and Clinical Search",
  generator: "v0.app",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={`font-sans ${dmSans.variable} ${spaceGrotesk.variable} ${GeistMono.variable}`}>{children}</body>
    </html>
  )
}
