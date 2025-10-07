# 🐉 DragonForce Bot - Xray WhatsApp VPN Manager

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116.2-009688.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful WhatsApp chatbot built with FastAPI that automates VPN configuration management through Marzban panel integration. Users can create, manage, and monitor their VPN configs through an intuitive WhatsApp interface with support for multiple Sri Lankan telecom packages.

## ✨ Features

- **Interactive WhatsApp Menu System** - Conversational bot interface with stage-based navigation
- **Multi-Provider VPN Configs** - Support for Dialog, Mobitel, Airtel, Hutch, and SLT packages
- **Real-time Usage Tracking** - Monitor data consumption and expiry dates
- **User Management** - Ban/unban users, config limits, and persistent storage
- **Redis Caching** - Fast session management and Marzban token caching
- **Rate Limiting** - Built-in protection against spam and abuse
- **Webhook Integration** - Seamless WhatsApp message processing via Wasender API

## 🏗️ Architecture

```
WhatsApp Message → Wasender Webhook → FastAPI Server → Redis Cache
                                           ↓
Supabase Database ← Config Management ← Marzban Panel API
                                           ↓
                    Response → Wasender API → WhatsApp User
```

### Component Overview

- **FastAPI Server** (`bot/server.py`) - Main application entry point
- **Webhook Router** (`bot/core/routes.py`) - Message processing and stage management
- **Supabase Handlers** (`bot/supabase/`) - User data and config storage
- **Marzban Integration** (`bot/core/marzban_handlers.py`) - VPN config creation and monitoring
- **Redis Cache** (`bot/cache/redis.py`) - Session state and token management
- **Message Utils** (`bot/core/utils.py`) - WhatsApp message sending utilities

## 🛠️ Tech Stack

- **Backend**: FastAPI 0.116.2, Python 3.13+
- **Database**: Supabase (PostgreSQL)
- **Cache**: Redis 6.4.0
- **VPN Management**: Marzban Panel API
- **WhatsApp Integration**: Wasender API
- **Environment**: python-decouple for config management

## 📋 Prerequisites

Before running the bot, ensure you have:

- Python 3.13 or higher
- Redis server instance
- Supabase project with PostgreSQL database
- Marzban panel with API access
- Wasender account for WhatsApp API
- Domain/server for webhook endpoints (HTTPS required)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/dumiduzee/XrayWa-Bot-.git
cd XrayWa-Bot-
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

Using Poetry (recommended):
```bash
pip install poetry
poetry install
```

Or using pip:
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
REDIS_USERNAME=default
REDIS_EXPIRE_TIME=3600

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_service_role_key

# Wasender API Configuration
WASENDER_BASE_URL=https://api.wasender.co
WASENDER_API_KEY=your_wasender_api_key

# Marzban Panel Configuration
MARZBAN_BASE_DOMAIN=your-marzban-domain.com
MARZBAN_PORT=443
MARZBAN_USERNAME=admin
MARZBAN_PASSWORD=your_marzban_password

