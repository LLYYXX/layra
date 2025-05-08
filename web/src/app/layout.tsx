import type { Metadata } from "next";
import "./globals.css";

// 不使用Google Fonts，改用系统字体
// import { Inter } from "next/font/google";
// const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "LAYRA",
  description: "LAYRA: Towards Visual-Driven Intelligent RAG",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="font-sans">
        <div className="">
          {/* <CityBackground /> */}
        </div>
        <div className="absolute w-full h-full top-0 left-0">{children}</div>
      </body>
    </html>
  );
}
