import { Navigate, Route, Routes } from "react-router-dom";
import { LoginPage } from "./features/auth/pages/LoginPage";
import { DocumentListPage } from "./features/documents/pages/DocumentListPage";
import { DocumentEditorPage } from "./features/documents/pages/DocumentEditorPage";
import { ProtectedRoute } from "./shared/components/ProtectedRoute";
import { AppLayout } from "./shared/components/AppLayout";

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      <Route
        path="/documents"
        element={
          <ProtectedRoute>
            <AppLayout>
              <DocumentListPage />
            </AppLayout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/documents/:id"
        element={
          <ProtectedRoute>
            <AppLayout>
              <DocumentEditorPage />
            </AppLayout>
          </ProtectedRoute>
        }
      />

      <Route path="/" element={<Navigate to="/documents" replace />} />
      <Route path="*" element={<Navigate to="/documents" replace />} />
    </Routes>
  );
}

export default App;