# Rate Limiting
RATE_LIMITER_REDIS=1
RATE_LIMITER_WINDOW=60
RATE_LIMITER_LIMIT=10
```

### 5. Run the Application

```bash
uvicorn bot.server:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000` with automatic docs at `/docs`.

## 🗄️ Supabase Database Setup

Create a `botusers` table in your Supabase project:

```sql
CREATE TABLE botusers (
    id SERIAL PRIMARY KEY,
    phoneNumber VARCHAR(20) UNIQUE NOT NULL,
    config TEXT,
    marzbanUsername VARCHAR(100),
    configCount INTEGER DEFAULT 0,
    package VARCHAR(50),
    isBanned BOOLEAN DEFAULT FALSE,
    createdAt TIMESTAMP DEFAULT NOW(),
    updatedAt TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_botusers_phone ON botusers(phoneNumber);
CREATE INDEX idx_botusers_username ON botusers(marzbanUsername);
```

### Required Supabase Policies

Ensure your service role key has full access, or create appropriate RLS policies:

```sql
-- Enable RLS
ALTER TABLE botusers ENABLE ROW LEVEL SECURITY;

-- Policy for service role
CREATE POLICY "Service role full access" ON botusers
FOR ALL USING (auth.role() = 'service_role');
```

## 📱 Conversation Flow

### Main Menu Options

When users send `start`, they receive the main menu with these options:

1. **Create Config** ✨ - Choose from 6 telecom packages
2. **Get All Configs** 📂 - View existing configurations
3. **Delete Config** 🗑️ - Remove current config with confirmation
4. **Get Usage** 📊 - Check data usage and expiry
5. **Package Details** 📦 - View all available packages and pricing

### Package Types

The bot supports these Sri Lankan telecom packages:

- **Dialog Router** (724 zoom package)
- **Mobitel Zoom** (222 zoom package)
- **Airtel Zoom** (215 zoom package)
- **Hutch Gaming** (505 gaming package)
- **SLT Zoom** (495 zoom package)
- **SLT Netflix** (1990 netflix package)

### Stage Management

User conversations are tracked through Redis-cached stages:

- `START` - Initial state, shows main menu
- `MAIN_MENU` - Waiting for main menu selection
- `MAIN_MENU_01_STAGE` - Config type selection
- `MAIN_MENU_03_STAGE` - Delete confirmation

## 🔌 API Reference

### Webhook Endpoint

**POST** `/api/webhook`

Receives WhatsApp message events from Wasender.

#### Request Schema

```json
{
  "event": "messages.upsert",
  "sessionId": "session_id",
  "data": {
    "messages": {
      "key": {
        "remoteJid": "94771234567@s.whatsapp.net",
        "fromMe": false,
        "id": "message_id"
      },
      "messageTimestamp": 1696723200,
      "pushName": "User Name",
      "message": {
        "conversation": "start"
      }
    }
  },
  "timestamp": 1696723200
}
```

#### Response

Returns `200 OK` for successful processing. Bot responses are sent via Wasender API.

## 🔄 Redis Usage

The bot uses Redis for:

### Session Management
- **Stage Keys**: `stage_{phone_number}` - Current conversation state
- **TTL**: Configurable via `REDIS_EXPIRE_TIME` (default: 1 hour)

### Token Caching
- **Marzban Token**: `marzban_token` - Cached for 30 minutes
- **Rate Limiting**: `rate_limit_{phone}_{endpoint}` - Request counting

### Clearing Cache

```bash
# Clear all stages
redis-cli --scan --pattern "stage_*" | xargs redis-cli del

# Clear specific user
redis-cli del "stage_94771234567"
```

## 🔧 External Service Configuration

### Wasender Webhook Setup

1. Log into your Wasender dashboard
2. Navigate to Webhooks section
3. Set webhook URL to: `https://your-domain.com/api/webhook`
4. Enable message events
5. Save and test the connection

### Marzban Panel Requirements

Ensure your Marzban panel has:

- API access enabled
- Admin user credentials configured
- Required inbound configurations named:
  - `Dialog 443`
  - `MOBITEL`
  - `Airtel`
  - `Hutch`
  - `Slt Zoom`
  - `Slt Netflix`

## 🧪 Testing Locally

### 1. Start the Development Server

```bash
uvicorn bot.server:app --reload --port 8000
```

### 2. Expose via Tunnel (for webhook testing)

```bash
# Using ngrok
ngrok http 8000

# Using cloudflared
cloudflared tunnel --url http://localhost:8000
```

### 3. Test with Sample Payload

```bash
curl -X POST "http://localhost:8000/api/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "event": "messages.upsert",
    "sessionId": "test_session",
    "data": {
      "messages": {
        "key": {
          "remoteJid": "94771234567@s.whatsapp.net",
          "fromMe": false,
          "id": "test_message"
        },
        "messageTimestamp": 1696723200,
        "pushName": "Test User",
        "message": {
          "conversation": "start"
        }
      }
    },
    "timestamp": 1696723200
  }'
```

## 🚨 Troubleshooting

### Common Issues

#### Supabase Connection Errors
```
Error: Invalid API key or URL
```
**Solution**: Verify `SUPABASE_URL` and `SUPABASE_KEY` in `.env`. Use service role key, not anon key.

#### Redis Connection Failed
```
ConnectionError: Connection refused
```
**Solution**: Ensure Redis server is running and credentials are correct.

#### Marzban Token Expired
```
401 Unauthorized from Marzban API
```
**Solution**: Token auto-refreshes, but check Marzban credentials and network access.

#### Wasender API Errors
```
Failed to send message: 401 Unauthorized
```
**Solution**: Verify `WASENDER_API_KEY` and ensure account has sufficient credits.

### Debug Mode

Enable debug logging by setting environment:

```bash
export UVICORN_LOG_LEVEL=debug
uvicorn bot.server:app --log-level debug
```

### Health Checks

Check service health:

```bash
# API health
curl http://localhost:8000/docs

# Redis connection
redis-cli ping

# Supabase connection
curl -H "Authorization: Bearer YOUR_KEY" \
     "https://your-project.supabase.co/rest/v1/botusers?select=count"
```

## 🚀 Deployment

### Environment Considerations

- **HTTPS Required**: Wasender webhooks require SSL/TLS
- **Redis Persistence**: Configure Redis with appropriate persistence settings
- **Database Connections**: Use connection pooling for production
- **Rate Limiting**: Monitor and adjust limits based on usage

### Docker Deployment (Optional)

```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "bot.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Recommendations

- Use a process manager like PM2 or supervisord
- Set up proper logging and monitoring
- Configure backup strategies for Supabase
- Implement health checks and auto-restart
- Use environment-specific configuration files

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Credits

- **FastAPI** - Modern Python web framework
- **Supabase** - Backend-as-a-Service platform
- **Marzban** - Xray configuration management panel
- **Redis** - In-memory data structure store
- **Wasender** - WhatsApp Business API platform

---

**Developed by [@dumiduzee](https://github.com/dumiduzee)**

For support or feature requests, please open an issue on GitHub.
