# 🔔 Sistema de Notificações Push - Ideia Futura

**Status**: 💡 Ideia/Planejamento  
**Prioridade**: Baixa  
**Complexidade**: Média  
**Data**: Setembro 2025

## 📋 Visão Geral

Sistema de notificações push para alertar usuários sobre eventos importantes mesmo quando não estão ativamente usando o app.

## 🎯 Casos de Uso

### 1. Notificações de Anomalias
- **Trigger**: Nova anomalia detectada com severidade alta
- **Conteúdo**: "⚠️ Anomalia detectada: Contrato 300% acima da média"
- **Ação**: Abrir investigação específica

### 2. Investigações Concluídas
- **Trigger**: Investigação finalizada
- **Conteúdo**: "✅ Investigação concluída: 15 anomalias encontradas"
- **Ação**: Ver relatório

### 3. Alertas de Threshold
- **Trigger**: Métrica ultrapassa limite configurado
- **Conteúdo**: "📊 Alerta: Gastos do Ministério X aumentaram 150%"
- **Ação**: Iniciar nova investigação

### 4. Atualizações do Sistema
- **Trigger**: Novos dados disponíveis
- **Conteúdo**: "🔄 Novos contratos disponíveis para análise"
- **Ação**: Ver novidades

## 🛠️ Arquitetura Proposta

### 1. **Backend Components**

```python
# src/services/notification_service.py
class NotificationService:
    async def send_push(
        user_id: str,
        title: str,
        body: str,
        data: Dict[str, Any],
        priority: str = "normal"
    ):
        # Lógica para enviar push
        pass
    
    async def register_device(
        user_id: str,
        device_token: str,
        platform: str  # 'web', 'ios', 'android'
    ):
        # Registrar dispositivo
        pass
```

### 2. **Database Schema**

```sql
-- Tabela de dispositivos
CREATE TABLE user_devices (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    device_token VARCHAR(255) UNIQUE,
    platform VARCHAR(20),
    created_at TIMESTAMP,
    last_seen TIMESTAMP,
    active BOOLEAN DEFAULT true
);

-- Tabela de preferências
CREATE TABLE notification_preferences (
    user_id UUID PRIMARY KEY,
    anomalies BOOLEAN DEFAULT true,
    investigations BOOLEAN DEFAULT true,
    reports BOOLEAN DEFAULT true,
    threshold_alerts BOOLEAN DEFAULT true,
    quiet_hours_start TIME,
    quiet_hours_end TIME
);
```

### 3. **API Endpoints**

```python
# Registrar dispositivo
POST /api/v1/notifications/register
{
    "device_token": "FCM_or_APNS_token",
    "platform": "android|ios|web"
}

# Configurar preferências
PUT /api/v1/notifications/preferences
{
    "anomalies": true,
    "investigations": true,
    "quiet_hours": {
        "start": "22:00",
        "end": "08:00"
    }
}

# Histórico de notificações
GET /api/v1/notifications/history?limit=50
```

## 📱 Implementação por Plataforma

### Web (PWA)
```javascript
// Service Worker
self.addEventListener('push', event => {
    const data = event.data.json();
    
    self.registration.showNotification(data.title, {
        body: data.body,
        icon: '/icon-192.png',
        badge: '/badge-72.png',
        data: data.data,
        actions: [
            { action: 'view', title: 'Ver' },
            { action: 'dismiss', title: 'Ignorar' }
        ]
    });
});
```

### Mobile (React Native)
```typescript
import messaging from '@react-native-firebase/messaging';

// Solicitar permissão
async function requestPermission() {
    const authStatus = await messaging().requestPermission();
    const enabled = authStatus === messaging.AuthorizationStatus.AUTHORIZED;
    
    if (enabled) {
        const token = await messaging().getToken();
        await registerDevice(token);
    }
}

// Lidar com notificações
messaging().onMessage(async remoteMessage => {
    // Notificação em foreground
    showInAppNotification(remoteMessage);
});

messaging().setBackgroundMessageHandler(async remoteMessage => {
    // Notificação em background
    await processBackgroundTask(remoteMessage);
});
```

