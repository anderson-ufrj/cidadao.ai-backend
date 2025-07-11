/**
 * CIDADÃO.AI - Reports Module
 * Handles report generation, management, and viewing
 */

let reportsData = [];
let reportTemplates = [];

/**
 * Initialize Reports Module
 */
function loadReports() {
    console.log('📄 Loading reports module...');
    
    // Load report templates and existing reports
    loadReportTemplates();
    loadReportsList();
    
    // Initialize form handlers
    initializeReportForm();
}

/**
 * Load Report Templates
 */
async function loadReportTemplates() {
    try {
        const templates = await CidadaoAI.api.getReportTemplates();
        reportTemplates = templates;
        
        // Populate template selector
        const templateSelector = document.getElementById('report-template');
        if (templateSelector) {
            templateSelector.innerHTML = templates.map(template => `
                <option value="${template.id}" data-description="${template.description}">
                    ${template.name}
                </option>
            `).join('');
            
            // Update description on selection change
            templateSelector.addEventListener('change', updateTemplateDescription);
        }
        
    } catch (error) {
        console.error('Failed to load report templates:', error);
        // Use default templates if API fails
        reportTemplates = getDefaultTemplates();
        populateDefaultTemplates();
    }
}

function getDefaultTemplates() {
    return [
        {
            id: 'investigation_summary',
            name: 'Resumo de Investigação',
            description: 'Relatório detalhado de uma investigação específica com anomalias encontradas',
            type: 'investigation',
            sections: ['summary', 'anomalies', 'recommendations']
        },
        {
            id: 'monthly_analysis',
            name: 'Análise Mensal',
            description: 'Relatório mensal consolidado com principais achados e tendências',
            type: 'periodic',
            sections: ['overview', 'trends', 'highlights', 'metrics']
        },
        {
            id: 'vendor_analysis',
            name: 'Análise de Fornecedores',
            description: 'Relatório focado em padrões e irregularidades de fornecedores',
            type: 'thematic',
            sections: ['vendor_overview', 'concentrations', 'anomalies', 'recommendations']
        },
        {
            id: 'spending_trends',
            name: 'Tendências de Gastos',
            description: 'Análise temporal de gastos públicos com identificação de padrões',
            type: 'analytical',
            sections: ['temporal_analysis', 'seasonal_patterns', 'outliers', 'projections']
        }
    ];
}

function populateDefaultTemplates() {
    const templateSelector = document.getElementById('report-template');
    if (templateSelector) {
        templateSelector.innerHTML = reportTemplates.map(template => `
            <option value="${template.id}" data-description="${template.description}">
                ${template.name}
            </option>
        `).join('');
        
        templateSelector.addEventListener('change', updateTemplateDescription);
    }
}

function updateTemplateDescription() {
    const selector = document.getElementById('report-template');
    const description = document.getElementById('template-description');
    
    if (selector && description) {
        const selectedOption = selector.selectedOptions[0];
        if (selectedOption) {
            description.textContent = selectedOption.dataset.description || '';
        }
    }
}

/**
 * Report Form Handling
 */
function initializeReportForm() {
    const form = document.getElementById('report-form');
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        await handleReportSubmit();
    });
    
    // Handle data source change
    const dataSourceSelect = document.getElementById('report-data-source');
    if (dataSourceSelect) {
        dataSourceSelect.addEventListener('change', updateDataSourceOptions);
    }
}

async function handleReportSubmit() {
    try {
        // Get form data
        const formData = getReportFormData();
        
        // Validate form
        if (!validateReportForm(formData)) {
            return;
        }
        
        // Show progress modal
        const modal = CidadaoAI.utils.showProgressModal('Gerando Relatório');
        
        // Start report generation
        const response = await CidadaoAI.api.generateReport(formData);
        
        if (response.report_id) {
            CidadaoAI.utils.showNotification('Relatório iniciado com sucesso!', 'success');
            
            // Clear form
            document.getElementById('report-form').reset();
            
            // Monitor report generation
            await monitorReportGeneration(response.report_id, modal);
            
            // Refresh reports list
            setTimeout(() => loadReportsList(), 1000);
            
        } else {
            throw new Error('Invalid response from server');
        }
        
    } catch (error) {
        console.error('Failed to start report generation:', error);
        CidadaoAI.utils.handleApiError(error, 'generate report');
        
        // Hide progress modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('progressModal'));
        if (modal) modal.hide();
    }
}

