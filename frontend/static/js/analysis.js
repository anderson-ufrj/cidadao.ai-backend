/**
 * CIDADÃO.AI - Analysis Module
 * Handles pattern analysis, correlations, and trend detection
 */

let analysisCharts = {};
let analysisData = [];

/**
 * Initialize Analysis Module
 */
function loadAnalysis() {
    console.log('📊 Loading analysis module...');
    
    // Load existing analyses
    loadAnalysesList();
    
    // Initialize charts container
    initializeAnalysisCharts();
}

/**
 * Start Different Types of Analysis
 */
async function startAnalysis(analysisType) {
    try {
        const analysisConfig = getAnalysisConfig(analysisType);
        
        if (!analysisConfig) {
            CidadaoAI.utils.showNotification('Tipo de análise não suportado', 'error');
            return;
        }
        
        // Show analysis configuration modal
        showAnalysisConfigModal(analysisType, analysisConfig);
        
    } catch (error) {
        console.error('Failed to start analysis:', error);
        CidadaoAI.utils.handleApiError(error, 'start analysis');
    }
}

function getAnalysisConfig(analysisType) {
    const configs = {
        'spending_trends': {
            title: 'Análise de Tendências de Gastos',
            description: 'Identifica padrões de crescimento, declínio ou sazonalidade nos gastos públicos',
            icon: 'fa-chart-line',
            color: 'primary',
            fields: [
                { name: 'data_source', label: 'Fonte de Dados', type: 'select', required: true },
                { name: 'time_period', label: 'Período', type: 'select', required: true },
                { name: 'organization', label: 'Órgão', type: 'text', required: false }
            ]
        },
        'vendor_patterns': {
            title: 'Análise de Padrões de Fornecedores',
            description: 'Detecta comportamentos suspeitos e concentração excessiva de fornecedores',
            icon: 'fa-project-diagram',
            color: 'success',
            fields: [
                { name: 'data_source', label: 'Fonte de Dados', type: 'select', required: true },
                { name: 'min_contracts', label: 'Mín. Contratos', type: 'number', required: false },
                { name: 'organization', label: 'Órgão', type: 'text', required: false }
            ]
        },
        'correlations': {
            title: 'Análise de Correlações',
            description: 'Descobre relações estatísticas entre diferentes variáveis dos dados',
            icon: 'fa-sitemap',
            color: 'warning',
            fields: [
                { name: 'data_source', label: 'Fonte de Dados', type: 'select', required: true },
                { name: 'variables', label: 'Variáveis', type: 'multiselect', required: true },
                { name: 'method', label: 'Método', type: 'select', required: false }
            ]
        }
    };
    
    return configs[analysisType];
}

function showAnalysisConfigModal(analysisType, config) {
    // Create or get modal
    let modal = document.getElementById('analysisConfigModal');
    if (!modal) {
        modal = createAnalysisConfigModal();
        document.body.appendChild(modal);
    }
    
    // Populate modal
    const modalTitle = modal.querySelector('.modal-title');
    const modalBody = modal.querySelector('.modal-body');
    const submitBtn = modal.querySelector('.btn-primary');
    
    modalTitle.innerHTML = `
        <i class="fas ${config.icon} text-${config.color} me-2"></i>
        ${config.title}
    `;
    
    modalBody.innerHTML = `
        <div class="mb-3">
            <p class="text-muted">${config.description}</p>
        </div>
        <form id="analysis-config-form">
            ${config.fields.map(field => renderAnalysisField(field)).join('')}
        </form>
    `;
    
    // Update submit button
    submitBtn.onclick = () => submitAnalysisConfig(analysisType);
    
    // Show modal
    const modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();
}

