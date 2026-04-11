"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { Upload, Activity, Database, ShieldCheck, ChevronRight, Loader2, CheckCircle2, XCircle, FlaskConical, DollarSign } from 'lucide-react';
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";

export default function MOFScreening() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  
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
      const res = await fetch("http://127.0.0.1:8000/analyze", { method: "POST", body: data });
      const result = await res.json();
      if (result.status === "success") setResults(result.results);
    } catch (err) { console.error("Error connecting to API"); }
    finally { setTimeout(() => setLoading(false), 800); }
  }, [formData, file]);

  useEffect(() => {
    if (file && Object.values(formData).every(val => val.trim() !== "")) {
      const timer = setTimeout(() => runLiveAnalysis(), 800);
      return () => clearTimeout(timer);
    } else { setResults(null); }
  }, [formData, file, runLiveAnalysis]);

  return (
    <div className="min-h-screen bg-[#F5F5F7] text-[#1D1D1F] font-sans antialiased selection:bg-indigo-100">
      <nav className="sticky top-0 z-50 w-full border-b border-[#D2D2D7]/30 bg-white/80 backdrop-blur-xl px-6 py-3">
        <div className="max-w-7xl mx-auto flex justify-between items-center italic font-semibold">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-indigo-600" />
            <span>MOF<span className="text-indigo-600">Scan</span></span>
          </div>
          <div className="text-[10px] text-[#86868B] uppercase tracking-widest font-bold">Research Dashboard</div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-12 px-6 grid grid-cols-1 lg:grid-cols-12 gap-10 text-left">
        
        {/* PANEL KIRI: INPUT */}
        <section className="lg:col-span-4 space-y-6">
          <div className="bg-white/70 backdrop-blur-md rounded-[28px] border border-white p-8 shadow-sm space-y-8">
            <h2 className="text-lg font-bold">Input Configuration</h2>
            
            <div className="space-y-6">
              <SectionTitle num="01" text="Upload CIF File" />
              <div 
                className={`group border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-all ${file ? 'border-indigo-400 bg-indigo-50/30' : 'border-[#D2D2D7]'}`}
                onClick={() => document.getElementById('cif-upload')?.click()}
              >
                <Upload className={`mx-auto w-6 h-6 mb-2 ${file ? 'text-indigo-600' : 'text-[#86868B]'}`} />
                <p className="text-xs font-semibold">{file ? file.name : "Select structure file"}</p>
                <input id="cif-upload" type="file" className="hidden" accept=".cif" onChange={(e) => setFile(e.target.files?.[0] || null)} />
              </div>

              <SectionTitle num="02" text="MOF Parameters" />
              <div className="grid grid-cols-2 gap-3">
                {['pv', 'gsa', 'vsa', 'lcd', 'pld', 'vf', 'density'].map((p) => (
                  <InputCell key={p} label={p.toUpperCase()} val={(formData as any)[p]} k={p} s={setFormData} d={formData} />
                ))}
              </div>

              <SectionTitle num="03" text="Synthesis Data" />
              <div className="grid grid-cols-2 gap-3">
                <InputCell label="Metal" val={formData.metal_name} k="metal_name" s={setFormData} d={formData} />
                <InputCell label="Linker" val={formData.linker_name} k="linker_name" s={setFormData} d={formData} />
                <InputCell label="Time (h)" val={formData.reaction_time} k="reaction_time" s={setFormData} d={formData} />
                <InputCell label="Temp (°C)" val={formData.temperature} k="temperature" s={setFormData} d={formData} />
              </div>
            </div>
          </div>
        </section>

        {/* PANEL KANAN: OUTPUT */}
        <section className="lg:col-span-8 relative">
          <div className="bg-white rounded-[32px] p-10 border border-[#D2D2D7]/20 shadow-sm sticky top-28 space-y-10 min-h-[600px]">
            {loading && <div className="absolute top-0 left-0 w-full h-1 bg-indigo-600 animate-pulse" />}
            
            <header className="flex justify-between items-center">
              <div>
                <h3 className="text-[10px] font-black text-[#86868B] uppercase tracking-[0.2em]">Screening Summary</h3>
                <h1 className={`text-5xl font-bold tracking-tighter ${results ? (results.is_overall_feasible ? 'text-[#0071E3]' : 'text-[#FF3B30]') : 'text-[#D2D2D7]'}`}>
                  {loading ? "Analyzing..." : results ? (results.is_overall_feasible ? "Feasible." : "Denied.") : "Pending."}
                </h1>
              </div>
              {results && <Badge className="bg-[#1D1D1F] text-white rounded-full px-4 py-1 text-[10px]">{results.stability_status}</Badge>}
            </header>

            {results ? (
              <div className="space-y-8 animate-in fade-in duration-500">
                {/* 1. HYDROGEN WORKING CAPACITY (DOE TARGET) */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h4 className="text-[11px] font-bold text-[#86868B] uppercase flex items-center gap-2"><Database className="w-4 h-4" /> 1. Hydrogen Working Capacity</h4>
                    <FeasibleBadge status={results.doe_feasible} />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <ResultBox label="Gravimetric" val={results.gravimetric_h2} unit="wt%" target="≥ 5.5" ok={results.gravimetric_h2 >= 5.5} />
                    <ResultBox label="Volumetric" val={results.volumetric_h2} unit="g/L" target="≥ 40" ok={results.volumetric_h2 >= 40} />
                  </div>
                </div>

                {/* 2. ECONOMIC ANALYSIS */}
                <div className="space-y-4 pt-6 border-t border-[#D2D2D7]/30">
                  <div className="flex items-center justify-between">
                    <h4 className="text-[11px] font-bold text-[#86868B] uppercase flex items-center gap-2"><DollarSign className="w-4 h-4" /> 2. Economic Analysis</h4>
                    <FeasibleBadge status={results.econ_feasible} />
                  </div>
                  <div className="grid grid-cols-4 gap-4 text-center">
                    <EconStat label="MOF Cost" val={`$${results.mof_cost}`} />
                    <EconStat label="Storage Cost" val={`$${results.storage_cost}`} />
                    <EconStat label="Q (Energy)" val={`${results.q_energy} kJ`} />
                    <EconStat label="Q Loss" val={`${results.q_loss} kJ`} />
                  </div>
                </div>

                {/* 3. STRUCTURE INTERPRETATION */}
                <div className="space-y-4 pt-6 border-t border-[#D2D2D7]/30">
                  <div className="flex items-center justify-between">
                    <h4 className="text-[11px] font-bold text-[#86868B] uppercase flex items-center gap-2"><ShieldCheck className="w-4 h-4" /> 3. Structural Interpretation</h4>
                    <FeasibleBadge status={results.stability_feasible} />
                  </div>
                  <div className="flex gap-10">
                    <div className="space-y-4 flex-1">
                      <div className="flex justify-between items-center bg-[#F5F5F7] p-4 rounded-2xl">
                        <span className="text-xs font-semibold">Delta E</span>
                        <span className="font-mono font-bold">{results.delta_e} kJ/mol</span>
                      </div>
                      <div className="flex justify-between items-center bg-[#F5F5F7] p-4 rounded-2xl">
                        <span className="text-xs font-semibold">RMSD</span>
                        <span className="font-mono font-bold">{results.rmsd} Å</span>
                      </div>
                    </div>
                    {/* Placeholder for 3D Structure */}
                    <div className="w-1/3 aspect-square bg-[#1D1D1F] rounded-[24px] flex items-center justify-center border border-white/10 shadow-2xl relative">
                       <FlaskConical className="w-8 h-8 text-indigo-400 opacity-50" />
                       <p className="absolute bottom-3 text-[8px] font-mono text-zinc-500 uppercase tracking-widest">3D Model Active</p>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="h-[400px] flex flex-col items-center justify-center opacity-30 space-y-4">
                <Loader2 className={`w-8 h-8 ${loading ? 'animate-spin text-indigo-600' : ''}`} />
                <p className="text-xs font-bold uppercase tracking-widest text-center">Awaiting data to verify DOE & Economic feasibility...</p>
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}

// SUB-COMPONENTS
function SectionTitle({ num, text }: any) {
  return <p className="text-[10px] font-bold text-[#86868B] uppercase tracking-widest">{num}. {text}</p>;
}

function InputCell({ label, val, k, s, d }: any) {
  return (
    <div className="space-y-1">
      <Label className="text-[9px] font-bold text-[#86868B] ml-1 uppercase">{label}</Label>
      <Input value={val} onChange={(e) => s({...d, [k]: e.target.value})} className="rounded-xl border-[#D2D2D7] bg-[#F5F5F7]/50 h-9 text-xs shadow-none" />
    </div>
  );
}

function ResultBox({ label, val, unit, target, ok }: any) {
  return (
    <div className="p-5 rounded-[24px] bg-[#F5F5F7] border border-[#D2D2D7]/30 flex justify-between items-center group transition-all hover:bg-white hover:shadow-md">
      <div>
        <p className="text-[9px] font-bold text-[#86868B] uppercase mb-1">{label}</p>
        <p className="text-2xl font-black">{val} <span className="text-xs font-medium text-[#86868B]">{unit}</span></p>
        <p className="text-[9px] text-[#86868B] mt-1 font-mono">Target: {target}</p>
      </div>
      {ok ? <CheckCircle2 className="text-[#34C759] w-8 h-8 stroke-[1.5]" /> : <XCircle className="text-[#FF3B30] w-8 h-8 stroke-[1.5]" />}
    </div>
  );
}

function EconStat({ label, val }: any) {
  return (
    <div className="space-y-1">
      <p className="text-[8px] font-bold text-[#86868B] uppercase">{label}</p>
      <p className="text-sm font-bold text-[#1D1D1F] tracking-tight">{val}</p>
    </div>
  );
}

function FeasibleBadge({ status }: { status: boolean }) {
  return (
    <Badge className={`rounded-full px-3 py-0.5 text-[8px] font-black uppercase ${status ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'}`}>
      {status ? "Passed" : "Failed"}
    </Badge>
  );
}