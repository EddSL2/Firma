# Firma de Correo Corporativa – Nubosoft
**Eduardo Salgado Licea** | Sales Engineer & Multi-Cloud Architect

Firma de correo profesional optimizada para Gmail y Outlook, desarrollada con tablas HTML anidadas, estilos estrictamente inline y assets en alta resolución con compatibilidad para pantallas Retina.

---

## 🚀 Previsualización y Copiado Directo
Puedes abrir la firma directamente en tu navegador abriendo el archivo `index.html` o a través de **GitHub Pages**:
- **Vista previa interactiva:** `https://eddsl2.github.io/Firma/`

---

## 🖼️ URLs Públicas para la Firma en Gmail
Gmail y los clientes de correo requieren que las imágenes y los GIFs estén alojados en URLs públicas HTTPS con CORS abierto.

Los enlaces públicos directos (vía CDN de jsDelivr con caché optimizada para email) son:

* **Logotipo Oficial Nubosoft (HD Transparente):**
  ```text
  https://cdn.jsdelivr.net/gh/EddSL2/Firma@main/badge/nubosoft_hd.png
  ```
* **Badge Animado de Partners Multicloud (Google Cloud MSP & AWS):**
  ```text
  https://cdn.jsdelivr.net/gh/EddSL2/Firma@main/badge/partners-badge-compact.gif
  ```

---

## 🛠️ Modificar y Regenerar Animaciones
Para cambiar cualquier imagen o actualizar los badges:
1. Reemplaza las imágenes en `badge/assets/` (`nubosoft.png`, `gcp-partner.png`, `aws-partner.png`).
2. Ejecuta:
   ```bash
   cd badge
   python generar_badge.py
   ```
3. Haz `git commit` y `git push` para actualizar los assets automáticamente.