function createAnalysisConfigModal() {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'analysisConfigModal';
    modal.tabIndex = -1;
    
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title"></h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <!-- Content will be populated dynamically -->
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <button type="button" class="btn btn-primary">Iniciar Análise</button>
                </div>
            </div>
        </div>
    `;
    
    return modal;
}

function renderAnalysisField(field) {
    const isRequired = field.required ? 'required' : '';
    
    switch (field.type) {
        case 'select':
            return `
                <div class="mb-3">
                    <label for="${field.name}" class="form-label">${field.label}</label>
                    <select class="form-select" id="${field.name}" name="${field.name}" ${isRequired}>
                        ${getSelectOptions(field.name)}
                    </select>
                </div>
            `;
        case 'multiselect':
            return `
                <div class="mb-3">
                    <label for="${field.name}" class="form-label">${field.label}</label>
                    <select class="form-select" id="${field.name}" name="${field.name}" multiple ${isRequired}>
                        ${getSelectOptions(field.name)}
                    </select>
                    <div class="form-text">Segure Ctrl para selecionar múltiplas opções</div>
                </div>
            `;
        case 'number':
            return `
                <div class="mb-3">
                    <label for="${field.name}" class="form-label">${field.label}</label>
                    <input type="number" class="form-control" id="${field.name}" name="${field.name}" ${isRequired}>
                </div>
            `;
        default:
            return `
                <div class="mb-3">
                    <label for="${field.name}" class="form-label">${field.label}</label>
                    <input type="text" class="form-control" id="${field.name}" name="${field.name}" ${isRequired}>
                </div>
            `;
    }
}

function getSelectOptions(fieldName) {
    const options = {
        'data_source': `
            <option value="contracts">Contratos</option>
            <option value="expenses">Despesas</option>
            <option value="agreements">Convênios</option>
            <option value="biddings">Licitações</option>
        `,
        'time_period': `
            <option value="3months">3 meses</option>
            <option value="6months">6 meses</option>
            <option value="1year">1 ano</option>
            <option value="2years">2 anos</option>
        `,
        'variables': `
            <option value="valor">Valor</option>
            <option value="prazo">Prazo</option>
            <option value="fornecedor">Fornecedor</option>
            <option value="orgao">Órgão</option>
            <option value="modalidade">Modalidade</option>
        `,
        'method': `
            <option value="pearson">Pearson</option>
            <option value="spearman">Spearman</option>
            <option value="kendall">Kendall</option>
        `
    };
    
    return options[fieldName] || '';
}

async function submitAnalysisConfig(analysisType) {
    try {
        const form = document.getElementById('analysis-config-form');
        const formData = new FormData(form);
        
        // Build analysis request
        const analysisRequest = {
            analysis_type: analysisType,
            data_source: formData.get('data_source'),
            include_correlations: true,
            include_trends: true
        };
        
        // Add type-specific parameters
        if (analysisType === 'spending_trends') {
            analysisRequest.time_period = formData.get('time_period');
        } else if (analysisType === 'vendor_patterns') {
            if (formData.get('min_contracts')) {
                analysisRequest.min_contracts = parseInt(formData.get('min_contracts'));
            }
        } else if (analysisType === 'correlations') {
            const variables = Array.from(form.querySelectorAll('[name="variables"] option:checked')).map(opt => opt.value);
            analysisRequest.variables = variables;
            if (formData.get('method')) {
                analysisRequest.method = formData.get('method');
            }
        }
        
        // Add common filters
        if (formData.get('organization')) {
            analysisRequest.filters = { organization: formData.get('organization') };
        }
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('analysisConfigModal'));
        modal.hide();
        
        // Show progress modal
        const progressModal = CidadaoAI.utils.showProgressModal('Executando Análise');
        
        // Start analysis
        const response = await CidadaoAI.api.startAnalysis(analysisRequest);
        
        if (response.analysis_id) {
            CidadaoAI.utils.showNotification('Análise iniciada com sucesso!', 'success');
            
            // Monitor analysis progress
            await monitorAnalysis(response.analysis_id, progressModal);
            
            // Refresh analyses list
            setTimeout(() => loadAnalysesList(), 1000);
            
        } else {
            throw new Error('Invalid response from server');
        }
        
    } catch (error) {
        console.error('Failed to submit analysis config:', error);
        CidadaoAI.utils.handleApiError(error, 'submit analysis');
    }
}

/**
 * Monitor Analysis Progress
 */
async function monitorAnalysis(analysisId, modal) {
    try {
        let completed = false;
        let attempts = 0;
        const maxAttempts = 60; // 5 minutes with 5-second intervals
        
        while (!completed && attempts < maxAttempts) {
            await new Promise(resolve => setTimeout(resolve, 5000)); // Wait 5 seconds
            
            try {
                const status = await CidadaoAI.api.getAnalysisStatus(analysisId);
                
                const percentage = Math.round(status.progress * 100);
                CidadaoAI.utils.updateProgress(
                    percentage,
                    status.status,
                    status.current_phase || 'Processando...',
                    `Analisando dados... (${status.analysis_type})`
                );
                
                if (status.status === 'completed') {
                    completed = true;
                    CidadaoAI.utils.showNotification('Análise concluída com sucesso!', 'success');
                    
                    // Auto-close modal after 2 seconds
                    setTimeout(() => {
                        if (modal) modal.hide();
                    }, 2000);
                    
                } else if (status.status === 'failed') {
                    completed = true;
                    CidadaoAI.utils.showNotification('Análise falhou', 'error');
                    setTimeout(() => {
                        if (modal) modal.hide();
                    }, 3000);
                }
                
            } catch (statusError) {
                console.warn('Failed to get analysis status:', statusError);
            }
            
            attempts++;
        }
        
        if (!completed) {
            CidadaoAI.utils.showNotification('Análise demorou mais que o esperado', 'warning');
            if (modal) modal.hide();
        }
        
    } catch (error) {
        console.error('Failed to monitor analysis:', error);
        if (modal) modal.hide();
    }
}

/**
 * Load Analyses List
 */
async function loadAnalysesList() {
    try {
        const container = document.getElementById('analysis-results');
        if (!container) return;
        
        CidadaoAI.utils.setElementLoading('analysis-results', true);
        
        // Get analyses from API
        const analyses = await CidadaoAI.api.getAnalyses({ limit: 20 });
        
        // Store data
        analysisData = analyses;
        
        // Render analyses
        if (analyses.length > 0) {
            container.innerHTML = `
                <div class="row">
                    ${analyses.map(renderAnalysisCard).join('')}
                </div>
            `;
        } else {
            container.innerHTML = `
                <div class="text-center text-muted py-5">
                    <i class="fas fa-chart-bar fa-3x mb-3"></i>
                    <h5>Nenhuma análise encontrada</h5>
                    <p>Inicie sua primeira análise usando os cartões acima.</p>
                </div>
            `;
        }
        
    } catch (error) {
        console.error('Failed to load analyses:', error);
        const container = document.getElementById('analysis-results');
        if (container) {
            container.innerHTML = `
                <div class="text-center text-danger py-4">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Erro ao carregar análises
                </div>
            `;
        }
    }
}

function renderAnalysisCard(analysis) {
    const statusBadge = CidadaoAI.utils.getStatusBadge(analysis.status);
    const startedAt = CidadaoAI.utils.formatDate(analysis.started_at);
    const completedAt = analysis.completed_at ? CidadaoAI.utils.formatDate(analysis.completed_at) : null;
    
    return `
        <div class="col-md-6 mb-4">
            <div class="card h-100">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h6 class="card-title mb-0">
                            <i class="fas ${getAnalysisIcon(analysis.analysis_type)} me-2"></i>
                            ${getAnalysisTitle(analysis.analysis_type)}
                        </h6>
                        ${statusBadge}
                    </div>
                    
                    <p class="card-text text-muted small">
                        <i class="fas fa-database me-1"></i>
                        ${formatDataSource(analysis.data_source)}
                    </p>
                    
                    <p class="card-text">
                        <small class="text-muted">
                            Iniciado em ${startedAt}
                            ${completedAt ? `<br>Concluído em ${completedAt}` : ''}
                        </small>
                    </p>
                    
                    ${renderAnalysisProgress(analysis)}
                </div>
                
                <div class="card-footer bg-transparent">
                    ${renderAnalysisActions(analysis)}
                </div>
            </div>
        </div>
    `;
}

function getAnalysisIcon(analysisType) {
    const icons = {
        'spending_trends': 'fa-chart-line',
        'vendor_patterns': 'fa-project-diagram',
        'correlations': 'fa-sitemap',
        'organizational_behavior': 'fa-building',
        'efficiency_metrics': 'fa-tachometer-alt'
    };
    return icons[analysisType] || 'fa-chart-bar';
}

function getAnalysisTitle(analysisType) {
    const titles = {
        'spending_trends': 'Tendências de Gastos',
        'vendor_patterns': 'Padrões de Fornecedores',
        'correlations': 'Análise de Correlações',
        'organizational_behavior': 'Comportamento Organizacional',
        'efficiency_metrics': 'Métricas de Eficiência'
    };
    return titles[analysisType] || analysisType;
}

function renderAnalysisProgress(analysis) {
    if (!['pending', 'running'].includes(analysis.status)) {
        return '';
    }
    
    const progress = Math.round((analysis.progress || 0) * 100);
    
    return `
        <div class="mt-3">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <small class="text-muted">Progresso</small>
                <small class="text-muted">${progress}%</small>
            </div>
            <div class="progress" style="height: 4px;">
                <div class="progress-bar progress-bar-striped progress-bar-animated" 
                     style="width: ${progress}%"></div>
            </div>
        </div>
    `;
}

function renderAnalysisActions(analysis) {
    if (analysis.status === 'completed') {
        return `
            <button class="btn btn-outline-primary btn-sm" onclick="viewAnalysisResults('${analysis.analysis_id}')">
                <i class="fas fa-eye"></i> Ver Resultados
            </button>
        `;
    } else if (['pending', 'running'].includes(analysis.status)) {
        return `
            <button class="btn btn-outline-info btn-sm" onclick="monitorAnalysisProgress('${analysis.analysis_id}')">
                <i class="fas fa-chart-line"></i> Monitorar
            </button>
        `;
    }
    
    return `
        <span class="text-muted small">
            <i class="fas fa-clock me-1"></i>
            Análise finalizada
        </span>
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
 * Analysis Actions
 */
async function viewAnalysisResults(analysisId) {
    try {
        CidadaoAI.utils.showLoading(true);
        
        const results = await CidadaoAI.api.getAnalysis(analysisId);
        
        CidadaoAI.utils.showLoading(false);
        
        // Show results in modal
        showAnalysisResultsModal(results);
        
    } catch (error) {
        CidadaoAI.utils.showLoading(false);
        CidadaoAI.utils.handleApiError(error, 'view analysis results');
    }
}

function showAnalysisResultsModal(results) {
    // Create modal if it doesn't exist
    let modal = document.getElementById('analysisResultsModal');
    if (!modal) {
        modal = createAnalysisResultsModal();
        document.body.appendChild(modal);
    }
    
    // Populate modal content
    const modalBody = modal.querySelector('.modal-body');
    modalBody.innerHTML = renderAnalysisResults(results);
    
    // Show modal
    const modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();
}

function createAnalysisResultsModal() {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'analysisResultsModal';
    modal.tabIndex = -1;
    
    modal.innerHTML = `
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <i class="fas fa-chart-area me-2"></i>
                        Resultados da Análise
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <!-- Content will be populated dynamically -->
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-primary" onclick="exportAnalysisResults()">
                        <i class="fas fa-download me-2"></i>Exportar
                    </button>
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
                </div>
            </div>
        </div>
    `;
    
    return modal;
}

function renderAnalysisResults(results) {
    return `
        <div class="analysis-summary mb-4">
            <div class="row">
                <div class="col-md-4">
                    <div class="text-center">
                        <h4 class="text-primary">${getAnalysisTitle(results.analysis_type)}</h4>
                        <small class="text-muted">Tipo de Análise</small>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="text-center">
                        <h4 class="text-success">${Math.round(results.confidence_score * 100)}%</h4>
                        <small class="text-muted">Confiança</small>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="text-center">
                        <h4 class="text-info">${results.processing_time.toFixed(1)}s</h4>
                        <small class="text-muted">Tempo de Processamento</small>
                    </div>
                </div>
            </div>
        </div>
        
        ${renderInsights(results.insights)}
        ${renderRecommendations(results.recommendations)}
        ${renderAnalysisData(results.results)}
    `;
}

function renderInsights(insights) {
    if (!insights || insights.length === 0) return '';
    
    return `
        <div class="mb-4">
            <h6><i class="fas fa-lightbulb text-warning me-2"></i>Insights Descobertos</h6>
            <div class="list-group">
                ${insights.map(insight => `
                    <div class="list-group-item">
                        <i class="fas fa-arrow-right text-primary me-2"></i>
                        ${insight}
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function renderRecommendations(recommendations) {
    if (!recommendations || recommendations.length === 0) return '';
    
    return `
        <div class="mb-4">
            <h6><i class="fas fa-clipboard-list text-success me-2"></i>Recomendações</h6>
            <div class="list-group">
                ${recommendations.map(recommendation => `
                    <div class="list-group-item">
                        <i class="fas fa-check text-success me-2"></i>
                        ${recommendation}
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function renderAnalysisData(data) {
    if (!data) return '';
    
    return `
        <div class="mb-4">
            <h6><i class="fas fa-chart-bar text-info me-2"></i>Dados da Análise</h6>
            <pre class="bg-light p-3 rounded"><code>${JSON.stringify(data, null, 2)}</code></pre>
        </div>
    `;
}

async function monitorAnalysisProgress(analysisId) {
    const modal = CidadaoAI.utils.showProgressModal('Monitorando Análise');
    await monitorAnalysis(analysisId, modal);
}

function exportAnalysisResults() {
    // TODO: Implement export functionality
    CidadaoAI.utils.showNotification('Funcionalidade de exportação em desenvolvimento', 'info');
}

/**
 * Initialize Charts Container
 */
function initializeAnalysisCharts() {
    // Charts will be created dynamically when analysis results are shown
    console.log('📊 Analysis charts container initialized');
}

// Export functions
window.loadAnalysis = loadAnalysis;
window.startAnalysis = startAnalysis;
window.viewAnalysisResults = viewAnalysisResults;
window.monitorAnalysisProgress = monitorAnalysisProgress;
window.exportAnalysisResults = exportAnalysisResults;