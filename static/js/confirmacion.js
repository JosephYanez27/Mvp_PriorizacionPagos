/**
 * confirmacion.js
 * ──────────────────────────────────────────────────────────
 * Módulo 2: Bandeja de Confirmación de Pagos.
 * Depende de: globals.js (formatCurrency, showToast)
 * ──────────────────────────────────────────────────────────
 */

// ── Estado ────────────────────────────────────────────────
let facturasConf    = [];
let currentConfList = [];

// ── DOM refs ──────────────────────────────────────────────
const tableBodyConf = document.getElementById('tableBodyConf');
const searchInput   = document.getElementById('searchInputConf');
const emptyState    = document.getElementById('emptyState');


// ══════════════════════════════════════════════════════════
//  CARGA Y FILTRADO
// ══════════════════════════════════════════════════════════

const cargarDatosConf = async () => {
    tableBodyConf.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:32px;color:var(--text-muted);font-weight:500;">Cargando lote de pre-autorizaciones...</td></tr>`;
    try {
        const response = await fetch('/api/aprobados/');
        if (!response.ok) throw new Error('Respuesta inválida.');
        facturasConf = await response.json();
        filtrarDatosConf();
    } catch (error) {
        console.error('Error al cargar aprobados:', error);
        tableBodyConf.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:32px;color:var(--danger);font-weight:600;">✕ No se pudieron extraer las facturas aprobadas.</td></tr>`;
    }
};

const filtrarDatosConf = () => {
    const search = searchInput.value.toLowerCase().trim();
    currentConfList = facturasConf.filter(f =>
        f.proveedor.toLowerCase().includes(search) || f.folio.toLowerCase().includes(search)
    );
    renderTableConf();
};

const renderTableConf = () => {
    tableBodyConf.innerHTML = '';

    if (currentConfList.length === 0) {
        emptyState.style.display = 'block';
        actualizarKPIsConf(0, 0);
        return;
    }
    emptyState.style.display = 'none';

    let totalAbonado = 0;

    currentConfList.forEach((f) => {
        totalAbonado += f.total_abonado;

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td style="font-weight:600;font-family:var(--font-mono);">${f.folio}</td>
            <td>${f.proveedor}</td>
            <td style="text-align:right;font-family:var(--font-mono);">${formatCurrency(f.monto_mxn)}</td>
            <td style="text-align:right;font-family:var(--font-mono);color:var(--text-muted);">${formatCurrency(f.saldo_neto)}</td>
            <td style="text-align:right;font-family:var(--font-mono);font-weight:600;color:var(--success);">${formatCurrency(f.total_abonado)}</td>
            <td style="text-align:center;">${f.dias_vencidos} días</td>
            <td style="text-align:center;">
                <div style="display:flex;gap:8px;justify-content:center;">
                    <button class="nav-btn primary" onclick="confirmarFactura(${f.id}, '${f.folio}')" style="padding:5px 12px;font-size:11px;">
                        <i data-lucide="check" style="width:12px;height:12px;"></i> Confirmar
                    </button>
                    <button class="nav-btn danger-outline" onclick="revertirFactura(${f.id}, '${f.folio}')" style="padding:5px 12px;font-size:11px;">
                        <i data-lucide="undo" style="width:12px;height:12px;"></i> Deshacer
                    </button>
                </div>
            </td>`;
        tableBodyConf.appendChild(tr);
    });

    actualizarKPIsConf(totalAbonado, currentConfList.length);
    lucide.createIcons();
};

const actualizarKPIsConf = (total, count) => {
    document.getElementById('kpi-conf-total').textContent         = formatCurrency(total);
    document.getElementById('kpi-conf-count').textContent         = `${count} facturas pre-aprobadas`;
    document.getElementById('kpi-conf-pending-count').textContent = count;
};


// ══════════════════════════════════════════════════════════
//  ACCIONES
// ══════════════════════════════════════════════════════════

const confirmarFactura = async (id, folio) => {
    try {
        const response = await fetch(`/api/facturas/${id}/confirmar/`, { method: 'POST' });
        const res = await response.json();
        if (res.ok) {
            showToast(`Factura ${folio} confirmada con éxito para remesa.`);
            cargarDatosConf();
        } else {
            showToast(`Error al confirmar: ${res.error}`, false);
        }
    } catch (err) {
        console.error('Error al confirmar:', err);
        showToast('Error de conexión.', false);
    }
};

const revertirFactura = async (id, folio) => {
    try {
        const response = await fetch(`/api/facturas/${id}/revertir/`, { method: 'POST' });
        const res = await response.json();
        if (res.ok) {
            showToast(`Factura ${folio} devuelta al flujo de priorización.`);
            cargarDatosConf();
        } else {
            showToast(`Error al revertir: ${res.error}`, false);
        }
    } catch (err) {
        console.error('Error al revertir:', err);
        showToast('Error de conexión.', false);
    }
};


// ── Filtros ───────────────────────────────────────────────
searchInput.addEventListener('input', filtrarDatosConf);


// ── Init ──────────────────────────────────────────────────
cargarDatosConf();
