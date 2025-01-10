import { Features } from './about/Features';
import { Hero } from './about/Hero';
import { HowItWorks } from './about/HowItWorks';

export default function About() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Hero />
      <Features />
      <HowItWorks />
    </div>
  );
}