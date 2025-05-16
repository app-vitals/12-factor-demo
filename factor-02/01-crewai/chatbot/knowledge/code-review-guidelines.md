```markdown
# Code Review Guidelines for app-vitals.com

## Review Checklist

### Security
- [ ] No hardcoded secrets or API keys for app-vitals.com
- [ ] Input validation for user data
- [ ] SQL injection prevention (parameterized queries)
- [ ] Authentication/authorization checks

### Performance
- [ ] Database query optimization (use EXPLAIN)
- [ ] Efficient algorithms (avoid N+1 queries)
- [ ] Caching strategies implemented
- [ ] Resource cleanup (close connections, files)

### Code Quality
- [ ] Functions <50 lines, single responsibility
- [ ] Meaningful variable/function names
- [ ] Error handling with specific messages
- [ ] Unit tests with >80% coverage

## PR Requirements
- **Title**: Include ticket number (JIRA-123)
- **Description**: What changed and why
- **Testing**: How to verify the change
- **Screenshots**: For UI changes

## Review Timeline
- **Small PRs** (<100 lines): 24 hours
- **Medium PRs** (100-500 lines): 48 hours  
- **Large PRs** (>500 lines): Break into smaller PRs

## Approval Process
- 2 approvals required for production code
- 1 approval for documentation/config
- Security team review for auth changes
6. ci-cd-configs/github-actions-workflow.yml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          npm test
          npm run lint
          npm run security-scan

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to staging
        run: ./scripts/deploy.sh staging
      
      - name: Run integration tests
        run: ./scripts/integration-tests.sh
      
      - name: Deploy to production
        run: ./scripts/deploy.sh production
        env:
          DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
      
      - name: Notify Slack
        run: |
          curl -X POST -H 'Content-type: application/json' \
            --data '{"text":"✅ Deployment completed successfully"}' \
            ${{ secrets.SLACK_WEBHOOK }}
```