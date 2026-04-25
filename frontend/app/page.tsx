"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { 
  Upload, Activity, Database, Loader2, 
  CheckCircle2, XCircle, FlaskConical, Layers, 
  Box, Thermometer, Clock, Beaker, Zap, AlertTriangle, ChevronDown, Search, Scale, DollarSign, Weight
} from 'lucide-react';

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";

export default function MOFScreening() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [price_db, setPriceDb] = useState<any>({ 
    metals: {}, 
    linkers: {}, 
    solvents: {}, 
    additives: {}, 
    modulators: {} 
  });

  const [showMetalList, setShowMetalList] = useState(false);
  const [showLinkerList, setShowLinkerList] = useState(false);
  const [showSolventList, setShowSolventList] = useState(false);
  const [showAdditiveList, setShowAdditiveList] = useState(false);
  const [showModulatorList, setShowModulatorList] = useState(false);
  
  const [formData, setFormData] = useState({
    pv: "1.2", gsa: "3000", vsa: "1500", lcd: "12.1", pld: "8", vf: "0.5", density: "0.8",
    solvent_name: "",   
    solvent_volume: "", 
    additive_name: "",  
    additive_volume: "", 
    modulator_name: "", 
    modulator_volume: "", 
    metal_name: "",     
    metal_mass: "", 
    linker_name: "",    
    linker_mass: "", 
    smiles: "",         
    product_mass: "0",   
    reaction_time: "24", 
    temperature: "120"   
  });

  useEffect(() => {
    fetch("http://127.0.0.1:8000/get-prices")
      .then(res => res.json())
      .then(data => { if (data && !data.error) setPriceDb(data); })
      .catch(err => console.error("Database offline"));
  }, []);

  useEffect(() => {
    if (formData.linker_name && price_db.linkers && price_db.linkers[formData.linker_name]) {
      const dbEntry = price_db.linkers[formData.linker_name];
      setFormData(prev => ({
        ...prev,
        smiles: dbEntry.smiles || dbEntry.SMILES1 || ""
      }));
    }
  }, [formData.linker_name, price_db.linkers]);

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
      <nav className="sticky top-0 z-50 w-full border-b border-zinc-200/50 bg-white/70 backdrop-blur-xl px-4 md:px-8 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-3 group cursor-pointer">
            <div className="p-2 bg-indigo-600 rounded-xl group-hover:rotate-12 transition-transform duration-300">
                <Activity className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold tracking-tight">MOF<span className="text-indigo-600">Scan</span></span>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 md:py-12 px-4 md:px-8 grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12">
        <section className="lg:col-span-4 space-y-8 animate-in slide-in-from-left duration-700">
          <div className="bg-white/80 backdrop-blur-2xl rounded-[32px] border border-white/50 p-6 md:p-8 shadow-sm space-y-8">
            <h2 className="text-2xl font-bold tracking-tight">Configuration</h2>
            
            <div className="space-y-4">
              <SectionHeader icon={<FlaskConical className="w-4 h-4" />} text="01 Structure File" />
              <div 
                className={`group relative overflow-hidden border-2 border-dashed rounded-3xl p-6 text-center cursor-pointer transition-all duration-500 shadow-sm ${file ? 'border-indigo-400 bg-indigo-50/50' : 'border-zinc-200 hover:border-indigo-300'}`}
                onClick={() => document.getElementById('cif-upload')?.click()}
              >
                <Upload className={`mx-auto w-8 h-8 mb-3 ${file ? 'text-indigo-600' : 'text-zinc-400'}`} />
                <p className="text-sm font-semibold truncate px-4">{file ? file.name : "Drop .cif file here"}</p>
                <input id="cif-upload" type="file" className="hidden" accept=".cif" onChange={(e) => setFile(e.target.files?.[0] || null)} />
              </div>
            </div>

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

            <div className="space-y-4 pt-6 border-t border-zinc-100">
              <SectionHeader icon={<Beaker className="w-4 h-4" />} text="03 Synthesis Conditions" />
              <div className="space-y-4">
                
                {/* 1. Solvent */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 items-start">
                  <div className="sm:col-span-2 space-y-2 relative">
                    <Label className="text-[11px] font-bold text-zinc-500 ml-1 uppercase tracking-wider">1. Solvent Name</Label>
                    <div className="relative group">
                      <Input 
                        placeholder="Mohon diisi" 
                        value={formData.solvent_name} 
                        onFocus={() => setShowSolventList(true)} 
                        onBlur={() => setTimeout(() => setShowSolventList(false), 200)} 
                        onChange={(e) => setFormData({...formData, solvent_name: e.target.value})} 
                        className="pl-11 pr-12 h-12 rounded-2xl border-zinc-300 bg-white font-medium focus:ring-4 focus:ring-indigo-100 shadow-sm transition-all" 
                      />
                      <Search className="absolute left-4 top-4 w-4 h-4 text-zinc-400 group-focus-within:text-indigo-600 transition-colors" />
                      <div className="absolute right-4 top-4 text-[10px] font-black text-zinc-300 uppercase">Solv</div>
                    </div>
                    {showSolventList && price_db.solvents && (
                      <div className="absolute z-50 w-full mt-2 bg-white/95 backdrop-blur-xl border border-zinc-200 rounded-2xl shadow-xl max-h-48 overflow-y-auto">
                        {Object.keys(price_db.solvents).filter(s => s.toLowerCase().includes(formData.solvent_name.toLowerCase())).map(s => (
                          <div key={s} className="px-5 py-3 text-sm hover:bg-indigo-50 cursor-pointer border-b border-zinc-50 font-semibold" onMouseDown={() => setFormData({...formData, solvent_name: s})}>{s}</div>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="sm:col-span-1">
                    <InputGroup label="Volume" unit="mL" val={formData.solvent_volume} k="solvent_volume" s={setFormData} d={formData} placeholder="0" />
                  </div>
                </div>

                {/* 2. Additive */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 items-start">
                  <div className="sm:col-span-2 space-y-2 relative">
                    <Label className="text-[11px] font-bold text-zinc-500 ml-1 uppercase tracking-wider">2. Additive Name</Label>
                    <div className="relative group">
                      <Input 
                        placeholder="Mohon diisi" 
                        value={formData.additive_name} 
                        onFocus={() => setShowAdditiveList(true)} 
                        onBlur={() => setTimeout(() => setShowAdditiveList(false), 200)} 
                        onChange={(e) => setFormData({...formData, additive_name: e.target.value})} 
                        className="pl-11 pr-12 h-12 rounded-2xl border-zinc-300 bg-white font-medium focus:ring-4 focus:ring-indigo-100 shadow-sm transition-all" 
                      />
                      <Search className="absolute left-4 top-4 w-4 h-4 text-zinc-400 group-focus-within:text-indigo-600 transition-colors" />
                      <div className="absolute right-4 top-4 text-[10px] font-black text-zinc-300 uppercase">Addit</div>
                    </div>
                    {showAdditiveList && price_db.additives && (
                      <div className="absolute z-50 w-full mt-2 bg-white/95 backdrop-blur-xl border border-zinc-200 rounded-2xl shadow-xl max-h-48 overflow-y-auto">
                        {Object.keys(price_db.additives).filter(a => a.toLowerCase().includes(formData.additive_name.toLowerCase())).map(a => (
                          <div key={a} className="px-5 py-3 text-sm hover:bg-indigo-50 cursor-pointer border-b border-zinc-50 font-semibold" onMouseDown={() => setFormData({...formData, additive_name: a})}>{a}</div>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="sm:col-span-1">
                    <InputGroup label="Volume" unit="mL" val={formData.additive_volume} k="additive_volume" s={setFormData} d={formData} placeholder="0" />
                  </div>
                </div>

                {/* 3. Modulator */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 items-start">
                  <div className="sm:col-span-2 space-y-2 relative">
                    <Label className="text-[11px] font-bold text-zinc-500 ml-1 uppercase tracking-wider">3. Modulator Name</Label>
                    <div className="relative group">
                      <Input 
                        placeholder="Mohon diisi" 
                        value={formData.modulator_name} 
                        onFocus={() => setShowModulatorList(true)} 
                        onBlur={() => setTimeout(() => setShowModulatorList(false), 200)} 
                        onChange={(e) => setFormData({...formData, modulator_name: e.target.value})} 
                        className="pl-11 pr-12 h-12 rounded-2xl border-zinc-300 bg-white font-medium focus:ring-4 focus:ring-indigo-100 shadow-sm transition-all" 
                      />
                      <Search className="absolute left-4 top-4 w-4 h-4 text-zinc-400 group-focus-within:text-indigo-600 transition-colors" />
                      <div className="absolute right-4 top-4 text-[10px] font-black text-zinc-300 uppercase">Mod</div>
                    </div>
                    {showModulatorList && price_db.modulators && (
                      <div className="absolute z-50 w-full mt-2 bg-white/95 backdrop-blur-xl border border-zinc-200 rounded-2xl shadow-xl max-h-48 overflow-y-auto">
                        {Object.keys(price_db.modulators).filter(m => m.toLowerCase().includes(formData.modulator_name.toLowerCase())).map(m => (
                          <div key={m} className="px-5 py-3 text-sm hover:bg-indigo-50 cursor-pointer border-b border-zinc-50 font-semibold" onMouseDown={() => setFormData({...formData, modulator_name: m})}>{m}</div>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="sm:col-span-1">
                    <InputGroup label="Volume" unit="mL" val={formData.modulator_volume} k="modulator_volume" s={setFormData} d={formData} placeholder="0" />
                  </div>
                </div>

                {/* 4. Metal */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 items-start">
                  <div className="sm:col-span-2 space-y-2 relative">
                    <Label className="text-[11px] font-bold text-zinc-500 ml-1 uppercase tracking-wider">4. Metal Name</Label>
                    <div className="relative group">
                      <Input 
                        placeholder="Mohon diisi" 
                        value={formData.metal_name} 
                        onFocus={() => setShowMetalList(true)} 
                        onBlur={() => setTimeout(() => setShowMetalList(false), 200)} 
                        onChange={(e) => setFormData({...formData, metal_name: e.target.value})} 
                        className="pl-11 pr-12 h-12 rounded-2xl border-zinc-300 bg-white font-medium focus:ring-4 focus:ring-indigo-100 shadow-sm transition-all" 
                      />
                      <Search className="absolute left-4 top-4 w-4 h-4 text-zinc-400 group-focus-within:text-indigo-600 transition-colors" />
                      <div className="absolute right-4 top-4 text-[10px] font-black text-zinc-300 uppercase">Metal</div>
                    </div>
                    {showMetalList && price_db.metals && (
                      <div className="absolute z-50 w-full mt-2 bg-white/95 backdrop-blur-xl border border-zinc-200 rounded-2xl shadow-xl max-h-48 overflow-y-auto">
                        {Object.keys(price_db.metals).filter(m => m.toLowerCase().includes(formData.metal_name.toLowerCase())).map(m => (
                          <div key={m} className="px-5 py-3 text-sm hover:bg-indigo-50 cursor-pointer border-b border-zinc-50 font-semibold" onMouseDown={() => setFormData({...formData, metal_name: m})}>{m}</div>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="sm:col-span-1">
                    <InputGroup label="Mass" unit="g" val={formData.metal_mass} k="metal_mass" s={setFormData} d={formData} placeholder="0" />
                  </div>
                </div>

                {/* 5. Linker & Auto SMILES */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 items-start">
                  <div className="sm:col-span-2 space-y-2 relative">
                    <Label className="text-[11px] font-bold text-zinc-500 ml-1 uppercase tracking-wider">5. Linker Name</Label>
                    <div className="relative group">
                      <Input 
                        placeholder="Mohon diisi" 
                        value={formData.linker_name} 
                        onFocus={() => setShowLinkerList(true)} 
                        onBlur={() => setTimeout(() => setShowLinkerList(false), 200)} 
                        onChange={(e) => setFormData({...formData, linker_name: e.target.value})} 
                        className="pl-11 pr-12 h-12 rounded-2xl border-zinc-300 bg-white font-medium focus:ring-4 focus:ring-indigo-100 shadow-sm transition-all" 
                      />
                      <Database className="absolute left-4 top-4 w-4 h-4 text-zinc-400 group-focus-within:text-indigo-600 transition-colors" />
                      <div className="absolute right-4 top-4 text-[10px] font-black text-zinc-300 uppercase">Linker</div>
                    </div>
                    {showLinkerList && price_db.linkers && (
                      <div className="absolute z-50 w-full mt-2 bg-white/95 backdrop-blur-xl border border-zinc-200 rounded-2xl shadow-xl max-h-48 overflow-y-auto">
                        {Object.keys(price_db.linkers).filter(l => l.toLowerCase().includes(formData.linker_name.toLowerCase())).map(l => (
                          <div key={l} className="px-5 py-3 text-sm hover:bg-indigo-50 cursor-pointer border-b border-zinc-50 font-semibold" onMouseDown={() => setFormData({...formData, linker_name: l})}>{l}</div>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="sm:col-span-1">
                    <InputGroup label="Mass" unit="mg" val={formData.linker_mass} k="linker_mass" s={setFormData} d={formData} placeholder="0" />
                  </div>
                </div>
                <div className="space-y-1">
                  <Label className="text-[10px] font-bold text-zinc-400 ml-1 uppercase italic tracking-tighter">SMILES (Auto-filled)</Label>
                  <Input value={formData.smiles} readOnly placeholder="Auto-filled from database..." className="h-10 rounded-2xl border-none bg-zinc-50 text-zinc-500 font-mono text-[10px] italic shadow-inner" />
                </div>

                {/* 6. Product Mass */}
                <InputGroup icon={<Scale className="w-4 h-4"/>} label="6. Product Mass" unit="mg" val={formData.product_mass} k="product_mass" s={setFormData} d={formData} placeholder="0" />

                <div className="grid grid-cols-2 gap-4">
                    <InputGroup icon={<Clock className="w-4 h-4"/>} label="9. Time" unit="h" val={formData.reaction_time} k="reaction_time" s={setFormData} d={formData} placeholder="0" />
                    <InputGroup icon={<Thermometer className="w-4 h-4"/>} label="10. Temp" unit="°C" val={formData.temperature} k="temperature" s={setFormData} d={formData} placeholder="0" />
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* RESULTS SECTION */}
        <section className="lg:col-span-8 relative animate-in fade-in zoom-in duration-1000">
          <div className="bg-white/90 backdrop-blur-3xl rounded-[48px] p-6 md:p-12 border border-white shadow-xl lg:sticky lg:top-28 space-y-8 md:space-y-12 min-h-[750px] flex flex-col overflow-hidden">
            {loading && <div className="absolute top-0 left-0 w-full h-1.5 bg-indigo-600 animate-pulse" />}
            
            <header className="flex flex-col sm:flex-row justify-between items-start gap-4 mb-12">
              <div className="space-y-2">
                <h3 className="text-[10px] md:text-[12px] font-black text-zinc-400 uppercase tracking-[0.3em]">Screening Result</h3>
                <h1 className={`text-5xl md:text-8xl font-black tracking-tighter transition-colors duration-500 ${results ? (results.is_overall_feasible ? 'text-indigo-600' : 'text-red-500') : 'text-zinc-200'}`}>
                  {loading ? "Analyzing..." : results ? (results.is_overall_feasible ? "Feasible" : "Denied") : "Pending"}
                </h1>
              </div>
              {results && (
                <div className="flex flex-col items-start sm:items-end gap-3">
                    <Badge className="bg-zinc-900 text-white rounded-full px-5 py-2 text-[10px] md:text-xs font-bold uppercase tracking-widest shadow-lg">{results.stability_status}</Badge>
                </div>
              )}
            </header>

            {results ? (
              <div className="space-y-10 md:space-y-12 animate-in fade-in slide-in-from-bottom-4 duration-1000">
                
                {/* Bagian 1: Metrik Hidrogen */}
                <div className="space-y-6">
                  <div className="flex items-center gap-4 text-zinc-400">
                    <h4 className="text-[10px] font-bold uppercase tracking-widest">Hydrogen Metrics</h4>
                    <div className="h-px bg-zinc-100 flex-1" />
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 md:gap-6">
                    <ResultBox label="Working Uptake Gravimetric" val={results.gravimetric_h2} unit="wt%" target="5.5" ok={results.gravimetric_h2 >= 5.5} />
                    <ResultBox label="Working Uptake Volumetric" val={results.volumetric_h2} unit="g/L" target="40" ok={results.volumetric_h2 >= 40} />
                  </div>
                </div>

                {/* Bagian 2: Ekonomi & Harga */}
                <div className="space-y-6">
                  <div className="flex items-center gap-4 text-zinc-400">
                    <h4 className="text-[10px] font-bold uppercase tracking-widest">Economic Analysis</h4>
                    <div className="h-px bg-zinc-100 flex-1" />
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                    <ResultBox icon={<DollarSign className="w-4 h-4"/>} label="MOF Production Cost" val={results.mof_cost} unit="USD/kg" target="30" ok={results.mof_cost <= 30} />
                    <ResultBox icon={<DollarSign className="w-4 h-4"/>} label="Hydrogen Storage Cost" val={results.storage_cost} unit="USD/kg H2" target="300" ok={results.storage_cost <= 300} />
                  </div>
                </div>

                {/* Bagian 3: Energy Synthesis (Table Layout & Metrics Boxes) */}
                <div className="space-y-6">
                  <div className="flex items-center gap-4 text-zinc-400">
                    <h4 className="text-[10px] font-bold uppercase tracking-widest">Energy Synthesis</h4>
                    <div className="h-px bg-zinc-100 flex-1" />
                  </div>
                  
                  {/* Table Energi Sensible */}
                  <div className="bg-white rounded-2xl border border-zinc-200 overflow-hidden shadow-sm">
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-sm whitespace-nowrap">
                        <thead className="bg-zinc-50/50 border-b border-zinc-200 text-zinc-500">
                          <tr>
                            <th scope="col" className="px-6 py-4 font-bold text-xs uppercase tracking-wider border-r border-zinc-200" rowSpan={2}>
                              Cp linker 1<br/><span className="text-[10px] font-medium text-zinc-400 normal-case">(J/mol.K)</span>
                            </th>
                            <th scope="col" className="px-6 py-3 font-bold text-xs uppercase tracking-wider text-center" colSpan={6}>
                              Energi Sensible (J)
                            </th>
                          </tr>
                          <tr className="bg-zinc-50 text-[11px] border-t border-zinc-200">
                            <th scope="col" className="px-4 py-2 font-semibold">Solvent</th>
                            <th scope="col" className="px-4 py-2 font-semibold">Additive</th>
                            <th scope="col" className="px-4 py-2 font-semibold">Modulator</th>
                            <th scope="col" className="px-4 py-2 font-semibold">Metal</th>
                            <th scope="col" className="px-4 py-2 font-semibold">Linker</th>
                            <th scope="col" className="px-4 py-2 font-semibold text-indigo-600">Total Sensible</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-zinc-100 bg-white">
                          <tr className="hover:bg-zinc-50 transition-colors">
                            <td className="px-6 py-4 font-mono text-zinc-600 border-r border-zinc-100">{results.cp_linker || "0.00"}</td>
                            <td className="px-4 py-4 font-mono text-zinc-800">{results.e_sensible_solvent || "0.00"}</td>
                            <td className="px-4 py-4 font-mono text-zinc-800">{results.e_sensible_additive || "0.00"}</td>
                            <td className="px-4 py-4 font-mono text-zinc-800">{results.e_sensible_modulator || "0.00"}</td>
                            <td className="px-4 py-4 font-mono text-zinc-800">{results.e_sensible_metal || "0.00"}</td>
                            <td className="px-4 py-4 font-mono text-zinc-800">{results.e_sensible_linker || "0.00"}</td>
                            <td className="px-4 py-4 font-mono font-bold text-indigo-600">{results.e_sensible_total || "0.00"}</td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {/* Energy Metric Boxes */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 mt-6">
                    <EconMiniCard icon={<Zap className="w-4 h-4 text-amber-500" />} label="Q Heat" val={results.q_energy || "0.00"} unit="MJ" />
                    <EconMiniCard icon={<AlertTriangle className="w-4 h-4 text-orange-500" />} label="Q Loss" val={results.q_loss || "0.00"} unit="MJ" />
                    <EconMiniCard icon={<Activity className="w-4 h-4 text-blue-500" />} label="E Stirr" val={results.e_stirr || "0.00"} unit="MJ" />
                    <EconMiniCard icon={<Zap className="w-4 h-4 text-emerald-500" />} label="E Tot" val={results.e_tot || "0.00"} unit="MJ" />
                  </div>
                </div>

                {/* Bagian 4: Struktur */}
                <div className="space-y-6 pt-6 border-t border-zinc-100">
                  <div className="flex items-center gap-4 text-zinc-400">
                    <h4 className="text-[10px] font-bold uppercase tracking-widest">Structure Analysis</h4>
                    <div className="h-px bg-zinc-100 flex-1" />
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 md:gap-6">
                    <div className="flex justify-between items-center bg-indigo-50/50 p-4 md:p-6 rounded-2xl border border-indigo-100/50 transition-all hover:scale-[1.02] shadow-sm">
                      <span className="text-xl md:text-2xl font-black text-indigo-600 tracking-tighter">ΔE</span>
                      <span className="font-mono font-bold text-lg md:text-2xl text-indigo-950">
                        {results.delta_e} <span className="text-sm font-medium text-zinc-400 normal-case">kJ/mol</span>
                      </span>
                    </div>
                    <div className="flex justify-between items-center bg-zinc-50 p-4 md:p-6 rounded-2xl border border-zinc-100 transition-all hover:scale-[1.02] shadow-sm">
                      <span className="text-[10px] font-bold text-zinc-400 uppercase tracking-widest">RMSD</span>
                      <span className="font-mono font-bold text-lg md:text-2xl text-zinc-800">
                        {results.rmsd} <span className="text-sm font-medium text-zinc-400 normal-case">Å</span>
                      </span>
                    </div>
                  </div>
                </div>

              </div>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center text-center space-y-4">
                <Loader2 className={`w-12 h-12 md:w-16 md:h-16 relative ${loading ? 'animate-spin text-indigo-600' : 'text-zinc-100 opacity-20'}`} />
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
    <div className="flex items-center gap-3 mb-2">
      <div className="p-2 bg-indigo-50 rounded-lg text-indigo-600 shadow-sm">{icon}</div>
      <p className="text-[10px] font-black text-zinc-400 uppercase tracking-[0.2em]">{text}</p>
    </div>
  );
}

function InputGroup({ icon, label, unit, val, k, s, d, placeholder }: any) {
  return (
    <div className="space-y-2">
      <Label className="text-[10px] md:text-[11px] font-bold text-zinc-500 ml-1 uppercase tracking-wider">{label}</Label>
      <div className="relative flex items-center group">
        {icon && <div className="absolute left-4 text-zinc-400 group-focus-within:text-indigo-600 transition-colors duration-300">{icon}</div>}
        <Input 
          type="number" 
          step="any"
          placeholder={placeholder || "0"}
          value={val} 
          onChange={(e) => s({...d, [k]: e.target.value})} 
          className={`pr-12 rounded-xl md:rounded-2xl border-zinc-300 h-11 md:h-12 text-sm font-semibold focus-visible:ring-4 focus-visible:ring-indigo-100 transition-all shadow-sm ${icon ? 'pl-11' : 'pl-4'}`} 
        />
        {unit && <div className="absolute right-4 text-[10px] font-black text-zinc-300 uppercase">{unit}</div>}
      </div>
    </div>
  );
}

function ResultBox({ icon, label, val, unit, target, ok }: any) {
  return (
    <div className={`p-6 md:p-8 rounded-[24px] md:rounded-[32px] border flex justify-between items-center transition-all hover:scale-[1.02] shadow-sm ${ok ? 'bg-indigo-50/30 border-indigo-100/50' : 'bg-red-50/30 border-red-100/50'}`}>
      <div className="space-y-1">
        <p className="text-[10px] font-black text-zinc-400 uppercase tracking-widest">{label}</p>
        <div className="flex items-baseline">
            <span className="text-3xl md:text-4xl font-black tracking-tighter text-[#1D1D1F]">{val}</span>
            <span className="ml-2 text-lg font-medium text-zinc-400 normal-case leading-none">{unit}</span>
        </div>
        <div className="flex items-center gap-2 mt-2">
            <p className="text-[10px] font-bold text-zinc-400 tracking-tight">Target: {target ? `≥ ${target}` : ''} <span className="normal-case">{unit}</span></p>
            {ok ? (
                <div className="flex items-center gap-1 text-emerald-600 text-[10px] font-bold">
                    <CheckCircle2 className="w-3 h-3" />
                    <span>Pass</span>
                </div>
            ) : (
                <div className="flex items-center gap-1 text-red-600 text-[10px] font-bold">
                    <XCircle className="w-3 h-3" />
                    <span>Fail</span>
                </div>
            )}
        </div>
      </div>
      <div className={`p-3 md:p-4 rounded-xl shadow-inner ${ok ? 'bg-indigo-100 text-indigo-600' : 'bg-red-100 text-red-600'}`}>
        {icon ? icon : (ok ? <CheckCircle2 className="w-5 h-5 md:w-6 md:h-6 stroke-[3]" /> : <XCircle className="w-5 h-5 md:w-6 md:h-6 stroke-[3]" />)}
      </div>
    </div>
  );
}

function EconMiniCard({ icon, label, val, unit }: any) {
  return (
    <div className="bg-white p-4 md:p-6 rounded-[20px] md:rounded-[24px] border border-zinc-100 text-center space-y-2 shadow-sm transition-all hover:scale-[1.02]">
      <div className="flex items-center justify-center gap-2">
        {icon}
        <span className="text-[9px] md:text-[10px] font-black text-zinc-400 uppercase tracking-widest">{label}</span>
      </div>
      <p className="text-xl md:text-2xl font-black tracking-tight text-zinc-800">
        {val} <span className="ml-1 text-[10px] font-medium text-zinc-400 normal-case">{unit}</span>
      </p>
    </div>
  );
}