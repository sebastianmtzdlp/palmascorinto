-- Palmascorinto: esquema de base de datos y almacenamiento
-- Ejecutar completo en Supabase > SQL Editor.
-- ANTES de ejecutar: cambia los correos de abajo por los reales (tuyo y de Miguel).

-- 1) Lista de personas autorizadas (solo ellos pueden ver o modificar nada)
create table if not exists public.allowed_users (
  email text primary key
);

alter table public.allowed_users enable row level security;
-- Sin políticas: nadie puede leer esta tabla desde el sitio, solo desde el panel de Supabase.

insert into public.allowed_users (email) values
  ('tu-correo@ejemplo.com'),
  ('miguel-correo@ejemplo.com')
on conflict do nothing;

-- Función que indica si el usuario que hace la petición está autorizado
create or replace function public.is_allowed()
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1 from public.allowed_users
    where lower(email) = lower(auth.jwt() ->> 'email')
  );
$$;

-- 2) Entradas: evidencias (fotos, videos, documentos) y reportes de avance
create table if not exists public.entries (
  id           uuid primary key default gen_random_uuid(),
  kind         text not null check (kind in ('evidencia', 'reporte')),
  area         text not null,                 -- cocina, baño, sala, instalaciones, etc.
  title        text not null,
  description  text,
  progress_pct int check (progress_pct between 0 and 100),  -- solo para reportes
  pendientes   text,
  taken_on     date not null default current_date,
  created_by   uuid references auth.users(id) default auth.uid(),
  created_at   timestamptz not null default now()
);

-- 3) Archivos adjuntos a cada entrada
create table if not exists public.files (
  id           uuid primary key default gen_random_uuid(),
  entry_id     uuid not null references public.entries(id) on delete cascade,
  storage_path text not null,
  file_name    text not null,
  mime_type    text,
  created_at   timestamptz not null default now()
);

alter table public.entries enable row level security;
alter table public.files   enable row level security;

create policy "entries: leer" on public.entries
  for select to authenticated using (public.is_allowed());

create policy "entries: crear" on public.entries
  for insert to authenticated with check (public.is_allowed());

create policy "entries: editar propias" on public.entries
  for update to authenticated using (created_by = auth.uid()) with check (created_by = auth.uid());

create policy "entries: borrar propias" on public.entries
  for delete to authenticated using (created_by = auth.uid());

create policy "files: leer" on public.files
  for select to authenticated using (public.is_allowed());

create policy "files: crear" on public.files
  for insert to authenticated with check (public.is_allowed());

create policy "files: borrar" on public.files
  for delete to authenticated using (public.is_allowed());

-- 4) Almacenamiento privado para los archivos
insert into storage.buckets (id, name, public)
values ('evidencias', 'evidencias', false)
on conflict (id) do nothing;

create policy "storage: leer" on storage.objects
  for select to authenticated
  using (bucket_id = 'evidencias' and public.is_allowed());

create policy "storage: subir" on storage.objects
  for insert to authenticated
  with check (bucket_id = 'evidencias' and public.is_allowed());

create policy "storage: borrar" on storage.objects
  for delete to authenticated
  using (bucket_id = 'evidencias' and public.is_allowed());
