/**
 * АСБН - API клиент
 * Разработчик: Голдашевский Н.С., гр. 4331
 */

const API_BASE = 'http://127.0.0.1:8000/api';

class ApiClient {
    constructor() {
        this.token = localStorage.getItem('asbn_token');
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem('asbn_token', token);
    }

    getToken() {
        return this.token;
    }

    clearToken() {
        this.token = null;
        localStorage.removeItem('asbn_token');
    }

    async request(endpoint, options = {}) {
        const url = `${API_BASE}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Ошибка запроса');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Авторизация
    async login(login, password) {
        const data = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ login, password })
        });
        this.setToken(data.access_token);
        return data;
    }

    async register(login, password, email) {
        return await this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ login, password, email })
        });
    }

    async getMe() {
        return await this.request('/auth/me');
    }

    // Мониторинг
    async getTopology() {
        return await this.request('/monitoring/topology');
    }

    async getMeasurements(nodeId = null, limit = 100) {
        const params = new URLSearchParams({ limit });
        if (nodeId) params.append('node_id', nodeId);
        return await this.request(`/monitoring/measurements?${params}`);
    }

    async getNodeStatus() {
        return await this.request('/monitoring/status');
    }

    async getIncidents(limit = 50) {
        return await this.request(`/monitoring/incidents?limit=${limit}`);
    }

    // Прогноз
    async getForecast(nodeId) {
        return await this.request(`/forecast/node/${nodeId}`);
    }

    async getForecastQuality() {
        return await this.request('/forecast/quality');
    }

    async calculateForecast(nodeId, horizonHours = 24) {
        return await this.request('/forecast/calculate', {
            method: 'POST',
            body: JSON.stringify({ 
                node_id: nodeId, 
                horizon_hours: horizonHours 
            })
        });
    }

    // Балансировка
    async getRecommendations() {
        return await this.request('/balancing/recommendations');
    }

    async confirmRecommendation(id) {
        return await this.request(`/balancing/confirm?recommendation_id=${id}`, {
            method: 'POST'
        });
    }

    async rejectRecommendation(id, reason = '') {
        return await this.request(`/balancing/reject?recommendation_id=${id}&reason=${reason}`, {
            method: 'POST'
        });
    }

    async getCommands(limit = 50) {
        return await this.request(`/balancing/commands?limit=${limit}`);
    }

    // Уведомления
    async getNotifications(limit = 50) {
        return await this.request(`/notifications?limit=${limit}`);
    }

    async markNotificationRead(id) {
        return await this.request(`/notifications/${id}/read`, {
            method: 'PUT'
        });
    }

    // Отчёты
    async getReports() {
        return await this.request('/reports');
    }

    async generateReport(reportType, startDate, endDate) {
        return await this.request('/reports/generate', {
            method: 'POST',
            body: JSON.stringify({
                report_type: reportType,
                start_date: startDate,
                end_date: endDate
            })
        });
    }

    // Админ
    async getUsers() {
        return await this.request('/admin/users');
    }

    async getSystemStatus() {
        return await this.request('/admin/system/status');
    }
}

// Глобальный экземпляр
const api = new ApiClient();