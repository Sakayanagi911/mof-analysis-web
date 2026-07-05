"use client";

import React, { useEffect, useRef, useState } from 'react';
import { Loader2, ZoomIn, ZoomOut, RotateCw, Maximize2 } from 'lucide-react';

interface MOF3DViewerProps {
  cifContent: string;
  style?: React.CSSProperties;
}

export default function MOF3DViewer({ cifContent, style }: MOF3DViewerProps) {
  const viewerRef = useRef<HTMLDivElement>(null);
  const viewerInstance = useRef<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!viewerRef.current || !cifContent) return;

    let isMounted = true;

    const initViewer = async () => {
      try {
        setLoading(true);
        setError(null);

        // Dynamically import 3Dmol
        const $3Dmol = (await import('3dmol')).default;

        if (!isMounted) return;

        // Create viewer
        const config = {
          backgroundColor: 'white',
        };
        
        const viewer = $3Dmol.createViewer(viewerRef.current!, config);
        viewerInstance.current = viewer;

        // Load CIF structure
        viewer.addModel(cifContent, 'cif');
        
        // Set style: ball and stick representation
        viewer.setStyle({}, {
          stick: { radius: 0.15, color: 'spectrum' },
          sphere: { scale: 0.25, colorscheme: 'Jmol' }
        });

        // Add unit cell box
        viewer.addUnitCell();

        // Center and zoom
        viewer.zoomTo();
        viewer.zoom(0.8);
        
        // Render
        viewer.render();

        setLoading(false);
      } catch (err) {
        console.error('3Dmol viewer error:', err);
        if (isMounted) {
          setError('Failed to load 3D structure');
          setLoading(false);
        }
      }
    };

    initViewer();

    return () => {
      isMounted = false;
      if (viewerInstance.current) {
        // Cleanup if needed
      }
    };
  }, [cifContent]);

  const handleZoomIn = () => {
    if (viewerInstance.current) {
      viewerInstance.current.zoom(1.2);
      viewerInstance.current.render();
    }
  };

  const handleZoomOut = () => {
    if (viewerInstance.current) {
      viewerInstance.current.zoom(0.8);
      viewerInstance.current.render();
    }
  };

  const handleReset = () => {
    if (viewerInstance.current) {
      viewerInstance.current.zoomTo();
      viewerInstance.current.zoom(0.8);
      viewerInstance.current.render();
    }
  };

  const handleFullscreen = () => {
    if (viewerRef.current) {
      if (viewerRef.current.requestFullscreen) {
        viewerRef.current.requestFullscreen();
      }
    }
  };

  return (
    <div className="relative w-full h-full" style={style}>
      {/* 3Dmol Viewer Container */}
      <div 
        ref={viewerRef} 
        className="w-full h-full rounded-xl overflow-hidden"
        style={{ minHeight: '400px' }}
      />

      {/* Loading Overlay */}
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center bg-white/80 backdrop-blur-sm rounded-xl">
          <div className="text-center space-y-3">
            <Loader2 className="w-10 h-10 text-indigo-600 animate-spin mx-auto" />
            <p className="text-sm font-semibold text-indigo-600">Loading 3D Structure...</p>
          </div>
        </div>
      )}

      {/* Error Overlay */}
      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-red-50/80 backdrop-blur-sm rounded-xl">
          <div className="text-center space-y-2 p-6">
            <p className="text-sm font-semibold text-red-600">{error}</p>
            <p className="text-xs text-red-500">Please check your CIF file format</p>
          </div>
        </div>
      )}

      {/* Control Buttons */}
      {!loading && !error && (
        <div className="absolute bottom-4 right-4 flex gap-2">
          <button
            onClick={handleZoomIn}
            className="p-2.5 bg-white/90 backdrop-blur-sm hover:bg-indigo-50 rounded-xl border border-indigo-100 shadow-lg transition-all hover:scale-105 group"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4 text-indigo-600 group-hover:text-indigo-700" />
          </button>
          <button
            onClick={handleZoomOut}
            className="p-2.5 bg-white/90 backdrop-blur-sm hover:bg-indigo-50 rounded-xl border border-indigo-100 shadow-lg transition-all hover:scale-105 group"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4 text-indigo-600 group-hover:text-indigo-700" />
          </button>
          <button
            onClick={handleReset}
            className="p-2.5 bg-white/90 backdrop-blur-sm hover:bg-indigo-50 rounded-xl border border-indigo-100 shadow-lg transition-all hover:scale-105 group"
            title="Reset View"
          >
            <RotateCw className="w-4 h-4 text-indigo-600 group-hover:text-indigo-700" />
          </button>
          <button
            onClick={handleFullscreen}
            className="p-2.5 bg-white/90 backdrop-blur-sm hover:bg-indigo-50 rounded-xl border border-indigo-100 shadow-lg transition-all hover:scale-105 group"
            title="Fullscreen"
          >
            <Maximize2 className="w-4 h-4 text-indigo-600 group-hover:text-indigo-700" />
          </button>
        </div>
      )}

      {/* Interaction Hint */}
      {!loading && !error && (
        <div className="absolute top-4 left-4 bg-indigo-600/90 backdrop-blur-sm px-4 py-2 rounded-full shadow-lg">
          <p className="text-xs font-semibold text-white">
            🖱️ Drag to rotate • Scroll to zoom
          </p>
        </div>
      )}
    </div>
  );
}
