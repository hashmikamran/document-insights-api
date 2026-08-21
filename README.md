# Document Insights API

A high-performance, asynchronous backend service built with Python 3.11+, FastAPI, MongoDB, and Redis. It handles document processing, simulated AI summarization, content caching, and per-user rate limiting.

---

## 🚀 Features

- **Asynchronous Worker**: Background processing pipeline with simulated latency (10–30s) and controlled ~10% failure rates for error resilience testing.
- **Per-User Rate Limiting**: Restricts users to a maximum of 3 active (`queued` / `processing`) jobs concurrently using Redis.
- **Content-Based Caching**: Computes SHA-256 hashes of input content to immediately serve cached summaries for duplicate submissions.
- **Health Checks & Monitoring**: `/health` endpoint to monitor local MongoDB and Redis connectivity.
- **Data Optimization**: Indexed MongoDB schemas (`user_id` + `status`, `content_hash`) for fast pagination and lookup.

---

## 🛠️ Local Setup & Execution

### 1. Prerequisites
Ensure you have the following services installed and running natively on your local machine:
- **Python**: 3.11 or higher
- **MongoDB**: Default port `27017`
- **Redis**: Default port `6379`

---

### 2. Installation & Configuration

1. **Clone & Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate