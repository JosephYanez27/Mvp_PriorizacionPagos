/**
 * conciliacion.js
 * ──────────────────────────────────────────────────────────
 * Módulo 3: Layout de Pagos y Conciliación Bancaria.
 * Depende de: globals.js (formatCurrency, showToast)
 * ──────────────────────────────────────────────────────────
 */

// ── Estado ────────────────────────────────────────────────
let facturasConc    = [];
let currentConcList = [];

// ── DOM refs ──────────────────────────────────────────────
const tableBodyConc = document.getElementById('tableBodyConc');
const emptyState    = document.getElementById('emptyState');


// ══════════════════════════════════════════════════════════
//  CARGA Y RENDER
// ══════════════════════════════════════════════════════════

const cargarDatosConc = async () => {
    tableBodyConc.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:32px;color:var(--text-muted);font-weight:500;">Extrayendo lote de remesas confirmadas...</td></tr>`;
    try {
        const response = await fetch('/api/confirmados/');
        if (!response.ok) throw new Error('Respuesta inválida.');
        facturasConc    = await response.json();
        currentConcList = [...facturasConc];
        renderTableConc();
    } catch (error) {
        console.error('Error al cargar confirmados:', error);
        tableBodyConc.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:32px;color:var(--danger);font-weight:600;">✕ No se pudieron extraer las facturas confirmadas.</td></tr>`;
    }
};

const renderTableConc = () => {
    tableBodyConc.innerHTML = '';

    if (currentConcList.length === 0) {
        emptyState.style.display = 'block';
        actualizarKPIsConc(0, 0);
        return;
    }
    emptyState.style.display = 'none';

    let totalConfirmado = 0;

    currentConcList.forEach((f) => {
        totalConfirmado += f.total_abonado;

        const estadoBadge = f.estado === 'PAGADO'
            ? `<span class="badge badge-ok">PAGADO</span>`
            : `<span class="badge badge-rev">CONFIRMADO</span>`;

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td style="font-weight:600;font-family:var(--font-mono);">${f.folio}</td>
            <td>${f.proveedor}</td>
            <td style="text-align:right;font-family:var(--font-mono);">${formatCurrency(f.monto_mxn)}</td>
            <td style="text-align:right;font-family:var(--font-mono);font-weight:600;color:var(--accent-dark);">${formatCurrency(f.total_abonado)}</td>
            <td style="text-align:center;font-family:var(--font-mono);">${f.moneda}</td>
            <td style="text-align:center;">${f.dias_vencidos} días</td>
            <td style="text-align:center;">${estadoBadge}</td>`;
        tableBodyConc.appendChild(tr);
    });

    actualizarKPIsConc(totalConfirmado, currentConcList.length);
};

const actualizarKPIsConc = (total, count) => {
    document.getElementById('kpi-conc-total').textContent = formatCurrency(total);
    document.getElementById('kpi-conc-count').textContent = `${count} facturas en remesa`;
};


// ══════════════════════════════════════════════════════════
//  EXPORTAR REMESA
// ══════════════════════════════════════════════════════════

const descargarRemesaExcel = async () => {
    try {
        showToast('Generando reporte de pagos bancarios...');
        const response = await fetch('/api/exportar-remesa/', { method: 'GET' });

        if (!response.ok) {
            const text = await response.text();
            try {
                const jsonErr = JSON.parse(text);
                showToast(`Error de exportación: ${jsonErr.error}`, false);
            } catch {
                showToast('No hay facturas confirmadas para exportar hoy.', false);
            }
            return;
        }

        const blob    = await response.blob();
        const url     = window.URL.createObjectURL(blob);
        const a       = document.createElement('a');
        a.style.display = 'none';
        a.href          = url;
        const dateStr   = new Date().toISOString().slice(0, 10).replace(/-/g, '');
        a.download      = `remesa_${dateStr}.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        showToast('Layout de Pagos descargado correctamente.');
    } catch (err) {
        console.error('Error al exportar remesa:', err);
        showToast('Fallo de red al solicitar el reporte de remesas.', false);
    }
};


// ══════════════════════════════════════════════════════════
//  CONCILIACIÓN BANCARIA (subir retorno)
// ══════════════════════════════════════════════════════════

const ejecutarConciliacion = async (fileInput) => {
    if (fileInput.files.length === 0) return;

    const file    = fileInput.files[0];
    const textEl  = document.getElementById('dropzone-compact-text');
    const origTxt = textEl.textContent;
    textEl.innerHTML = `<span style="color:var(--accent-dark);">🔄 Conciliando lote...</span>`;

    const formData = new FormData();
    formData.append('archivo', file);

    try {
        const response = await fetch('/api/conciliar/', { method: 'POST', body: formData });
        const res      = await response.json();

        if (res.ok) {
            showToast(res.message);

            document.getElementById('rec-stat-matched').textContent  = res.matched.length;
            document.getElementById('rec-stat-notfound').textContent = res.not_found.length;
            document.getElementById('rec-stat-already').textContent  = res.already_paid.length;
            document.getElementById('rec-stat-wrong').textContent    = res.wrong_state.length;
            document.getElementById('rec-list-matched').textContent  = res.matched.length  > 0 ? res.matched.join(', ')    : 'Ninguno';
            document.getElementById('rec-list-notfound').textContent = res.not_found.length > 0 ? res.not_found.join(', ') : 'Ninguno';

            abrirModalConciliacion();
            cargarDatosConc();
        } else {
            showToast(`Error al conciliar: ${res.error}`, false);
        }
    } catch (err) {
        console.error('Error al conciliar:', err);
        showToast('No se pudo conectar con el servicio de conciliación.', false);
    } finally {
        fileInput.value  = '';
        textEl.textContent = origTxt;
    }
};

const abrirModalConciliacion = () => {
    document.getElementById('conciliacion-modal-overlay').classList.add('open');
    document.getElementById('conciliacion-modal').classList.add('open');
};

const cerrarModalConciliacion = () => {
    document.getElementById('conciliacion-modal-overlay').classList.remove('open');
    document.getElementById('conciliacion-modal').classList.remove('open');
};


// ── Init ──────────────────────────────────────────────────
cargarDatosConc();
