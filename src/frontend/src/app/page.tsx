"use client";

import { useState } from "react";
import { Loader } from "@/components/Loader";
import { NavBar } from "@/components/NavBar";
import { Hero } from "@/components/Hero";
import { HowItWorks } from "@/components/HowItWorks";
import { Agents } from "@/components/Agents";
import { Impact } from "@/components/Impact";
import { CtaFooter } from "@/components/CtaFooter";

export default function Home() {
  const [loaded, setLoaded] = useState(false);

  return (
    <>
      <Loader onComplete={() => setLoaded(true)} />
      <div
        className={`relative z-10 transition-opacity duration-700 ${
          loaded ? "opacity-100" : "opacity-0"
        }`}
      >
        <NavBar />
        <main>
          <Hero />
          <HowItWorks />
          <Agents />
          <Impact />
        </main>
        <CtaFooter />
      </div>
    </>
  );
}
