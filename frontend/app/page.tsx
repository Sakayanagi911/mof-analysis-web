"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { Upload, Activity, Database, ChevronRight, Loader2 } from 'lucide-react';
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";

export default function MOFScreening() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  
  // Data input dengan contoh angka (placeholder/default value)
  const [formData, setFormData] = useState({
    pv: "0.85", gsa: "1250", vsa: "1050", lcd: "12.4", pld: "7.2", vf: "0.65", density: "1150",
    metal_name: "Zr", linker_name: "BDC", reaction_time: "24", temperature: "120"
  });

  const runLiveAnalysis = useCallback(async () => {
    setLoading(true);
    const data = new FormData();
    if (file) data.append('file', file);
    Object.entries(formData).forEach(([key, val]) => data.append(key, val));

    try {
      const res = await fetch("http://127.0.0.1:8000/analyze", { 
        method: "POST", 
        body: data 
      });
      const result = await res.json();
      if (result.status === "success") setResults(result.results);
    } catch (err) {
      console.error("API Error");
    } finally {
      setTimeout(() => setLoading(false), 800);
    }
  }, [formData, file]);

  useEffect(() => {
    const isFileReady = file !== null;
    const isFormReady = Object.values(formData).every(val => val.trim() !== "");

    if (isFileReady && isFormReady) {
      const timer = setTimeout(() => runLiveAnalysis(), 800);
      return () => clearTimeout(timer);
    } else {
      setResults(null); 
    }
  }, [formData, file, runLiveAnalysis]);

  return (
    <div className="min-h-screen bg-[#F5F5F7] text-[#1D1D1F] font-sans antialiased">
      
      {/* HEADER */}
      <nav className="sticky top-0 z-50 w-full border-b border-[#D2D2D7]/30 bg-white/80 backdrop-blur-xl px-6 py-3">
        <div className="max-w-6xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-indigo-600 rounded-lg flex items-center justify-center">
              <Activity className="w-4 h-4 text-white" />
            </div>
            <span className="font-semibold tracking-tight text-lg italic">MOF<span className="text-indigo-600 font-black">Scan</span></span>
          </div>
          <div className="text-sm font-medium text-[#86868B]">v1.0.4 Research Edition</div>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto py-12 px-6 grid grid-cols-1 lg:grid-cols-12 gap-10">
        
        {/* PANEL KIRI: INPUT */}
        <section className="lg:col-span-5 space-y-8">
          <div className="bg-white/60 backdrop-blur-md rounded-[24px] border border-white p-8 shadow-sm space-y-8">
            <h2 className="text-xl font-semibold">Configuration</h2>
            
            {/* 01. UPLOAD CIF */}
            <div className="space-y-3">
              <p className="text-[11px] font-bold text-[#86868B] uppercase tracking-wider font-mono">01. Structure File</p>
              <div 
                className={`group border-2 border-dashed rounded-2xl p-8 text-center transition-all cursor-pointer ${file ? 'border-indigo-400 bg-indigo-50/30' : 'border-[#D2D2D7] hover:border-[#86868B]'}`}
                onClick={() => document.getElementById('cif-upload')?.click()}
              >
                <Upload className={`mx-auto w-10 h-10 mb-3 ${file ? 'text-indigo-600' : 'text-[#86868B]'}`} />
                <p className="text-sm font-medium">{file ? file.name : "Upload .cif file"}</p>
                <input id="cif-upload" type="file" className="hidden" accept=".cif" onChange={(e) => setFile(e.target.files?.[0] || null)} />
              </div>
            </div>

            {/* 02. PARAMETER MOF */}
            <div className="space-y-4 pt-4 border-t border-[#D2D2D7]/30">
              <p className="text-[11px] font-bold text-[#86868B] uppercase tracking-wider font-mono">02. Parameter MOF</p>
              <div className="grid grid-cols-2 gap-4">
                <InputCell label="PV" unit="cm³/g" val={formData.pv} k="pv" s={setFormData} d={formData} />
                <InputCell label="GSA" unit="m²/g" val={formData.gsa} k="gsa" s={setFormData} d={formData} />
                <InputCell label="VSA" unit="m²/m³" val={formData.vsa} k="vsa" s={setFormData} d={formData} />
                <InputCell label="LCD" unit="Å" val={formData.lcd} k="lcd" s={setFormData} d={formData} />
                <InputCell label="PLD" unit="Å" val={formData.pld} k="pld" s={setFormData} d={formData} />
                <InputCell label="VF" unit="φ" val={formData.vf} k="vf" s={setFormData} d={formData} />
                <InputCell label="Density" unit="kg/m³" val={formData.density} k="density" s={setFormData} d={formData} />
              </div>
            </div>

            {/* 03. DATA SINTESIS */}
            <div className="space-y-4 pt-4 border-t border-[#D2D2D7]/30">
              <p className="text-[11px] font-bold text-[#86868B] uppercase tracking-wider font-mono">03. Synthesis Condition</p>
              <div className="grid grid-cols-2 gap-4">
                <InputCell label="Metal" unit="Sym" val={formData.metal_name} k="metal_name" s={setFormData} d={formData} />
                <InputCell label="Linker" unit="Name" val={formData.linker_name} k="linker_name" s={setFormData} d={formData} />
                <InputCell label="Time (t)" unit="h" val={formData.reaction_time} k="reaction_time" s={setFormData} d={formData} />
                <InputCell label="Temp (T)" unit="°C" val={formData.temperature} k="temperature" s={setFormData} d={formData} />
              </div>
            </div>
          </div>
        </section>

        {/* PANEL KANAN: OUTPUT */}
        <section className="lg:col-span-7 relative">
          <div className="bg-white rounded-[24px] p-10 border border-[#D2D2D7]/20 shadow-sm min-h-[500px] overflow-hidden sticky top-28 flex flex-col">
            
            {/* Header Status Tetap Ada */}
            <div className="flex justify-between items-start mb-12">
              <div className="space-y-2">
                <h3 className="text-[13px] font-bold text-[#86868B] uppercase tracking-[0.2em]">Live Analysis Results</h3>
                
                {/* Logika Teks Berubah */}
                <div className="flex items-center gap-3">
                  <h1 className={`text-6xl font-bold tracking-tighter transition-colors duration-500 ${results?.is_feasible ? 'text-[#0071E3]' : results ? 'text-[#FF3B30]' : 'text-[#D2D2D7]'}`}>
                    {loading ? "Analyzing..." : results ? (results.is_feasible ? "Feasible." : "Denied.") : "Pending."}
                  </h1>
                  {loading && <Loader2 className="w-8 h-8 text-indigo-600 animate-spin mt-2" />}
                </div>
              </div>
              {results && (
                <Badge className={`rounded-full px-5 py-2 text-xs font-semibold ${results.is_feasible ? 'bg-[#34C759] text-white' : 'bg-[#FF3B30] text-white'}`}>
                  {results.stability_status}
                </Badge>
              )}
            </div>

            {/* Konten Utama */}
            {results ? (
              <div className="space-y-10 animate-in fade-in duration-700">
                <div className="w-full overflow-hidden rounded-[20px] border border-[#D2D2D7]/30 bg-[#F5F5F7]/30">
                  <table className="w-full text-left">
                    <thead>
                      <tr className="bg-[#F5F5F7]/80 text-[10px] uppercase font-bold text-[#86868B]">
                        <th className="px-6 py-4">Metric</th>
                        <th className="px-6 py-4">Score</th>
                        <th className="px-6 py-4 text-right">Standard</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#D2D2D7]/30 text-sm">
                      <Row label="Gravimetric H₂" val={results.gravimetric_h2} u="wt%" t="≥ 5.5" ok={results.gravimetric_h2 >= 5.5} />
                      <Row label="Volumetric H₂" val={results.volumetric_h2} u="g/L" t="≥ 40" ok={results.volumetric_h2 >= 40} />
                      <Row label="Synthesis Cost" val={results.mof_cost_usd_kg} u="$/kg" t="≤ 30" ok={results.mof_cost_usd_kg <= 30} />
                      <Row label="Stability (ΔE)" val="4.20" u="kJ/mol" t="< 5.0" ok={true} />
                    </tbody>
                  </table>
                </div>

                <div className="p-6 bg-[#1D1D1F] rounded-[20px] text-white flex justify-between items-center group cursor-pointer hover:bg-black transition-all">
                  <div className="flex items-center gap-4">
                    <div className="p-3 bg-white/10 rounded-xl"><Database className="w-5 h-5 text-indigo-400" /></div>
                    <p className="font-bold text-lg">Launch 3D Visualizer</p>
                  </div>
                  <ChevronRight className="w-6 h-6 group-hover:translate-x-1 transition-transform text-zinc-500" />
                </div>
              </div>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center text-[#86868B] space-y-6 opacity-40">
                <Activity className={`w-12 h-12 ${loading ? 'hidden' : 'animate-pulse'}`} />
                <div className="text-center space-y-2 max-w-[280px]">
                  <p className="text-sm font-semibold uppercase tracking-widest leading-relaxed">
                    {loading ? "Processing Molecular Data" : "Waiting for Complete Parameters"}
                  </p>
                  {!loading && <p className="text-[10px] normal-case tracking-normal">Please upload .cif file and fill all configuration fields to start screening.</p>}
                </div>
              </div>
            )}
            
            <p className="mt-auto text-center text-[#86868B] text-[10px] pt-8 border-t border-[#D2D2D7]/20">
              Computed via Pendidikan Teknologi Informasi MOF-Scan Framework
            </p>
          </div>
        </section>
      </main>
    </div>
  );
}

function InputCell({ label, unit, val, k, s, d }: any) {
  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center px-1 text-[#86868B]">
        <Label className="text-[11px] font-semibold capitalize">{label}</Label>
        <span className="text-[9px] font-mono opacity-60">{unit}</span>
      </div>
      <Input 
        value={val} 
        onChange={(e) => s({...d, [k]: e.target.value})}
        className="rounded-xl border-[#D2D2D7] bg-[#F5F5F7]/50 focus-visible:ring-indigo-600 h-11 text-sm shadow-none"
      />
    </div>
  );
}

function Row({ label, val, u, t, ok }: any) {
  return (
    <tr className="hover:bg-white/50 transition-colors">
      <td className="px-6 py-5 font-semibold text-[#424245]">{label}</td>
      <td className="px-6 py-5"><span className="font-bold text-[#1D1D1F]">{val}</span> <span className="text-[10px] text-[#86868B] font-mono">{u}</span></td>
      <td className={`px-6 py-5 text-right font-mono text-[11px] ${ok ? 'text-[#34C759]' : 'text-[#FF3B30]'}`}>{t}</td>
    </tr>
  );
}