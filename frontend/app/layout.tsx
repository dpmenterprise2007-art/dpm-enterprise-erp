import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DPM ENTERPRISE ERP",
  description: "Billing, accounting and project management for DPM ENTERPRISE PRIVATE LIMITED.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
