```markdown
# Error Rate Alert Runbook

## Alert: API Error Rate > 5%

### Context
- **Threshold**: >5% error rate for 5 minutes
- **Impact**: User-facing API degradation
- **Notification**: #alerts Slack, PagerDuty

### Investigation Checklist
1. **Check recent deployments**
   - Review last 2 hours of deployments
   - Compare timing with alert start

2. **Analyze error distribution**
   ```bash
   # Check error breakdown by endpoint
   grep "HTTP 5" /var/log/api/access.log | awk '{print $7}' | sort | uniq -c
Resource utilization
CPU/Memory usage in Grafana
Database connection pool status
Redis cache hit rate
Common Causes & Solutions
Database timeouts: Scale read replicas
Cache misses: Warm cache or increase memory
Rate limiting: Check if legitimate traffic spike
External service failures: Enable circuit breaker
Escalation
If error rate >10% or not resolved in 15 minutes:

Page engineering manager
Consider triggering rollback
Update status page if customer-facing