```markdown
# Blue-Green Deployment Process

## Overview
Zero-downtime deployments using two identical production environments.

## Prerequisites
- [ ] All tests passing in staging
- [ ] Database migrations completed
- [ ] Rollback plan documented

## Deployment Steps

### 1. Prepare Green Environment
```bash
# Deploy to green environment
./deploy.sh --environment=green --version=$NEW_VERSION

# Health check green environment
curl -f https://green.api.company.com/health
2. Route Traffic
# Update load balancer to point to green
aws elbv2 modify-target-group \
  --target-group-arn $TARGET_GROUP_ARN \
  --targets Id=green-instance-1,Port=8080
3. Monitor & Validate
Watch error rates in DataDog
Check logs for anomalies: kubectl logs -f deployment/api
Verify key user flows in New Relic
4. Complete or Rollback
Success: Update DNS to point to green permanently Failure: Route traffic back to blue environment

Rollback Procedure
# Quick rollback (< 30 seconds)
./scripts/rollback.sh --to-blue

# Verify rollback
curl -f https://api.company.com/health