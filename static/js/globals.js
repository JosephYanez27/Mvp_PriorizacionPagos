/**
 * globals.js
 * ──────────────────────────────────────────────────────────
 * Utilidades y lógica compartida entre todos los módulos de
 * Tesorería Inteligente.  No contiene lógica de módulo específico.
 * ──────────────────────────────────────────────────────────
 */

// ── Formato moneda ────────────────────────────────────────
const formatCurrency = (amount) =>
    new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(amount);


// ── Toast ────────────────────────────────────────────────
const showToast = (message, isSuccess = true) => {
    const toast = document.getElementById('toast');
    toast.className = isSuccess ? 'ok' : 'fail';
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3500);
};


// ── Estrellas HTML ────────────────────────────────────────
const buildStarsHtml = (starsCount) => {
    let html = '<div class="star-container">';
    for (let i = 1; i <= 5; i++) {
        html += i <= starsCount
            ? `<svg class="star-svg" viewBox="0 0 24 24" fill="#f59e0b" stroke="#f59e0b" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>`
            : `<svg class="star-svg" viewBox="0 0 24 24" fill="none" stroke="#e5e7eb" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>`;
    }
    html += '</div>';
    return html;
};


// ── Celda de scoring con barra ────────────────────────────
const buildScoreCell = (score) => {
    let metricClass = 'high';
    if      (score >= 75) metricClass = 'low';
    else if (score >= 50) metricClass = 'mid';

    const color = score >= 75 ? 'var(--danger)' : score >= 50 ? 'var(--warning)' : 'var(--accent)';
    return `
        <div style="display:flex;align-items:center;gap:8px;">
            <span class="score-cell ${metricClass}">${score}%</span>
            <div style="flex:1;background:var(--border);height:6px;border-radius:3px;overflow:hidden;min-width:60px;">
                <div style="width:${score}%;height:100%;background:${color};border-radius:3px;"></div>
            </div>
        </div>`;
};


// ══════════════════════════════════════════════════════════
//  MODAL AUDITAR PROVEEDOR (batch)
//  Usado desde: priorizacion.js (y cualquier otro módulo que lo necesite)
// ══════════════════════════════════════════════════════════
let modalFacturas = [];

const abrirAuditarModal = async (proveedorId, proveedorNombre, estrellas) => {
    document.getElementById('auditar-modal-title').textContent = `Auditar Proveedor: ${proveedorNombre}`;
    document.getElementById('auditar-modal-stars').innerHTML = buildStarsHtml(estrellas);

    const tbody = document.getElementById('auditar-table-body');
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:24px;color:var(--text-muted);">Cargando facturas...</td></tr>`;

    document.getElementById('auditar-modal-count').textContent        = '0';
    document.getElementById('auditar-modal-total-deuda').textContent  = formatCurrency(0);
    document.getElementById('auditar-selected-count').textContent     = '0 de 0';
    document.getElementById('auditar-selected-total').textContent     = formatCurrency(0);
    document.getElementById('auditar-master-checkbox').checked        = true;
    document.getElementById('auditar-submit-btn').disabled            = false;

    document.getElementById('auditar-modal-overlay').classList.add('open');
    document.getElementById('auditar-modal').classList.add('open');

    try {
        const response = await fetch(`/api/proveedores/${proveedorId}/facturas/`);
        if (!response.ok) throw new Error('Error al cargar facturas');

        modalFacturas = await response.json();

        if (modalFacturas.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:24px;color:var(--text-muted);">No hay facturas pendientes para este proveedor.</td></tr>`;
            return;
        }

        let totalDeuda = 0;
        modalFacturas.forEach(f => {
            totalDeuda     += f.saldo_neto;
            f.selected      = true;
            f.abono_input   = f.saldo_neto;
            f.notas_input   = '';
        });

        document.getElementById('auditar-modal-count').textContent       = modalFacturas.length;
        document.getElementById('auditar-modal-total-deuda').textContent = formatCurrency(totalDeuda);

        _renderAuditarModalTable();
    } catch (err) {
        console.error(err);
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:24px;color:var(--danger);font-weight:600;">✕ Error al cargar las facturas del proveedor.</td></tr>`;
    }
};

