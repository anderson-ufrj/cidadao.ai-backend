/**
 * CIDADÃO.AI - Investigations Module
 * Handles investigation creation, monitoring, and real-time updates
 */

let activeStreams = new Map();
let investigationsData = [];

/**
 * Initialize Investigations Module
 */
function loadInvestigations() {
    console.log('🔍 Loading investigations...');
    
    // Initialize form handlers
    initializeInvestigationForm();
    
    // Load existing investigations
    loadInvestigationsList();
}

/**
 * Investigation Form Handling
 */
function initializeInvestigationForm() {
    const form = document.getElementById('investigation-form');
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        await handleInvestigationSubmit();
    });
}

async function handleInvestigationSubmit() {
    try {
        // Get form data
        const formData = getInvestigationFormData();
        
        // Validate form
        if (!validateInvestigationForm(formData)) {
            return;
        }
        
        // Show progress modal
        const modal = CidadaoAI.utils.showProgressModal('Iniciando Investigação');
        
        // Start investigation
        const response = await CidadaoAI.api.startInvestigation(formData);
        
        if (response.investigation_id) {
            CidadaoAI.utils.showNotification('Investigação iniciada com sucesso!', 'success');
            
            // Clear form
            document.getElementById('investigation-form').reset();
            
            // Start monitoring the investigation
            monitorInvestigation(response.investigation_id, modal);
            
            // Refresh investigations list
            setTimeout(() => loadInvestigationsList(), 1000);
            
        } else {
            throw new Error('Invalid response from server');
        }
        
    } catch (error) {
        console.error('Failed to start investigation:', error);
        CidadaoAI.utils.handleApiError(error, 'start investigation');
        
        // Hide progress modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('progressModal'));
        if (modal) modal.hide();
    }
}

function getInvestigationFormData() {
    return {
        query: document.getElementById('investigation-query').value.trim(),
        data_source: document.getElementById('data-source').value,
        filters: getInvestigationFilters(),
        anomaly_types: getSelectedAnomalyTypes(),
        include_explanations: document.getElementById('include-explanations').checked,
        stream_results: true
    };
}

function getInvestigationFilters() {
    const filters = {};
    
    const organization = document.getElementById('organization').value.trim();
    if (organization) {
        filters.organization = organization;
    }
    
    // Add other filters as needed
    return filters;
}

function getSelectedAnomalyTypes() {
    const checkboxes = document.querySelectorAll('input[type="checkbox"][value]:checked');
    return Array.from(checkboxes)
        .filter(cb => cb.value !== 'include-explanations')
        .map(cb => cb.value);
}

function validateInvestigationForm(data) {
    if (!data.query) {
        CidadaoAI.utils.showNotification('Por favor, descreva o que você quer investigar', 'warning');
        document.getElementById('investigation-query').focus();
        return false;
    }
    
    if (data.anomaly_types.length === 0) {
        CidadaoAI.utils.showNotification('Selecione pelo menos um tipo de anomalia', 'warning');
        return false;
    }
    
    return true;
}

/**
 * Investigation Monitoring with Real-time Streaming
 */
async function monitorInvestigation(investigationId, modal) {
    try {
        // Start streaming updates
        CidadaoAI.api.streamInvestigation(
            investigationId,
            (data) => handleInvestigationUpdate(data, modal),
            (error) => handleStreamError(error, investigationId, modal),
            () => handleStreamComplete(investigationId, modal)
        );
        
        // Store active stream
        activeStreams.set(investigationId, {
            startTime: Date.now(),
            modal: modal
        });
        
    } catch (error) {
        console.error('Failed to start investigation monitoring:', error);
        CidadaoAI.utils.handleApiError(error, 'monitor investigation');
    }
}

function handleInvestigationUpdate(data, modal) {
    console.log('📡 Investigation update:', data);
    
    switch (data.type) {
        case 'progress':
            handleProgressUpdate(data, modal);
            break;
        case 'anomaly':
            handleAnomalyFound(data, modal);
            break;
        case 'completion':
            handleInvestigationComplete(data, modal);
            break;
        default:
            console.log('Unknown update type:', data.type);
    }
}

function handleProgressUpdate(data, modal) {
    const percentage = Math.round(data.progress * 100);
    const status = getProgressStatus(data.current_phase);
    
    CidadaoAI.utils.updateProgress(
        percentage,
        status,
        data.current_phase,
        `Processando ${data.records_processed || 0} registros...`
    );
}