function getReportFormData() {
    return {
        title: document.getElementById('report-title').value.trim(),
        template_id: document.getElementById('report-template').value,
        data_source: document.getElementById('report-data-source').value,
        date_range: getReportDateRange(),
        filters: getReportFilters(),
        format: document.getElementById('report-format').value || 'html',
        include_charts: document.getElementById('include-charts').checked,
        include_raw_data: document.getElementById('include-raw-data').checked
    };
}

function getReportDateRange() {
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;
    
    if (startDate && endDate) {
        return {
            start_date: startDate,
            end_date: endDate
        };
    }
    
    // Default to last 30 days
    const end = new Date();
    const start = new Date();
    start.setDate(start.getDate() - 30);
    
    return {
        start_date: start.toISOString().split('T')[0],
        end_date: end.toISOString().split('T')[0]
    };
}

function getReportFilters() {
    const filters = {};
    
    const organization = document.getElementById('report-organization').value.trim();
    if (organization) {
        filters.organization = organization;
    }
    
    const minValue = document.getElementById('min-value').value;
    if (minValue) {
        filters.min_value = parseFloat(minValue);
    }
    
    const maxValue = document.getElementById('max-value').value;
    if (maxValue) {
        filters.max_value = parseFloat(maxValue);
    }
    
    return filters;
}

function validateReportForm(data) {
    if (!data.title) {
        CidadaoAI.utils.showNotification('Por favor, informe um título para o relatório', 'warning');
        document.getElementById('report-title').focus();
        return false;
    }
    
    if (!data.template_id) {
        CidadaoAI.utils.showNotification('Selecione um modelo de relatório', 'warning');
        return false;
    }
    
    return true;
}

function updateDataSourceOptions() {
    const dataSource = document.getElementById('report-data-source').value;
    const orgField = document.getElementById('report-organization');
    
    // Update organization field placeholder based on data source
    if (orgField) {
        const placeholders = {
            'contracts': 'Ex: 26000 (Ministério da Educação)',
            'expenses': 'Ex: 20000 (Presidência da República)',
            'agreements': 'Ex: 86000 (Ministério da Saúde)',
            'biddings': 'Ex: 24000 (Ministério do Trabalho)'
        };
        
        orgField.placeholder = placeholders[dataSource] || 'Código ou nome do órgão';
    }
}

/**
 * Monitor Report Generation
 */
async function monitorReportGeneration(reportId, modal) {
    try {
        let completed = false;
        let attempts = 0;
        const maxAttempts = 120; // 10 minutes with 5-second intervals
        
        while (!completed && attempts < maxAttempts) {
            await new Promise(resolve => setTimeout(resolve, 5000)); // Wait 5 seconds
            
            try {
                const status = await CidadaoAI.api.getReportStatus(reportId);
                
                const percentage = Math.round(status.progress * 100);
                CidadaoAI.utils.updateProgress(
                    percentage,
                    status.status,
                    status.current_section || 'Processando...',
                    `Gerando relatório... (${status.template_name || 'Template'})`
                );
                
                if (status.status === 'completed') {
                    completed = true;
                    CidadaoAI.utils.showNotification('Relatório gerado com sucesso!', 'success');
                    
                    // Auto-close modal after 2 seconds
                    setTimeout(() => {
                        if (modal) modal.hide();
                    }, 2000);
                    
                } else if (status.status === 'failed') {
                    completed = true;
                    CidadaoAI.utils.showNotification('Falha na geração do relatório', 'error');
                    setTimeout(() => {
                        if (modal) modal.hide();
                    }, 3000);
                }
                
            } catch (statusError) {
                console.warn('Failed to get report status:', statusError);
            }
            
            attempts++;
        }
        
        if (!completed) {
            CidadaoAI.utils.showNotification('Relatório demorou mais que o esperado', 'warning');
            if (modal) modal.hide();
        }
        
    } catch (error) {
        console.error('Failed to monitor report generation:', error);
        if (modal) modal.hide();
    }
}

/**
 * Load Reports List
 */
async function loadReportsList() {
    try {
        const container = document.getElementById('reports-list');
        if (!container) return;
        
        CidadaoAI.utils.setElementLoading('reports-list', true);
        
        // Get reports from API
        const reports = await CidadaoAI.api.getReports({ limit: 20 });
        
        // Store data
        reportsData = reports;
        
        // Render reports
        if (reports.length > 0) {
            container.innerHTML = `
                <div class="row">
                    ${reports.map(renderReportCard).join('')}
                </div>
            `;
        } else {
            container.innerHTML = `
                <div class="text-center text-muted py-5">
                    <i class="fas fa-file-alt fa-3x mb-3"></i>
                    <h5>Nenhum relatório encontrado</h5>
                    <p>Gere seu primeiro relatório usando o formulário acima.</p>
                </div>
            `;
        }
        
    } catch (error) {
        console.error('Failed to load reports:', error);
        const container = document.getElementById('reports-list');
        if (container) {
            container.innerHTML = `
                <div class="text-center text-danger py-4">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Erro ao carregar relatórios
                </div>
            `;
        }
    }
}