const _renderAuditarModalTable = () => {
    const tbody = document.getElementById('auditar-table-body');
    tbody.innerHTML = '';

    modalFacturas.forEach((f, idx) => {
        const scoringColor = f.scoring >= 75 ? 'var(--danger)' : f.scoring >= 50 ? 'var(--warning)' : 'var(--accent)';

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td class="checkbox-cell">
                <input type="checkbox" class="checkbox-custom row-checkbox" data-idx="${idx}" ${f.selected ? 'checked' : ''}>
            </td>
            <td style="font-family:var(--font-mono);font-weight:600;font-size:13px;">${f.folio}</td>
            <td style="text-align:center;">
                <span class="badge" style="background:${scoringColor}15;color:${scoringColor};font-weight:700;">${f.scoring}%</span>
            </td>
            <td style="text-align:center;color:var(--text-secondary);">${f.dias_vencidos} días</td>
            <td style="text-align:right;font-family:var(--font-mono);font-weight:600;color:var(--text-secondary);">${formatCurrency(f.saldo_neto)}</td>
            <td style="text-align:right;">
                <input type="number" step="0.01" min="0" max="${f.saldo_neto}"
                       class="auditar-input-abono" data-idx="${idx}" value="${f.abono_input.toFixed(2)}"
                       ${!f.selected ? 'disabled' : ''}>
            </td>
            <td>
                <input type="text" class="auditar-input-notas" data-idx="${idx}"
                       placeholder="Notas de auditoría..." value="${f.notas_input}"
                       ${!f.selected ? 'disabled' : ''}>
            </td>`;

        const checkbox  = tr.querySelector('.row-checkbox');
        const abonoInput = tr.querySelector('.auditar-input-abono');
        const notasInput = tr.querySelector('.auditar-input-notas');

        checkbox.addEventListener('change', (e) => {
            f.selected = e.target.checked;
            abonoInput.disabled = !f.selected;
            notasInput.disabled = !f.selected;
            if (f.selected && (parseFloat(abonoInput.value) === 0 || abonoInput.value === '')) {
                abonoInput.value = f.saldo_neto.toFixed(2);
                f.abono_input    = f.saldo_neto;
            }
            document.getElementById('auditar-master-checkbox').checked = modalFacturas.every(i => i.selected);
            _actualizarAuditarResumen();
        });

        abonoInput.addEventListener('input', (e) => {
            const val = parseFloat(e.target.value);
            const invalid = isNaN(val) || val < 0 || val > f.saldo_neto;
            e.target.classList.toggle('error', invalid);
            f.abono_input = invalid ? val : val;
            _actualizarAuditarResumen();
        });

        notasInput.addEventListener('input', (e) => { f.notas_input = e.target.value; });

        tbody.appendChild(tr);
    });

    _actualizarAuditarResumen();
};

const _actualizarAuditarResumen = () => {
    let selectedCount = 0;
    let totalAbonar   = 0;
    let hasErrors     = false;

    modalFacturas.forEach(f => {
        if (!f.selected) return;
        selectedCount++;
        totalAbonar += f.abono_input;
        if (f.abono_input < 0 || f.abono_input > f.saldo_neto || isNaN(f.abono_input)) hasErrors = true;
    });

    document.getElementById('auditar-selected-count').textContent = `${selectedCount} de ${modalFacturas.length}`;
    document.getElementById('auditar-selected-total').textContent = formatCurrency(totalAbonar);
    document.getElementById('auditar-submit-btn').disabled        = (selectedCount === 0 || hasErrors);
};

const cerrarAuditarModal = () => {
    document.getElementById('auditar-modal-overlay').classList.remove('open');
    document.getElementById('auditar-modal').classList.remove('open');
    modalFacturas = [];
};

// Master checkbox del modal auditar
document.addEventListener('DOMContentLoaded', () => {
    const masterCb = document.getElementById('auditar-master-checkbox');
    if (masterCb) {
        masterCb.addEventListener('change', (e) => {
            modalFacturas.forEach(f => { f.selected = e.target.checked; });
            _renderAuditarModalTable();
        });
    }
});

const enviarAuditoriaLote = async () => {
    const selected = modalFacturas.filter(f => f.selected);
    if (selected.length === 0) return;

    const submitBtn  = document.getElementById('auditar-submit-btn');
    const origText   = submitBtn.textContent;
    submitBtn.textContent = 'Autorizando lote...';
    submitBtn.disabled    = true;

    const payload = {
        autorizaciones: selected.map(f => ({
            id_factura:      f.id,
            abono:           f.abono_input,
            notas_auditoria: f.notas_input
        }))
    };

    try {
        const response = await fetch('/api/facturas/autorizar-lote/', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify(payload)
        });
        const res = await response.json();
        if (res.ok) {
            showToast(`✅ ${res.message}`);
            cerrarAuditarModal();
            // Notifica al módulo activo para recargar su tabla
            if (typeof onAuditarLoteSuccess === 'function') onAuditarLoteSuccess();
        } else {
            showToast(`❌ Error: ${res.error}`, false);
            submitBtn.disabled    = false;
            submitBtn.textContent = origText;
        }
    } catch (err) {
        console.error(err);
        showToast('✕ Fallo de red al autorizar facturas.', false);
        submitBtn.disabled    = false;
        submitBtn.textContent = origText;
    }
};