function handleAnomalyFound(data, modal) {
    const anomaly = data.result;
    const logMessage = `🚨 Anomalia encontrada: ${anomaly.type} (confiança: ${Math.round(anomaly.confidence * 100)}%)`;
    
    CidadaoAI.utils.updateProgress(null, null, null, logMessage);
    
    // Show notification for high-confidence anomalies
    if (anomaly.confidence > 0.8) {
        CidadaoAI.utils.showNotification(
            `Anomalia de alta confiança detectada: ${anomaly.description}`,
            'warning',
            3000
        );
    }
}

function handleInvestigationComplete(data, modal) {
    CidadaoAI.utils.updateProgress(
        100,
        'Concluído',
        'completed',
        `✅ Investigação finalizada. ${data.total_anomalies || 0} anomalias encontradas.`
    );
    
    // Auto-close modal after 3 seconds
    setTimeout(() => {
        if (modal) modal.hide();
    }, 3000);
    
    // Show completion notification
    CidadaoAI.utils.showNotification(
        `Investigação concluída! ${data.total_anomalies || 0} anomalias encontradas.`,
        'success'
    );
    
    // Refresh investigations list
    setTimeout(() => loadInvestigationsList(), 1000);
}

function handleStreamError(error, investigationId, modal) {
    console.error('Stream error for investigation:', investigationId, error);
    
    CidadaoAI.utils.updateProgress(
        null,
        'Erro',
        'error',
        `❌ Erro na transmissão: ${error.message}`
    );
    
    // Clean up
    activeStreams.delete(investigationId);
    
    // Close modal after delay
    setTimeout(() => {
        if (modal) modal.hide();
    }, 5000);
}

function handleStreamComplete(investigationId, modal) {
    console.log('Stream completed for investigation:', investigationId);
    
    // Clean up
    activeStreams.delete(investigationId);
    
    // Refresh investigations list
    loadInvestigationsList();
}

function getProgressStatus(phase) {
    const statuses = {
        'initializing': 'Inicializando sistema...',
        'data_retrieval': 'Coletando dados...',
        'anomaly_detection': 'Detectando anomalias...',
        'analysis': 'Analisando padrões...',
        'summary_generation': 'Gerando resumo...',
        'completed': 'Investigação concluída',
        'failed': 'Investigação falhou'
    };
    
    return statuses[phase] || 'Processando...';
}

/**
 * Load Investigations List
 */
async function loadInvestigationsList() {
    try {
        const container = document.getElementById('investigations-list');
        if (!container) return;
        
        CidadaoAI.utils.setElementLoading('investigations-list', true);
        
        // Get investigations from API
        const investigations = await CidadaoAI.api.getInvestigations({ limit: 20 });
        
        // Store data
        investigationsData = investigations;
        
        // Render investigations
        if (investigations.length > 0) {
            container.innerHTML = investigations.map(renderInvestigationCard).join('');
        } else {
            container.innerHTML = `
                <div class="text-center text-muted py-5">
                    <i class="fas fa-search fa-3x mb-3"></i>
                    <h5>Nenhuma investigação encontrada</h5>
                    <p>Inicie sua primeira investigação usando o formulário acima.</p>
                </div>
            `;
        }
        
    } catch (error) {
        console.error('Failed to load investigations:', error);
        const container = document.getElementById('investigations-list');
        if (container) {
            container.innerHTML = `
                <div class="text-center text-danger py-4">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Erro ao carregar investigações
                </div>
            `;
        }
    }
}

function renderInvestigationCard(investigation) {
    const statusBadge = CidadaoAI.utils.getStatusBadge(investigation.status);
    const startedAt = CidadaoAI.utils.formatDate(investigation.started_at);
    const completedAt = investigation.completed_at ? CidadaoAI.utils.formatDate(investigation.completed_at) : null;
    
    return `
        <div class="card mb-3">
            <div class="card-body">
                <div class="row">
                    <div class="col-md-8">
                        <h6 class="card-title mb-2">
                            <i class="fas fa-search me-2"></i>
                            ${investigation.query || 'Investigação sem título'}
                        </h6>
                        <p class="card-text text-muted mb-2">
                            <small>
                                <i class="fas fa-database me-1"></i>
                                Fonte: ${formatDataSource(investigation.data_source)}
                                ${investigation.organization ? ` • Órgão: ${investigation.organization}` : ''}
                            </small>
                        </p>
                        <p class="card-text">
                            <small class="text-muted">
                                Iniciado em ${startedAt}
                                ${completedAt ? ` • Concluído em ${completedAt}` : ''}
                            </small>
                        </p>
                    </div>
                    <div class="col-md-4 text-md-end">
                        <div class="mb-2">
                            ${statusBadge}
                        </div>
                        ${renderInvestigationMetrics(investigation)}
                        <div class="btn-group btn-group-sm" role="group">
                            ${renderInvestigationActions(investigation)}
                        </div>
                    </div>
                </div>
                ${renderProgressBar(investigation)}
            </div>
        </div>
    `;
}

