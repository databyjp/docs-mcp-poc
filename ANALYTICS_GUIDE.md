# Analytics Guide: Analyzing MCP Usage in Google Cloud Logging

This guide shows you how to analyze usage of your Weaviate documentation MCP server deployed on Cloud Run.

## What's Being Logged

Your MCP server now logs the following events as structured JSON:

### Tool Calls (search_chunks, search_documents)
```json
{
  "timestamp": "2025-10-26T10:30:00",
  "level": "INFO",
  "message": "Tool execution completed",
  "product": "weaviate",
  "event_type": "tool_call",
  "tool_name": "search_chunks",
  "query": "how to create a collection",
  "limit": 5,
  "duration_ms": 123.45,
  "result_count": 5,
  "status": "success"
}
```

### Resource Access (doc:// fetches)
```json
{
  "timestamp": "2025-10-26T10:31:00",
  "level": "INFO",
  "message": "Resource access completed",
  "product": "weaviate",
  "event_type": "resource_access",
  "resource_name": "fetch_document_by_url",
  "url": "https://docs.weaviate.io/weaviate/manage-data/collections",
  "duration_ms": 89.23,
  "result_size_chars": 15234,
  "status": "success"
}
```

## Accessing Logs in Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to **Logging** > **Logs Explorer**
3. Select your project
4. Filter by your Cloud Run service name

## Key Analytics Queries

### 1. How Often Is It Being Used?

**Total tool calls over time:**
```
resource.type="cloud_run_revision"
jsonPayload.event_type="tool_call"
jsonPayload.status="success"
```

**Daily usage breakdown:**
```
resource.type="cloud_run_revision"
jsonPayload.event_type="tool_call"
jsonPayload.status="success"
```
Then click **"Create Metric"** > Set aggregation to **COUNT** > Group by **day**

**Usage by tool type:**
```
resource.type="cloud_run_revision"
jsonPayload.event_type="tool_call"
```
Then group by `jsonPayload.tool_name`

### 2. How Many Users?

Since MCP runs on Cloud Run with HTTP transport, you can identify unique users by IP address:

**Unique IPs accessing the service:**
```
resource.type="cloud_run_revision"
jsonPayload.event_type="tool_call"
```
Then create a metric with **COUNT DISTINCT** on `httpRequest.remoteIp`

**Note:** For more accurate user counting, you'd need to implement API keys or authentication headers.

### 3. What Queries Are Being Run?

**All search queries:**
```
resource.type="cloud_run_revision"
jsonPayload.event_type="tool_call"
jsonPayload.query!=""
```

**Most common queries (manual analysis):**
```
resource.type="cloud_run_revision"
jsonPayload.event_type="tool_call"
jsonPayload.query!=""
```
Export logs to BigQuery (see below) for SQL-based analysis

**Failed queries (to identify UX issues):**
```
resource.type="cloud_run_revision"
jsonPayload.event_type="tool_call"
jsonPayload.status="error"
```

**Slow queries (performance monitoring):**
```
resource.type="cloud_run_revision"
jsonPayload.event_type="tool_call"
jsonPayload.duration_ms>1000
```

## Creating Log-Based Metrics

For persistent tracking, create log-based metrics:

1. In Logs Explorer, click **"More Actions"** > **"Create log-based metric"**
2. Choose **Counter** for counting events or **Distribution** for duration analysis

### Recommended Metrics

**1. Total MCP Requests (Counter)**
- Filter: `jsonPayload.event_type="tool_call" AND jsonPayload.status="success"`
- Metric name: `mcp_tool_calls_total`

**2. Query Latency (Distribution)**
- Filter: `jsonPayload.event_type="tool_call"`
- Value field: `jsonPayload.duration_ms`
- Metric name: `mcp_query_duration_ms`

**3. Error Rate (Counter)**
- Filter: `jsonPayload.event_type="tool_call" AND jsonPayload.status="error"`
- Metric name: `mcp_errors_total`

## Exporting to BigQuery for Advanced Analysis

For SQL-based analysis (e.g., "what are the top 10 most common queries?"), export logs to BigQuery:

1. Go to **Logging** > **Log Router**
2. Click **"Create Sink"**
3. Choose **BigQuery dataset** as destination
4. Apply filter:
   ```
   resource.type="cloud_run_revision"
   jsonPayload.event_type="tool_call"
   ```

### Example BigQuery Queries

**Top 10 most common queries:**
```sql
SELECT
  JSON_VALUE(jsonPayload.query) as query,
  COUNT(*) as frequency
FROM `your-project.your_dataset.cloud_run_logs`
WHERE JSON_VALUE(jsonPayload.event_type) = "tool_call"
  AND JSON_VALUE(jsonPayload.query) IS NOT NULL
GROUP BY query
ORDER BY frequency DESC
LIMIT 10
```

**Daily active users (by IP):**
```sql
SELECT
  DATE(timestamp) as date,
  COUNT(DISTINCT httpRequest.remoteIp) as unique_users
FROM `your-project.your_dataset.cloud_run_logs`
WHERE JSON_VALUE(jsonPayload.event_type) = "tool_call"
GROUP BY date
ORDER BY date DESC
```

**Average query latency over time:**
```sql
SELECT
  DATE(timestamp) as date,
  AVG(CAST(JSON_VALUE(jsonPayload.duration_ms) AS FLOAT64)) as avg_latency_ms
FROM `your-project.your_dataset.cloud_run_logs`
WHERE JSON_VALUE(jsonPayload.event_type) = "tool_call"
  AND JSON_VALUE(jsonPayload.status) = "success"
GROUP BY date
ORDER BY date DESC
```

## Setting Up Alerts

To get notified about important events:

1. Go to **Monitoring** > **Alerting**
2. Click **"Create Policy"**
3. Example alert conditions:
   - **High error rate**: `mcp_errors_total` > 10/minute
   - **No usage**: `mcp_tool_calls_total` = 0 for 1 hour (service down?)
   - **Slow queries**: 95th percentile of `mcp_query_duration_ms` > 2000ms

## Creating a Dashboard

1. Go to **Monitoring** > **Dashboards** > **Create Dashboard**
2. Add charts for:
   - **Request rate**: Line chart of `mcp_tool_calls_total`
   - **Error rate**: Line chart of `mcp_errors_total`
   - **Latency**: Heatmap of `mcp_query_duration_ms`
   - **Top queries**: Table widget (requires BigQuery export)

## Quick Summary Commands

### View last 100 queries:
```
resource.type="cloud_run_revision"
jsonPayload.query!=""
```
Set time range to "Last 1 hour" or "Last 24 hours"

### Count queries in last 7 days:
Use the query above, set time range to "Last 7 days", then look at the count in the histogram.

### Check service health:
```
resource.type="cloud_run_revision"
jsonPayload.event_type="server_ready"
```
Should see recent startup logs if service is healthy.

## Privacy Considerations

Current implementation logs:
- ✅ Query text (what users are searching for)
- ✅ IP addresses (via Cloud Run default logging)
- ✅ Timestamps

If you want to anonymize:
- **Hash IP addresses**: Modify Cloud Run logging config
- **Redact PII from queries**: Add a filter in `logging_utils.py` to detect/redact sensitive patterns

## Next Steps

1. **Set up BigQuery export** if you want SQL-based analysis
2. **Create a dashboard** with your key metrics
3. **Set up alerts** for errors or downtime
4. **Review logs weekly** to understand usage patterns

For questions, see the GCP Cloud Logging documentation:
https://cloud.google.com/logging/docs
