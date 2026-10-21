// Datos del proyecto de remodelación. Edita este archivo para ajustar áreas, fases y fechas.
// Aquí NO pongas datos privados (dirección exacta, costos, contratos): el repositorio es público.
// status de cada fase: 'pendiente' | 'en curso' | 'terminada'
window.PROJECT = {
  name: 'Remodelación del departamento',
  description:
    'Seguimiento de la obra: evidencias fotográficas, reportes semanales y avance por área.',
  startDate: '2026-11-01',   // ajusta
  targetDate: '2027-01-31',  // ajusta

  // Áreas a seguir. El avance de cada una sale del último reporte que se suba.
  areas: [
    'Cocina',
    'Baño',
    'Sala',
    'Recámara',
    'Instalación eléctrica',
    'Plomería',
    'Pisos',
    'Acabados',
  ],

  phases: [
    { name: 'Diagnóstico y presupuesto', status: 'pendiente' },
    { name: 'Demolición y retiro', status: 'pendiente' },
    { name: 'Instalaciones (eléctrica y plomería)', status: 'pendiente' },
    { name: 'Albañilería y pisos', status: 'pendiente' },
    { name: 'Acabados y pintura', status: 'pendiente' },
    { name: 'Limpieza y entrega', status: 'pendiente' },
  ],
};
