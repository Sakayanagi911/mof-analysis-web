"use client"; // Diperlukan untuk interaksi form dan state

import React, { useState } from 'react';
import { Upload, Beaker, CheckCircle2, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!file) return alert("Upload file CIF terlebih dahulu!");

    setLoading(true);
    const formData = new FormData();
    const target = e.target as any;

    // Poin 3: CIF File
    formData.append('file', file);

    // Poin 1: Structural Parameters
    const structuralParams = ['pv', 'gsa', 'vsa', 'lcd', 'pld', 'vf', 'density'];
    structuralParams.forEach(param => formData.append(param, target[param].value));

    // Poin 2: Chemical & Synthesis
    formData.append('metal_name', target.metal_name.value);
    formData.append('linker_name', target.linker_name.value);
    formData.append('reaction_time', target.reaction_time.value);
    formData.append('temperature', target.temperature.value);
    formData.append('smiles', target.smiles.value);

    try {
      const res = await fetch("http://127.0.0.1:8000/analyze", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setResults(data.results);
    } catch (err) {
      console.error("Koneksi gagal:", err);
    } finally {
      setLoading(false);
    }
  };

  if (results) return <ResultsView data={results} onBack={() => setResults(null)} />;

  return (
    <div className="min-h-screen bg-zinc-50 py-12 px-6 font-sans">
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold tracking-tight text-zinc-900">MOF Screening Platform</h1>
          <p className="text-zinc-500">Analisis penyimpanan hidrogen, ekonomi, dan stabilitas MOF.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* BAGIAN 3: UPLOAD CIF */}
          <Card className="border-indigo-100">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-bold flex items-center gap-2">
                <Badge className="bg-indigo-600">3</Badge> UPLOAD CIF FILE
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div 
                className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${file ? 'border-indigo-500 bg-indigo-50' : 'border-zinc-200'}`}
                onClick={() => document.getElementById('cif-upload')?.click()}
              >
                <Upload className="mx-auto w-8 h-8 text-zinc-400 mb-2" />
                <p className="text-sm font-medium">{file ? file.name : "Pilih file .cif"}</p>
                <input id="cif-upload" type="file" className="hidden" accept=".cif" onChange={(e) => setFile(e.target.files?.[0] || null)} />
              </div>
            </CardContent>
          </Card>

          {/* BAGIAN 1: PARAMETER STRUKTURAL */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-bold flex items-center gap-2">
                <Badge className="bg-zinc-800">1</Badge> PARAMETER MOF
              </CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {['pv', 'gsa', 'vsa', 'lcd', 'pld', 'vf', 'density'].map((p) => (
                <div key={p} className="space-y-1">
                  <Label className="text-[10px] uppercase font-bold text-zinc-500">{p}</Label>
                  <Input name={p} type="number" step="0.0001" placeholder="0.00" required />
                </div>
              ))}
            </CardContent>
          </Card>

          {/* BAGIAN 2: DATA KIMIA & SINTESIS */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-bold flex items-center gap-2">
                <Badge className="bg-zinc-800">2</Badge> DATA KIMIA & SINTESIS
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1"><Label>Metal Name</Label><Input name="metal_name" required /></div>
                <div className="space-y-1"><Label>Linker Name</Label><Input name="linker_name" required /></div>
                <div className="space-y-1"><Label>Time (h)</Label><Input name="reaction_time" type="number" required /></div>
                <div className="space-y-1"><Label>Temp (°C)</Label><Input name="temperature" type="number" required /></div>
              </div>
              <div className="space-y-1"><Label>SMILES</Label><Input name="smiles" required /></div>
            </CardContent>
          </Card>

          <Button type="submit" disabled={loading} className="w-full h-12 bg-indigo-600 hover:bg-indigo-700 text-lg">
            {loading ? "Menganalisis..." : "Run MOF Analysis"}
          </Button>
        </form>
      </div>
    </div>
  );
}

// Tampilan Hasil (Summary Dashboard)
function ResultsView({ data, onBack }: any) {
  return (
    <div className="min-h-screen bg-zinc-50 p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <Button variant="outline" onClick={onBack}>← Kembali</Button>
        <h2 className="text-2xl font-bold">Hasil Analisis</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="p-4">
            <p className="text-xs font-bold text-zinc-400 uppercase">Kapasitas H2</p>
            <p className="text-2xl font-bold">{data.gravimetric_h2} wt%</p>
            <p className="text-sm text-zinc-500">{data.volumetric_h2} g/L</p>
          </Card>
          <Card className="p-4">
            <p className="text-xs font-bold text-zinc-400 uppercase">Harga MOF</p>
            <p className="text-2xl font-bold">${data.mof_cost_usd_kg}/kg</p>
          </Card>
          <Card className="p-4">
            <p className="text-xs font-bold text-zinc-400 uppercase">Stabilitas</p>
            <p className="text-2xl font-bold">{data.stability_status}</p>
          </Card>
        </div>

        <Card className={`p-6 border-2 ${data.is_feasible ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}`}>
          <div className="flex items-center gap-3">
            {data.is_feasible ? <CheckCircle2 className="text-green-600" /> : <AlertCircle className="text-red-600" />}
            <div>
              <p className="font-bold text-lg">{data.is_feasible ? "Feasible" : "Not Feasible"}</p>
              <p className="text-sm opacity-80">Berdasarkan analisis ekonomi dan target DOE.</p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}