"use client";

import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { 
  Upload, Activity, Database, Loader2, 
  CheckCircle2, XCircle, FlaskConical, Layers, 
  Box, Thermometer, Clock, Beaker, Zap, AlertTriangle, ChevronDown, Search, Scale, DollarSign, Weight, X
} from 'lucide-react';

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import MOF3DViewer from "@/components/MOF3DViewer";
import LinkerStructureViewer from "@/components/LinkerStructureViewer";  // NEW: Import Linker Viewer

export default function MOFScreening() {
  const [showAbout, setShowAbout] = useState(false);
  const scrollRef = useRef<number>(0);  // Track scroll position
  const [dragOver, setDragOver] = useState({ free: false, embedded: false });

  // Drag and drop handlers
  const handleDragOver = useCallback((e: React.DragEvent, type: 'free' | 'embedded') => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(prev => ({ ...prev, [type]: true }));
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent, type: 'free' | 'embedded') => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(prev => ({ ...prev, [type]: false }));
  }, []);

  const handleDrop = useCallback((e: React.DragEvent, type: 'free' | 'embedded') => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(prev => ({ ...prev, [type]: false }));
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      if (file.name.endsWith('.xyz')) {
        if (type === 'free') {
          setFreeLinkerFile(file);
        } else {
          setEmbeddedLinkerFile(file);
        }
      } else {
        alert('Please upload only .xyz files');
      }
    }
  }, []);

  // Mouse position tracking for smooth scroll
  const handleMouseMove = useCallback((e: MouseEvent) => {
    scrollRef.current = window.scrollY;
  }, []);

  // Scroll preservation during state changes
  const preserveScroll = useCallback(() => {
    const currentScroll = scrollRef.current;
    requestAnimationFrame(() => {
      window.scrollTo({ top: currentScroll, behavior: 'instant' });
    });
  }, []);

  useEffect(() => {
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, [handleMouseMove]);

  // Preserve scroll during dropdown operations
  const handleDropdownFocus = useCallback((setter: () => void) => {
    return (e: React.FocusEvent) => {
      e.preventDefault();
      const currentScroll = window.scrollY;
      setter();
      requestAnimationFrame(() => {
        window.scrollTo({ top: currentScroll, behavior: 'instant' });
      });
    };
  }, []);

  const handleDropdownBlur = useCallback((setter: () => void) => {
    return (e: React.FocusEvent) => {
      e.preventDefault();
      const currentScroll = window.scrollY;
      setTimeout(() => {
        setter();
        requestAnimationFrame(() => {
          window.scrollTo({ top: currentScroll, behavior: 'instant' });
        });
      }, 200);
    };
  }, []);

  const [file, setFile] = useState<File | null>(null);  // CIF for 3D visualization
  const [freeLinkerFile, setFreeLinkerFile] = useState<File | null>(null);  // NEW: Free linker XYZ
  const [embeddedLinkerFile, setEmbeddedLinkerFile] = useState<File | null>(null);  // NEW: Embedded linker XYZ
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
    // Geometric Factors - updated default values for testing
    pv: "1.32", gsa: "3553", vsa: "2156", lcd: "11.53", pld: "8.55", vf: "0.8", density: "0.61",
    
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
    fetch("http://localhost:8000/get-prices")
      .then(res => res.json())
      .then(data => { if (data && !data.error) setPriceDb(data); })
      .catch(err => console.error("Database offline"));
    
    // Load SMILES mapping
    fetch("http://localhost:8000/get-smiles-mapping")
      .then(res => res.json())
      .then(data => { 
        if (data && !data.error) {
          setSmilesMapping(data.mapping || {});
        }
      })
      .catch(err => console.error("SMILES mapping offline"));
    
    // REMOVED: Load concentration mapping - user input manual
  }, []);

  // Auto-fill Linker Name dari SMILES - gunakan Name1 sebagai prioritas
  useEffect(() => {
    if (formData.smiles && smilesMapping[formData.smiles]) {
      const linkerData = smilesMapping[formData.smiles];
      
      // Handle name1 as string (which may contain [ ] brackets)
      let displayName = "";
      if (linkerData.name1) {
        displayName = linkerData.name1;
      } else if (linkerData.linker_name) {
        displayName = linkerData.linker_name;
      } else {
        displayName = "";
      }
      
      setFormData(prev => ({
        ...prev,
        linker_name: displayName
      }));
    }
  }, [formData.smiles, smilesMapping]);

  // Separate calculation functions for different sections
  const calculateHydrogenMetrics = useCallback(() => {
    // Jika ada geometric factor yang 0 atau kosong, return 0 untuk semua
    const f_pv = parseFloat(formData.pv) || 0;
    const f_gsa = parseFloat(formData.gsa) || 0;
    const f_vsa = parseFloat(formData.vsa) || 0;
    const f_lcd = parseFloat(formData.lcd) || 0;
    const f_pld = parseFloat(formData.pld) || 0;
    const f_density = parseFloat(formData.density) || 0;
    const f_vf = parseFloat(formData.vf) || 0;
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
      const res = await fetch("http://localhost:8000/analyze", { method: "POST", body: data });
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
    // THREE MODES:
    // Mode 1 (BEST): freeLinkerFile + embeddedLinkerFile → Two XYZ analysis
    // Mode 2: embeddedLinkerFile only → Auto-optimize 
    // Mode 3: file (CIF) only → Auto-extract + optimize (less accurate)
    
    // Check if we have two XYZ files (Mode 1 - BEST)
    if (freeLinkerFile && embeddedLinkerFile) {
      const data = new FormData();
      data.append('file_free', freeLinkerFile);
      data.append('file_embedded', embeddedLinkerFile);
      
      // Add minimal required fields
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
        const res = await fetch("http://localhost:8000/analyze", { method: "POST", body: data });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        
        const result = await res.json();
        if (result.status === "success") {
          console.log('✅ Two XYZ API response:', result.results);
          console.log('📊 free_structure:', result.results.free_structure);
          console.log('📊 embedded_structure:', result.results.embedded_structure);
          
          return {
            conformational_energy_kcal: result.results.conformational_energy_kcal || 0.0,
            rmsd_final_angstrom: result.results.rmsd_final_angstrom || 0.0,
            me_delta_length_angstrom: result.results.me_delta_length_angstrom || 0.0,
            me_delta_angle_deg: result.results.me_delta_angle_deg || 0.0,
            structure_status: result.results.structure_status || "Two XYZ files analyzed",
            structure_feasible: result.results.structure_feasible,
            xtb_available: result.results.xtb_available || true,
            stability_score: result.results.stability_score || "Unknown",
            stability_level: result.results.stability_level || 0,
            upload_mode: result.results.upload_mode || "two_xyz",
            free_structure: result.results.free_structure,
            embedded_structure: result.results.embedded_structure
          };
        }
      } catch (err) {
        console.error("Two XYZ analysis failed:", err);
      }
    }
    
    // Mode 2: Single embedded XYZ (auto-optimize)
    if (embeddedLinkerFile) {
      const data = new FormData();
      data.append('file_embedded', embeddedLinkerFile);
      
      // Add minimal required fields
      data.append('metal_name', formData.metal_name || "Cu");
      data.append('smiles', formData.smiles || "O=C(O)c1ccc(cc1)C(=O)O");
      data.append('pv', formData.pv); data.append('gsa', formData.gsa); data.append('vsa', formData.vsa);
      data.append('lcd', formData.lcd); data.append('pld', formData.pld); data.append('vf', formData.vf); 
      data.append('density', formData.density);
      
      // Add default values
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
        const res = await fetch("http://localhost:8000/analyze", { method: "POST", body: data });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        
        const result = await res.json();
        if (result.status === "success") {
          return {
            conformational_energy_kcal: result.results.conformational_energy_kcal || 0.0,
            rmsd_final_angstrom: result.results.rmsd_final_angstrom || 0.0,
            me_delta_length_angstrom: result.results.me_delta_length_angstrom || 0.0,
            me_delta_angle_deg: result.results.me_delta_angle_deg || 0.0,
            structure_status: result.results.structure_status || "Single XYZ analyzed",
            structure_feasible: result.results.structure_feasible,
            xtb_available: result.results.xtb_available || true,
            stability_score: result.results.stability_score || "Unknown",
            stability_level: result.results.stability_level || 0,
            upload_mode: result.results.upload_mode || "single_xyz",
            free_structure: result.results.free_structure,
            embedded_structure: result.results.embedded_structure
          };
        }
      } catch (err) {
        console.error("Single XYZ analysis failed:", err);
      }
    }
    
    // Mode 3: CIF file (auto-extract, less accurate)
    if (file && file.name.endsWith('.cif')) {
      const data = new FormData();
      data.append('file', file);
      
      // Add minimal required fields
      data.append('metal_name', formData.metal_name || "Cu");
      data.append('smiles', formData.smiles || "O=C(O)c1ccc(cc1)C(=O)O");
      data.append('pv', formData.pv); data.append('gsa', formData.gsa); data.append('vsa', formData.vsa);
      data.append('lcd', formData.lcd); data.append('pld', formData.pld); data.append('vf', formData.vf); 
      data.append('density', formData.density);
      
      // Add default values
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
        const res = await fetch("http://localhost:8000/analyze", { method: "POST", body: data });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        
        const result = await res.json();
        if (result.status === "success") {
          return {
            conformational_energy_kcal: result.results.conformational_energy_kcal || 0.0,
            rmsd_final_angstrom: result.results.rmsd_final_angstrom || 0.0,
            me_delta_length_angstrom: result.results.me_delta_length_angstrom || 0.0,
            me_delta_angle_deg: result.results.me_delta_angle_deg || 0.0,
            structure_status: result.results.structure_status || "CIF analyzed",
            structure_feasible: result.results.structure_feasible,
            xtb_available: result.results.xtb_available || true,
            stability_score: result.results.stability_score || "Unknown",
            stability_level: result.results.stability_level || 0,
            upload_mode: result.results.upload_mode || "cif",
            free_structure: result.results.free_structure,
            embedded_structure: result.results.embedded_structure
          };
        }
      } catch (err) {
        console.error("CIF analysis failed:", err);
      }
    }
    
    // No files uploaded
    return {
      conformational_energy_kcal: 0.0,
      rmsd_final_angstrom: 0.0,
      me_delta_length_angstrom: 0.0,
      me_delta_angle_deg: 0.0,
      structure_status: "No structure file uploaded",
      structure_feasible: null,
      xtb_available: true,
      stability_score: "Unknown",
      stability_level: 0,
      upload_mode: "none"
    };
  }, [freeLinkerFile, embeddedLinkerFile, file, formData.metal_name, formData.smiles, formData.pv, formData.gsa, formData.vsa, formData.lcd, formData.pld, formData.vf, formData.density]);

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
    structure_status: "No structure files uploaded", structure_feasible: null, xtb_available: true,
    stability_score: "Unknown", stability_level: 0, upload_mode: "none",
    free_structure: null as any, embedded_structure: null as any
  });
  
  const [structure3D, setStructure3D] = useState<any>(null);  // NEW: For 3D visualization
  const [loading3D, setLoading3D] = useState(false);  // NEW: Loading state for 3D

  const [loadingStates, setLoadingStates] = useState({
    hydrogen: false, costEnergy: false, structure: false
  });
  
  // NEW: Fetch 3D visualization when CIF file is uploaded
  useEffect(() => {
    console.log("📂 File changed:", file?.name, "Type:", file?.type);
    
    if (file && file.name.endsWith('.cif')) {
      console.log("✅ CIF file detected, fetching 3D data...");
      setLoading3D(true);
      const data = new FormData();
      data.append('file', file);
      
      fetch("http://localhost:8000/api/structure/3d-view", {
        method: "POST",
        body: data
      })
        .then(res => {
          console.log("📡 Response status:", res.status);
          return res.json();
        })
        .then(result => {
          console.log("📦 3D data received:", result);
          if (result.status === "success") {
            setStructure3D(result);
            console.log("✅ 3D structure set successfully");
          } else {
            console.error("❌ API returned error:", result);
          }
        })
        .catch(err => {
          console.error("❌ 3D visualization failed:", err);
        })
        .finally(() => {
          setLoading3D(false);
          console.log("🏁 3D loading finished");
        });
    } else {
      console.log("ℹ️ No CIF file, clearing 3D structure");
      setStructure3D(null);
    }
  }, [file]);

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
        console.log("💰 Cost Analysis Results:", results);
        setCostEnergyResults(results);
        setLoadingStates(prev => ({ ...prev, costEnergy: false }));
      }, 500); // 500ms debounce for cost/energy
      return () => clearTimeout(timer);
    } else {
      // Reset when required fields are empty
      console.log("❌ Cost Analysis Reset - missing metal_name or smiles:", { metal_name: formData.metal_name, smiles: formData.smiles });
      setCostEnergyResults({
        mof_cost: 0, storage_cost: 0, q_energy: 0, q_loss: 0, e_stirr: 0, e_tot: 0, econ_feasible: false,
        cp_linker: 0, linker_mw: 0, e_sensible_solvent: 0, e_sensible_additive: 0, 
        e_sensible_modulator: 0, e_sensible_metal: 0, e_sensible_linker: 0, e_sensible_total: 0
      });
    }
  }, [calculateCostAndEnergy]);

  // 3. Structure Analysis - API call when files change
  useEffect(() => {
    if (freeLinkerFile || embeddedLinkerFile || (file && file.name.endsWith('.cif'))) {
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
        structure_status: "No structure files uploaded", structure_feasible: null, xtb_available: true,
        stability_score: "Unknown", stability_level: 0, upload_mode: "none",
        free_structure: null, embedded_structure: null
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
    
    // Updated cost feasibility: handle case when SMILES is empty (cost analysis doesn't run)
    const costOk = !formData.smiles ? true : // If no SMILES, skip cost check (treat as OK)
                   ((costEnergyResults.mof_cost === 0 || (costEnergyResults.mof_cost > 0 && costEnergyResults.mof_cost <= MAX_MOF_COST)) && 
                   (costEnergyResults.storage_cost === 0 || (costEnergyResults.storage_cost > 0 && costEnergyResults.storage_cost <= MAX_STORAGE_COST)));
    
    // Simplified structure feasibility - treat no file upload as OK, only fail if energy > 250
    const structureOk = !freeLinkerFile && !embeddedLinkerFile && !file ? true : // No files uploaded = OK
                       (structureResults.conformational_energy_kcal <= 250 || 
                        structureResults.conformational_energy_kcal === 0);

    // Debug: Log all feasibility components for troubleshooting
    console.log("🔍 DEBUG Feasibility Components:", {
      hydrogenMetrics_doe_feasible: hydrogenMetrics.doe_feasible,
      costOk: costOk,
      timeOk: timeOk, 
      tempOk: tempOk,
      structureOk: structureOk,
      conformational_energy: structureResults.conformational_energy_kcal,
      structure_feasible_property: structureResults.structure_feasible,
      mof_cost: costEnergyResults.mof_cost,
      storage_cost: costEnergyResults.storage_cost,
      reaction_time: formData.reaction_time,
      temperature: formData.temperature,
      final_is_overall_feasible: hydrogenMetrics.doe_feasible && costOk && timeOk && tempOk && structureOk
    });

    return {
      is_overall_feasible: hydrogenMetrics.doe_feasible && costOk && timeOk && tempOk && structureOk,
      doe_feasible: hydrogenMetrics.doe_feasible,
      econ_feasible: costOk,
      time_ok: timeOk,
      temp_ok: tempOk,
      structure_feasible: structureResults.structure_feasible
    };
  }, [hydrogenMetrics.doe_feasible, costEnergyResults.mof_cost, costEnergyResults.storage_cost, 
      formData.reaction_time, formData.temperature, formData.smiles, 
      structureResults.structure_feasible, structureResults.conformational_energy_kcal,
      freeLinkerFile, embeddedLinkerFile, file]);

  return (
    <div className="min-h-screen bg-[#F5F5F7] text-[#1D1D1F] font-sans antialiased selection:bg-indigo-100">
      <style jsx global>{`
        * {
          scroll-behavior: smooth;
        }
        
        html {
          scroll-behavior: smooth;
        }
        
        /* Enhanced scroll behavior for better UX */
        body {
          scroll-behavior: smooth;
          scroll-padding-top: 2rem;
        }
        
        /* Prevent focus-related scroll jumping */
        input:focus, 
        textarea:focus, 
        select:focus, 
        button:focus {
          scroll-margin: 0;
          outline: none;
        }
        
        /* Smooth scroll restoration */
        html, body {
          scroll-snap-type: none;
        }
        
        /* Enhanced focus behavior */
        input:focus-visible,
        textarea:focus-visible,
        select:focus-visible,
        button:focus-visible {
          outline: 2px solid #3b82f6;
          outline-offset: 2px;
        }
        
        /* Custom scrollbar for better UX */
        ::-webkit-scrollbar {
          width: 8px;
        }
        
        ::-webkit-scrollbar-track {
          background: #f1f5f9;
          border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb {
          background: #cbd5e1;
          border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
          background: #94a3b8;
        }
        
        /* Prevent scroll jumps on interaction */
        .no-scroll-jump {
          scroll-margin: 0 !important;
        }
        
        /* Smooth transitions for interactive elements */
        button, input, textarea, select {
          transition: all 0.2s ease-in-out;
        }
        
        /* Ensure smooth scrolling for all browsers */
        @media (prefers-reduced-motion: no-preference) {
          html {
            scroll-behavior: smooth;
          }
        }
      `}</style>
      
      <nav className="sticky top-0 z-50 w-full border-b border-zinc-200/50 bg-white/70 backdrop-blur-xl px-4 md:px-8 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-3">
            {/* TRIAXIS-MOF Logo */}
            <div className="relative">
              <img 
                src="/triaxismof.svg" 
                alt="TRIAXIS-MOF Logo" 
                className="w-10 h-10 rounded-full"
              />
            </div>
            <span className="text-xl font-bold tracking-tight">
              TRIAXIS<span className="text-indigo-600">-MOF</span>
            </span>
          </div>
          
          {/* About Button */}
          <button 
            onClick={(e) => {
              e.preventDefault();
              setShowAbout(true);
            }}
            className="px-4 py-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-600 font-medium rounded-xl transition-colors duration-200"
            style={{ scrollMargin: 0 }}
          >
            About
          </button>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 md:py-12 px-4 md:px-8 grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12">
        <section className="lg:col-span-4 space-y-8 animate-in slide-in-from-left duration-700">
          <div className="sticky top-4 bg-white/80 backdrop-blur-2xl rounded-[32px] border border-white/50 p-6 md:p-8 shadow-sm space-y-8">
            <h2 className="text-2xl font-bold tracking-tight">Configuration</h2>
            
            <div className="space-y-4">
              <SectionHeader icon={<Layers className="w-4 h-4" />} text="01 Geometric Factors" />
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
              <SectionHeader icon={<Beaker className="w-4 h-4" />} text="02 Synthesis Conditions" />
              <div className="space-y-4">
                
                {/* 1. Solvent */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 items-start">
                  <div className="sm:col-span-2 space-y-1.5 relative">
                    <Label className="text-[11px] font-medium text-zinc-500 ml-1 tracking-wide">1. Solvent Name</Label>
                    <div className="relative flex items-center group">
                      <Input 
                        placeholder="Search" 
                        value={solventSearch} 
                        onFocus={handleDropdownFocus(() => {
                          setShowSolventList(true);
                          setShowAdditiveList(false);
                          setShowModulatorList(false);
                          setShowMetalList(false);
                          setShowSmilesDropdown(false);
                        })}
                        onBlur={handleDropdownBlur(() => setShowSolventList(false))} 
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
                        onFocus={handleDropdownFocus(() => {
                          setShowAdditiveList(true);
                          setShowSolventList(false);
                          setShowModulatorList(false);
                          setShowMetalList(false);
                          setShowSmilesDropdown(false);
                        })}
                        onBlur={handleDropdownBlur(() => setShowAdditiveList(false))} 
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
                        onFocus={handleDropdownFocus(() => {
                          setShowModulatorList(true);
                          setShowSolventList(false);
                          setShowAdditiveList(false);
                          setShowMetalList(false);
                          setShowSmilesDropdown(false);
                        })}
                        onBlur={handleDropdownBlur(() => setShowModulatorList(false))} 
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
                        onFocus={handleDropdownFocus(() => {
                          setShowMetalList(true);
                          setShowSolventList(false);
                          setShowAdditiveList(false);
                          setShowModulatorList(false);
                          setShowSmilesDropdown(false);
                        })}
                        onBlur={handleDropdownBlur(() => setShowMetalList(false))} 
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
                        onFocus={handleDropdownFocus(() => {
                          setShowSmilesDropdown(true);
                          setShowSolventList(false);
                          setShowAdditiveList(false);
                          setShowModulatorList(false);
                          setShowMetalList(false);
                        })}
                        onBlur={handleDropdownBlur(() => setShowSmilesDropdown(false))}
                        onChange={(e) => setFormData({...formData, smiles: e.target.value})} 
                        className="pl-11 pr-4 h-11 md:h-12 w-full rounded-[14px] border-zinc-200 bg-white/80 backdrop-blur-sm font-mono text-[12px] focus-visible:ring-4 focus-visible:ring-blue-500/10 focus-visible:border-blue-500/30 shadow-sm transition-all no-scroll-jump" 
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
                                   data.linker_name?.toLowerCase().includes(searchTerm) ||
                                   data.name1?.toLowerCase().includes(searchTerm) ||
                                   data.cas1?.toLowerCase().includes(searchTerm);
                          })
                          // TIDAK ADA LIMIT - TAMPILKAN SEMUA
                          .map(([smiles, data]: [string, any]) => (
                            <div 
                              key={smiles} 
                              className="px-5 py-3 hover:bg-blue-50/50 cursor-pointer border-b border-zinc-50 transition-colors group"
                              onMouseDown={() => setFormData({...formData, smiles: smiles})}
                            >
                              <div className="flex items-start justify-between gap-3">
                                <div className="flex-1 min-w-0">
                                  <div 
                                    className="text-sm font-bold font-mono text-black mb-2 overflow-hidden relative"
                                    onMouseEnter={(e) => {
                                      const textEl = e.currentTarget.querySelector('.marquee-text');
                                      const containerWidth = e.currentTarget.clientWidth;
                                      const textWidth = textEl.scrollWidth;
                                      
                                      if (textWidth > containerWidth) {
                                        const scrollDistance = textWidth - containerWidth + 20;
                                        textEl.style.transform = `translateX(-${scrollDistance}px)`;
                                        textEl.style.transition = `transform ${Math.max(3, scrollDistance / 30)}s linear`;
                                      }
                                    }}
                                    onMouseLeave={(e) => {
                                      const textEl = e.currentTarget.querySelector('.marquee-text');
                                      textEl.style.transform = 'translateX(0)';
                                      textEl.style.transition = 'transform 0.5s ease-out';
                                    }}
                                  >
                                    <div className="marquee-text whitespace-nowrap">
                                      {smiles}
                                    </div>
                                  </div>
                                  <div 
                                    className="text-xs font-semibold text-blue-600 mb-1 overflow-hidden relative"
                                    onMouseEnter={(e) => {
                                      const textEl = e.currentTarget.querySelector('.marquee-text');
                                      const containerWidth = e.currentTarget.clientWidth;
                                      const textWidth = textEl.scrollWidth;
                                      
                                      if (textWidth > containerWidth) {
                                        const scrollDistance = textWidth - containerWidth + 20;
                                        textEl.style.transform = `translateX(-${scrollDistance}px)`;
                                        textEl.style.transition = `transform ${Math.max(3, scrollDistance / 30)}s linear`;
                                      }
                                    }}
                                    onMouseLeave={(e) => {
                                      const textEl = e.currentTarget.querySelector('.marquee-text');
                                      textEl.style.transform = 'translateX(0)';
                                      textEl.style.transition = 'transform 0.5s ease-out';
                                    }}
                                  >
                                    <div className="marquee-text whitespace-nowrap">
                                      {data.name1 || "Unknown Name"}
                                    </div>
                                  </div>
                                  <div className="text-[10px] text-zinc-500">
                                    CAS: {data.cas1 || "N/A"}
                                  </div>
                                </div>
                                {data.price_eur_per_g !== null && data.price_eur_per_g !== undefined && (
                                  <div className="text-[10px] font-bold text-green-600 whitespace-nowrap">
                                    ${(data.price_eur_per_g * 1.15).toFixed(2)}/g
                                  </div>
                                )}
                              </div>
                            </div>
                          ))}
                        {Object.entries(smilesMapping).filter(([smiles, data]: [string, any]) => {
                          const searchTerm = formData.smiles.toLowerCase();
                          if (!searchTerm) return false; // Jika tidak ada search, tidak tampilkan "no results"
                          return smiles.toLowerCase().includes(searchTerm) || 
                                 data.linker_name?.toLowerCase().includes(searchTerm) ||
                                 data.name1?.toLowerCase().includes(searchTerm) ||
                                 data.cas1?.toLowerCase().includes(searchTerm);
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
                      <div 
                        className="h-10 rounded-[12px] border-none bg-zinc-100/50 text-zinc-500 font-medium text-[13px] shadow-inner cursor-default flex items-center px-3 overflow-hidden relative"
                        onMouseEnter={(e) => {
                          const textEl = e.currentTarget.querySelector('.marquee-text');
                          const containerWidth = e.currentTarget.clientWidth - 24; // Account for padding
                          const textWidth = textEl.scrollWidth;
                          
                          if (textWidth > containerWidth) {
                            const scrollDistance = textWidth - containerWidth + 20;
                            textEl.style.transform = `translateX(-${scrollDistance}px)`;
                            textEl.style.transition = `transform ${Math.max(3, scrollDistance / 30)}s linear`;
                          }
                        }}
                        onMouseLeave={(e) => {
                          const textEl = e.currentTarget.querySelector('.marquee-text');
                          textEl.style.transform = 'translateX(0)';
                          textEl.style.transition = 'transform 0.5s ease-out';
                        }}
                      >
                        <div className="marquee-text whitespace-nowrap">
                          {formData.linker_name || "Auto-filled from SMILES..."}
                        </div>
                      </div>
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

            <div className="space-y-4 pt-6 border-t border-zinc-100">
              <SectionHeader icon={<FlaskConical className="w-4 h-4" />} text="02 Structure Files" />
              
              <div className="space-y-4">
                {/* Free Linker XYZ Upload */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label className="text-xs font-semibold text-zinc-600">
                      Free Linker (XYZ)
                    </Label>
                  </div>
                  <p className="text-[10px] text-zinc-500 italic">
                    Optimized free linker • For accurate ΔE with embedded linker
                  </p>
                  <div 
                    className={`group relative overflow-hidden border-2 border-dashed rounded-3xl p-6 text-center cursor-pointer transition-all duration-500 shadow-sm ${
                      freeLinkerFile ? 'border-blue-400 bg-blue-50/50' : 
                      dragOver.free ? 'border-blue-500 bg-blue-50 scale-105' :
                      'border-zinc-200 hover:border-blue-300'
                    }`}
                    onDragOver={(e) => handleDragOver(e, 'free')}
                    onDragLeave={(e) => handleDragLeave(e, 'free')}
                    onDrop={(e) => handleDrop(e, 'free')}
                  >
                    <Upload className={`mx-auto w-8 h-8 mb-3 pointer-events-none relative z-0 ${freeLinkerFile ? 'text-blue-600' : 'text-zinc-400'}`} />
                    <p className="text-sm font-semibold truncate px-4 pointer-events-none relative z-0">{freeLinkerFile ? freeLinkerFile.name : "Click or drag free linker .xyz file"}</p>
                    <input 
                      id="free-xyz-upload" 
                      type="file" 
                      className="absolute inset-0 opacity-0 cursor-pointer z-10" 
                      accept=".xyz" 
                      onChange={(e) => {
                        console.log('Free linker file selected:', e.target.files?.[0]);
                        setFreeLinkerFile(e.target.files?.[0] || null);
                      }} 
                    />
                  </div>
                </div>
                
                {/* Embedded Linker XYZ Upload */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label className="text-xs font-semibold text-zinc-600">
                      Embedded Linker (XYZ)
                    </Label>
                  </div>
                  <p className="text-[10px] text-zinc-500 italic">
                    Linker extracted from MOF • For conformational energy (ΔE)
                  </p>
                  <div 
                    className={`group relative overflow-hidden border-2 border-dashed rounded-3xl p-6 text-center cursor-pointer transition-all duration-500 shadow-sm ${
                      embeddedLinkerFile ? 'border-green-400 bg-green-50/50' : 
                      dragOver.embedded ? 'border-green-500 bg-green-50 scale-105' :
                      'border-zinc-200 hover:border-green-300'
                    }`}
                    onDragOver={(e) => handleDragOver(e, 'embedded')}
                    onDragLeave={(e) => handleDragLeave(e, 'embedded')}
                    onDrop={(e) => handleDrop(e, 'embedded')}
                  >
                    <Upload className={`mx-auto w-8 h-8 mb-3 pointer-events-none relative z-0 ${embeddedLinkerFile ? 'text-green-600' : 'text-zinc-400'}`} />
                    <p className="text-sm font-semibold truncate px-4 pointer-events-none relative z-0">{embeddedLinkerFile ? embeddedLinkerFile.name : "Click or drag embedded linker .xyz file"}</p>
                    <input 
                      id="embedded-xyz-upload" 
                      type="file" 
                      className="absolute inset-0 opacity-0 cursor-pointer z-10" 
                      accept=".xyz" 
                      onChange={(e) => {
                        console.log('Embedded linker file selected:', e.target.files?.[0]);
                        setEmbeddedLinkerFile(e.target.files?.[0] || null);
                      }} 
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
        {/* RESULTS SECTION */}
        <section className="lg:col-span-8 relative animate-in fade-in zoom-in duration-1000">
          <div className="bg-white/90 backdrop-blur-3xl rounded-[48px] p-6 md:p-12 border border-white shadow-xl lg:sticky lg:top-28 space-y-8 md:space-y-12 min-h-[750px] flex flex-col overflow-hidden">
            {(loadingStates.costEnergy || loadingStates.structure) && <div className="absolute top-0 left-0 w-full h-1.5 bg-indigo-600 animate-pulse" />}
            
            <header className="relative">
              {/* Subtle Background */}
              <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/3 via-purple-500/3 to-blue-500/3 rounded-2xl -z-10" />
              
              <div className="flex flex-col sm:flex-row justify-between items-start gap-4 p-6 mb-6">
                <div className="space-y-3">
                  {/* Compact Title with Icon */}
                  <div className="flex items-center gap-2">
                    <div className="w-6 h-6 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
                      <Activity className="w-3 h-3 text-white" />
                    </div>
                    <h3 className="text-[10px] font-bold text-indigo-600 uppercase tracking-[0.2em]">
                      Screening Result
                    </h3>
                  </div>
                  
                  {/* Compact Main Status - Based on xTB Structure Analysis */}
                  <div className="relative">
                    <h1 className={`text-4xl md:text-6xl font-black tracking-tight transition-all duration-700 ${
                      (structureResults.conformational_energy_kcal <= 250 && structureResults.conformational_energy_kcal > 0)
                        ? 'text-transparent bg-clip-text bg-gradient-to-r from-green-500 to-emerald-600' 
                        : 'text-transparent bg-clip-text bg-gradient-to-r from-red-500 to-rose-600'
                    }`}>
                      {loadingStates.costEnergy || loadingStates.structure ? (
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-500 to-indigo-600 animate-pulse">
                          Analyzing...
                        </span>
                      ) : (structureResults.conformational_energy_kcal <= 250 && structureResults.conformational_energy_kcal > 0) ? "Feasible" : "Rejected"}
                    </h1>
                    
                    {/* Compact underline */}
                    <div className={`h-1 rounded-full mt-1 transition-all duration-700 ${
                      (structureResults.conformational_energy_kcal <= 250 && structureResults.conformational_energy_kcal > 0)
                        ? 'bg-gradient-to-r from-green-500 to-emerald-600 w-full' 
                        : 'bg-gradient-to-r from-red-500 to-rose-600 w-3/4'
                    }`} />
                  </div>
                  
                  {/* Compact Description - Based on xTB */}
                  <p className={`text-xs font-medium transition-colors duration-500 ${
                    (structureResults.conformational_energy_kcal <= 250 && structureResults.conformational_energy_kcal > 0)
                      ? 'text-green-700' 
                      : 'text-red-700'
                  }`}>
                    {loadingStates.costEnergy || loadingStates.structure 
                      ? "Running analysis..." 
                      : (structureResults.conformational_energy_kcal <= 250 && structureResults.conformational_energy_kcal > 0)
                        ? "Structure meets stability criteria" 
                        : "Structure stability criteria not met"}
                  </p>
                </div>
                
                {/* Compact Status Badges */}
                <div className="flex flex-col items-start sm:items-end gap-2">
                  {structureResults.structure_status && (
                    <Badge className={`rounded-xl px-3 py-1.5 text-[10px] font-semibold uppercase tracking-wide border-0 shadow-lg text-white ${
                      structureResults.conformational_energy_kcal <= 50
                        ? 'bg-gradient-to-r from-green-500 to-emerald-600' 
                        : structureResults.conformational_energy_kcal <= 85
                        ? 'bg-gradient-to-r from-blue-500 to-cyan-600'
                        : structureResults.conformational_energy_kcal <= 250
                        ? 'bg-gradient-to-r from-yellow-500 to-amber-600' 
                        : 'bg-gradient-to-r from-red-500 to-rose-600'
                    }`}>
                      {loadingStates.structure ? (
                        <div className="flex items-center gap-1.5">
                          <div className="w-1.5 h-1.5 bg-white/80 rounded-full animate-pulse" />
                          Analyzing...
                        </div>
                      ) : structureResults.structure_status}
                    </Badge>
                  )}
                  
                  {/* Compact Score Indicator - Based on xTB Structure Analysis */}
                  <div className="flex items-center gap-1.5 bg-white/80 backdrop-blur-sm rounded-xl px-3 py-1.5 border border-zinc-200">
                    <div className={`w-2 h-2 rounded-full transition-colors duration-500 ${
                      (structureResults.conformational_energy_kcal <= 250 && structureResults.conformational_energy_kcal > 0) 
                        ? 'bg-green-500 animate-pulse' 
                        : 'bg-red-500'
                    }`} />
                    <span className="text-[10px] font-bold text-zinc-600">
                      {(structureResults.conformational_energy_kcal <= 250 && structureResults.conformational_energy_kcal > 0) 
                        ? 'PASS' : 'FAIL'}
                    </span>
                  </div>
                </div>
              </div>
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
                      ((Number(dynamicCosts.mof_cost) >= 0 && Number(dynamicCosts.mof_cost) <= 30) && 
                       (Number(dynamicCosts.storage_cost) >= 0 && Number(dynamicCosts.storage_cost) <= 300))
                        ? 'text-green-600 bg-green-50' 
                        : 'text-red-600 bg-red-50'
                    }`}>
                      {((Number(dynamicCosts.mof_cost) >= 0 && Number(dynamicCosts.mof_cost) <= 30) && 
                        (Number(dynamicCosts.storage_cost) >= 0 && Number(dynamicCosts.storage_cost) <= 300))
                        ? 'FEASIBLE' : 'NOT FEASIBLE'}
                    </div>
                  )}
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  <ResultBox icon={<DollarSign className="w-4 h-4"/>} label="MOF Production Cost" val={dynamicCosts.mof_cost} unit="USD/kg" target="30" ok={Number(dynamicCosts.mof_cost) >= 0 && Number(dynamicCosts.mof_cost) <= 30} />
                  <ResultBox icon={<DollarSign className="w-4 h-4"/>} label="Hydrogen Storage Cost" val={dynamicCosts.storage_cost} unit="USD/kg H2" target="300" ok={Number(dynamicCosts.storage_cost) >= 0 && Number(dynamicCosts.storage_cost) <= 300} />
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
                      structureResults.conformational_energy_kcal <= 250
                        ? 'text-green-600 bg-green-50' 
                        : 'text-red-600 bg-red-50'
                    }`}>
                      {structureResults.conformational_energy_kcal <= 250
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
                
                {/* Stability Interpretation Card - Based on ΔE */}
                {(freeLinkerFile || embeddedLinkerFile) && structureResults.conformational_energy_kcal > 0 && (
                  <div className={`p-4 md:p-6 rounded-2xl border-2 transition-all ${
                    structureResults.conformational_energy_kcal <= 50
                      ? 'bg-gradient-to-br from-green-50 to-emerald-50 border-green-300' 
                      : structureResults.conformational_energy_kcal <= 85
                      ? 'bg-gradient-to-br from-blue-50 to-cyan-50 border-blue-300' 
                      : structureResults.conformational_energy_kcal <= 250
                      ? 'bg-gradient-to-br from-yellow-50 to-amber-50 border-yellow-300'
                      : 'bg-gradient-to-br from-red-50 to-rose-50 border-red-300'
                  }`}>
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="text-xs font-bold uppercase tracking-wider flex items-center gap-2">
                        {structureResults.conformational_energy_kcal <= 50 && <CheckCircle2 className="w-4 h-4 text-green-600" />}
                        {structureResults.conformational_energy_kcal > 50 && structureResults.conformational_energy_kcal <= 85 && <CheckCircle2 className="w-4 h-4 text-blue-600" />}
                        {structureResults.conformational_energy_kcal > 85 && structureResults.conformational_energy_kcal <= 250 && <AlertTriangle className="w-4 h-4 text-yellow-600" />}
                        {structureResults.conformational_energy_kcal > 250 && <XCircle className="w-4 h-4 text-red-600" />}
                        <span className={
                          structureResults.conformational_energy_kcal <= 50
                            ? 'text-green-700' 
                            : structureResults.conformational_energy_kcal <= 85
                            ? 'text-blue-700'
                            : structureResults.conformational_energy_kcal <= 250
                            ? 'text-yellow-700' 
                            : 'text-red-700'
                        }>
                          Stability Assessment
                        </span>
                      </h4>
                      <Badge className={`text-xs font-bold ${
                        structureResults.conformational_energy_kcal <= 50
                          ? 'bg-green-100 text-green-700 border-green-200' 
                          : structureResults.conformational_energy_kcal <= 85
                          ? 'bg-blue-100 text-blue-700 border-blue-200'
                          : structureResults.conformational_energy_kcal <= 250
                          ? 'bg-yellow-100 text-yellow-700 border-yellow-200' 
                          : 'bg-red-100 text-red-700 border-red-200'
                      }`}>
                        {structureResults.conformational_energy_kcal <= 50
                          ? '✓ Very Stable' 
                          : structureResults.conformational_energy_kcal <= 85
                          ? '✓ Stable'
                          : structureResults.conformational_energy_kcal <= 250
                          ? '⚠ Less Stable' 
                          : '✗ Unstable'}
                      </Badge>
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center gap-3">
                        <div className="text-3xl font-bold font-mono">
                          <span className={
                            structureResults.conformational_energy_kcal <= 50
                              ? 'text-green-700' 
                              : structureResults.conformational_energy_kcal <= 85
                              ? 'text-blue-700'
                              : structureResults.conformational_energy_kcal <= 250
                              ? 'text-yellow-700' 
                              : 'text-red-700'
                          }>
                            ΔE = {structureResults.conformational_energy_kcal.toFixed(2)}
                          </span>
                          <span className="text-lg ml-2 opacity-70">kcal/mol</span>
                        </div>
                      </div>
                      <p className="text-xs leading-relaxed opacity-80">
                        {structureResults.conformational_energy_kcal <= 50
                          ? 'Low conformational energy indicates excellent linker adaptability within the MOF framework. Structure is very stable and feasible for synthesis.' 
                          : structureResults.conformational_energy_kcal <= 85
                          ? 'Moderate conformational energy shows good linker adaptation. Structure is stable with high synthesis feasibility.'
                          : structureResults.conformational_energy_kcal <= 250
                          ? 'High conformational energy indicates strain on the linker. Structure is less stable, synthesis requires special optimization conditions.' 
                          : 'Very high conformational energy shows significant linker distortion. Structure is unstable, synthesis is extremely challenging or not feasible.'}
                      </p>
                      {/* Visual Scale */}
                      <div className="relative pt-3">
                        <div className="h-2 bg-gradient-to-r from-green-300 via-blue-300 via-yellow-300 to-red-300 rounded-full"></div>
                        <div 
                          className="absolute top-3 w-1 h-4 bg-gray-900 rounded-full transition-all"
                          style={{
                            left: `${Math.min(100, Math.max(0, (structureResults.conformational_energy_kcal / 300) * 100))}%`
                          }}
                        ></div>
                        <div className="flex justify-between text-[9px] font-medium mt-1 opacity-60">
                          <span>0</span>
                          <span>50</span>
                          <span>85</span>
                          <span>250</span>
                          <span>300+</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                
                {/* 4 Output xTB */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 md:gap-6">
                  {/* 1. Conformational Energy with stability-based colors */}
                  <div className={`p-4 md:p-6 rounded-2xl border transition-all hover:scale-[1.02] shadow-sm ${
                    structureResults.conformational_energy_kcal <= 50
                      ? 'bg-gradient-to-br from-green-50 to-emerald-50 border-green-100/50'
                      : structureResults.conformational_energy_kcal <= 85
                      ? 'bg-gradient-to-br from-blue-50 to-cyan-50 border-blue-100/50'
                      : structureResults.conformational_energy_kcal <= 250
                      ? 'bg-gradient-to-br from-yellow-50 to-amber-50 border-yellow-100/50'
                      : 'bg-gradient-to-br from-red-50 to-rose-50 border-red-100/50'
                  }`}>
                    <div className="flex items-center justify-between mb-2">
                      <span className={`text-xs font-bold uppercase tracking-wider ${
                        structureResults.conformational_energy_kcal <= 50
                          ? 'text-green-600'
                          : structureResults.conformational_energy_kcal <= 85
                          ? 'text-blue-600'
                          : structureResults.conformational_energy_kcal <= 250
                          ? 'text-yellow-600'
                          : 'text-red-600'
                      }`}>Conformational Energy</span>
                      <Zap className={`w-4 h-4 ${
                        structureResults.conformational_energy_kcal <= 50
                          ? 'text-green-500'
                          : structureResults.conformational_energy_kcal <= 85
                          ? 'text-blue-500'
                          : structureResults.conformational_energy_kcal <= 250
                          ? 'text-yellow-500'
                          : 'text-red-500'
                      }`} />
                    </div>
                    <div className="flex items-baseline gap-2">
                      <span className={`text-2xl md:text-3xl font-bold font-mono ${
                        structureResults.conformational_energy_kcal <= 50
                          ? 'text-green-900'
                          : structureResults.conformational_energy_kcal <= 85
                          ? 'text-blue-900'
                          : structureResults.conformational_energy_kcal <= 250
                          ? 'text-yellow-900'
                          : 'text-red-900'
                      }`}>
                        {structureResults.conformational_energy_kcal.toFixed(1)}
                      </span>
                      <span className={`text-sm font-medium ${
                        structureResults.conformational_energy_kcal <= 50
                          ? 'text-green-600'
                          : structureResults.conformational_energy_kcal <= 85
                          ? 'text-blue-600'
                          : structureResults.conformational_energy_kcal <= 250
                          ? 'text-yellow-600'
                          : 'text-red-600'
                      }`}>kcal/mol</span>
                    </div>
                  </div>

                  {/* 2. RMSD Final (Å) with simple explanation */}
                  <div className={`p-4 md:p-6 rounded-2xl border transition-all hover:scale-[1.02] shadow-sm ${
                    structureResults.rmsd_final_angstrom <= 0.7 
                      ? 'bg-gradient-to-br from-green-50 to-emerald-50 border-green-100/50'
                      : 'bg-gradient-to-br from-red-50 to-rose-50 border-red-100/50'
                  }`}>
                    <div className="flex items-center justify-between mb-2">
                      <span className={`text-xs font-bold uppercase tracking-wider ${
                        structureResults.rmsd_final_angstrom <= 0.7 ? 'text-green-600' : 'text-red-600'
                      }`}>RMSD Final</span>
                      <Activity className={`w-4 h-4 ${
                        structureResults.rmsd_final_angstrom <= 0.7 ? 'text-green-500' : 'text-red-500'
                      }`} />
                    </div>
                    <div className="flex items-baseline gap-2">
                      <span className={`text-2xl md:text-3xl font-bold font-mono ${
                        structureResults.rmsd_final_angstrom <= 0.7 ? 'text-green-900' : 'text-red-900'
                      }`}>
                        {structureResults.rmsd_final_angstrom.toFixed(4)}
                      </span>
                      <span className={`text-sm font-medium ${
                        structureResults.rmsd_final_angstrom <= 0.7 ? 'text-green-600' : 'text-red-600'
                      }`}>Å</span>
                    </div>
                    <p className={`text-[10px] mt-2 font-medium ${
                      structureResults.rmsd_final_angstrom <= 0.7 ? 'text-green-700' : 'text-red-700'
                    }`}>
                      {structureResults.rmsd_final_angstrom <= 0.7 
                        ? '≤ 0.7 Å: Good structural alignment' 
                        : '> 0.7 Å: Poor structural alignment'}
                    </p>
                  </div>

                  {/* 3. ME delta length (Å) - always green */}
                  <div className="bg-gradient-to-br from-green-50 to-emerald-50 border-green-100/50 p-4 md:p-6 rounded-2xl border transition-all hover:scale-[1.02] shadow-sm">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-bold uppercase tracking-wider text-green-600">ME Δ Length</span>
                      <Box className="w-4 h-4 text-green-500" />
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-baseline gap-2">
                        <span className="text-2xl md:text-3xl font-bold font-mono text-green-900">
                          {structureResults.me_delta_length_angstrom < 0 
                            ? structureResults.me_delta_length_angstrom.toFixed(6)
                            : structureResults.me_delta_length_angstrom.toFixed(6)}
                        </span>
                        <span className="text-sm font-medium text-green-600">Å</span>
                      </div>
                      <p className="text-[10px] font-medium text-green-700">
                        {structureResults.me_delta_length_angstrom < 0 
                          ? '-0.1 (bond shortening)'
                          : structureResults.me_delta_length_angstrom > 0 
                          ? '+0.7 (bond elongation)'
                          : '0.0 (no change)'}
                      </p>
                    </div>
                  </div>

                  {/* 4. ME delta angle (deg) - always green */}
                  <div className="bg-gradient-to-br from-green-50 to-emerald-50 border-green-100/50 p-4 md:p-6 rounded-2xl border transition-all hover:scale-[1.02] shadow-sm">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-bold uppercase tracking-wider text-green-600">ME Δ Angle</span>
                      <Thermometer className="w-4 h-4 text-green-500" />
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-baseline gap-2">
                        <span className="text-2xl md:text-3xl font-bold font-mono text-green-900">
                          {structureResults.me_delta_angle_deg < 0 
                            ? structureResults.me_delta_angle_deg.toFixed(4)
                            : structureResults.me_delta_angle_deg.toFixed(4)}
                        </span>
                        <span className="text-sm font-medium text-green-600">deg</span>
                      </div>
                      <p className="text-[10px] font-medium text-green-700">
                        {structureResults.me_delta_angle_deg < 0 
                          ? '-0.3 (angle narrowing)'
                          : structureResults.me_delta_angle_deg > 0 
                          ? '+0.2 (angle widening)'
                          : '0.0 (no change)'}
                      </p>
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
              
              {/* NEW: 3D Linker Structure Visualization - Two XYZ Files */}
              {(structureResults.free_structure || structureResults.embedded_structure) && (
                <div className="space-y-6 pt-8 border-t border-zinc-100 animate-in slide-in-from-bottom duration-700">
                  <LinkerStructureViewer
                    freeStructure={structureResults.free_structure}
                    embeddedStructure={structureResults.embedded_structure}
                    uploadMode={structureResults.upload_mode || 'none'}
                    loading={loadingStates.structure}
                  />
                </div>
              )}
              
              {/* NEW: 3D Visualization from CIF - Futuristic & Dynamic */}
              {structure3D && (
                <div className="space-y-6 pt-8 border-t border-zinc-100 animate-in slide-in-from-bottom duration-700">
                  {/* Section Header - Futuristic */}
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-3 bg-gradient-to-r from-indigo-500 to-purple-600 px-4 py-2 rounded-full shadow-lg">
                      <Box className="w-4 h-4 text-white animate-pulse" />
                      <h4 className="text-[10px] font-bold text-white uppercase tracking-[0.2em]">3D Structure</h4>
                    </div>
                    <div className="h-0.5 bg-gradient-to-r from-indigo-200 via-purple-200 to-transparent flex-1" />
                    {loading3D && (
                      <div className="flex items-center gap-2 text-[8px] text-indigo-600 font-bold bg-indigo-50 px-3 py-1.5 rounded-full animate-pulse border border-indigo-200">
                        <Loader2 className="w-3 h-3 animate-spin" />
                        LOADING
                      </div>
                    )}
                  </div>
                  
                  {/* Structure Info Cards - Modern Grid */}
                  <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
                    {/* Formula */}
                    <div className="group relative bg-gradient-to-br from-blue-500 to-cyan-600 p-5 rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-[1.02] overflow-hidden">
                      <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity" />
                      <div className="relative z-10">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-[9px] font-bold text-white/80 uppercase tracking-[0.15em]">Formula</span>
                          <Database className="w-3.5 h-3.5 text-white/60" />
                        </div>
                        <div className="text-base md:text-lg font-mono font-black text-white break-all">
                          {structure3D.formula || 'N/A'}
                        </div>
                      </div>
                    </div>

                    {/* Total Atoms */}
                    <div className="group relative bg-gradient-to-br from-purple-500 to-pink-600 p-5 rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-[1.02] overflow-hidden">
                      <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity" />
                      <div className="relative z-10">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-[9px] font-bold text-white/80 uppercase tracking-[0.15em]">Atoms</span>
                          <Layers className="w-3.5 h-3.5 text-white/60" />
                        </div>
                        <div className="text-2xl md:text-3xl font-black text-white tabular-nums">
                          {structure3D.structure_3d?.atoms?.length || 0}
                        </div>
                      </div>
                    </div>

                    {/* Cell Length */}
                    <div className="group relative bg-gradient-to-br from-emerald-500 to-teal-600 p-5 rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-[1.02] overflow-hidden">
                      <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity" />
                      <div className="relative z-10">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-[9px] font-bold text-white/80 uppercase tracking-[0.15em]">Cell a</span>
                          <Box className="w-3.5 h-3.5 text-white/60" />
                        </div>
                        <div className="flex items-baseline gap-1">
                          <span className="text-2xl md:text-3xl font-black text-white tabular-nums">
                            {structure3D.cell_params?.a?.toFixed(2) || 'N/A'}
                          </span>
                          <span className="text-xs font-bold text-white/70">Å</span>
                        </div>
                      </div>
                    </div>

                    {/* Volume */}
                    <div className="group relative bg-gradient-to-br from-orange-500 to-red-600 p-5 rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-[1.02] overflow-hidden">
                      <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity" />
                      <div className="relative z-10">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-[9px] font-bold text-white/80 uppercase tracking-[0.15em]">Volume</span>
                          <Scale className="w-3.5 h-3.5 text-white/60" />
                        </div>
                        <div className="flex items-baseline gap-1">
                          <span className="text-xl md:text-2xl font-black text-white tabular-nums">
                            {structure3D.cell_params ? 
                              (structure3D.cell_params.a * structure3D.cell_params.b * structure3D.cell_params.c).toFixed(0) 
                              : 'N/A'}
                          </span>
                          <span className="text-xs font-bold text-white/70">Å³</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {/* 3D Viewer Container - Futuristic Design */}
                  <div className="relative rounded-3xl overflow-hidden shadow-2xl border border-indigo-100/50 bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/50">
                    {/* Animated Header */}
                    <div className="relative overflow-hidden bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-600 bg-size-200 animate-gradient">
                      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSAwIDEwIEwgNDAgMTAgTSAxMCAwIEwgMTAgNDAgTSAwIDIwIEwgNDAgMjAgTSAyMCAwIEwgMjAgNDAgTSAwIDMwIEwgNDAgMzAgTSAzMCAwIEwgMzAgNDAiIGZpbGw9Im5vbmUiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS1vcGFjaXR5PSIwLjA1IiBzdHJva2Utd2lkdGg9IjEiLz48L3BhdHRlcm4+PC9kZWZzPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9InVybCgjZ3JpZCkiLz48L3N2Zz4=')] opacity-30" />
                      <div className="relative px-6 py-4 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="p-2 bg-white/20 rounded-xl backdrop-blur-sm">
                            <Box className="w-5 h-5 text-white" />
                          </div>
                          <div>
                            <h3 className="text-sm md:text-base font-black text-white uppercase tracking-wider">MOF Structure</h3>
                            <p className="text-[10px] text-white/70 font-medium">Unit Cell Visualization</p>
                          </div>
                        </div>
                        <Badge className="bg-white/20 text-white border-white/30 backdrop-blur-sm font-bold text-[10px] px-3 py-1">
                          Interactive View
                        </Badge>
                      </div>
                    </div>
                    
                    {/* Viewer Area */}
                    <div className="p-6">
                      <div className="relative bg-gradient-to-br from-white via-slate-50 to-blue-50/30 rounded-2xl border-2 border-indigo-100 overflow-hidden shadow-inner" style={{ height: '480px' }}>
                        {/* Decorative grid background */}
                        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9InNtYWxsR3JpZCIgd2lkdGg9IjYwIiBoZWlnaHQ9IjYwIiBwYXR0ZXJuVW5pdHM9InVzZXJTcGFjZU9uVXNlIj48cGF0aCBkPSJNIDYwIDAgTCAwIDAgMCA2MCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjZTBlN2ZmIiBzdHJva2Utd2lkdGg9IjEiLz48L3BhdHRlcm4+PC9kZWZzPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9InVybCgjc21hbGxHcmlkKSIvPjwvc3ZnPg==')] opacity-40" />
                        
                        {/* Real 3D Viewer using 3Dmol.js */}
                        <div className="relative z-10 w-full h-full">
                          {structure3D.cif_content ? (
                            <MOF3DViewer 
                              cifContent={structure3D.cif_content}
                              style={{ width: '100%', height: '100%' }}
                            />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center p-8">
                              <div className="text-center space-y-4">
                                <Loader2 className="w-12 h-12 text-indigo-600 animate-spin mx-auto" />
                                <p className="text-sm font-bold text-indigo-600">Loading CIF content...</p>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

            </div>
          </div>
        </section>
      </main>
      
      {/* About Modal */}
      {showAbout && (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-16 bg-black/20 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="relative w-full max-w-4xl mx-4 bg-white rounded-[32px] shadow-2xl animate-in slide-in-from-top duration-300">
            {/* Header */}
            <div className="flex items-center justify-between p-8 border-b border-zinc-100">
              <div className="flex items-center gap-4">
                <img 
                  src="/triaxismof.svg" 
                  alt="TRIAXIS-MOF Logo" 
                  className="w-12 h-12 rounded-full"
                />
                <div>
                  <h2 className="text-2xl font-bold tracking-tight">TRIAXIS-MOF</h2>
                  <p className="text-sm text-zinc-500">Triple-Modality Analytics for Explainable, Integrated Screening</p>
                </div>
              </div>
              <button 
                onClick={(e) => {
                  e.preventDefault();
                  setShowAbout(false);
                }}
                className="p-2 hover:bg-zinc-100 rounded-xl transition-colors"
              >
                <X className="w-5 h-5 text-zinc-400" />
              </button>
            </div>
            
            {/* Content */}
            <div className="p-8 max-h-96 overflow-y-auto">
              <div className="prose prose-zinc max-w-none">
                <p className="text-lg leading-relaxed mb-6">
                  <strong>TRIAXIS-MOF</strong> (Triple-Modality Analytics for Explainable, Integrated Screening of Metal–Organic Frameworks) 
                  is an integrated, data-driven screening platform designed to identify high-performance MOF materials for industrial 
                  hydrogen storage applications.
                </p>
                
                <div className="bg-gradient-to-br from-indigo-50 to-blue-50 p-6 rounded-2xl mb-6">
                  <h3 className="text-lg font-semibold text-indigo-900 mb-3">Database Coverage</h3>
                  <p className="text-indigo-700">
                    Built on a comprehensive database of <strong>98,694 CoRE-MOF</strong>, more than <strong>500 SynMOF</strong> and 
                    <strong> MOF DB-BAM</strong> structures, ensuring extensive material coverage and reliable predictions.
                  </p>
                </div>
                
                <h3 className="text-lg font-semibold mb-4">Three Core Analytical Pillars</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div className="bg-white border border-zinc-200 p-5 rounded-xl">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                        <span className="text-green-600 font-bold text-sm">1</span>
                      </div>
                      <h4 className="font-semibold text-green-800">White-box ML</h4>
                    </div>
                    <p className="text-sm text-zinc-600">
                      Interpretable machine learning for transparent performance prediction with full explainability.
                    </p>
                  </div>
                  
                  <div className="bg-white border border-zinc-200 p-5 rounded-xl">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                        <span className="text-blue-600 font-bold text-sm">2</span>
                      </div>
                      <h4 className="font-semibold text-blue-800">Energy Evaluation</h4>
                    </div>
                    <p className="text-sm text-zinc-600">
                      Synthesis energy assessment for comprehensive economic feasibility analysis.
                    </p>
                  </div>
                  
                  <div className="bg-white border border-zinc-200 p-5 rounded-xl">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                        <span className="text-purple-600 font-bold text-sm">3</span>
                      </div>
                      <h4 className="font-semibold text-purple-800">DFT Validation</h4>
                    </div>
                    <p className="text-sm text-zinc-600">
                      Quantum-level density functional theory analysis for stability validation.
                    </p>
                  </div>
                </div>
                
                <div className="bg-gradient-to-br from-zinc-50 to-slate-50 p-6 rounded-2xl">
                  <h3 className="text-lg font-semibold mb-3">Unified Decision Pipeline</h3>
                  <p className="text-zinc-700 mb-4">
                    These three modalities are unified into a single explainable and physically consistent decision pipeline, 
                    ensuring transparency, scientific rigor, and full auditability.
                  </p>
                  <p className="text-zinc-700">
                    <strong>TRIAXIS-MOF</strong> generates robust material fingerprints, interpretable predictions, and 
                    quantum-validated stability insights, accelerating the discovery of hydrogen storage materials that are 
                    both technically viable and economically competitive.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Footer */}
      <footer className="mt-16 border-t border-zinc-200/50 bg-white/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 md:px-8 py-6">
          <div className="text-center">
            <p className="text-sm text-zinc-500">
              © 2026 TRIAXIS-MOF. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
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
          className={`pr-9 sm:pr-10 rounded-[14px] border-zinc-200 bg-white/80 backdrop-blur-sm h-11 md:h-12 w-full text-[14px] font-medium focus-visible:ring-4 focus-visible:ring-blue-500/10 focus-visible:border-blue-500/30 transition-all shadow-sm no-scroll-jump ${icon ? 'pl-10 md:pl-11' : 'pl-4'}`} 
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