## 🔧 Configuração

### Firebase Cloud Messaging (FCM)
```json
// google-services.json / GoogleService-Info.plist
{
    "project_info": {
        "project_id": "cidadao-ai",
        "firebase_url": "https://cidadao-ai.firebaseio.com",
        "storage_bucket": "cidadao-ai.appspot.com"
    }
}
```

### Web Push VAPID Keys
```python
# .env
VAPID_PUBLIC_KEY=BKj3...
VAPID_PRIVATE_KEY=4kX9...
VAPID_EMAIL=push@cidadao.ai
```

## 📊 Estratégias de Engajamento

### 1. **Smart Notifications**
- Agrupar notificações similares
- Respeitar quiet hours
- Frequência máxima por dia
- Relevância baseada em histórico

### 2. **Rich Notifications**
```javascript
{
    title: "Nova Anomalia Detectada",
    body: "Contrato suspeito no Ministério da Saúde",
    image: "https://api.cidadao.ai/charts/anomaly-preview.png",
    actions: [
        { action: "investigate", title: "Investigar" },
        { action: "ignore", title: "Ignorar" },
        { action: "report", title: "Reportar" }
    ],
    data: {
        investigation_id: "INV-2025-123",
        severity: "high",
        type: "price_anomaly"
    }
}
```

### 3. **Personalização**
- Horários preferenciais
- Tipos de alerta
- Severidade mínima
- Canais (push, email, SMS)

## 🎯 Métricas de Sucesso

### KPIs
- **Opt-in rate**: % usuários com push ativo
- **CTR**: % clicks nas notificações
- **Churn**: % desativações após push
- **Engagement**: Ações após notificação

### Analytics
```python
# Rastrear eventos
track_notification_event({
    "event": "notification_sent",
    "user_id": user_id,
    "type": "anomaly_alert",
    "severity": "high",
    "delivered": True,
    "clicked": False,
    "action_taken": None
})
```

## 🚨 Considerações

### Privacidade
- Não incluir dados sensíveis no push
- Criptografar tokens de dispositivo
- Permitir opt-out fácil
- Conformidade com LGPD

### Performance
- Rate limiting por usuário
- Batch de notificações
- Retry com backoff
- Fallback para email

### UX
- Não ser intrusivo
- Valor claro na notificação
- Deep linking correto
- Preview antes de ativar

## 🔮 Roadmap Sugerido

### Fase 1: MVP (2 semanas)
- [ ] Backend básico
- [ ] Web Push (PWA)
- [ ] Notificações de anomalias
- [ ] Preferências simples

### Fase 2: Mobile (2 semanas)
- [ ] FCM integration
- [ ] iOS/Android support
- [ ] Rich notifications
- [ ] Deep linking

### Fase 3: Inteligência (1 mês)
- [ ] ML para relevância
- [ ] Agrupamento smart
- [ ] A/B testing
- [ ] Analytics completo

### Fase 4: Expansão (futuro)
- [ ] Email fallback
- [ ] SMS para críticos
- [ ] Webhook para integrações
- [ ] API pública

## 💰 Estimativa de Custos

### Firebase Cloud Messaging
- **Free tier**: 1M dispositivos
- **Custo**: Gratuito para nosso volume

### Infraestrutura
- **Redis**: +5% uso (queue)
- **Bandwidth**: +10% (push payload)
- **Storage**: +1GB (histórico)

### Total Estimado
- **Desenvolvimento**: 6 semanas
- **Custo mensal**: +R$ 50/mês
- **ROI**: +25% engajamento

---

**Nota**: Esta é uma proposta conceitual. A implementação real deve considerar os requisitos específicos do projeto e feedback dos usuários.