import type { Metadata } from "next";
import "../styles/globals.css";
import { Toaster } from "@/components/ui/sonner";

export const metadata: Metadata = {
  title: "intigriti",
  description: "Global bug bounty platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <main>{children}</main>
        <Toaster />
      </body>
    </html>
  );
}
