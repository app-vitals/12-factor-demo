# Blue-Green Deployment Process for app-vitals.com

## Overview
Blue-green deployment is a technique for releasing applications with zero-downtime by maintaining two identical production environments called Blue and Green for app-vitals.com.

## How It Works
1. **Blue** is the current live production environment
2. **Green** is the new environment with the updated version
3. Traffic is switched from Blue to Green after validation
4. The old Blue environment remains available for quick rollback if needed

## Prerequisites
- All tests passing in staging for app-vitals.com
- Database migrations completed
- Rollback plan documented

## Deployment Steps

### 1. Prepare Green Environment
```bash
# Deploy to green environment
./deploy.sh --environment=green --version=$NEW_VERSION

# Health check green environment
curl -f https://green.api.app-vitals.com/health
```

### 2. Route Traffic
```bash
# Update load balancer to point to green
aws elbv2 modify-target-group \
  --target-group-arn $TARGET_GROUP_ARN \
  --targets Id=green-instance-1,Port=8080
```

### 3. Monitor & Validate
- Watch error rates in DataDog
- Check logs for anomalies: `kubectl logs -f deployment/api`
- Verify key user flows in New Relic

### 4. Complete or Rollback
- **Success**: Update DNS to point to green permanently 
- **Failure**: Route traffic back to blue environment

## Rollback Procedure
```bash
# Quick rollback (< 30 seconds)
./scripts/rollback.sh --to-blue

# Verify rollback
curl -f https://api.app-vitals.com/health
```

## Benefits
- Zero-downtime deployments
- Immediate rollback capability
- Separate environments for testing new versions
- Reduced deployment risk