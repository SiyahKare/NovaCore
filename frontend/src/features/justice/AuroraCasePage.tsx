// AuroraCasePage.tsx
// Page component for Aurora Case File view

import React from "react";
import { useParams } from "react-router-dom";
import { AuroraCaseView } from "./AuroraCaseView";

export const AuroraCasePage: React.FC = () => {
  const { userId } = useParams<{ userId: string }>();

  if (!userId) {
    return (
      <div className="p-6 text-sm text-slate-400">UserId eksik.</div>
    );
  }

  // Demo token - gerçek uygulamada auth store'dan gelecek
  const token = "demo-token";

  return (
    <div className="max-w-6xl mx-auto">
      <AuroraCaseView userId={userId} token={token} />
    </div>
  );
};

