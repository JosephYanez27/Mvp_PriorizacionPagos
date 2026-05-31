/**
 * priorizacion.js
 * ──────────────────────────────────────────────────────────
 * Módulo 1: Cuentas por Pagar agrupadas por proveedor.
 * Depende de: globals.js (formatCurrency, showToast,
 *             buildStarsHtml, abrirAuditarModal, enviarAuditoriaLote)
 * ──────────────────────────────────────────────────────────
 */

// ── Estado del módulo ─────────────────────────────────────
let facturasPrio        = [];
let currentPrioList     = [];
let isSortPrioDesc      = true;
let selectedStarFilter  = 'all';
let selectedPrioIndex   = null;

// ── DOM refs ──────────────────────────────────────────────
const tableBodyPrio  = document.getElementById('tableBodyPrio');
const searchInput    = document.getElementById('searchInputPrio');
const starFilter     = document.getElementById('starFilterPrio');
const sortBtn        = document.getElementById('sortBtnPrio');
const sortIcon       = document.getElementById('sort-icon-prio');
const emptyState     = document.getElementById('emptyState');
const bladeOverlay   = document.getElementById('blade-overlay');
const blade          = document.getElementById('blade');
const excelFileInput = document.getElementById('excelFileInput');


// ══════════════════════════════════════════════════════════
//  CARGA Y FILTRADO
// ══════════════════════════════════════════════════════════

const cargarDatosPrio = async () => {
    tableBodyPrio.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:32px;color:var(--text-muted);font-weight:500;">Conectando con cuentas por pagar...</td></tr>`;
    try {
        const response = await fetch('/api/pagos/por-proveedor/');
        if (!response.ok) throw new Error('Respuesta de red inválida.');
        facturasPrio = await response.json();
        filtrarDatosPrio();
    } catch (error) {
        console.error('Error al cargar prioritarios:', error);
        tableBodyPrio.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:32px;color:var(--danger);font-weight:600;">✕ Fallo de Sincronización: No se pudieron extraer las cuentas pendientes.</td></tr>`;
    }
};

const filtrarDatosPrio = () => {
    const search = searchInput.value.toLowerCase().trim();

    currentPrioList = facturasPrio.filter(f => {
        const matchesSearch = f.proveedor.toLowerCase().includes(search) ||
            f.folios.some(folio => folio.toLowerCase().includes(search));
        const matchesStars = selectedStarFilter === 'all' ||
            Math.floor(f.estrellas).toString() === selectedStarFilter;
        return matchesSearch && matchesStars;
    });

    currentPrioList.sort((a, b) =>
        isSortPrioDesc ? b.suma_saldo_neto - a.suma_saldo_neto : a.suma_saldo_neto - b.suma_saldo_neto
    );

    renderTablePrio();
};

const renderTablePrio = () => {
    tableBodyPrio.innerHTML = '';

    if (currentPrioList.length === 0) {
        emptyState.style.display = 'block';
        actualizarKPIsPrio(0, 0, 0, 0);
        return;
    }
    emptyState.style.display = 'none';

    let totalSaldoNeto     = 0;
    let totalFacturasGlobal = 0;
    let sumaEstrellas       = 0;

    currentPrioList.forEach((f) => {
        totalSaldoNeto      += f.suma_saldo_neto;
        totalFacturasGlobal += f.total_facturas;
        sumaEstrellas       += f.estrellas;

        const foliosDisplay = f.folios.length > 2
            ? `${f.folios[0]}, ${f.folios[1]} <span style="color:var(--text-muted);font-size:11px;">+${f.folios.length - 2}</span>`
            : f.folios.join(', ');

        const tr = document.createElement('tr');
        tr.style.cursor = 'pointer';
        tr.innerHTML = `
            <td style="text-align:center;font-weight:600;">${f.total_facturas}</td>
            <td style="font-weight:600;color:var(--text-primary);font-family:var(--font-mono);font-size:13px;">${foliosDisplay}</td>
            <td style="font-weight:500;">${f.proveedor}</td>
            <td style="text-align:center;">${buildStarsHtml(f.estrellas)}</td>
            <td style="text-align:right;font-family:var(--font-mono);">${formatCurrency(f.suma_monto_original)}</td>
            <td style="text-align:right;font-family:var(--font-mono);font-weight:600;color:var(--text-secondary);">${formatCurrency(f.suma_saldo_neto)}</td>
            <td style="text-align:center;">
                <button class="review-btn" onclick="event.stopPropagation(); abrirAuditoria(${f.proveedor_id})">Auditar</button>
            </td>`;
        tr.addEventListener('click', () => abrirAuditarModal(f.proveedor_id, f.proveedor, f.estrellas));
        tableBodyPrio.appendChild(tr);
    });

    const avgEstrellas = (sumaEstrellas / currentPrioList.length).toFixed(1);
    actualizarKPIsPrio(totalSaldoNeto, currentPrioList.length, totalFacturasGlobal, avgEstrellas);
};