function renderInvestigationMetrics(investigation) {
    if (investigation.status !== 'completed') {
        return `
            <div class="text-muted small mb-2">
                <i class="fas fa-cog fa-spin me-1"></i>
                ${investigation.records_processed || 0} registros processados
            </div>
        `;
    }
    
    return `
        <div class="text-muted small mb-2">
            <div><i class="fas fa-exclamation-triangle text-warning me-1"></i>${investigation.anomalies_found || 0} anomalias</div>
            <div><i class="fas fa-file-alt text-info me-1"></i>${investigation.total_records_analyzed || 0} registros</div>
        </div>
    `;
}

function renderInvestigationActions(investigation) {
    const actions = [];
    
    if (investigation.status === 'completed') {
        actions.push(`
            <button class="btn btn-outline-primary" onclick="viewInvestigationResults('${investigation.investigation_id}')">
                <i class="fas fa-eye"></i> Ver Resultados
            </button>
        `);
    } else if (['pending', 'running'].includes(investigation.status)) {
        actions.push(`
            <button class="btn btn-outline-info" onclick="monitorInvestigationProgress('${investigation.investigation_id}')">
                <i class="fas fa-chart-line"></i> Monitorar
            </button>
        `);
        actions.push(`
            <button class="btn btn-outline-danger" onclick="cancelInvestigation('${investigation.investigation_id}')">
                <i class="fas fa-stop"></i> Cancelar
            </button>
        `);
    }
    
    return actions.join('');
}

function renderProgressBar(investigation) {
    if (!['pending', 'running'].includes(investigation.status)) {
        return '';
    }
    
    const progress = Math.round((investigation.progress || 0) * 100);
    
    return `
        <div class="mt-3">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <small class="text-muted">Progresso</small>
                <small class="text-muted">${progress}%</small>
            </div>
            <div class="progress" style="height: 6px;">
                <div class="progress-bar progress-bar-striped progress-bar-animated" 
                     style="width: ${progress}%"></div>
            </div>
        </div>
    `;
}

function formatDataSource(dataSource) {
    const sources = {
        'contracts': 'Contratos',
        'expenses': 'Despesas',
        'agreements': 'Convênios',
        'biddings': 'Licitações',
        'servants': 'Servidores'
    };
    return sources[dataSource] || dataSource;
}

/**
 * Investigation Actions
 */
async function viewInvestigationResults(investigationId) {
    try {
        CidadaoAI.utils.showLoading(true);
        
        const results = await CidadaoAI.api.getInvestigation(investigationId);
        
        CidadaoAI.utils.showLoading(false);
        
        // Show results in modal
        showInvestigationResultsModal(results);
        
    } catch (error) {
        CidadaoAI.utils.showLoading(false);
        CidadaoAI.utils.handleApiError(error, 'view investigation results');
    }
}

function showInvestigationResultsModal(results) {
    // Create modal if it doesn't exist
    let modal = document.getElementById('investigationResultsModal');
    if (!modal) {
        modal = createInvestigationResultsModal();
        document.body.appendChild(modal);
    }
    
    // Populate modal content
    const modalBody = modal.querySelector('.modal-body');
    modalBody.innerHTML = renderInvestigationResults(results);
    
    // Show modal
    const modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();
}

function createInvestigationResultsModal() {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'investigationResultsModal';
    modal.tabIndex = -1;
    
    modal.innerHTML = `
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <i class="fas fa-search-plus me-2"></i>
                        Resultados da Investigação
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <!-- Content will be populated dynamically -->
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-primary" onclick="exportInvestigationResults()">
                        <i class="fas fa-download me-2"></i>Exportar
                    </button>
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
                </div>
            </div>
        </div>
    `;
    
    return modal;
}

