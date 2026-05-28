import type { Metadata } from "next";
import { Inter } from "next/font/google";
import localFont from "next/font/local";
import "./globals.css";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import ChalkboardFrame from "@/components/ChalkboardFrame";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const sparklyYarn = localFont({
  src: "../fonts/SparklyYarn.ttf",
  variable: "--font-chalk-title",
  display: "swap",
});

const pigment = localFont({
  src: "../fonts/Pigment.otf",
  variable: "--font-pigment",
  display: "swap",
});

const chalkSprouts = localFont({
  src: "../fonts/ChalkSprouts.ttf",
  variable: "--font-chalk-sprouts",
  display: "swap",
});

const chalkBoard = localFont({
  src: "../fonts/ChalkBoard.ttf",
  variable: "--font-chalk-board",
  display: "swap",
});

const aldenburg = localFont({
  src: "../fonts/Aldenburg.otf",
  variable: "--font-aldenburg",
  display: "swap",
});


export const metadata: Metadata = {
  title: "Eigenquestions",
  description: "Rank the most important questions in physics",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${sparklyYarn.variable} ${pigment.variable} ${chalkSprouts.variable} ${chalkBoard.variable} ${aldenburg.variable}`}
    >
      <body
        className={`${inter.className} min-h-screen flex flex-col`}
      >
        <ChalkboardFrame />
        <Navbar />
        {children}
        <Footer />
      </body>
    </html>
  );
}
