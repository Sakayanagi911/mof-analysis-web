"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { 
  Upload, Activity, Database, ShieldCheck, ChevronRight, Loader2, 
  CheckCircle2, XCircle, FlaskConical, DollarSign, Layers, Maximize, 
  Scaling, Box, Weight, Ruler, Thermometer, Clock, Beaker, Zap, AlertTriangle
} from 'lucide-react';
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";

export default function MOFScreening() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  
  const [formData, setFormData] = useState({
    pv: "1.2", gsa: "3000", vsa: "1500", lcd: "12.1", pld: "8", vf: "0.5", density: "0.8",
    metal_name: "Zr", linker_name: "BDC", smiles: "C1=CC=C(C=C1)C(=O)O",
    reaction_time: "24", temperature: "120"
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
      <nav className="sticky top-0 z-50 w-full border-b border-[#D2D2D7]/30 bg-white/80 backdrop-blur-xl px-6 py-3 text-left">
        <div className="max-w-7xl mx-auto flex justify-between items-center italic font-semibold text-left">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-indigo-600" />
            <span>MOF<span className="text-indigo-600 font-black">Scan</span></span>
          </div>
          <div className="text-[10px] text-[#86868B] uppercase tracking-widest font-bold">Research Dashboard</div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-12 px-6 grid grid-cols-1 lg:grid-cols-12 gap-10 text-left">
        
        {/* PANEL KIRI: INPUT */}
        <section className="lg:col-span-4 space-y-6 text-left">
          <div className="bg-white/70 backdrop-blur-md rounded-[24px] border border-white p-8 shadow-sm space-y-6">
            <h2 className="text-xl font-semibold">Configuration</h2>
            
            <div className="space-y-4 text-left">
              <SectionHeader icon={<FlaskConical className="w-4 h-4" />} text="01 Structure File" />
              <div 
                className={`group border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-all ${file ? 'border-indigo-400 bg-indigo-50/20' : 'border-[#D2D2D7] hover:bg-zinc-50'}`}
                onClick={() => document.getElementById('cif-upload')?.click()}
              >
                <Upload className={`mx-auto w-6 h-6 mb-2 ${file ? 'text-indigo-600' : 'text-[#86868B]'}`} />
                <p className="text-xs font-semibold truncate px-2">{file ? file.name : "Select .cif file"}</p>
                <input id="cif-upload" type="file" className="hidden" accept=".cif" onChange={(e) => setFile(e.target.files?.[0] || null)} />
              </div>
            </div>

            <div className="space-y-4 pt-4 border-t border-zinc-100 text-left">
              <SectionHeader icon={<Layers className="w-4 h-4" />} text="02 Geometric Factors" />
              <div className="space-y-3">
                <InputGroup icon={<Activity className="w-4 h-4"/>} label="ASA Gravimetric" unit="m²/g" val={formData.gsa} k="gsa" s={setFormData} d={formData} />
                <InputGroup icon={<Layers className="w-4 h-4"/>} label="ASA Volumetric" unit="m²/cm³" val={formData.vsa} k="vsa" s={setFormData} d={formData} />
                <InputGroup icon={<Box className="w-4 h-4"/>} label="Void Fraction" unit="φ" val={formData.vf} k="vf" s={setFormData} d={formData} />
                <InputGroup icon={<Maximize className="w-4 h-4"/>} label="Pore Volume" unit="cm³/g" val={formData.pv} k="pv" s={setFormData} d={formData} />
                <InputGroup icon={<Weight className="w-4 h-4"/>} label="Density" unit="g/cm³" val={formData.density} k="density" s={setFormData} d={formData} />
                <InputGroup icon={<Ruler className="w-4 h-4"/>} label="LCD" unit="Å" val={formData.lcd} k="lcd" s={setFormData} d={formData} />
                <InputGroup icon={<Scaling className="w-4 h-4"/>} label="PLD" unit="Å" val={formData.pld} k="pld" s={setFormData} d={formData} />
              </div>
            </div>

            <div className="space-y-4 pt-4 border-t border-zinc-100 text-left">
              <SectionHeader icon={<Beaker className="w-4 h-4" />} text="03 Synthesis Conditions" />
              <div className="space-y-3">
                <InputGroup icon={<FlaskConical className="w-4 h-4"/>} label="Metal Name" unit="Sym" val={formData.metal_name} k="metal_name" s={setFormData} d={formData} />
                <InputGroup icon={<Database className="w-4 h-4"/>} label="Linker Name" unit="Name" val={formData.linker_name} k="linker_name" s={setFormData} d={formData} />
                <InputGroup icon={<Beaker className="w-4 h-4"/>} label="SMILES" unit="Str" val={formData.smiles} k="smiles" s={setFormData} d={formData} />
                <InputGroup icon={<Clock className="w-4 h-4"/>} label="Reaction Time (t)" unit="h" val={formData.reaction_time} k="reaction_time" s={setFormData} d={formData} />
                <InputGroup icon={<Thermometer className="w-4 h-4"/>} label="Temperature (T)" unit="°C" val={formData.temperature} k="temperature" s={setFormData} d={formData} />
              </div>
            </div>
          </div>
        </section>

        {/* PANEL KANAN: OUTPUT */}
        <section className="lg:col-span-8 relative text-left">
          <div className="bg-white rounded-[32px] p-10 border border-[#D2D2D7]/20 shadow-sm sticky top-28 space-y-8 min-h-[600px] flex flex-col text-left">
            {loading && <div className="absolute top-0 left-0 w-full h-1 bg-indigo-600 animate-pulse" />}
            
            <header className="flex justify-between items-center text-left">
              <div className="text-left">
                <h3 className="text-[10px] font-black text-[#86868B] uppercase tracking-[0.2em] text-left">Screening Result</h3>
                <h1 className={`text-6xl font-bold tracking-tighter text-left ${results ? (results.is_overall_feasible ? 'text-[#0071E3]' : 'text-[#FF3B30]') : 'text-[#D2D2D7]'}`}>
                  {loading ? "Analyzing..." : results ? (results.is_overall_feasible ? "Feasible." : "Denied.") : "Pending."}
                </h1>
              </div>
              {results && <Badge className="bg-[#1D1D1F] text-white rounded-full px-4 py-1 text-[10px] uppercase font-bold tracking-widest">{results.stability_status}</Badge>}
            </header>

            {results ? (
              <div className="space-y-8 animate-in fade-in duration-500 text-left">
                {/* 1. HYDROGEN CAPACITY */}
                <div className="space-y-4 text-left">
                  <div className="flex items-center justify-between">
                    <h4 className="text-[11px] font-bold text-[#86868B] uppercase tracking-wider text-left">1. Hydrogen Working Capacity (Whitebox)</h4>
                    <FeasibleBadge status={results.doe_feasible} />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <ResultBox label="Gravimetric" val={results.gravimetric_h2} unit="wt%" target="≥ 5.5" ok={results.gravimetric_h2 >= 5.5} />
                    <ResultBox label="Volumetric" val={results.volumetric_h2} unit="g/L" target="≥ 40" ok={results.volumetric_h2 >= 40} />
                  </div>
                </div>

                {/* 2. ECONOMIC ANALYSIS & ENERGY FINGERPRINT (REVISI) */}
                <div className="space-y-4 pt-6 border-t border-[#D2D2D7]/30 text-left">
                  <div className="flex items-center justify-between">
                    <h4 className="text-[11px] font-bold text-[#86868B] uppercase tracking-wider text-left">2. Economic Analysis & Energy Fingerprint</h4>
                    <FeasibleBadge status={results.econ_feasible} />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <ResultBox label="MOF Cost" val={results.mof_cost} unit="USD/kg" target="≤ 30" ok={results.mof_cost <= 30} />
                    <ResultBox label="Storage Cost" val={results.storage_cost} unit="USD/kg H2" target="≤ 300" ok={results.storage_cost <= 300} />
                  </div>
                  
                  {/* Grid Energi - Menambahkan E Stirring */}
                  <div className="grid grid-cols-3 gap-4">
                    <EconMiniCard icon={<Zap className="w-3 h-3 text-amber-500" />} label="Q Heat" val={results.q_energy} unit="MJ" />
                    <EconMiniCard icon={<AlertTriangle className="w-3 h-3 text-orange-500" />} label="Q Loss" val={results.q_loss} unit="MJ" />
                    <EconMiniCard icon={<Activity className="w-3 h-3 text-blue-500" />} label="E Stirring" val={results.e_stirr} unit="MJ" />
                  </div>

                  {/* Monitoring Threshold UI */}
                  <div className="grid grid-cols-2 gap-4">
                    <ConditionMiniCard 
                      icon={<Clock className="w-3 h-3" />} 
                      label="Synthesis Time" 
                      val={results.reaction_time} 
                      unit=" / 48h" 
                      ok={results.reaction_time < 48} 
                    />
                    <ConditionMiniCard 
                      icon={<Thermometer className="w-3 h-3" />} 
                      label="Reaction Temp" 
                      val={results.temperature} 
                      unit=" / 180°C" 
                      ok={results.temperature <= 180} 
                    />
                  </div>
                </div>

                {/* 3. STRUCTURAL INTERPRETATION */}
                <div className="space-y-4 pt-6 border-t border-[#D2D2D7]/30 text-left">
                  <div className="flex items-center justify-between">
                    <h4 className="text-[11px] font-bold text-[#86868B] uppercase tracking-wider text-left">3. Structural Interpretation</h4>
                    <FeasibleBadge status={results.stability_feasible} />
                  </div>
                  <div className="flex gap-8">
                    <div className="space-y-3 flex-1 text-left">
                      <div className="flex justify-between items-center bg-[#F5F5F7] p-4 rounded-2xl border border-zinc-100">
                        <span className="text-xs font-semibold text-zinc-500">Delta E (Hybrid)</span>
                        <span className="font-mono font-bold">{results.delta_e} kJ/mol</span>
                      </div>
                      <div className="flex justify-between items-center bg-[#F5F5F7] p-4 rounded-2xl border border-zinc-100">
                        <span className="text-xs font-semibold text-zinc-500">RMSD</span>
                        <span className="font-mono font-bold">{results.rmsd} Å</span>
                      </div>
                    </div>
                    <div className="w-1/3 aspect-square bg-[#1D1D1F] rounded-[24px] flex items-center justify-center border border-white/10 shadow-lg relative">
                       <FlaskConical className="w-8 h-8 text-indigo-400 opacity-50" />
                       <p className="absolute bottom-3 text-[8px] font-mono text-zinc-500 uppercase tracking-widest text-center">3D Struct Active</p>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center opacity-30 space-y-4 text-left">
                <Loader2 className={`w-8 h-8 ${loading ? 'animate-spin text-indigo-600' : ''}`} />
                <p className="text-xs font-bold uppercase tracking-widest text-center px-10">Please upload .cif file and fill all configuration fields to start screening.</p>
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}

// --- COMPONENTS ---

function SectionHeader({ icon, text }: any) {
  return (
    <div className="flex items-center gap-2 mb-2 text-left">
      <div className="p-1.5 bg-indigo-50 rounded-lg text-indigo-600">{icon}</div>
      <p className="text-[10px] font-bold text-[#86868B] uppercase tracking-widest">{text}</p>
    </div>
  );
}

function InputGroup({ icon, label, unit, val, k, s, d }: any) {
  return (
    <div className="space-y-1.5 text-left">
      <Label className="text-[11px] font-medium text-[#424245] ml-1">{label}</Label>
      <div className="relative flex items-center group">
        <div className="absolute left-3 text-[#86868B] group-focus-within:text-indigo-600 transition-colors">
          {icon}
        </div>
        <Input 
          type={k === 'metal_name' || k === 'linker_name' || k === 'smiles' ? 'text' : 'number'}
          step="any"
          value={val} 
          onChange={(e) => s({...d, [k]: e.target.value})} 
          className="pl-10 pr-16 rounded-xl border-[#D2D2D7] bg-white h-11 text-sm shadow-none focus-visible:ring-1 focus-visible:ring-indigo-500 transition-all"
        />
        <div className="absolute right-3 text-[10px] font-mono font-bold text-[#D2D2D7]">
          {unit}
        </div>
      </div>
    </div>
  );
}

function ResultBox({ label, val, unit, target, ok }: any) {
  return (
    <div className={`p-5 rounded-[24px] border transition-all flex justify-between items-center ${ok ? 'bg-emerald-50/20 border-emerald-100/50' : 'bg-red-50/20 border-red-100/50'}`}>
      <div className="text-left">
        <p className="text-[9px] font-bold text-[#86868B] uppercase mb-1">{label}</p>
        <p className="text-2xl font-black">{val} <span className="text-xs font-medium text-[#86868B]">{unit}</span></p>
        <p className="text-[9px] text-[#86868B] mt-1 font-mono">Target: {target}</p>
      </div>
      {ok ? <CheckCircle2 className="text-[#34C759] w-8 h-8 stroke-[1.5]" /> : <XCircle className="text-[#FF3B30] w-8 h-8 stroke-[1.5]" />}
    </div>
  );
}

function EconMiniCard({ icon, label, val, unit }: any) {
  return (
    <div className="bg-[#F5F5F7] p-3 rounded-xl border border-zinc-100 text-center space-y-1">
      <div className="flex items-center justify-center gap-1">
        {icon}
        <span className="text-[8px] font-bold text-zinc-400 uppercase tracking-tighter">{label}</span>
      </div>
      <p className="text-xs font-bold">{val} <span className="text-[8px] font-normal text-zinc-400">{unit}</span></p>
    </div>
  );
}

function ConditionMiniCard({ icon, label, val, unit, ok }: any) {
  return (
    <div className={`p-3 rounded-xl border text-center space-y-1 ${ok ? 'bg-emerald-50/30 border-emerald-100/50' : 'bg-red-50/30 border-red-100/50'}`}>
      <div className="flex items-center justify-center gap-1 text-center">
        <span className={ok ? 'text-emerald-600' : 'text-red-600'}>{icon}</span>
        <span className={`text-[8px] font-bold uppercase tracking-tighter ${ok ? 'text-emerald-700' : 'text-red-700'}`}>{label}</span>
      </div>
      <p className={`text-xs font-bold ${ok ? 'text-emerald-900' : 'text-red-900'}`}>{val}{unit}</p>
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