function renderReportCard(report) {
    const statusBadge = CidadaoAI.utils.getStatusBadge(report.status);
    const generatedAt = CidadaoAI.utils.formatDate(report.generated_at || report.started_at);
    const fileSize = report.file_size ? formatFileSize(report.file_size) : null;
    
    return `
        <div class="col-md-6 col-lg-4 mb-4">
            <div class="card h-100">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h6 class="card-title mb-0">
                            <i class="fas ${getReportIcon(report.template_id)} me-2"></i>
                            ${report.title}
                        </h6>
                        ${statusBadge}
                    </div>
                    
                    <p class="card-text text-muted small">
                        <i class="fas fa-template me-1"></i>
                        ${getTemplateName(report.template_id)}
                    </p>
                    
                    <p class="card-text text-muted small">
                        <i class="fas fa-database me-1"></i>
                        ${formatDataSource(report.data_source)}
                        ${report.date_range ? ` • ${formatDateRange(report.date_range)}` : ''}
                    </p>
                    
                    <p class="card-text">
                        <small class="text-muted">
                            Gerado em ${generatedAt}
                            ${fileSize ? `<br>Tamanho: ${fileSize}` : ''}
                        </small>
                    </p>
                    
                    ${renderReportProgress(report)}
                </div>
                
                <div class="card-footer bg-transparent">
                    ${renderReportActions(report)}
                </div>
            </div>
        </div>
    `;
}

function getReportIcon(templateId) {
    const icons = {
        'investigation_summary': 'fa-search',
        'monthly_analysis': 'fa-calendar-alt',
        'vendor_analysis': 'fa-building',
        'spending_trends': 'fa-chart-line'
    };
    return icons[templateId] || 'fa-file-alt';
}

