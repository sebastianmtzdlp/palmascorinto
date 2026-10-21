// Contenido editable de la página. Todo lo que dice "ejemplo" es de relleno: reemplázalo.
// El repositorio es público: no pongas dirección exacta, contratos, costos reales ni datos personales.
window.PROJECT = {
  // true muestra una franja "Vista de ejemplo". Cámbialo a false cuando el contenido sea real.
  sample: true,

  name: 'Palmascorinto',
  description: 'Seguimiento de la obra: evidencias fotográficas, reportes semanales y avance por área.',
  startDate: '2026-11-01',
  targetDate: '2027-01-31',

  hero: {
    badge: 'Preventa · Cupo limitado',
    title: 'Un departamento pensado para vivirse',
    subtitle: 'Espacios luminosos, acabados cuidados y una obra que puedes seguir paso a paso.',
    image: 'assets/ejemplo/sala.jpg',
    imageAlt: 'Sala luminosa con piso de duela y ventanales',
    cta: 'Quiero información',
    stats: [
      { value: '52–88 m²', label: 'Superficies' },
      { value: '1–2', label: 'Recámaras' },
      { value: 'Ene 2027', label: 'Entrega estimada' },
    ],
  },

  highlights: [
    { icon: '☀️', title: 'Luz natural', text: 'Ventanales amplios y distribución abierta que aprovechan la luz durante todo el día.' },
    { icon: '🛠️', title: 'Acabados de calidad', text: 'Materiales seleccionados en cocina, baños y pisos, con supervisión en cada etapa.' },
    { icon: '📍', title: 'Buena ubicación', text: 'Zona con servicios, transporte y comercio cerca. (Texto de ejemplo.)' },
  ],

  // status: 'disponible' | 'apartado' | 'vendido'
  units: [
    { name: 'Tipo A', rooms: '1 recámara', baths: '1 baño', area: '52 m²', price: 'Desde $2,450,000', status: 'disponible' },
    { name: 'Tipo B', rooms: '2 recámaras', baths: '2 baños', area: '74 m²', price: 'Desde $3,280,000', status: 'disponible' },
    { name: 'Tipo C', rooms: '2 recámaras + estudio', baths: '2 baños', area: '88 m²', price: 'Desde $3,950,000', status: 'apartado' },
  ],
  priceNote: 'Precios en MXN, de ejemplo. Sujetos a cambio sin previo aviso.',

  gallery: [
    { src: 'assets/ejemplo/sala.jpg', alt: 'Sala con duela y ventanales', caption: 'Sala' },
    { src: 'assets/ejemplo/cocina.jpg', alt: 'Cocina blanca con barra', caption: 'Cocina' },
    { src: 'assets/ejemplo/recamara.jpg', alt: 'Recámara principal', caption: 'Recámara principal' },
    { src: 'assets/ejemplo/edificio.jpg', alt: 'Fachada del edificio', caption: 'Fachada' },
    { src: 'assets/ejemplo/estancia.jpg', alt: 'Estancia con vista', caption: 'Estancia' },
    { src: 'assets/ejemplo/cocina-isla.jpg', alt: 'Cocina con isla', caption: 'Cocina con isla' },
  ],

  payment: [
    { step: '1', title: 'Apartado', text: 'Reserva tu unidad con un pago inicial.', value: '5%' },
    { step: '2', title: 'Enganche', text: 'Se completa durante la obra en mensualidades.', value: '25%' },
    { step: '3', title: 'Entrega', text: 'Liquidación al recibir tu departamento.', value: '70%' },
  ],

  // Contacto: llena al menos uno. whatsapp en formato internacional sin signos, ej. '5215512345678'
  contact: {
    whatsapp: '',
    email: '',
    message: 'Hola, me interesa Palmascorinto. ¿Me pueden dar información?',
  },

  // Áreas que se siguen en la obra. El avance sale del último reporte de cada una.
  areas: ['Cocina', 'Baño', 'Sala', 'Recámara', 'Instalación eléctrica', 'Plomería', 'Pisos', 'Acabados'],

  // status: 'pendiente' | 'en curso' | 'terminada'
  phases: [
    { name: 'Diagnóstico y presupuesto', status: 'pendiente' },
    { name: 'Demolición y retiro', status: 'pendiente' },
    { name: 'Instalaciones (eléctrica y plomería)', status: 'pendiente' },
    { name: 'Albañilería y pisos', status: 'pendiente' },
    { name: 'Acabados y pintura', status: 'pendiente' },
    { name: 'Limpieza y entrega', status: 'pendiente' },
  ],
};
