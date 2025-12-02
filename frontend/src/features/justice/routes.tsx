// routes.tsx
// Admin routing for Aurora Justice features

import React from "react";
import { Routes, Route } from "react-router-dom";
import { AuroraCasePage } from "./AuroraCasePage";

/**
 * Aurora Justice routes for admin panel
 * 
 * Usage in main router:
 * 
 * ```tsx
 * import { AuroraJusticeRoutes } from "@/features/justice/routes";
 * 
 * <Routes>
 *   <Route path="/admin/aurora/*" element={<AuroraJusticeRoutes />} />
 * </Routes>
 * ```
 */
export const AuroraJusticeRoutes: React.FC = () => {
  return (
    <Routes>
      <Route path="case/:userId" element={<AuroraCasePage />} />
      {/* Future routes:
      <Route path="appeal" element={<AppealPage />} />
      <Route path="violations" element={<ViolationsListPage />} />
      */}
    </Routes>
  );
};

