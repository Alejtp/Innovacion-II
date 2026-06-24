# 📊 Dashboard — Merma Textil
**Proyecto:** Gestión de Residuos en Empresas Textiles  
**Sprint:** 2 — Feature 1: Diseño de Dashboard  
**Equipo:** Renato Muñoz · Alejandro Tapia · Sebastian Larraguibel · Javier Sanchez · Jorge García

---

## 🗂️ Estructura del proyecto

```
merma-textil-dashboard/
├── index.html          ← Dashboard principal (abrir aquí)
├── README.md           ← Este archivo
└── .vscode/
    ├── settings.json   ← Configuración de VS Code
    └── extensions.json ← Extensiones recomendadas
```

---

## 🚀 Cómo abrir el dashboard

### Opción 1 — Directo en el navegador (más rápido)
1. Abre la carpeta en el Explorador de archivos
2. Doble clic en `index.html`
3. Se abre en Chrome / Edge / Firefox automáticamente ✅

### Opción 2 — Con VS Code + Live Server (recomendado para editar)
1. Abre VS Code
2. `Archivo → Abrir Carpeta` → selecciona `merma-textil-dashboard/`
3. VS Code te sugerirá instalar las extensiones recomendadas → acepta
4. Abre `index.html`
5. Botón **"Go Live"** en la barra inferior derecha de VS Code
6. Se abre en `http://127.0.0.1:5500` y se refresca automáticamente al guardar ✅

---

## ✏️ Cómo reemplazar los datos ficticios por datos reales

Busca en `index.html` las secciones marcadas con comentarios `<!-- DATOS -->`.  
Los valores a reemplazar están en la tabla de hallazgos y en los KPIs del top.

Para regenerar los gráficos con datos reales, ejecutar el script Python:
```bash
python3 generar_graficos.py
```
*(El script se agregará en el Sprint 3 cuando se integren datos reales)*

---

## 📋 Contenido del dashboard

| Sección | Descripción |
|---|---|
| **KPIs** | Merma promedio, pérdida económica, empresas, etapas críticas |
| **Gráfico 1** | Merma por etapa productiva (barras horizontales) |
| **Gráfico 2** | Clasificación de tipos de merma (donut) |
| **Gráfico 3** | Evolución mensual por empresa (líneas) |
| **Gráfico 4** | Impacto económico apilado por empresa (barras) |
| **Tabla** | Hallazgos clave Sprint 1 por empresa |
| **Tarjetas** | Problemas frecuentes · Hallazgos positivos · Próximos pasos |

---

## 🗓️ Sprints

- ✅ **Sprint 1** — Recopilación de información
  - Investigación de empresas (Muñoz / Tapia)
  - Levantamiento del proceso actual (Larraguibel / Sanchez)
  - Organización de hallazgos (García / Sanchez)
- 🔁 **Sprint 2** — Diseño y análisis *(en curso)*
  - Feature 1: Dashboard ← **estás aquí**
  - Feature 2: Integración datos reales
  - Feature 3: Análisis comparativo

---

> ⚠️ *Los datos numéricos del dashboard son ficticios y deben reemplazarse con información real en Sprint 3.*
