"use client";

import React, { useEffect, useRef } from 'react';
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Loader2, Layers } from 'lucide-react';

interface StructureData {
  atoms: Array<{symbol: string, x: number, y: number, z: number}>;
  bonds: Array<[number, number]>;
  num_atoms: number;
  delta_r?: number[];  // Atom-wise displacement for color mapping
  delta_r_min?: number;
  delta_r_max?: number;
}

interface LinkerStructureViewerProps {
  freeStructure: StructureData | null;
  embeddedStructure: StructureData | null;
  uploadMode: string;
  loading?: boolean;
}

declare global {
  interface Window {
    $3Dmol: any;
  }
}

const LinkerStructureViewer: React.FC<LinkerStructureViewerProps> = ({
  freeStructure,
  embeddedStructure,
  uploadMode,
  loading = false
}) => {
  const freeViewerRef = useRef<HTMLDivElement>(null);  // For side-by-side view
  const overlayViewerRef = useRef<HTMLDivElement>(null);  // For overlay view
  const [viewMode, setViewMode] = React.useState<'sidebyside' | 'overlay'>('sidebyside');

  // Helper function: Map delta_r value to viridis color (matches notebook)
  const deltaRToColor = (value: number, min: number, max: number): string => {
    // Normalize to 0-1
    const t = (value - min) / (max - min);
    
    // Viridis colormap approximation (RGB values at key points)
    const viridis = [
      [68, 1, 84],      // Purple (t=0)
      [59, 82, 139],    // Blue (t=0.25)
      [33, 145, 140],   // Cyan (t=0.5)
      [94, 201, 98],    // Green (t=0.75)
      [253, 231, 37]    // Yellow (t=1)
    ];
    
    // Linear interpolation
    const segments = viridis.length - 1;
    const segment = Math.min(Math.floor(t * segments), segments - 1);
    const localT = (t * segments) - segment;
    
    const c1 = viridis[segment];
    const c2 = viridis[segment + 1];
    
    const r = Math.round(c1[0] + (c2[0] - c1[0]) * localT);
    const g = Math.round(c1[1] + (c2[1] - c1[1]) * localT);
    const b = Math.round(c1[2] + (c2[2] - c1[2]) * localT);
    
    return `rgb(${r},${g},${b})`;
  };

  // Convert structure data to XYZ format
  const structureToXYZ = (structure: StructureData, title: string, offsetY: number = 0): string => {
    let xyz = `${structure.atoms.length}\n`;
    xyz += `${title}\n`;
    for (const atom of structure.atoms) {
      xyz += `${atom.symbol} ${atom.x.toFixed(6)} ${(atom.y + offsetY).toFixed(6)} ${atom.z.toFixed(6)}\n`;
    }
    return xyz;
  };

  // Initialize 3Dmol viewer for side-by-side view (visual offset Y+4.9)
  useEffect(() => {
    if (viewMode !== 'sidebyside') return;
    
    if (typeof window === 'undefined' || !window.$3Dmol) {
      console.warn('3Dmol.js not loaded yet');
      return;
    }

    if (freeStructure && embeddedStructure && freeViewerRef.current && uploadMode === 'two_xyz') {
      const viewer = window.$3Dmol.createViewer(freeViewerRef.current, {
        backgroundColor: 'white',
        antialias: true
      });

      const freeAtoms = freeStructure.atoms;
      const embeddedAtoms = embeddedStructure.atoms;
      
      // Calculate centers
      const freeCenterX = freeAtoms.reduce((sum: number, a: any) => sum + a.x, 0) / freeAtoms.length;
      const freeCenterY = freeAtoms.reduce((sum: number, a: any) => sum + a.y, 0) / freeAtoms.length;
      const freeCenterZ = freeAtoms.reduce((sum: number, a: any) => sum + a.z, 0) / freeAtoms.length;
      
      const embCenterX = embeddedAtoms.reduce((sum: number, a: any) => sum + a.x, 0) / embeddedAtoms.length;
      const embCenterY = embeddedAtoms.reduce((sum: number, a: any) => sum + a.y, 0) / embeddedAtoms.length;
      const embCenterZ = embeddedAtoms.reduce((sum: number, a: any) => sum + a.z, 0) / embeddedAtoms.length;
      
      const VISUAL_SHIFT_Y = 4.9;

      // Add free linker (centered, gray)
      let xyzFree = `${freeAtoms.length}\nfree_centered\n`;
      for (const atom of freeAtoms) {
        xyzFree += `${atom.symbol} ${(atom.x - freeCenterX).toFixed(6)} ${(atom.y - freeCenterY).toFixed(6)} ${(atom.z - freeCenterZ).toFixed(6)}\n`;
      }
      
      viewer.addModel(xyzFree, 'xyz');
      viewer.setStyle({ model: 0 }, { stick: { radius: 0.13, color: 'lightgray' }, sphere: { radius: 0.25, color: 'lightgray' } });

      // Add embedded linker (centered + visual offset, colored by Δr)
      let xyzEmbedded = `${embeddedAtoms.length}\nembedded_centered_visual\n`;
      for (const atom of embeddedAtoms) {
        xyzEmbedded += `${atom.symbol} ${(atom.x - embCenterX).toFixed(6)} ${((atom.y - embCenterY) + VISUAL_SHIFT_Y).toFixed(6)} ${(atom.z - embCenterZ).toFixed(6)}\n`;
      }
      
      viewer.addModel(xyzEmbedded, 'xyz');
      
      // Color by delta_r
      if (embeddedStructure.delta_r && embeddedStructure.delta_r_min !== undefined && embeddedStructure.delta_r_max !== undefined) {
        const deltaR = embeddedStructure.delta_r;
        const minDelta = embeddedStructure.delta_r_min;
        const maxDelta = embeddedStructure.delta_r_max;
        
        for (let i = 0; i < deltaR.length; i++) {
          const color = deltaRToColor(deltaR[i], minDelta, maxDelta);
          viewer.setStyle({ model: 1, index: i }, { stick: { radius: 0.18, color }, sphere: { radius: 0.32, color } });
        }
      } else {
        viewer.setStyle({ model: 1 }, { stick: { radius: 0.18, colorscheme: 'Jmol' }, sphere: { radius: 0.32, colorscheme: 'Jmol' } });
      }
      
      viewer.zoomTo();
      viewer.render();
      viewer.zoom(1.0);
    }
  }, [freeStructure, embeddedStructure, uploadMode, viewMode]);

  // Initialize 3Dmol viewer for overlay view (both at same center)
  useEffect(() => {
    if (viewMode !== 'overlay') return;
    
    if (typeof window === 'undefined' || !window.$3Dmol) {
      console.warn('3Dmol.js not loaded yet');
      return;
    }

    if (freeStructure && embeddedStructure && overlayViewerRef.current && uploadMode === 'two_xyz') {
      const viewer = window.$3Dmol.createViewer(overlayViewerRef.current, {
        backgroundColor: 'white',
        antialias: true
      });

      const freeAtoms = freeStructure.atoms;
      const embeddedAtoms = embeddedStructure.atoms;
      
      // Calculate centers
      const freeCenterX = freeAtoms.reduce((sum: number, a: any) => sum + a.x, 0) / freeAtoms.length;
      const freeCenterY = freeAtoms.reduce((sum: number, a: any) => sum + a.y, 0) / freeAtoms.length;
      const freeCenterZ = freeAtoms.reduce((sum: number, a: any) => sum + a.z, 0) / freeAtoms.length;
      
      const embCenterX = embeddedAtoms.reduce((sum: number, a: any) => sum + a.x, 0) / embeddedAtoms.length;
      const embCenterY = embeddedAtoms.reduce((sum: number, a: any) => sum + a.y, 0) / embeddedAtoms.length;
      const embCenterZ = embeddedAtoms.reduce((sum: number, a: any) => sum + a.z, 0) / embeddedAtoms.length;

      // Add free linker (centered, gray, thinner)
      let xyzFree = `${freeAtoms.length}\nfree_centered\n`;
      for (const atom of freeAtoms) {
        xyzFree += `${atom.symbol} ${(atom.x - freeCenterX).toFixed(6)} ${(atom.y - freeCenterY).toFixed(6)} ${(atom.z - freeCenterZ).toFixed(6)}\n`;
      }
      
      viewer.addModel(xyzFree, 'xyz');
      viewer.setStyle({ model: 0 }, { stick: { radius: 0.13, color: 'lightgray' }, sphere: { radius: 0.25, color: 'lightgray' } });

      // Add embedded linker (centered, colored by Δr, thicker)
      let xyzEmbedded = `${embeddedAtoms.length}\nembedded_centered\n`;
      for (const atom of embeddedAtoms) {
        xyzEmbedded += `${atom.symbol} ${(atom.x - embCenterX).toFixed(6)} ${(atom.y - embCenterY).toFixed(6)} ${(atom.z - embCenterZ).toFixed(6)}\n`;
      }
      
      viewer.addModel(xyzEmbedded, 'xyz');
      
      // Color by delta_r
      if (embeddedStructure.delta_r && embeddedStructure.delta_r_min !== undefined && embeddedStructure.delta_r_max !== undefined) {
        const deltaR = embeddedStructure.delta_r;
        const minDelta = embeddedStructure.delta_r_min;
        const maxDelta = embeddedStructure.delta_r_max;
        
        for (let i = 0; i < deltaR.length; i++) {
          const color = deltaRToColor(deltaR[i], minDelta, maxDelta);
          viewer.setStyle({ model: 1, index: i }, { stick: { radius: 0.18, color }, sphere: { radius: 0.35, color } });
        }
      } else {
        viewer.setStyle({ model: 1 }, { stick: { radius: 0.18, colorscheme: 'Jmol' }, sphere: { radius: 0.35, colorscheme: 'Jmol' } });
      }
      
      viewer.zoomTo();
      viewer.render();
      viewer.zoom(1.0);
    }
  }, [freeStructure, embeddedStructure, uploadMode, viewMode]);

  // Loading state
  if (loading) {
    return (
      <Card className="p-8">
        <div className="flex flex-col items-center justify-center gap-4">
          <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
          <p className="text-sm text-zinc-600">Analyzing structures...</p>
        </div>
      </Card>
    );
  }

  // No structures uploaded
  if (!freeStructure && !embeddedStructure) {
    return (
      <Card className="p-8 bg-gradient-to-br from-zinc-50 to-slate-50">
        <div className="text-center space-y-3">
          <div className="mx-auto w-16 h-16 bg-zinc-100 rounded-full flex items-center justify-center">
            <svg className="w-8 h-8 text-zinc-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-zinc-700">No Structure Data</h3>
          <p className="text-sm text-zinc-500">
            Upload <strong>free + embedded XYZ files</strong> to view 3D structures
          </p>
        </div>
      </Card>
    );
  }

  // Two XYZ mode (BEST) - Show visualization with toggle buttons
  if (uploadMode === 'two_xyz' && freeStructure && embeddedStructure) {
    const deltaMin = embeddedStructure.delta_r_min || 0;
    const deltaMax = embeddedStructure.delta_r_max || 1;
    const legendLevels = [0, 0.25, 0.5, 0.75, 1].map(t => deltaMin + t * (deltaMax - deltaMin));
    const legendColors = legendLevels.map(val => deltaRToColor(val, deltaMin, deltaMax));

    return (
      <div className="space-y-6">
        {/* Header with Toggle Buttons */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-3 bg-gradient-to-r from-indigo-500 to-purple-600 px-4 py-2.5 rounded-xl shadow-lg">
              <Layers className="w-5 h-5 text-white" />
              <h4 className="text-sm font-bold text-white">Distortion Visualization</h4>
            </div>
          </div>
          
          {/* Modern Toggle Buttons */}
          <div className="flex items-center gap-2 bg-gradient-to-r from-gray-100 to-gray-200 p-1.5 rounded-xl shadow-inner">
            <button
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                setViewMode('sidebyside');
              }}
              className={`px-5 py-2.5 text-sm font-semibold rounded-lg transition-all duration-300 flex items-center gap-2 no-scroll-jump ${
                viewMode === 'sidebyside'
                  ? 'bg-white text-indigo-700 shadow-lg scale-105'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
              Side-by-Side
            </button>
            <button
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                setViewMode('overlay');
              }}
              className={`px-5 py-2.5 text-sm font-semibold rounded-lg transition-all duration-300 flex items-center gap-2 no-scroll-jump ${
                viewMode === 'overlay'
                  ? 'bg-white text-purple-700 shadow-lg scale-105'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
              Overlay
            </button>
          </div>
        </div>

        {/* Visualization Container */}
        <Card className="overflow-hidden shadow-xl">
          <div className={`p-4 border-b ${viewMode === 'sidebyside' ? 'bg-gradient-to-r from-blue-50 to-cyan-50' : 'bg-gradient-to-r from-purple-50 to-pink-50'}`}>
            <div className="flex items-center justify-between">
              <div>
                <h4 className={`text-sm font-bold ${viewMode === 'sidebyside' ? 'text-blue-900' : 'text-purple-900'}`}>
                  {viewMode === 'sidebyside' ? '📊 Side-by-Side View' : '📊 Overlay View'}
                </h4>
                <p className={`text-xs mt-1 ${viewMode === 'sidebyside' ? 'text-blue-600' : 'text-purple-600'}`}>
                  {viewMode === 'sidebyside' 
                    ? 'Free linker visually shifted (offset Y = +4.9 Å) • Calculations use same center'
                    : 'Both structures at same center • Shows geometric distortion clearly'}
                </p>
              </div>
              <Badge variant="outline" className="text-xs bg-white">
                {embeddedStructure.num_atoms} atoms
              </Badge>
            </div>
          </div>
          
          {/* 3D Viewer with Legend Overlay */}
          <div className="relative bg-white">
            {/* Side-by-side viewer */}
            {viewMode === 'sidebyside' && (
              <div 
                ref={freeViewerRef} 
                className="w-full h-[600px] bg-white"
                style={{ position: 'relative' }}
              />
            )}
            
            {/* Overlay viewer */}
            {viewMode === 'overlay' && (
              <div 
                ref={overlayViewerRef} 
                className="w-full h-[600px] bg-white"
                style={{ position: 'relative' }}
              />
            )}
            
            {/* Legend Overlay - Bottom Left */}
            <div className="absolute bottom-4 left-4 bg-white/95 backdrop-blur-sm rounded-lg shadow-2xl p-4 border-2 border-indigo-200 max-w-xs">
              <h5 className="text-xs font-bold text-zinc-800 mb-2 flex items-center gap-2">
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
                </svg>
                Atom-wise Displacement (Δr)
              </h5>
              
              {/* Viridis Gradient Bar */}
              <div className="mb-2">
                <div className="h-4 rounded-md shadow-inner" style={{
                  background: `linear-gradient(to right, ${legendColors.join(', ')})`
                }}></div>
                <div className="flex justify-between mt-1 text-[10px] text-zinc-600 font-mono">
                  <span>{deltaMin.toFixed(3)} Å</span>
                  <span>{deltaMax.toFixed(3)} Å</span>
                </div>
              </div>
              
              {/* Structure Legend */}
              <div className="space-y-1.5 mt-3 pt-3 border-t border-zinc-200">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-gray-400 border border-gray-500"></div>
                  <span className="text-[10px] text-zinc-700 font-medium">Free Linker (optimized)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{
                    background: `linear-gradient(to right, ${legendColors[0]}, ${legendColors[legendColors.length-1]})`
                  }}></div>
                  <span className="text-[10px] text-zinc-700 font-medium">Embedded (colored by Δr)</span>
                </div>
              </div>
            </div>
          </div>
          
          {/* Info Footer */}
          <div className={`p-3 border-t text-center ${viewMode === 'sidebyside' ? 'bg-blue-50/50' : 'bg-purple-50/50'}`}>
            <p className={`text-xs font-medium ${viewMode === 'sidebyside' ? 'text-blue-700' : 'text-purple-700'}`}>
              {viewMode === 'sidebyside'
                ? 'ℹ️ Visual offset only for clarity • All calculations (RMSD, ΔE, bond/angle) use same center'
                : 'ℹ️ Deviations show how MOF framework strains bond lengths and angles (RMSD, ΔLength, ΔAngle)'}
            </p>
          </div>
        </Card>

        {/* Energy Info Card */}
        <Card className="p-4 bg-gradient-to-r from-green-50 to-emerald-50 border-green-200">
          <div className="flex items-start gap-3">
            <div className="bg-green-100 p-2 rounded-lg">
              <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div className="flex-1">
              <p className="text-xs text-green-900 font-bold">
                ΔE_conformational = E(embedded) - E(free)
              </p>
              <p className="text-xs text-green-700 mt-1">
                Energy penalty for linker to fit into MOF framework. Lower values → easier synthesis.
              </p>
            </div>
          </div>
        </Card>
      </div>
    );
  }

  // Single structure mode (embedded only)
  if (embeddedStructure) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-bold text-zinc-800">Linker Structure</h3>
          <Badge className="bg-gradient-to-r from-amber-500 to-orange-500 text-white">
            {uploadMode === 'single_xyz' ? 'Mode 2: Single XYZ' : 'Mode 3: CIF Extract'}
          </Badge>
        </div>

        <Card className="overflow-hidden">
          <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-4 border-b">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-bold text-green-900">Embedded Linker</h4>
                <p className="text-xs text-green-600">Extracted from MOF</p>
              </div>
              <Badge variant="outline" className="text-xs bg-white">
                {embeddedStructure.num_atoms} atoms
              </Badge>
            </div>
          </div>
          <div 
            ref={embeddedViewerRef} 
            className="w-full h-[500px] bg-gradient-to-br from-slate-50 to-zinc-50"
            style={{ position: 'relative' }}
          />
          <div className="p-3 bg-amber-50/50 border-t text-center">
            <p className="text-xs text-amber-700 font-medium">
              {uploadMode === 'single_xyz' 
                ? '⚠️ Auto-optimized to get free linker (less accurate)'
                : '⚠️ Auto-extracted from CIF (may have errors)'}
            </p>
          </div>
        </Card>
      </div>
    );
  }

  return null;
};

export default LinkerStructureViewer;
