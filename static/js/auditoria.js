/**
 * auditoria.js
 * ──────────────────────────────────────────────────────────
 * Módulo 4: Historial de Auditoría Proveedor.
 * Depende de: globals.js (formatCurrency, showToast)
 * ──────────────────────────────────────────────────────────
 */

// ── DOM refs ──────────────────────────────────────────────
const tableBodyAuditoria = document.getElementById('tableBodyAuditoria');
const emptyState         = document.getElementById('emptyState');


// ══════════════════════════════════════════════════════════
//  CARGA Y RENDER
// ══════════════════════════════════════════════════════════

const cargarAuditoria = async (filtroProveedor = null) => {
    tableBodyAuditoria.innerHTML = `
        <tr>
            <td colspan="7" style="text-align:center;padding:20px;color:var(--text-muted);">
                Cargando auditoría...
            </td>
        </tr>`;

    try {
        const url      = filtroProveedor
            ? `/api/auditoria/?proveedor=${encodeURIComponent(filtroProveedor)}`
            : '/api/auditoria/';
        const response = await fetch(url);

        if (!response.ok) throw new Error('Error backend');

        const data = await response.json();

        if (data.length === 0) {
            tableBodyAuditoria.innerHTML = '';
            emptyState.style.display = 'block';
            actualizarKPIsAud(0, 0, 0);
            return;
        }
        emptyState.style.display = 'none';

        let autorizados = 0;
        let riesgos     = 0;

        tableBodyAuditoria.innerHTML = '';

        data.forEach(a => {
            if (a.accion === 'AUTORIZADO')        autorizados++;
            if (a.accion.includes('RIESGO'))       riesgos++;

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${a.fecha}</td>
                <td>${a.proveedor}</td>
                <td style="font-family:var(--font-mono);font-weight:600;">${a.folio}</td>
                <td>${a.usuario}</td>
                <td>
                    <span class="badge ${getBadgeClass(a.accion)}">${a.accion}</span>
                </td>
                <td style="text-align:right;font-family:var(--font-mono);">${formatCurrency(a.abono)}</td>
                <td style="color:var(--text-muted);">${a.notas || '—'}</td>`;
            tableBodyAuditoria.appendChild(tr);
        });

        actualizarKPIsAud(data.length, autorizados, riesgos);

    } catch (err) {
        console.error(err);
        tableBodyAuditoria.innerHTML = `
            <tr>
                <td colspan="7" style="text-align:center;color:var(--danger);padding:20px;font-weight:600;">
                    ✕ Error cargando auditoría
                </td>
            </tr>`;
    }
};

const actualizarKPIsAud = (total, ok, risk) => {
    document.getElementById('kpi-aud-total').textContent = total;
    document.getElementById('kpi-aud-ok').textContent    = ok;
    document.getElementById('kpi-aud-risk').textContent  = risk;
};

// Mapea acción a clase de badge visual
const getBadgeClass = (accion) => {
    if (accion === 'AUTORIZADO')           return 'badge-ok';
    if (accion.includes('RIESGO'))         return 'badge-error';
    if (accion === 'REVERTIDO')            return 'badge-warn';
    if (accion === 'CONFIRMADO')           return 'badge-rev';
    return 'badge-adm';
};


// ── Init: soporta ?proveedor= en la URL ──────────────────
const params           = new URLSearchParams(window.location.search);
const filtroProveedor  = params.get('proveedor') || null;
cargarAuditoria(filtroProveedor);