function renderInvestigationResults(results) {
    if (!results.results || results.results.length === 0) {
        return `
            <div class="text-center text-muted py-4">
                <i class="fas fa-info-circle fa-2x mb-3"></i>
                <h5>Nenhuma anomalia encontrada</h5>
                <p>Esta investigação não identificou irregularidades nos dados analisados.</p>
            </div>
        `;
    }
    
    return `
        <div class="investigation-summary mb-4">
            <div class="row">
                <div class="col-md-3">
                    <div class="text-center">
                        <h3 class="text-primary">${results.anomalies_found}</h3>
                        <small class="text-muted">Anomalias Encontradas</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <h3 class="text-info">${CidadaoAI.utils.formatNumber(results.total_records_analyzed)}</h3>
                        <small class="text-muted">Registros Analisados</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <h3 class="text-success">${Math.round(results.confidence_score * 100)}%</h3>
                        <small class="text-muted">Confiança Média</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <h3 class="text-warning">${results.processing_time.toFixed(1)}s</h3>
                        <small class="text-muted">Tempo de Processamento</small>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="investigation-summary-text mb-4">
            <h6>Resumo da Investigação</h6>
            <p class="text-muted">${results.summary}</p>
        </div>
        
        <div class="investigation-anomalies">
            <h6>Anomalias Detectadas</h6>
            ${results.results.map(renderAnomalyCard).join('')}
        </div>
    `;
}

function renderAnomalyCard(anomaly) {
    const confidenceColor = anomaly.confidence > 0.8 ? 'danger' : anomaly.confidence > 0.6 ? 'warning' : 'info';
    
    return `
        <div class="card mb-3">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <h6 class="card-title mb-0">
                        <i class="fas fa-exclamation-triangle text-${confidenceColor} me-2"></i>
                        ${anomaly.description}
                    </h6>
                    <span class="badge bg-${confidenceColor}">
                        ${Math.round(anomaly.confidence * 100)}% confiança
                    </span>
                </div>
                
                <p class="card-text">${anomaly.explanation}</p>
                
                <div class="row">
                    <div class="col-md-6">
                        <small class="text-muted">
                            <strong>Tipo:</strong> ${formatAnomalyType(anomaly.type)}<br>
                            <strong>Severidade:</strong> ${formatSeverity(anomaly.severity)}<br>
                            <strong>Registros Afetados:</strong> ${anomaly.affected_records.length}
                        </small>
                    </div>
                    <div class="col-md-6">
                        ${renderSuggestedActions(anomaly.suggested_actions)}
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderSuggestedActions(actions) {
    if (!actions || actions.length === 0) return '';
    
    return `
        <div>
            <small class="text-muted"><strong>Ações Sugeridas:</strong></small>
            <ul class="small text-muted mt-1">
                ${actions.map(action => `<li>${action}</li>`).join('')}
            </ul>
        </div>
    `;
}

function formatAnomalyType(type) {
    const types = {
        'price': 'Preço Anômalo',
        'vendor': 'Concentração de Fornecedor',
        'temporal': 'Padrão Temporal',
        'payment': 'Irregularidade de Pagamento',
        'duplicate': 'Duplicação',
        'pattern': 'Padrão Suspeito'
    };
    return types[type] || type;
}

function formatSeverity(severity) {
    const severities = {
        'low': 'Baixa',
        'medium': 'Média',
        'high': 'Alta',
        'critical': 'Crítica'
    };
    return severities[severity] || severity;
}

async function monitorInvestigationProgress(investigationId) {
    const modal = CidadaoAI.utils.showProgressModal('Monitorando Investigação');
    await monitorInvestigation(investigationId, modal);
}

async function cancelInvestigation(investigationId) {
    if (!confirm('Tem certeza que deseja cancelar esta investigação?')) {
        return;
    }
    
    try {
        await CidadaoAI.api.cancelInvestigation(investigationId);
        CidadaoAI.utils.showNotification('Investigação cancelada com sucesso', 'success');
        
        // Stop any active stream
        activeStreams.delete(investigationId);
        
        // Refresh list
        loadInvestigationsList();
        
    } catch (error) {
        CidadaoAI.utils.handleApiError(error, 'cancel investigation');
    }
}

function exportInvestigationResults() {
    // TODO: Implement export functionality
    CidadaoAI.utils.showNotification('Funcionalidade de exportação em desenvolvimento', 'info');
}

/**
 * Global refresh function
 */
window.refreshInvestigations = function() {
    loadInvestigationsList();
};

// Export functions
window.loadInvestigations = loadInvestigations;
window.viewInvestigationResults = viewInvestigationResults;
window.monitorInvestigationProgress = monitorInvestigationProgress;
window.cancelInvestigation = cancelInvestigation;
window.exportInvestigationResults = exportInvestigationResults;

// Cleanup active streams on page unload
window.addEventListener('beforeunload', () => {
    activeStreams.clear();
});