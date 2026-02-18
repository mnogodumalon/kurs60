import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from '@/components/Layout';
import DashboardOverview from '@/pages/DashboardOverview';
import DozentenPage from '@/pages/DozentenPage';
import TeilnehmerPage from '@/pages/TeilnehmerPage';
import RaeumePage from '@/pages/RaeumePage';
import KursePage from '@/pages/KursePage';
import AnmeldungenPage from '@/pages/AnmeldungenPage';

export default function App() {
  return (
    <BrowserRouter basename={import.meta.env.BASE_URL}>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<DashboardOverview />} />
          <Route path="dozenten" element={<DozentenPage />} />
          <Route path="teilnehmer" element={<TeilnehmerPage />} />
          <Route path="raeume" element={<RaeumePage />} />
          <Route path="kurse" element={<KursePage />} />
          <Route path="anmeldungen" element={<AnmeldungenPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}