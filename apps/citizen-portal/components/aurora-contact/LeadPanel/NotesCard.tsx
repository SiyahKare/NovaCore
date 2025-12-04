"use client";

import { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { useAuroraAPI } from "@aurora/hooks";

interface Props {
  leadId: string;
}

export function NotesCard({ leadId }: Props) {
  const { fetchAPI } = useAuroraAPI();
  const [notes, setNotes] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async () => {
    if (!notes.trim() || isSaving) return;
    
    setIsSaving(true);
    
    try {
      const { data, error } = await fetchAPI(
        `/admin/telegram/leads/${leadId}/notes?notes=${encodeURIComponent(notes)}`,
        {
          method: "POST",
        }
      );
      
      if (error) {
        alert(`Hata: ${error.detail || 'Notlar kaydedilemedi'}`);
      } else {
        alert("Notlar kaydedildi!");
        setNotes("");
      }
    } catch (err) {
      alert(`Hata: ${err instanceof Error ? err.message : 'Bilinmeyen hata'}`);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Card className="border-slate-800 bg-slate-950">
      <CardHeader className="py-2">
        <CardTitle className="text-xs text-slate-100">Nurella Notları</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 py-2">
        <Textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Internal notes..."
          className="min-h-[80px] bg-slate-900 text-[11px] text-slate-100 placeholder:text-slate-500"
        />
        <Button 
          size="sm" 
          onClick={handleSave} 
          disabled={isSaving}
          className="h-7 w-full text-[10px] disabled:opacity-50"
        >
          {isSaving ? "Kaydediliyor..." : "Kaydet"}
        </Button>
      </CardContent>
    </Card>
  );
}

