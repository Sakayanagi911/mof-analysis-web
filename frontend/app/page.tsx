"use client";

import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
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
  const [price_db, setPriceDb] = useState<any>({ 
    metals: {}, 
    solvents: {}, 
    additives: {}, 
    modulators: {} 
  });

  const [showMetalList, setShowMetalList] = useState(false);
  const [showSmilesDropdown, setShowSmilesDropdown] = useState(false);
  const [showSolventList, setShowSolventList] = useState(false);
  const [showAdditiveList, setShowAdditiveList] = useState(false);
  const [showModulatorList, setShowModulatorList] = useState(false);
  
  // Search terms untuk setiap dropdown - default FATQID values
  const [solventSearch, setSolventSearch] = useState("DMF");
  const [additiveSearch, setAdditiveSearch] = useState("");
  const [modulatorSearch, setModulatorSearch] = useState("HNO3");
  const [metalSearch, setMetalSearch] = useState("CuSO₄·5H₂O");
  
  const [formData, setFormData] = useState({
    // Geometric Factors - default values (LCD = 12.0)
    pv: "1.2", gsa: "3000", vsa: "1500", lcd: "12.0", pld: "8", vf: "0.5", density: "0.8",
    
    // FATQID (Use Case 1) - Default values (kecuali SMILES tetap kosong)
    solvent_name: "DMF",   
    solvent_volume: "2", 
    additive_name: "",  
    additive_volume: "", 
    modulator_name: "HNO3", 
    modulator_volume: "0.05", 
    modulator_concentration: "4.44",  // FATQID concentration
    metal_name: "CuSO₄·5H₂O",     
    metal_mass: "8", 
    smiles: "",         // Tetap kosong seperti sebelumnya
    linker_name: "",    // Auto-filled dari SMILES lookup
    linker_mass: "5", 
    product_mass: "9.12",   // FATQID product mass
    reaction_time: "24", 
    temperature: "85"   // FATQID temperature
  });

  const [smilesMapping, setSmilesMapping] = useState<any>({});
  // REMOVED: concentrationMapping - tidak ada auto-fill

  useEffect(() => {
    fetch("http://127.0.0.1:8000/get-prices")
      .then(res => res.json())
      .then(data => { if (data && !data.error) setPriceDb(data); })
      .catch(err => console.error("Database offline"));
    
    // Load SMILES mapping
    fetch("http://127.0.0.1:8000/get-smiles-mapping")
      .then(res => res.json())
      .then(data => { if (data && !data.error) setSmilesMapping(data.mapping || {}); })
      .catch(err => console.error("SMILES mapping offline"));
    
    // REMOVED: Load concentration mapping - user input manual
  }, []);

  // Auto-fill Linker Name dari SMILES (tanpa auto-fill concentration)
  useEffect(() => {
    if (formData.smiles && smilesMapping[formData.smiles]) {
      const linkerData = smilesMapping[formData.smiles];
      
      setFormData(prev => ({
        ...prev,
        linker_name: linkerData.linker_name || ""
        // REMOVED: auto-fill concentration - user input manual
      }));
    }
  }, [formData.smiles, smilesMapping]);

  // Separate calculation functions for different sections
  const calculateHydrogenMetrics = useCallback(() => {
    const f_pv = parseFloat(formData.pv) || 1.2;
    const f_gsa = parseFloat(formData.gsa) || 3000;
    const f_vsa = parseFloat(formData.vsa) || 1500;
    const f_lcd = parseFloat(formData.lcd) || 12.1;
    const f_pld = parseFloat(formData.pld) || 8.0;
    const f_density = parseFloat(formData.density) || 0.8;
    const f_vf = parseFloat(formData.vf) || 0.5;
    const valid_vf = f_vf > 1.0 ? f_vf / 100.0 : f_vf;

    // Calculate WUG using the correct polynomial equation (4-1)
    const p = f_density;
    const GSA = f_gsa;
    const VSA = f_vsa;
    const VF = valid_vf;
    const PV = f_pv;
    const LCD = f_lcd;
    const PLD = f_pld;

    const wug = (
      -4.47194 + (1.77349 * p) + (0.000511149 * GSA) + (0.00163429 * VSA) + 
      (3.92696 * VF) + (5.59522 * PV) - (0.0764434 * LCD) + (0.262302 * PLD) - 
      (0.163317 * (p**2)) - (0.00133171 * p * GSA) + (7.69048e-5 * p * VSA) - 
      (2.66592 * p * VF) + (2.45092 * p * PV) + (0.089082 * p * LCD) - 
      (0.0975448 * p * PLD) - (4.1166e-8 * (GSA**2)) - (1.15768e-7 * GSA * VSA) + 
      (0.00280453 * GSA * VF) - (2.35326e-5 * GSA * PV) + (8.39123e-6 * GSA * LCD) - 
      (3.89128e-6 * GSA * PLD) + (2.21456e-7 * (VSA**2)) - (0.00231186 * VSA * VF) - 
      (0.00180075 * VSA * PV) + (4.34998e-6 * VSA * LCD) + (1.65433e-5 * VSA * PLD) + 
      (4.52648 * (VF**2)) - (3.82519 * VF * PV) - (0.0639716 * VF * LCD) - 
      (0.283064 * VF * PLD) - (0.0213098 * (PV**2)) + (0.000824477 * PV * LCD) + 
      (0.00253194 * PV * PLD) + (0.000521033 * (LCD**2)) + (0.000700743 * LCD * PLD) - 
      (0.000244913 * (PLD**2))
    );

    // Calculate WUV using the correct polynomial equation (4-2)
    const wuv = (
      -49.6238 + (17.4843 * p) - (0.000310481 * GSA) + (0.0214365 * VSA) + 
      (32.4082 * VF) + (14.1933 * PV) + (0.0660557 * LCD) + (1.66494 * PLD) - 
      (1.79789 * (p**2)) - (0.00754047 * p * GSA) - (0.0012505 * p * VSA) - 
      (22.99 * p * VF) + (69.0864 * p * PV) + (0.861169 * p * LCD) - 
      (0.523851 * p * PLD) + (1.51676e-7 * (GSA**2)) + (3.18358e-7 * GSA * VSA) + 
      (0.0145422 * GSA * VF) - (5.75705e-5 * GSA * PV) + (0.000157672 * GSA * LCD) - 
      (2.93554e-5 * GSA * PLD) + (7.11672e-7 * (VSA**2)) - (0.0162344 * VSA * VF) - 
      (0.0208807 * VSA * PV) + (3.334e-5 * VSA * LCD) + (0.000196064 * VSA * PLD) + 
      (44.1803 * (VF**2)) - (14.2407 * VF * PV) - (1.95209 * VF * LCD) - 
      (2.23509 * VF * PLD) - (0.0384937 * (PV**2)) - (0.00185746 * PV * LCD) + 
      (0.0410538 * PV * PLD) + (0.00735029 * (LCD**2)) + (0.00119741 * LCD * PLD) + 
      (0.00386859 * (PLD**2))
    );

    return {
      gravimetric_h2: Math.max(0, wug),
      volumetric_h2: Math.max(0, wuv),
      doe_feasible: wug >= 5.5 && wuv >= 40.0
    };
  }, [formData.pv, formData.gsa, formData.vsa, formData.lcd, formData.pld, formData.density, formData.vf]);

  const calculateCostAndEnergy = useCallback(async () => {
    // Only calculate if synthesis conditions are filled
    if (!formData.metal_name || !formData.smiles) {
      return {
        mof_cost: 0,
        storage_cost: 0,
        q_energy: 0,
        q_loss: 0,
        e_stirr: 0,
        e_tot: 0,
        econ_feasible: false
      };
    }

    const data = new FormData();
    
    // Add synthesis condition fields
    const synthesisFields = {
      'metal_name': formData.metal_name,
      'metal_mass': formData.metal_mass || "0",
      'smiles': formData.smiles,
      'linker_mass': formData.linker_mass || "0",
      'solvent_name': formData.solvent_name || "-",
      'solvent_volume': formData.solvent_volume || "0",
      'additive_name': formData.additive_name || "-",
      'additive_volume': formData.additive_volume || "0",
      'modulator_name': formData.modulator_name || "-",
      'modulator_volume': formData.modulator_volume || "0",
      'modulator_concentration': formData.modulator_concentration || "100.0",  // NEW: Send concentration
      'product_mass': formData.product_mass || "0",
      'reaction_time': formData.reaction_time || "24",
      'temperature': formData.temperature || "120",
      // Add geometric factors for calculation
      'pv': formData.pv, 'gsa': formData.gsa, 'vsa': formData.vsa,
      'lcd': formData.lcd, 'pld': formData.pld, 'vf': formData.vf, 'density': formData.density
    };

    Object.entries(synthesisFields).forEach(([key, value]) => {
      data.append(key, String(value));
    });

    try {
      const res = await fetch("http://127.0.0.1:8000/analyze", { method: "POST", body: data });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      
      const result = await res.json();
      if (result.status === "success") {
        return {
          mof_cost: result.results.mof_cost || 0,
          storage_cost: result.results.storage_cost || 0,
          q_energy: result.results.q_energy || 0,
          q_loss: result.results.q_loss || 0,
          e_stirr: result.results.e_stirr || 0,
          e_tot: result.results.e_tot || 0,
          econ_feasible: result.results.econ_feasible || false,
          // Energy details for table
          cp_linker: result.results.cp_linker || 0,
          linker_mw: result.results.linker_mw || 0,
          e_sensible_solvent: result.results.e_sensible_solvent || 0,
          e_sensible_additive: result.results.e_sensible_additive || 0,
          e_sensible_modulator: result.results.e_sensible_modulator || 0,
          e_sensible_metal: result.results.e_sensible_metal || 0,
          e_sensible_linker: result.results.e_sensible_linker || 0,
          e_sensible_total: result.results.e_sensible_total || 0
        };
      }
    } catch (err) {
      console.error("Cost/Energy calculation failed:", err);
    }

    return {
      mof_cost: 0, storage_cost: 0, q_energy: 0, q_loss: 0, e_stirr: 0, e_tot: 0, econ_feasible: false,
      cp_linker: 0, linker_mw: 0, e_sensible_solvent: 0, e_sensible_additive: 0, 
      e_sensible_modulator: 0, e_sensible_metal: 0, e_sensible_linker: 0, e_sensible_total: 0
    };
  }, [
    formData.metal_name, formData.smiles, formData.metal_mass, formData.linker_mass,
    formData.solvent_name, formData.solvent_volume, formData.additive_name, formData.additive_volume,
    formData.modulator_name, formData.modulator_volume, formData.modulator_concentration, formData.product_mass,  // Added concentration
    formData.reaction_time, formData.temperature,
    formData.pv, formData.gsa, formData.vsa, formData.lcd, formData.pld, formData.vf, formData.density
  ]);

  const calculateStructureAnalysis = useCallback(async () => {
    if (!file || !file.name.endsWith('.cif')) {
      return {
        conformational_energy_kcal: 0.0,
        rmsd_final_angstrom: 0.0,
        me_delta_length_angstrom: 0.0,
        me_delta_angle_deg: 0.0,
        structure_status: "No CIF file uploaded",
        structure_feasible: null,
        xtb_available: true
      };
    }

    const data = new FormData();
    data.append('file', file);
    
    // Add minimal required fields for structure analysis
    data.append('metal_name', formData.metal_name || "Cu");
    data.append('smiles', formData.smiles || "O=C(O)c1ccc(cc1)C(=O)O");
    data.append('pv', formData.pv); data.append('gsa', formData.gsa); data.append('vsa', formData.vsa);
    data.append('lcd', formData.lcd); data.append('pld', formData.pld); data.append('vf', formData.vf); 
    data.append('density', formData.density);
    
    // Add default values for other required fields
    ['metal_mass', 'linker_mass', 'product_mass', 'reaction_time', 'temperature'].forEach(field => {
      data.append(field, "0");
    });
    ['solvent_name', 'additive_name', 'modulator_name'].forEach(field => {
      data.append(field, "-");
    });
    ['solvent_volume', 'additive_volume', 'modulator_volume'].forEach(field => {
      data.append(field, "0");
    });

    try {
      const res = await fetch("http://127.0.0.1:8000/analyze", { method: "POST", body: data });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      
      const result = await res.json();
      if (result.status === "success") {
        return {
          conformational_energy_kcal: result.results.conformational_energy_kcal || 0.0,
          rmsd_final_angstrom: result.results.rmsd_final_angstrom || 0.0,
          me_delta_length_angstrom: result.results.me_delta_length_angstrom || 0.0,
          me_delta_angle_deg: result.results.me_delta_angle_deg || 0.0,
          structure_status: result.results.structure_status || "Analysis completed",
          structure_feasible: result.results.structure_feasible,
          xtb_available: result.results.xtb_available || true
        };
      }
    } catch (err) {
      console.error("Structure analysis failed:", err);
    }

    return {
      conformational_energy_kcal: 0.0, rmsd_final_angstrom: 0.0, 
      me_delta_length_angstrom: 0.0, me_delta_angle_deg: 0.0,
      structure_status: "Analysis failed", structure_feasible: false, xtb_available: true
    };
  }, [file, formData.metal_name, formData.smiles, formData.pv, formData.gsa, formData.vsa, formData.lcd, formData.pld, formData.vf, formData.density]);

  // State for different calculation results
  const [hydrogenMetrics, setHydrogenMetrics] = useState({
    gravimetric_h2: 0, volumetric_h2: 0, doe_feasible: false
  });
  
  const [costEnergyResults, setCostEnergyResults] = useState({
    mof_cost: 0, storage_cost: 0, q_energy: 0, q_loss: 0, e_stirr: 0, e_tot: 0, econ_feasible: false,
    cp_linker: 0, linker_mw: 0, e_sensible_solvent: 0, e_sensible_additive: 0, 
    e_sensible_modulator: 0, e_sensible_metal: 0, e_sensible_linker: 0, e_sensible_total: 0
  });
  
  const [structureResults, setStructureResults] = useState({
    conformational_energy_kcal: 0.0, rmsd_final_angstrom: 0.0, 
    me_delta_length_angstrom: 0.0, me_delta_angle_deg: 0.0,
    structure_status: "No CIF file uploaded", structure_feasible: null, xtb_available: true
  });

  const [loadingStates, setLoadingStates] = useState({
    hydrogen: false, costEnergy: false, structure: false
  });

  // Real-time calculation effects for different sections
  
  // 1. Hydrogen Metrics - instant calculation (no API call needed)
  useEffect(() => {
    const metrics = calculateHydrogenMetrics();
    setHydrogenMetrics(metrics);
  }, [calculateHydrogenMetrics]);

  // 2. Cost & Energy - API call with debounce for synthesis conditions
  useEffect(() => {
    if (formData.metal_name && formData.smiles) {
      setLoadingStates(prev => ({ ...prev, costEnergy: true }));
      const timer = setTimeout(async () => {
        const results = await calculateCostAndEnergy();
        setCostEnergyResults(results);
        setLoadingStates(prev => ({ ...prev, costEnergy: false }));
      }, 500); // 500ms debounce for cost/energy
      return () => clearTimeout(timer);
    } else {
      // Reset when required fields are empty
      setCostEnergyResults({
        mof_cost: 0, storage_cost: 0, q_energy: 0, q_loss: 0, e_stirr: 0, e_tot: 0, econ_feasible: false,
        cp_linker: 0, linker_mw: 0, e_sensible_solvent: 0, e_sensible_additive: 0, 
        e_sensible_modulator: 0, e_sensible_metal: 0, e_sensible_linker: 0, e_sensible_total: 0
      });
    }
  }, [calculateCostAndEnergy]);

  // 3. Structure Analysis - API call when file changes
  useEffect(() => {
    if (file && file.name.endsWith('.cif')) {
      setLoadingStates(prev => ({ ...prev, structure: true }));
      const timer = setTimeout(async () => {
        const results = await calculateStructureAnalysis();
        setStructureResults(results);
        setLoadingStates(prev => ({ ...prev, structure: false }));
      }, 300); // 300ms debounce for structure
      return () => clearTimeout(timer);
    } else {
      // Reset when no file
      setStructureResults({
        conformational_energy_kcal: 0.0, rmsd_final_angstrom: 0.0, 
        me_delta_length_angstrom: 0.0, me_delta_angle_deg: 0.0,
        structure_status: "No CIF file uploaded", structure_feasible: null, xtb_available: true
      });
    }
  }, [calculateStructureAnalysis]);

  // Kalkulasi Live Cost Berdasarkan Database & Input
  const dynamicCosts = useMemo(() => {
    return {
      mof_cost: costEnergyResults.mof_cost.toFixed(3),
      storage_cost: costEnergyResults.storage_cost.toFixed(3)
    };
  }, [costEnergyResults.mof_cost, costEnergyResults.storage_cost]);

  // Overall feasibility calculation
  const overallFeasibility = useMemo(() => {
    const MAX_MOF_COST = 30.0;
    const MAX_STORAGE_COST = 300.0;
    const MAX_REACTION_TIME = 48.0;
    const MAX_TEMPERATURE = 180.0;

    const timeOk = parseFloat(formData.reaction_time) <= MAX_REACTION_TIME;
    const tempOk = parseFloat(formData.temperature) <= MAX_TEMPERATURE;
    const costOk = costEnergyResults.mof_cost <= MAX_MOF_COST && costEnergyResults.storage_cost <= MAX_STORAGE_COST;
    const structureOk = structureResults.structure_feasible !== false;

    return {
      is_overall_feasible: hydrogenMetrics.doe_feasible && costOk && timeOk && tempOk && structureOk,
      doe_feasible: hydrogenMetrics.doe_feasible,
      econ_feasible: costOk,
      time_ok: timeOk,
      temp_ok: tempOk,
      structure_feasible: structureResults.structure_feasible
    };
  }, [hydrogenMetrics.doe_feasible, costEnergyResults.mof_cost, costEnergyResults.storage_cost, 
      formData.reaction_time, formData.temperature, structureResults.structure_feasible]);

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
                  <div className="sm:col-span-2 space-y-1.5 relative">
                    <Label className="text-[11px] font-medium text-zinc-500 ml-1 tracking-wide">1. Solvent Name</Label>
                    <div className="relative flex items-center group">
                      <Input 
                        placeholder="Search" 
                        value={solventSearch} 
                        onFocus={() => {
                          setShowSolventList(true);
                          setShowAdditiveList(false);
                          setShowModulatorList(false);
                          setShowMetalList(false);
                          setShowSmilesDropdown(false);
                        }} 
                        onBlur={() => setTimeout(() => setShowSolventList(false), 200)} 
                        onChange={(e) => {
                          setSolventSearch(e.target.value);
                          setFormData({...formData, solvent_name: e.target.value});
                        }} 
                        className="pl-11 pr-14 h-11 md:h-12 w-full rounded-[14px] border-zinc-200 bg-white/80 backdrop-blur-sm font-medium focus-visible:ring-4 focus-visible:ring-blue-500/10 focus-visible:border-blue-500/30 shadow-sm transition-all text-[14px]" 
                      />
                      <Search className="absolute left-4 w-4 h-4 text-zinc-400 group-focus-within:text-blue-500 transition-colors z-10 pointer-events-none" />
                      <div className="absolute right-4 text-[10px] font-semibold text-zinc-400 uppercase tracking-widest z-10 pointer-events-none">Solv</div>
                    </div>
                    {showSolventList && price_db.solvents && (
                      <div className="absolute z-50 w-full mt-2 bg-white/95 backdrop-blur-xl border border-zinc-200 rounded-2xl shadow-xl max-h-48 overflow-y-auto">
                        {Object.keys(price_db.solvents).filter(s => s.toLowerCase().includes(solventSearch.toLowerCase())).map(s => (
                          <div key={s} className="px-5 py-3 text-sm hover:bg-blue-50/50 hover:text-blue-600 cursor-pointer border-b border-zinc-50 font-medium transition-colors" onMouseDown={() => {
                            setFormData({...formData, solvent_name: s});
                            setSolventSearch(s);
                          }}>{s}</div>
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
                  <div className="sm:col-span-2 space-y-1.5 relative">
                    <Label className="text-[11px] font-medium text-zinc-500 ml-1 tracking-wide">2. Additive Name</Label>
                    <div className="relative flex items-center group">
                      <Input 
                        placeholder="Search" 
                        value={additiveSearch} 
                        onFocus={() => {
                          setShowAdditiveList(true);
                          setShowSolventList(false);
                          setShowModulatorList(false);
                          setShowMetalList(false);
                          setShowSmilesDropdown(false);
                        }} 
                        onBlur={() => setTimeout(() => setShowAdditiveList(false), 200)} 
                        onChange={(e) => {
                          setAdditiveSearch(e.target.value);
                          setFormData({...formData, additive_name: e.target.value});
                        }} 
                        className="pl-11 pr-14 h-11 md:h-12 w-full rounded-[14px] border-zinc-200 bg-white/80 backdrop-blur-sm font-medium focus-visible:ring-4 focus-visible:ring-blue-500/10 focus-visible:border-blue-500/30 shadow-sm transition-all text-[14px]" 
                      />
                      <Search className="absolute left-4 w-4 h-4 text-zinc-400 group-focus-within:text-blue-500 transition-colors z-10 pointer-events-none" />
                      <div className="absolute right-4 text-[10px] font-semibold text-zinc-400 uppercase tracking-widest z-10 pointer-events-none">Addit</div>
                    </div>
                    {showAdditiveList && price_db.additives && (
                      <div className="absolute z-50 w-full mt-2 bg-white/95 backdrop-blur-xl border border-zinc-200 rounded-2xl shadow-xl max-h-48 overflow-y-auto">
                        {Object.keys(price_db.additives).filter(a => a.toLowerCase().includes(additiveSearch.toLowerCase())).map(a => (
                          <div key={a} className="px-5 py-3 text-sm hover:bg-blue-50/50 hover:text-blue-600 cursor-pointer border-b border-zinc-50 font-medium transition-colors" onMouseDown={() => {
                            setFormData({...formData, additive_name: a});
                            setAdditiveSearch(a);
                          }}>{a}</div>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="sm:col-span-1">
                    <InputGroup label="Volume" unit="mL" val={formData.additive_volume} k="additive_volume" s={setFormData} d={formData} placeholder="0" />
                  </div>
                </div>

                {/* 3. Modulator */}
                <div className="space-y-4">
                  {/* Modulator Name - full width */}
                  <div className="space-y-1.5 relative">
                    <Label className="text-[11px] font-medium text-zinc-500 ml-1 tracking-wide">3. Modulator Name</Label>
                    <div className="relative flex items-center group">
                      <Input 
                        placeholder="Search" 
                        value={modulatorSearch} 
                        onFocus={() => {
                          setShowModulatorList(true);
                          setShowSolventList(false);
                          setShowAdditiveList(false);
                          setShowMetalList(false);
                          setShowSmilesDropdown(false);
                        }} 
                        onBlur={() => setTimeout(() => setShowModulatorList(false), 200)} 
                        onChange={(e) => {
                          setModulatorSearch(e.target.value);
                          setFormData({...formData, modulator_name: e.target.value});
                        }} 
                        className="pl-11 pr-14 h-11 md:h-12 w-full rounded-[14px] border-zinc-200 bg-white/80 backdrop-blur-sm font-medium focus-visible:ring-4 focus-visible:ring-blue-500/10 focus-visible:border-blue-500/30 shadow-sm transition-all text-[14px]" 
                      />
                      <Search className="absolute left-4 w-4 h-4 text-zinc-400 group-focus-within:text-blue-500 transition-colors z-10 pointer-events-none" />
                      <div className="absolute right-4 text-[10px] font-semibold text-zinc-400 uppercase tracking-widest z-10 pointer-events-none">Mod</div>
                    </div>
                    {showModulatorList && price_db.modulators && (
                      <div className="absolute z-50 w-full mt-2 bg-white/95 backdrop-blur-xl border border-zinc-200 rounded-2xl shadow-xl max-h-48 overflow-y-auto">
                        {Object.keys(price_db.modulators).filter(m => m.toLowerCase().includes(modulatorSearch.toLowerCase())).map(m => (
                          <div key={m} className="px-5 py-3 text-sm hover:bg-blue-50/50 hover:text-blue-600 cursor-pointer border-b border-zinc-50 font-medium transition-colors" onMouseDown={() => {
                            setFormData({...formData, modulator_name: m});
                            setModulatorSearch(m);
                          }}>{m}</div>
                        ))}
                      </div>
                    )}
                  </div>
                  
                  {/* Volume and Concentration side by side */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <InputGroup label="Volume" unit="mL" val={formData.modulator_volume} k="modulator_volume" s={setFormData} d={formData} placeholder="0" />
                    <InputGroup label="Concentration" unit="%" val={formData.modulator_concentration} k="modulator_concentration" s={setFormData} d={formData} placeholder="100.0" />
                  </div>
                </div>

                {/* 4. Metal */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 items-start">
                  <div className="sm:col-span-2 space-y-1.5 relative">
                    <Label className="text-[11px] font-medium text-zinc-500 ml-1 tracking-wide">4. Metal Name</Label>
                    <div className="relative flex items-center group">
                      <Input 
                        placeholder="Search" 
                        value={metalSearch} 
                        onFocus={() => {
                          setShowMetalList(true);
                          setShowSolventList(false);
                          setShowAdditiveList(false);
                          setShowModulatorList(false);
                          setShowSmilesDropdown(false);
                        }} 
                        onBlur={() => setTimeout(() => setShowMetalList(false), 200)} 
                        onChange={(e) => {
                          setMetalSearch(e.target.value);
                          setFormData({...formData, metal_name: e.target.value});
                        }} 
                        className="pl-11 pr-14 h-11 md:h-12 w-full rounded-[14px] border-zinc-200 bg-white/80 backdrop-blur-sm font-medium focus-visible:ring-4 focus-visible:ring-blue-500/10 focus-visible:border-blue-500/30 shadow-sm transition-all text-[14px]" 
                      />
                      <Search className="absolute left-4 w-4 h-4 text-zinc-400 group-focus-within:text-blue-500 transition-colors z-10 pointer-events-none" />
                      <div className="absolute right-4 text-[10px] font-semibold text-zinc-400 uppercase tracking-widest z-10 pointer-events-none">Metal</div>
                    </div>
                    {showMetalList && price_db.metals && (
                      <div className="absolute z-50 w-full mt-2 bg-white/95 backdrop-blur-xl border border-zinc-200 rounded-2xl shadow-xl max-h-48 overflow-y-auto">
                        {Object.keys(price_db.metals).filter(m => m.toLowerCase().includes(metalSearch.toLowerCase())).map(m => (
                          <div key={m} className="px-5 py-3 text-sm hover:bg-blue-50/50 hover:text-blue-600 cursor-pointer border-b border-zinc-50 font-medium transition-colors" onMouseDown={() => {
                            setFormData({...formData, metal_name: m});
                            setMetalSearch(m);
                          }}>{m}</div>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="sm:col-span-1">
                    <InputGroup label="Mass" unit="mg" val={formData.metal_mass} k="metal_mass" s={setFormData} d={formData} placeholder="0" />
                  </div>
                </div>

                {/* 5. SMILES (Dropdown dengan Search) & Auto-filled Linker Name */}
                <div className="space-y-4">
                  <div className="space-y-1.5 relative">
                    <Label className="text-[11px] font-medium text-zinc-500 ml-1 tracking-wide">5. Linker SMILES</Label>
                    <div className="relative flex items-center group">
                      <Input 
                        placeholder="Search or select SMILES..." 
                        value={formData.smiles} 
                        onFocus={() => {
                          setShowSmilesDropdown(true);
                          setShowSolventList(false);
                          setShowAdditiveList(false);
                          setShowModulatorList(false);
                          setShowMetalList(false);
                        }}
                        onBlur={() => setTimeout(() => setShowSmilesDropdown(false), 200)}
                        onChange={(e) => setFormData({...formData, smiles: e.target.value})} 
                        className="pl-11 pr-4 h-11 md:h-12 w-full rounded-[14px] border-zinc-200 bg-white/80 backdrop-blur-sm font-mono text-[12px] focus-visible:ring-4 focus-visible:ring-blue-500/10 focus-visible:border-blue-500/30 shadow-sm transition-all" 
                      />
                      <Search className="absolute left-4 w-4 h-4 text-zinc-400 group-focus-within:text-blue-500 transition-colors z-10 pointer-events-none" />
                    </div>
                    
                    {/* Dropdown SMILES List */}
                    {showSmilesDropdown && smilesMapping && Object.keys(smilesMapping).length > 0 && (
                      <div className="absolute z-50 w-full mt-2 bg-white/95 backdrop-blur-xl border border-zinc-200 rounded-2xl shadow-xl max-h-80 overflow-y-auto">
                        {Object.entries(smilesMapping)
                          .filter(([smiles, data]: [string, any]) => {
                            const searchTerm = formData.smiles.toLowerCase();
                            // Jika ada search term, filter. Jika tidak, tampilkan semua
                            if (!searchTerm) return true;
                            return smiles.toLowerCase().includes(searchTerm) || 
                                   data.linker_name?.toLowerCase().includes(searchTerm);
                          })
                          // TIDAK ADA LIMIT - TAMPILKAN SEMUA
                          .map(([smiles, data]: [string, any]) => (
                            <div 
                              key={smiles} 
                              className="px-5 py-3 hover:bg-blue-50/50 cursor-pointer border-b border-zinc-50 transition-colors"
                              onMouseDown={() => setFormData({...formData, smiles: smiles})}
                            >
                              <div className="flex items-start justify-between gap-3">
                                <div className="flex-1 min-w-0">
                                  <div className="text-xs font-semibold text-blue-600 mb-1">
                                    {data.linker_name || "Unknown"}
                                  </div>
                                  <div className="text-[10px] font-mono text-zinc-500 truncate">
                                    {smiles.length > 60 ? smiles.substring(0, 60) + "..." : smiles}
                                  </div>
                                </div>
                                {data.price_eur_per_g !== null && data.price_eur_per_g !== undefined && (
                                  <div className="text-[10px] font-bold text-green-600 whitespace-nowrap">
                                    €{data.price_eur_per_g.toFixed(2)}/g
                                  </div>
                                )}
                              </div>
                            </div>
                          ))}
                        {Object.entries(smilesMapping).filter(([smiles, data]: [string, any]) => {
                          const searchTerm = formData.smiles.toLowerCase();
                          if (!searchTerm) return false; // Jika tidak ada search, tidak tampilkan "no results"
                          return smiles.toLowerCase().includes(searchTerm) || 
                                 data.linker_name?.toLowerCase().includes(searchTerm);
                        }).length === 0 && formData.smiles && (
                          <div className="px-5 py-4 text-sm text-zinc-400 text-center">
                            No matching SMILES found
                          </div>
                        )}
                        {!formData.smiles && (
                          <div className="px-5 py-3 text-[10px] text-zinc-400 text-center border-t border-zinc-100 bg-zinc-50/50">
                            Showing all {Object.keys(smilesMapping).length} SMILES entries
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 items-start">
                    <div className="sm:col-span-2 space-y-1.5">
                      <Label className="text-[11px] font-medium text-zinc-400 ml-1 tracking-wide">Linker Name (Auto-filled)</Label>
                      <Input 
                        value={formData.linker_name} 
                        readOnly 
                        placeholder="Auto-filled from SMILES..." 
                        className="h-10 rounded-[12px] border-none bg-zinc-100/50 text-zinc-500 font-medium text-[13px] shadow-inner cursor-not-allowed" 
                      />
                    </div>
                    <div className="sm:col-span-1">
                      <InputGroup label="Mass" unit="mg" val={formData.linker_mass} k="linker_mass" s={setFormData} d={formData} placeholder="0" />
                    </div>
                  </div>
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
            {(loadingStates.costEnergy || loadingStates.structure) && <div className="absolute top-0 left-0 w-full h-1.5 bg-indigo-600 animate-pulse" />}
            
            <header className="flex flex-col sm:flex-row justify-between items-start gap-4 mb-12">
              <div className="space-y-2">
                <h3 className="text-[10px] md:text-[12px] font-black text-zinc-400 uppercase tracking-[0.3em]">Screening Result</h3>
                <h1 className={`text-5xl md:text-8xl font-black tracking-tighter transition-colors duration-500 ${overallFeasibility.is_overall_feasible ? 'text-indigo-600' : 'text-red-500'}`}>
                  {loadingStates.costEnergy || loadingStates.structure ? "Analyzing..." : overallFeasibility.is_overall_feasible ? "Feasible" : "Denied"}
                </h1>
              </div>
              {structureResults.structure_status && (
                <div className="flex flex-col items-start sm:items-end gap-3">
                    <Badge className="bg-zinc-900 text-white rounded-full px-5 py-2 text-[10px] md:text-xs font-bold uppercase tracking-widest shadow-lg">
                      {loadingStates.structure ? "Analyzing Structure..." : structureResults.structure_status}
                    </Badge>
                </div>
              )}
            </header>

            <div className="space-y-10 md:space-y-12 animate-in fade-in slide-in-from-bottom-4 duration-1000">
              
              {/* Bagian 1: Metrik Hidrogen - Real-time dari Geometric Factors */}
              <div className="space-y-6">
                <div className="flex items-center gap-4 text-zinc-400">
                  <h4 className="text-[10px] font-bold uppercase tracking-widest">Hydrogen Metrics</h4>
                  <div className="h-px bg-zinc-100 flex-1" />
                  <div className={`text-[8px] font-semibold px-2 py-1 rounded-full ${
                    hydrogenMetrics.doe_feasible 
                      ? 'text-green-600 bg-green-50' 
                      : 'text-red-600 bg-red-50'
                  }`}>
                    {hydrogenMetrics.doe_feasible ? 'FEASIBLE' : 'NOT FEASIBLE'}
                  </div>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 md:gap-6">
                  <ResultBox label="Working Uptake Gravimetric" val={hydrogenMetrics.gravimetric_h2.toFixed(3)} unit="wt%" target="5.5" targetSign="≥" ok={hydrogenMetrics.gravimetric_h2 >= 5.5} />
                  <ResultBox label="Working Uptake Volumetric" val={hydrogenMetrics.volumetric_h2.toFixed(3)} unit="g/L" target="40" targetSign="≥" ok={hydrogenMetrics.volumetric_h2 >= 40} />
                </div>
              </div>

              {/* Bagian 2: Ekonomi & Harga - Real-time dari Synthesis Conditions */}
              <div className="space-y-6">
                <div className="flex items-center gap-4 text-zinc-400">
                  <h4 className="text-[10px] font-bold uppercase tracking-widest">Economic Analysis</h4>
                  <div className="h-px bg-zinc-100 flex-1" />
                  {loadingStates.costEnergy ? (
                    <div className="text-[8px] text-blue-600 font-semibold bg-blue-50 px-2 py-1 rounded-full animate-pulse">CALCULATING</div>
                  ) : (
                    <div className={`text-[8px] font-semibold px-2 py-1 rounded-full ${
                      (Number(dynamicCosts.mof_cost) > 0 && Number(dynamicCosts.mof_cost) <= 30 && 
                       Number(dynamicCosts.storage_cost) > 0 && Number(dynamicCosts.storage_cost) <= 300)
                        ? 'text-green-600 bg-green-50' 
                        : 'text-red-600 bg-red-50'
                    }`}>
                      {(Number(dynamicCosts.mof_cost) > 0 && Number(dynamicCosts.mof_cost) <= 30 && 
                        Number(dynamicCosts.storage_cost) > 0 && Number(dynamicCosts.storage_cost) <= 300)
                        ? 'FEASIBLE' : 'NOT FEASIBLE'}
                    </div>
                  )}
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  <ResultBox icon={<DollarSign className="w-4 h-4"/>} label="MOF Production Cost" val={dynamicCosts.mof_cost} unit="USD/kg" target="30" ok={Number(dynamicCosts.mof_cost) > 0 && Number(dynamicCosts.mof_cost) <= 30} />
                  <ResultBox icon={<DollarSign className="w-4 h-4"/>} label="Hydrogen Storage Cost" val={dynamicCosts.storage_cost} unit="USD/kg H2" target="300" ok={Number(dynamicCosts.storage_cost) > 0 && Number(dynamicCosts.storage_cost) <= 300} />
                </div>
              </div>

              {/* Bagian 3: Energy Synthesis - Real-time dari Synthesis Conditions */}
              <div className="space-y-6">
                <div className="flex items-center gap-4 text-zinc-400">
                  <h4 className="text-[10px] font-bold uppercase tracking-widest">Energy Synthesis</h4>
                  <div className="h-px bg-zinc-100 flex-1" />
                  {loadingStates.costEnergy && (
                    <div className="text-[8px] text-blue-600 font-semibold bg-blue-50 px-2 py-1 rounded-full animate-pulse">CALCULATING</div>
                  )}
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
                          <td className="px-6 py-4 font-mono text-zinc-600 border-r border-zinc-100">{costEnergyResults.cp_linker.toFixed(2)}</td>
                          <td className="px-4 py-4 font-mono text-zinc-800">{costEnergyResults.e_sensible_solvent.toFixed(2)}</td>
                          <td className="px-4 py-4 font-mono text-zinc-800">{costEnergyResults.e_sensible_additive.toFixed(2)}</td>
                          <td className="px-4 py-4 font-mono text-zinc-800">{costEnergyResults.e_sensible_modulator.toFixed(2)}</td>
                          <td className="px-4 py-4 font-mono text-zinc-800">{costEnergyResults.e_sensible_metal.toFixed(2)}</td>
                          <td className="px-4 py-4 font-mono text-zinc-800">{costEnergyResults.e_sensible_linker.toFixed(2)}</td>
                          <td className="px-4 py-4 font-mono font-bold text-indigo-600">{costEnergyResults.e_sensible_total.toFixed(2)}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Energy Metric Boxes */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 mt-6">
                  <EconMiniCard icon={<Zap className="w-4 h-4 text-amber-500" />} label="Q Heat" val={costEnergyResults.q_energy.toFixed(5)} unit="MJ" />
                  <EconMiniCard icon={<AlertTriangle className="w-4 h-4 text-orange-500" />} label="Q Loss" val={costEnergyResults.q_loss.toFixed(5)} unit="MJ" />
                  <EconMiniCard icon={<Activity className="w-4 h-4 text-blue-500" />} label="E Stirr" val={costEnergyResults.e_stirr.toFixed(5)} unit="MJ" />
                  <EconMiniCard icon={<Zap className="w-4 h-4 text-emerald-500" />} label="E Tot" val={costEnergyResults.e_tot.toFixed(5)} unit="MJ" />
                </div>
              </div>
              {/* Bagian 4: Structure Analysis (xTB) - dari CIF File */}
              <div className="space-y-6 pt-6 border-t border-zinc-100">
                <div className="flex items-center gap-4 text-zinc-400">
                  <h4 className="text-[10px] font-bold uppercase tracking-widest">Structure Analysis (xTB)</h4>
                  <div className="h-px bg-zinc-100 flex-1" />
                  {loadingStates.structure ? (
                    <div className="text-[8px] text-blue-600 font-semibold bg-blue-50 px-2 py-1 rounded-full animate-pulse">ANALYZING</div>
                  ) : (
                    <div className={`text-[8px] font-semibold px-2 py-1 rounded-full ${
                      (structureResults.conformational_energy_kcal >= 0 && structureResults.conformational_energy_kcal <= 20 &&
                       structureResults.rmsd_final_angstrom >= 0 && structureResults.rmsd_final_angstrom <= 1.0 &&
                       structureResults.me_delta_length_angstrom >= 0 && structureResults.me_delta_length_angstrom <= 0.05 &&
                       structureResults.me_delta_angle_deg >= 0 && structureResults.me_delta_angle_deg <= 10)
                        ? 'text-green-600 bg-green-50' 
                        : 'text-red-600 bg-red-50'
                    }`}>
                      {(structureResults.conformational_energy_kcal >= 0 && structureResults.conformational_energy_kcal <= 20 &&
                        structureResults.rmsd_final_angstrom >= 0 && structureResults.rmsd_final_angstrom <= 1.0 &&
                        structureResults.me_delta_length_angstrom >= 0 && structureResults.me_delta_length_angstrom <= 0.05 &&
                        structureResults.me_delta_angle_deg >= 0 && structureResults.me_delta_angle_deg <= 10)
                        ? 'FEASIBLE' : 'NOT FEASIBLE'}
                    </div>
                  )}
                </div>
                
                {/* Status Badge */}
                {structureResults.structure_status && (
                  <div className="flex justify-center">
                    <Badge className={`px-4 py-2 text-xs font-medium rounded-full ${
                      structureResults.structure_feasible === true ? 'bg-green-100 text-green-700 border-green-200' :
                      structureResults.structure_feasible === false ? 'bg-red-100 text-red-700 border-red-200' :
                      'bg-gray-100 text-gray-700 border-gray-200'
                    }`}>
                      {loadingStates.structure ? "Analyzing structure..." : structureResults.structure_status}
                    </Badge>
                  </div>
                )}
                
                {/* 4 Output xTB */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 md:gap-6">
                  {/* 1. Energi konformasi linker (kcal/mol) */}
                  <div className="bg-gradient-to-br from-purple-50 to-indigo-50 p-4 md:p-6 rounded-2xl border border-purple-100/50 transition-all hover:scale-[1.02] shadow-sm">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-bold text-purple-600 uppercase tracking-wider">Conformational Energy</span>
                      <Zap className="w-4 h-4 text-purple-500" />
                    </div>
                    <div className="flex items-baseline gap-2">
                      <span className="text-2xl md:text-3xl font-bold text-purple-900 font-mono">
                        {structureResults.conformational_energy_kcal.toFixed(1)}
                      </span>
                      <span className="text-sm font-medium text-purple-600">kcal/mol</span>
                    </div>
                  </div>

                  {/* 2. RMSD Final (Å) */}
                  <div className="bg-gradient-to-br from-blue-50 to-cyan-50 p-4 md:p-6 rounded-2xl border border-blue-100/50 transition-all hover:scale-[1.02] shadow-sm">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-bold text-blue-600 uppercase tracking-wider">RMSD Final</span>
                      <Activity className="w-4 h-4 text-blue-500" />
                    </div>
                    <div className="flex items-baseline gap-2">
                      <span className="text-2xl md:text-3xl font-bold text-blue-900 font-mono">
                        {structureResults.rmsd_final_angstrom.toFixed(4)}
                      </span>
                      <span className="text-sm font-medium text-blue-600">Å</span>
                    </div>
                  </div>

                  {/* 3. ME delta length (Å) */}
                  <div className="bg-gradient-to-br from-green-50 to-emerald-50 p-4 md:p-6 rounded-2xl border border-green-100/50 transition-all hover:scale-[1.02] shadow-sm">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-bold text-green-600 uppercase tracking-wider">ME Δ Length</span>
                      <Box className="w-4 h-4 text-green-500" />
                    </div>
                    <div className="flex items-baseline gap-2">
                      <span className="text-2xl md:text-3xl font-bold text-green-900 font-mono">
                        {structureResults.me_delta_length_angstrom.toFixed(6)}
                      </span>
                      <span className="text-sm font-medium text-green-600">Å</span>
                    </div>
                  </div>

                  {/* 4. ME delta angle (deg) */}
                  <div className="bg-gradient-to-br from-orange-50 to-amber-50 p-4 md:p-6 rounded-2xl border border-orange-100/50 transition-all hover:scale-[1.02] shadow-sm">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-bold text-orange-600 uppercase tracking-wider">ME Δ Angle</span>
                      <Thermometer className="w-4 h-4 text-orange-500" />
                    </div>
                    <div className="flex items-baseline gap-2">
                      <span className="text-2xl md:text-3xl font-bold text-orange-900 font-mono">
                        {structureResults.me_delta_angle_deg.toFixed(4)}
                      </span>
                      <span className="text-sm font-medium text-orange-600">deg</span>
                    </div>
                  </div>
                </div>
                
                {/* xTB Availability Status */}
                <div className="text-center">
                  <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium ${
                    structureResults.xtb_available ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                  }`}>
                    <div className={`w-2 h-2 rounded-full ${structureResults.xtb_available ? 'bg-green-500' : 'bg-yellow-500'}`} />
                    xTB {structureResults.xtb_available ? 'Available' : 'Not Available'}
                  </div>
                </div>
              </div>

            </div>
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
      <div className="p-2 bg-zinc-100/80 rounded-[10px] text-zinc-600 shadow-sm border border-zinc-200/50">{icon}</div>
      <p className="text-[11px] font-semibold text-zinc-500 uppercase tracking-[0.15em]">{text}</p>
    </div>
  );
}

function InputGroup({ icon, label, unit, val, k, s, d, placeholder }: any) {
  return (
    <div className="space-y-1.5">
      <Label className="text-[11px] font-medium text-zinc-500 ml-1 tracking-wide truncate pr-2">{label}</Label>
      <div className="relative flex items-center group">
        {icon && <div className="absolute left-3.5 md:left-4 text-zinc-400 group-focus-within:text-blue-500 transition-colors duration-300 z-10 pointer-events-none">{icon}</div>}
        <Input 
          type="number" 
          step="any"
          placeholder={placeholder || "0"}
          value={val} 
          onChange={(e) => s({...d, [k]: e.target.value})} 
          className={`pr-9 sm:pr-10 rounded-[14px] border-zinc-200 bg-white/80 backdrop-blur-sm h-11 md:h-12 w-full text-[14px] font-medium focus-visible:ring-4 focus-visible:ring-blue-500/10 focus-visible:border-blue-500/30 transition-all shadow-sm ${icon ? 'pl-10 md:pl-11' : 'pl-4'}`} 
        />
        {unit && <div className="absolute right-3 md:right-4 text-[10px] sm:text-[11px] font-semibold text-zinc-400 pointer-events-none bg-transparent z-10">{unit}</div>}
      </div>
    </div>
  );
}

function ResultBox({ icon, label, val, unit, target, targetSign = "≤", ok }: any) {
  return (
    <div className={`p-6 md:p-8 rounded-[24px] border bg-white/90 backdrop-blur-xl flex justify-between items-center transition-all duration-300 hover:scale-[1.01] hover:shadow-md shadow-sm ${ok ? 'border-zinc-200/60' : 'border-red-200/60'}`}>
      <div className="space-y-1.5">
        <p className="text-[12px] font-medium text-zinc-500 tracking-wide">{label}</p>
        <div className="flex items-baseline">
            <span className={`text-3xl md:text-4xl font-semibold tracking-tight ${ok ? 'text-zinc-900' : 'text-red-600'}`}>{val}</span>
            <span className="ml-2 text-[15px] font-medium text-zinc-400 leading-none">{unit}</span>
        </div>
        <div className="flex items-center gap-2 mt-2">
            <p className="text-[11px] font-medium text-zinc-400">Target: {target ? `${targetSign} ${target}` : ''} <span className="normal-case">{unit}</span></p>
            {ok ? (
                <div className="flex items-center gap-1 text-emerald-500 text-[11px] font-semibold bg-emerald-50 px-2 py-0.5 rounded-full">
                    <CheckCircle2 className="w-3 h-3" />
                    <span>Pass</span>
                </div>
            ) : (
                <div className="flex items-center gap-1 text-red-500 text-[11px] font-semibold bg-red-50 px-2 py-0.5 rounded-full">
                    <XCircle className="w-3 h-3" />
                    <span>Fail</span>
                </div>
            )}
        </div>
      </div>
      <div className={`p-3 md:p-4 rounded-[16px] shadow-sm ${ok ? 'bg-zinc-100/80 text-zinc-600 border border-zinc-200/50' : 'bg-red-50 text-red-500 border border-red-100'}`}>
        {icon ? icon : (ok ? <CheckCircle2 className="w-5 h-5 md:w-6 md:h-6 stroke-[2]" /> : <XCircle className="w-5 h-5 md:w-6 md:h-6 stroke-[2]" />)}
      </div>
    </div>
  );
}

function EconMiniCard({ icon, label, val, unit }: any) {
  return (
    <div className="bg-white/80 backdrop-blur-xl p-4 md:p-5 rounded-[20px] border border-zinc-200/60 text-center space-y-3 shadow-sm transition-all duration-300 hover:scale-[1.02] hover:shadow-md">
      <div className="flex items-center justify-center gap-2">
        {icon}
        <span className="text-[10px] md:text-[11px] font-semibold text-zinc-500 tracking-wide">{label}</span>
      </div>
      <div className="space-y-1">
        <p className="text-lg md:text-xl font-bold tracking-tight text-zinc-800 font-mono">
          {val}
        </p>
        <p className="text-[10px] md:text-[11px] font-medium text-zinc-400 uppercase tracking-wider">
          {unit}
        </p>
      </div>
    </div>
  );
}