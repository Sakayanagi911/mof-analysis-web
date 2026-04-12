"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { 
  Upload, Activity, Database, Loader2, 
  CheckCircle2, XCircle, FlaskConical, Layers, Maximize, 
  Scaling, Box, Weight, Ruler, Thermometer, Clock, Beaker, Zap, AlertTriangle, ChevronDown, Search
} from 'lucide-react';

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";

export default function MOFScreening() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [price_db, setPriceDb] = useState<any>({ metals: {}, linkers: {} });

  // State untuk dropdown kustom
  const [metalSearch, setMetalSearch] = useState("");
  const [linkerSearch, setLinkerSearch] = useState("");
  const [showMetalList, setShowMetalList] = useState(false);
  const [showLinkerList, setShowLinkerList] = useState(false);

  const [formData, setFormData] = useState({
    pv: "1.2", gsa: "3000", vsa: "1500", lcd: "12.1", pld: "8", vf: "0.5", density: "0.8",
    metal_name: "", linker_name: "", smiles: "",
    reaction_time: "24", temperature: "120"
  });

  useEffect(() => {
    fetch("http://127.0.0.1:8000/get-prices")
      .then(res => res.json())
      .then(data => { if (data && !data.error) setPriceDb(data); })
      .catch(err => console.error("Database offline"));
  }, []);

  const runLiveAnalysis = useCallback(async () => {
    setLoading(true);
    const data = new FormData();
    if (file) data.append('file', file);
    Object.entries(formData).forEach(([key, val]) => data.append(key, val));

    try {
      const res = await fetch("http://127.0.0.1:8000/analyze", { method: "POST", body: data });
      const result = await res.json();
      if (result.status === "success") setResults(result.results);
    } catch (err) { console.error("Analysis failed"); }
    finally { setTimeout(() => setLoading(false), 800); }
  }, [formData, file]);

  useEffect(() => {
    if (file && formData.metal_name && formData.linker_name) {
      const timer = setTimeout(() => runLiveAnalysis(), 800);
      return () => clearTimeout(timer);
    }
  }, [formData, file, runLiveAnalysis]);

  return (
    <div className="min-h-screen bg-[#F5F5F7] text-[#1D1D1F] font-sans antialiased selection:bg-indigo-100">
      {/* NAVBAR MODERN */}
      <nav className="sticky top-0 z-50 w-full border-b border-zinc-200/50 bg-white/70 backdrop-blur-xl px-8 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-3 group cursor-pointer">
            <div className="p-2 bg-indigo-600 rounded-xl group-hover:rotate-12 transition-transform duration-300">
                <Activity className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold tracking-tight">MOF<span className="text-indigo-600">Scan</span></span>
          </div>
          <div className="flex items-center gap-6">
            <div className="text-[11px] text-[#86868B] uppercase tracking-[0.2em] font-bold bg-zinc-100 px-3 py-1 rounded-full">Pro Edition</div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-12 px-8 grid grid-cols-1 lg:grid-cols-12 gap-12">
        {/* PANEL KIRI: CONFIGURATION */}
        <section className="lg:col-span-4 space-y-8 animate-in slide-in-from-left duration-700">
          <div className="bg-white/80 backdrop-blur-2xl rounded-[32px] border border-white/50 p-8 shadow-[0_8px_32px_rgba(0,0,0,0.04)] space-y-8">
            <h2 className="text-2xl font-bold tracking-tight">Configuration</h2>
            
            {/* 01. Structure File */}
            <div className="space-y-4">
              <SectionHeader icon={<FlaskConical className="w-4 h-4" />} text="01 Structure File" />
              <div 
                className={`group relative overflow-hidden border-2 border-dashed rounded-3xl p-8 text-center cursor-pointer transition-all duration-500 ${file ? 'border-indigo-400 bg-indigo-50/50' : 'border-zinc-200 hover:border-indigo-300 hover:bg-zinc-50'}`}
                onClick={() => document.getElementById('cif-upload')?.click()}
              >
                <Upload className={`mx-auto w-8 h-8 mb-3 transition-colors ${file ? 'text-indigo-600' : 'text-zinc-400'}`} />
                <p className="text-sm font-semibold tracking-tight truncate px-4">{file ? file.name : "Drop .cif file here"}</p>
                <input id="cif-upload" type="file" className="hidden" accept=".cif" onChange={(e) => setFile(e.target.files?.[0] || null)} />
              </div>
            </div>

            {/* 02. Geometric Factors */}
            <div className="space-y-4 pt-6 border-t border-zinc-100">
              <SectionHeader icon={<Layers className="w-4 h-4" />} text="02 Geometric Factors" />
              <div className="grid grid-cols-1 gap-4">
                <InputGroup icon={<Activity className="w-4 h-4"/>} label="ASA Gravimetric" unit="m²/g" val={formData.gsa} k="gsa" s={setFormData} d={formData} />
                <InputGroup icon={<Layers className="w-4 h-4"/>} label="ASA Volumetric" unit="m²/cm³" val={formData.vsa} k="vsa" s={setFormData} d={formData} />
                <InputGroup icon={<Box className="w-4 h-4"/>} label="Void Fraction" unit="φ" val={formData.vf} k="vf" s={setFormData} d={formData} />
                <div className="grid grid-cols-2 gap-4">
                    <InputGroup label="Pore Volume" unit="cm³/g" val={formData.pv} k="pv" s={setFormData} d={formData} />
                    <InputGroup label="Density" unit="g/cm³" val={formData.density} k="density" s={setFormData} d={formData} />
                </div>
                <div className="grid grid-cols-2 gap-4">
                    <InputGroup label="LCD" unit="Å" val={formData.lcd} k="lcd" s={setFormData} d={formData} />
                    <InputGroup label="PLD" unit="Å" val={formData.pld} k="pld" s={setFormData} d={formData} />
                </div>
              </div>
            </div>

            {/* 03. Synthesis Conditions */}
            <div className="space-y-4 pt-6 border-t border-zinc-100">
              <SectionHeader icon={<Beaker className="w-4 h-4" />} text="03 Synthesis Conditions" />
              <div className="space-y-4">
                {/* Modern Metal Search Box */}
                <div className="space-y-2 relative">
                  <Label className="text-[12px] font-bold text-zinc-500 ml-1 uppercase tracking-wider">Metal Name</Label>
                  <div className="relative group cursor-pointer" onClick={() => setShowMetalList(!showMetalList)}>
                    <Input 
                      placeholder="Search metal..."
                      value={formData.metal_name || metalSearch}
                      onChange={(e) => {
                        setMetalSearch(e.target.value);
                        setFormData({...formData, metal_name: e.target.value});
                        setShowMetalList(true);
                      }}
                      className="pl-11 pr-10 h-12 rounded-2xl border-zinc-200 bg-white shadow-sm focus:ring-4 focus:ring-indigo-100 transition-all font-medium"
                    />
                    <Search className="absolute left-4 top-4 w-4 h-4 text-zinc-400" />
                    <ChevronDown className={`absolute right-4 top-4 w-4 h-4 text-zinc-400 transition-transform duration-300 ${showMetalList ? 'rotate-180' : ''}`} />
                  </div>
                  {showMetalList && (
                    <div className="absolute z-50 w-full mt-2 bg-white/95 backdrop-blur-xl border border-zinc-200 rounded-3xl shadow-2xl max-h-60 overflow-y-auto animate-in fade-in zoom-in duration-200">
                      {Object.keys(price_db.metals).filter(m => m.toLowerCase().includes(formData.metal_name.toLowerCase())).map(m => (
                        <div key={m} className="px-5 py-3.5 text-sm hover:bg-indigo-50 cursor-pointer transition-colors border-b border-zinc-50 last:border-0 font-semibold text-zinc-700"
                          onClick={() => { setFormData({...formData, metal_name: m}); setShowMetalList(false); }}>{m}</div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Modern Linker Search Box */}
                <div className="space-y-2 relative">
                  <Label className="text-[12px] font-bold text-zinc-500 ml-1 uppercase tracking-wider">Linker Name</Label>
                  <div className="relative group cursor-pointer" onClick={() => setShowLinkerList(!showLinkerList)}>
                    <Input 
                      placeholder="Search linker..."
                      value={formData.linker_name || linkerSearch}
                      onChange={(e) => {
                        setLinkerSearch(e.target.value);
                        setFormData({...formData, linker_name: e.target.value});
                        setShowLinkerList(true);
                      }}
                      className="pl-11 pr-10 h-12 rounded-2xl border-zinc-200 bg-white shadow-sm focus:ring-4 focus:ring-indigo-100 transition-all font-medium"
                    />
                    <Database className="absolute left-4 top-4 w-4 h-4 text-zinc-400" />
                    <ChevronDown className={`absolute right-4 top-4 w-4 h-4 text-zinc-400 transition-transform duration-300 ${showLinkerList ? 'rotate-180' : ''}`} />
                  </div>
                  {showLinkerList && (
                    <div className="absolute z-50 w-full mt-2 bg-white/95 backdrop-blur-xl border border-zinc-200 rounded-3xl shadow-2xl max-h-60 overflow-y-auto animate-in fade-in zoom-in duration-200">
                      {Object.keys(price_db.linkers).filter(l => l.toLowerCase().includes(formData.linker_name.toLowerCase())).map(l => (
                        <div key={l} className="px-5 py-3.5 text-sm hover:bg-indigo-50 cursor-pointer transition-colors border-b border-zinc-50 last:border-0 font-semibold text-zinc-700"
                          onClick={() => { setFormData({...formData, linker_name: l}); setShowLinkerList(false); }}>{l}</div>
                      ))}
                    </div>
                  )}
                </div>

                <InputGroup icon={<Beaker className="w-4 h-4"/>} label="SMILES" unit="Str" val={formData.smiles} k="smiles" s={setFormData} d={formData} />
                <div className="grid grid-cols-2 gap-4">
                    <InputGroup icon={<Clock className="w-4 h-4"/>} label="Time" unit="h" val={formData.reaction_time} k="reaction_time" s={setFormData} d={formData} />
                    <InputGroup icon={<Thermometer className="w-4 h-4"/>} label="Temp" unit="°C" val={formData.temperature} k="temperature" s={setFormData} d={formData} />
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* PANEL KANAN: OUTPUT */}
        <section className="lg:col-span-8 relative animate-in fade-in zoom-in duration-1000">
          <div className="bg-white/90 backdrop-blur-3xl rounded-[48px] p-12 border border-white shadow-[0_24px_80px_rgba(0,0,0,0.06)] sticky top-28 space-y-12 min-h-[700px] flex flex-col overflow-hidden">
            {loading && <div className="absolute top-0 left-0 w-full h-1.5 bg-indigo-600 animate-pulse" />}
            
            <header className="flex justify-between items-start">
              <div className="space-y-2">
                <h3 className="text-[12px] font-black text-zinc-400 uppercase tracking-[0.3em]">Screening Result</h3>
                <h1 className={`text-8xl font-black tracking-tighter transition-colors duration-500 ${results ? (results.is_overall_feasible ? 'text-indigo-600' : 'text-red-500') : 'text-zinc-200'}`}>
                  {loading ? "Analyzing..." : results ? (results.is_overall_feasible ? "Feasible" : "Denied") : "Pending"}
                </h1>
              </div>
              {results && (
                <div className="flex flex-col items-end gap-3">
                    <Badge className="bg-zinc-900 text-white rounded-full px-6 py-2 text-xs font-bold uppercase tracking-widest">{results.stability_status}</Badge>
                    <div className="flex gap-2">
                        <div className="w-3 h-3 rounded-full bg-indigo-500 animate-ping" />
                        <span className="text-[10px] font-bold text-indigo-500 uppercase tracking-tighter">Live Engine Active</span>
                    </div>
                </div>
              )}
            </header>

            {results ? (
              <div className="space-y-12 animate-in fade-in duration-1000 slide-in-from-bottom-4">
                {/* 1. Hydrogen Capacity */}
                <div className="space-y-6">
                  <div className="flex items-center gap-4">
                    <h4 className="text-sm font-bold text-zinc-400 uppercase tracking-widest">Hydrogen Storage Metrics</h4>
                    <div className="h-px bg-zinc-100 flex-1" />
                  </div>
                  <div className="grid grid-cols-2 gap-6">
                    <ResultBox label="Gravimetric" val={results.gravimetric_h2} unit="wt%" target="≥ 5.5" ok={results.gravimetric_h2 >= 5.5} />
                    <ResultBox label="Volumetric" val={results.volumetric_h2} unit="g/L" target="≥ 40" ok={results.volumetric_h2 >= 40} />
                  </div>
                </div>

                {/* 2. Economic & Energy */}
                <div className="space-y-6">
                  <div className="flex items-center gap-4">
                    <h4 className="text-sm font-bold text-zinc-400 uppercase tracking-widest">Economy & Energy Fingerprint</h4>
                    <div className="h-px bg-zinc-100 flex-1" />
                  </div>
                  <div className="grid grid-cols-2 gap-6">
                    <ResultBox label="MOF Cost" val={results.mof_cost} unit="USD/kg" target="≤ 30" ok={results.mof_cost <= 30} />
                    <ResultBox label="Storage Cost" val={results.storage_cost} unit="USD/kg H2" target="≤ 300" ok={results.storage_cost <= 300} />
                  </div>
                  <div className="grid grid-cols-3 gap-6">
                    <EconMiniCard icon={<Zap className="w-4 h-4 text-amber-500" />} label="Q Heat" val={results.q_energy} unit="MJ" />
                    <EconMiniCard icon={<AlertTriangle className="w-4 h-4 text-orange-500" />} label="Q Loss" val={results.q_loss} unit="MJ" />
                    <EconMiniCard icon={<Activity className="w-4 h-4 text-indigo-500" />} label="E Stirring" val={results.e_stirr} unit="MJ" />
                  </div>
                </div>

                {/* 3. Structural Interpretation */}
                <div className="space-y-6">
                   <div className="flex items-center gap-4">
                    <h4 className="text-sm font-bold text-zinc-400 uppercase tracking-widest">Structural Analysis</h4>
                    <div className="h-px bg-zinc-100 flex-1" />
                  </div>
                  <div className="flex gap-10">
                    <div className="space-y-4 flex-1">
                      <div className="group flex justify-between items-center bg-indigo-50/50 p-6 rounded-3xl border border-indigo-100/50 hover:bg-indigo-100 transition-colors duration-300">
                        <span className="text-2xl font-black text-indigo-600 tracking-tighter">ΔE</span>
                        <span className="font-mono font-bold text-2xl text-indigo-950">{results.delta_e} <span className="text-[10px] text-indigo-400 ml-1">kJ/mol</span></span>
                      </div>
                      <div className="group flex justify-between items-center bg-zinc-50 p-6 rounded-3xl border border-zinc-100 hover:bg-zinc-100 transition-colors duration-300">
                        <span className="text-xs font-bold text-zinc-400 tracking-widest uppercase">RMSD Score</span>
                        <span className="font-mono font-bold text-2xl">{results.rmsd} <span className="text-[10px] text-zinc-400 ml-1">Å</span></span>
                      </div>
                    </div>
                    <div className="w-1/3 aspect-square bg-zinc-900 rounded-[40px] flex items-center justify-center border border-white/10 shadow-2xl relative group overflow-hidden">
                       <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                       <FlaskConical className="w-12 h-12 text-white/20 group-hover:text-indigo-400 group-hover:scale-110 transition-all duration-500" />
                       <div className="absolute bottom-4 text-[8px] text-white/30 font-bold uppercase tracking-[0.3em]">3D View</div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center text-center space-y-6">
                <div className="relative">
                    <div className="absolute inset-0 bg-indigo-500/20 blur-3xl rounded-full animate-pulse" />
                    <Loader2 className={`w-16 h-16 relative ${loading ? 'animate-spin text-indigo-600' : 'text-zinc-100'}`} />
                </div>
                <div className="space-y-2">
                    <p className="text-sm font-bold uppercase tracking-[0.3em] text-zinc-400">Ready for Scan</p>
                    <p className="text-xs text-zinc-400 max-w-[280px] leading-relaxed">Please configure synthesis parameters and upload structure file to begin.</p>
                </div>
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}

// --- SUB-COMPONENTS ---
function SectionHeader({ icon, text }: any) {
  return (
    <div className="flex items-center gap-3 mb-2 group">
      <div className="p-2 bg-indigo-50 rounded-xl text-indigo-600 group-hover:bg-indigo-600 group-hover:text-white transition-all duration-300">{icon}</div>
      <p className="text-[10px] font-black text-zinc-400 uppercase tracking-[0.2em]">{text}</p>
    </div>
  );
}

function InputGroup({ icon, label, unit, val, k, s, d }: any) {
  return (
    <div className="space-y-2">
      <Label className="text-[11px] font-bold text-zinc-500 ml-1 uppercase tracking-wider">{label}</Label>
      <div className="relative flex items-center group">
        {icon && <div className="absolute left-4 text-zinc-400 group-focus-within:text-indigo-600 transition-colors duration-300">{icon}</div>}
        <Input 
          type={k === 'smiles' ? 'text' : 'number'} 
          step="any" 
          value={val} 
          onChange={(e) => s({...d, [k]: e.target.value})} 
          className={`pr-14 rounded-2xl border-zinc-200 h-12 text-sm font-semibold shadow-sm focus-visible:ring-4 focus-visible:ring-indigo-100 transition-all ${icon ? 'pl-11' : 'pl-4'}`} 
        />
        <div className="absolute right-4 text-[10px] font-black text-zinc-300 uppercase">{unit}</div>
      </div>
    </div>
  );
}

function ResultBox({ label, val, unit, target, ok }: any) {
  return (
    <div className={`p-8 rounded-[32px] border flex justify-between items-center transition-all duration-500 hover:scale-[1.02] ${ok ? 'bg-indigo-50/30 border-indigo-100/50' : 'bg-red-50/30 border-red-100/50'}`}>
      <div className="space-y-1">
        <p className="text-[10px] font-black text-zinc-400 uppercase tracking-widest">{label}</p>
        <p className="text-4xl font-black tracking-tighter">{val} <span className="text-sm font-bold text-zinc-300 uppercase ml-1">{unit}</span></p>
        <p className="text-[10px] font-bold text-zinc-400 mt-2 italic opacity-60">Target: {target}</p>
      </div>
      <div className={`p-4 rounded-2xl ${ok ? 'bg-indigo-100 text-indigo-600' : 'bg-red-100 text-red-600'}`}>
        {ok ? <CheckCircle2 className="w-6 h-6 stroke-[3]" /> : <XCircle className="w-6 h-6 stroke-[3]" />}
      </div>
    </div>
  );
}

function EconMiniCard({ icon, label, val, unit }: any) {
  return (
    <div className="bg-white p-6 rounded-[24px] border border-zinc-100 text-center space-y-3 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
      <div className="flex items-center justify-center gap-2">
        <div className="p-2 bg-zinc-50 rounded-lg">{icon}</div>
        <span className="text-[10px] font-black text-zinc-400 uppercase tracking-widest">{label}</span>
      </div>
      <p className="text-2xl font-black tracking-tight">{val} <span className="text-[10px] font-bold text-zinc-300 uppercase">{unit}</span></p>
    </div>
  );
}