const actualizarKPIsPrio = (total, provCount, facturasCount, promEstrellas) => {
    document.getElementById('kpi-prio-total').textContent           = formatCurrency(total);
    document.getElementById('kpi-prio-count').textContent           = `${facturasCount} facturas en cola`;
    document.getElementById('kpi-prio-criticos').textContent        = provCount;
    document.getElementById('kpi-prio-avg-estrellas').textContent   = isNaN(promEstrellas) ? '0.0' : promEstrellas;
};

// Wrapper para el botón "Auditar" de la tabla
const abrirAuditoria = (proveedorId) => {
    const prov = currentPrioList.find(p => p.proveedor_id === proveedorId);
    if (prov) abrirAuditarModal(prov.proveedor_id, prov.proveedor, prov.estrellas);
};

// Callback que globals.js invoca tras autorizar el lote con éxito
const onAuditarLoteSuccess = () => cargarDatosPrio();


// ══════════════════════════════════════════════════════════
//  BLADE (detalle de factura individual)
// ══════════════════════════════════════════════════════════

const abrirDetalleBlade = (idx) => {
    selectedPrioIndex = idx;
    const f = currentPrioList[idx];
    if (!f) return;

    document.getElementById('blade-folio').textContent       = `Factura ${f.folio}`;
    document.getElementById('blade-prov-name').textContent   = f.proveedor;
    document.getElementById('blade-monto-orig').textContent  = `${formatCurrency(f.monto_original)} ${f.moneda}`;
    document.getElementById('blade-monto-mxn').textContent   = formatCurrency(f.monto_mxn);
    document.getElementById('blade-total').textContent       = formatCurrency(f.total);
    document.getElementById('blade-saldo-neto').textContent  = formatCurrency(f.saldo_neto);
    document.getElementById('blade-factor-prov').textContent = `${f.estrellas} / 5 Estrellas`;
    document.getElementById('blade-factor-tiempo').textContent = `${f.dias_vencidos} días de retraso`;

    const abonoInput = document.getElementById('abonoInput');
    abonoInput.value = f.saldo_neto;
    abonoInput.max   = f.saldo_neto;
    document.getElementById('abono-error-msg').style.display  = 'none';
    document.getElementById('notasAuditoriaInput').value      = f.notas_auditoria || '';

    const alertZone  = document.getElementById('blade-alert-zone');
    const alertTitle = document.getElementById('blade-alert-title');
    const alertDesc  = document.getElementById('blade-alert-desc');
    alertZone.className = 'alert-box';

    if (f.scoring >= 75) {
        alertZone.classList.add('critical');
        alertTitle.textContent = `Riesgo Crítico: Scoring ${f.scoring}%`;
        alertDesc.textContent  = 'Prioridad de pago de emergencia. Supera el umbral operativo por acumulación grave de días de retraso.';
    } else if (f.scoring >= 50) {
        alertZone.classList.add('warning');
        alertTitle.textContent = `Atención Moderada: Scoring ${f.scoring}%`;
        alertDesc.textContent  = 'Evolución de deuda intermedia. Monitorear penalidades del contrato comercial.';
    } else {
        alertZone.classList.add('info');
        alertTitle.textContent = `Estatus Controlado: Scoring ${f.scoring}%`;
        alertDesc.textContent  = 'Parámetros saludables. Factura con vencimiento reciente, bajo riesgo operativo.';
    }

    bladeOverlay.classList.add('open');
    blade.classList.add('open');
};

const cerrarBlade = () => {
    bladeOverlay.classList.remove('open');
    blade.classList.remove('open');
    selectedPrioIndex = null;
};

