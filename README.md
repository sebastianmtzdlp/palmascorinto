# Palmascorinto · Evidencias y avance de obra

Sitio estático (GitHub Pages) + Supabase (base de datos, autenticación y almacenamiento de archivos).
Solo las personas en la tabla `allowed_users` pueden entrar y ver o subir información.

## Estructura

```
index.html        Página principal
app.js            Lógica: login, subir evidencias/reportes, listar, resumen por área
styles.css        Estilos
config.js         URL y clave pública de Supabase (editar)
supabase/schema.sql  Tablas, políticas de seguridad y bucket de archivos
CNAME             Dominio personalizado para GitHub Pages
```

## 1. Crear el proyecto en Supabase

1. Entra a https://supabase.com, crea un proyecto (elige la región más cercana).
2. En **Project Settings > API** copia:
   - **Project URL**
   - **anon public key**
3. Pégalos en `config.js`.
4. En **SQL Editor** pega todo el contenido de `supabase/schema.sql`.
   Antes de ejecutarlo, cambia los dos correos de `allowed_users` por los reales (el tuyo y el de Miguel).
5. En **Authentication > Sign In / Providers > Email**, desactiva **Allow new users to sign up**
   para que nadie más pueda registrarse.
6. Crea las cuentas de ustedes en **Authentication > Users > Add user**, con correo y contraseña.
   Marca **Auto Confirm User** para que no tengan que confirmar por correo.

> Nota: en el plan gratuito, Supabase pausa el proyecto tras una semana sin actividad.
> Si pasa, se reactiva desde el panel con un clic.

## 2. Probar en local

Abre `index.html` con cualquier servidor estático, por ejemplo:

```bash
cd palmascorinto
python3 -m http.server 8000
```

Luego entra a http://localhost:8000 y prueba con una cuenta creada en el paso 6.

## 3. Publicar en GitHub Pages

1. Crea un repositorio público llamado `palmascorinto` (o el nombre que prefieras) y sube estos archivos a la rama `main`.
   - Como el repositorio es público, el código queda visible. Los datos no: están protegidos por las políticas de Supabase.
2. En el repositorio: **Settings > Pages**.
   - Source: **Deploy from a branch**
   - Branch: **main** / **(root)**
   - En **Custom domain** escribe `palmascorinto.xyz` y guarda. El archivo `CNAME` ya lo incluye.

## 4. Configurar el dominio (DNS)

En el panel donde compraste `palmascorinto.xyz`, crea estos registros:

| Tipo  | Nombre | Valor                       |
|-------|--------|-----------------------------|
| A     | @      | 185.199.108.153             |
| A     | @      | 185.199.109.153             |
| A     | @      | 185.199.110.153             |
| A     | @      | 185.199.111.153             |
| CNAME | www    | TU-USUARIO.github.io        |

La propagación puede tardar desde unos minutos hasta algunas horas.
Cuando GitHub active el certificado, marca **Enforce HTTPS** en Settings > Pages.

## Uso diario

- **Miguel** entra, elige *Evidencia* o *Reporte de avance*, pone área, título, archivos y guarda.
- Los **reportes** llevan un % de avance por área. El resumen de arriba toma el último reporte de cada área.
- Las fotos y documentos se guardan en Supabase Storage (bucket privado). Los enlaces son temporales (1 hora).
- Cada persona solo puede borrar lo que ella misma subió.

## Pendientes sugeridos para después

- Exportar los reportes a PDF.
- Aviso por correo cuando se suba un reporte nuevo (Supabase Edge Function).
- Compresión de fotos antes de subirlas, para ahorrar espacio.