function getTemplateName(templateId) {
    const template = reportTemplates.find(t => t.id === templateId);
    return template ? template.name : templateId;
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

function formatDateRange(dateRange) {
    if (!dateRange.start_date || !dateRange.end_date) return '';
    
    const start = new Date(dateRange.start_date).toLocaleDateString('pt-BR');
    const end = new Date(dateRange.end_date).toLocaleDateString('pt-BR');
    
    return `${start} - ${end}`;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

function renderReportProgress(report) {
    if (!['pending', 'running'].includes(report.status)) {
        return '';
    }
    
    const progress = Math.round((report.progress || 0) * 100);
    
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

function renderReportActions(report) {
    const actions = [];
    
    if (report.status === 'completed') {
        actions.push(`
            <button class="btn btn-outline-primary btn-sm me-1" onclick="viewReport('${report.report_id}')">
                <i class="fas fa-eye"></i> Ver
            </button>
        `);
        actions.push(`
            <button class="btn btn-outline-success btn-sm me-1" onclick="downloadReport('${report.report_id}', '${report.format}')">
                <i class="fas fa-download"></i> Download
            </button>
        `);
    } else if (['pending', 'running'].includes(report.status)) {
        actions.push(`
            <button class="btn btn-outline-info btn-sm me-1" onclick="monitorReportProgress('${report.report_id}')">
                <i class="fas fa-chart-line"></i> Monitorar
            </button>
        `);
    }
    
    actions.push(`
        <button class="btn btn-outline-danger btn-sm" onclick="deleteReport('${report.report_id}')">
            <i class="fas fa-trash"></i>
        </button>
    `);
    
    return `<div class="btn-group btn-group-sm" role="group">${actions.join('')}</div>`;
}

/**
 * Report Actions
 */
async function viewReport(reportId) {
    try {
        CidadaoAI.utils.showLoading(true);
        
        const report = await CidadaoAI.api.getReport(reportId);
        
        CidadaoAI.utils.showLoading(false);
        
        // Show report in modal
        showReportViewModal(report);
        
    } catch (error) {
        CidadaoAI.utils.showLoading(false);
        CidadaoAI.utils.handleApiError(error, 'view report');
    }
}

function showReportViewModal(report) {
    // Create modal if it doesn't exist
    let modal = document.getElementById('reportViewModal');
    if (!modal) {
        modal = createReportViewModal();
        document.body.appendChild(modal);
    }
    
    // Populate modal content
    const modalTitle = modal.querySelector('.modal-title');
    const modalBody = modal.querySelector('.modal-body');
    
    modalTitle.innerHTML = `
        <i class="fas ${getReportIcon(report.template_id)} me-2"></i>
        ${report.title}
    `;
    
    modalBody.innerHTML = report.content || `
        <div class="text-center text-muted py-4">
            <i class="fas fa-file-alt fa-3x mb-3"></i>
            <h5>Conteúdo não disponível</h5>
            <p>O conteúdo deste relatório não pode ser exibido inline.</p>
            <button class="btn btn-primary" onclick="downloadReport('${report.report_id}', '${report.format}')">
                <i class="fas fa-download me-2"></i>Download do Relatório
            </button>
        </div>
    `;
    
    // Show modal
    const modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();
}

function createReportViewModal() {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'reportViewModal';
    modal.tabIndex = -1;
    
    modal.innerHTML = `
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title"></h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <!-- Content will be populated dynamically -->
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
                </div>
            </div>
        </div>
    `;
    
    return modal;
}

async function downloadReport(reportId, format = 'html') {
    try {
        CidadaoAI.utils.showNotification('Iniciando download...', 'info');
        
        const blob = await CidadaoAI.api.downloadReport(reportId, format);
        
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `relatorio-${reportId}.${format}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        window.URL.revokeObjectURL(url);
        
        CidadaoAI.utils.showNotification('Download concluído!', 'success');
        
    } catch (error) {
        CidadaoAI.utils.handleApiError(error, 'download report');
    }
}

async function deleteReport(reportId) {
    if (!confirm('Tem certeza que deseja excluir este relatório? Esta ação não pode ser desfeita.')) {
        return;
    }
    
    try {
        await CidadaoAI.api.deleteReport(reportId);
        CidadaoAI.utils.showNotification('Relatório excluído com sucesso', 'success');
        
        // Refresh list
        loadReportsList();
        
    } catch (error) {
        CidadaoAI.utils.handleApiError(error, 'delete report');
    }
}

async function monitorReportProgress(reportId) {
    const modal = CidadaoAI.utils.showProgressModal('Monitorando Geração de Relatório');
    await monitorReportGeneration(reportId, modal);
}

/**
 * Bulk Actions
 */
function selectAllReports() {
    const checkboxes = document.querySelectorAll('.report-checkbox');
    const selectAllCheckbox = document.getElementById('select-all-reports');
    
    checkboxes.forEach(checkbox => {
        checkbox.checked = selectAllCheckbox.checked;
    });
    
    updateBulkActions();
}

function updateBulkActions() {
    const selectedReports = document.querySelectorAll('.report-checkbox:checked');
    const bulkActions = document.getElementById('bulk-actions');
    
    if (bulkActions) {
        if (selectedReports.length > 0) {
            bulkActions.classList.remove('d-none');
            document.getElementById('selected-count').textContent = selectedReports.length;
        } else {
            bulkActions.classList.add('d-none');
        }
    }
}

async function bulkDeleteReports() {
    const selectedCheckboxes = document.querySelectorAll('.report-checkbox:checked');
    const reportIds = Array.from(selectedCheckboxes).map(cb => cb.value);
    
    if (reportIds.length === 0) {
        CidadaoAI.utils.showNotification('Nenhum relatório selecionado', 'warning');
        return;
    }
    
    if (!confirm(`Tem certeza que deseja excluir ${reportIds.length} relatório(s)? Esta ação não pode ser desfeita.`)) {
        return;
    }
    
    try {
        CidadaoAI.utils.showLoading(true);
        
        // Delete reports in parallel
        const deletePromises = reportIds.map(id => CidadaoAI.api.deleteReport(id));
        await Promise.allSettled(deletePromises);
        
        CidadaoAI.utils.showLoading(false);
        CidadaoAI.utils.showNotification(`${reportIds.length} relatório(s) excluído(s) com sucesso`, 'success');
        
        // Refresh list
        loadReportsList();
        
    } catch (error) {
        CidadaoAI.utils.showLoading(false);
        CidadaoAI.utils.handleApiError(error, 'bulk delete reports');
    }
}

// Export functions
window.loadReports = loadReports;
window.viewReport = viewReport;
window.downloadReport = downloadReport;
window.deleteReport = deleteReport;
window.monitorReportProgress = monitorReportProgress;
window.selectAllReports = selectAllReports;
window.updateBulkActions = updateBulkActions;
window.bulkDeleteReports = bulkDeleteReports;