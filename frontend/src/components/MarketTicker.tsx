export default function MarketTicker() {
  return (
    <div className="w-full overflow-hidden bg-surface-container-highest border-b border-outline-variant py-1">
      <div className="whitespace-nowrap animate-marquee flex space-x-12 font-mono text-xs text-secondary">
        <span className="flex items-center gap-1">NIFTY 50 <span className="text-primary">▲ 0.45%</span></span>
        <span className="flex items-center gap-1">SENSEX <span className="text-red-500">▼ 0.12%</span></span>
        <span className="flex items-center gap-1">BANK NIFTY <span className="text-primary">▲ 1.20%</span></span>
        <span className="flex items-center gap-1">NIFTY IT <span className="text-primary">▲ 0.85%</span></span>
        
        {/* Duplicate for seamless looping */}
        <span className="flex items-center gap-1">NIFTY 50 <span className="text-primary">▲ 0.45%</span></span>
        <span className="flex items-center gap-1">SENSEX <span className="text-red-500">▼ 0.12%</span></span>
        <span className="flex items-center gap-1">BANK NIFTY <span className="text-primary">▲ 1.20%</span></span>
        <span className="flex items-center gap-1">NIFTY IT <span className="text-primary">▲ 0.85%</span></span>
      </div>
    </div>
  );
}