document.getElementById('closeBladeBtn').addEventListener('click', cerrarBlade);
document.getElementById('cancelBladeBtn').addEventListener('click', cerrarBlade);
bladeOverlay.addEventListener('click', cerrarBlade);

document.getElementById('confirmAutorizarBtn').addEventListener('click', async () => {
    if (selectedPrioIndex === null) return;
    const f = currentPrioList[selectedPrioIndex];
    if (!f) return;

    const abonoVal = parseFloat(document.getElementById('abonoInput').value);
    const notasVal = document.getElementById('notasAuditoriaInput').value.trim();
    const errorMsg = document.getElementById('abono-error-msg');

    if (isNaN(abonoVal) || abonoVal < 0) {
        errorMsg.textContent = 'El abono no puede ser negativo ni vacío.';
        errorMsg.style.display = 'block';
        return;
    }
    if (abonoVal > f.saldo_neto) {
        errorMsg.textContent = `El abono no puede superar el saldo neto disponible (${formatCurrency(f.saldo_neto)}).`;
        errorMsg.style.display = 'block';
        return;
    }
    errorMsg.style.display = 'none';

    try {
        const response = await fetch(`/api/facturas/${f.id}/autorizar/`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ notas_auditoria: notasVal, abono: abonoVal })
        });
        const res = await response.json();
        if (res.ok) {
            showToast(`Factura ${f.folio} autorizada correctamente por ${formatCurrency(abonoVal)}.`);
            cerrarBlade();
            cargarDatosPrio();
        } else {
            showToast(`Error al autorizar: ${res.error}`, false);
        }
    } catch (err) {
        console.error('Error en autorización:', err);
        showToast('Fallo de comunicación con el servidor.', false);
    }
});


// ══════════════════════════════════════════════════════════
//  MODAL CARGA EXCEL
// ══════════════════════════════════════════════════════════

const abrirModalCarga = () => {
    excelFileInput.value = '';
    document.getElementById('dropzone-text').style.display = 'block';
    document.getElementById('file-name-preview').style.display = 'none';
    document.getElementById('upload-modal-overlay').classList.add('open');
    document.getElementById('upload-modal').classList.add('open');
};

const cerrarModalCarga = () => {
    document.getElementById('upload-modal-overlay').classList.remove('open');
    document.getElementById('upload-modal').classList.remove('open');
};

excelFileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        document.getElementById('dropzone-text').style.display = 'none';
        const preview = document.getElementById('file-name-preview');
        preview.textContent = `✓ Seleccionado: ${e.target.files[0].name}`;
        preview.style.display = 'block';
    }
});

document.getElementById('formSubirExcel').addEventListener('submit', async function (e) {
    e.preventDefault();
    const submitBtn  = document.getElementById('submitBtn');
    const fileInput  = document.getElementById('excelFileInput');
    if (fileInput.files.length === 0) return;

    const origText      = submitBtn.textContent;
    submitBtn.textContent = 'Importando lote...';
    submitBtn.disabled    = true;

    const formData = new FormData();
    formData.append('archivo', fileInput.files[0]);

    try {
        const response = await fetch('/api/cargas/excel/', { method: 'POST', body: formData });
        const res = await response.json();
        if (res.ok) {
            showToast(`✅ ${res.message}`);
            cerrarModalCarga();
            cargarDatosPrio();
        } else {
            showToast(`❌ Error: ${res.error}`, false);
        }
    } catch (err) {
        console.error('Error de importación:', err);
        showToast('No se pudo comunicar con el cargador de facturas.', false);
    } finally {
        submitBtn.textContent = origText;
        submitBtn.disabled    = false;
    }
});


// ── Filtros y ordenamiento ────────────────────────────────
starFilter.addEventListener('change', (e) => {
    selectedStarFilter = e.target.value;
    filtrarDatosPrio();
});

searchInput.addEventListener('input', filtrarDatosPrio);

sortBtn.addEventListener('click', () => {
    isSortPrioDesc = !isSortPrioDesc;
    sortBtn.querySelector('span').textContent = isSortPrioDesc ? 'Deuda: Mayor a Menor' : 'Deuda: Menor a Mayor';
    sortIcon.setAttribute('data-lucide', isSortPrioDesc ? 'arrow-down-narrow-wide' : 'arrow-up-narrow-wide');
    lucide.createIcons();
    filtrarDatosPrio();
});


// ── Init ──────────────────────────────────────────────────
cargarDatosPrio();
