# AI Configuration for Pricing Intelligence Platform

## Environment Variables for AI Integration

To enable real AI-powered insights, set one or more of the following environment variables:

### OpenAI Integration
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

### Azure OpenAI Integration
```bash
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com"
export AZURE_OPENAI_KEY="your-azure-openai-key-here"
```

### Anthropic Claude Integration
```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key-here"
```

## Configuration Priority

The system will automatically detect and use the first available provider in this order:
1. OpenAI (if OPENAI_API_KEY is set)
2. Azure OpenAI (if both AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY are set)
3. Anthropic Claude (if ANTHROPIC_API_KEY is set)
4. Mock/Local generation (if no API keys are available)

## Setting Environment Variables

### For Development (Linux/Mac)
```bash
# Add to your ~/.bashrc or ~/.zshrc
export OPENAI_API_KEY="sk-your-key-here"

# Or set for current session only
export OPENAI_API_KEY="sk-your-key-here"
```

### For Production Deployment
```bash
# In your deployment script or environment
export OPENAI_API_KEY="sk-your-key-here"

# Or use a .env file (not recommended for production)
echo "OPENAI_API_KEY=sk-your-key-here" >> .env
```

### For Docker Deployment
```dockerfile
ENV OPENAI_API_KEY="sk-your-key-here"
```

## Testing AI Configuration

You can test your AI configuration using the insights config endpoint:
```bash
curl http://localhost:5001/api/insights-config
```

This will return:
- Current provider being used
- Model name
- Whether mock mode is active
- Available providers based on configured API keys

## API Key Security

**Important Security Notes:**
- Never commit API keys to version control
- Use environment variables or secure secret management
- Rotate API keys regularly
- Monitor API usage and costs
- Set usage limits on your AI provider accounts

## Cost Considerations

AI API calls have associated costs:
- **OpenAI GPT-4**: ~$0.03-0.06 per 1K tokens
- **Azure OpenAI**: Similar to OpenAI pricing
- **Anthropic Claude**: ~$0.015-0.075 per 1K tokens

Each vehicle insight generation typically uses 500-1500 tokens, so costs are approximately:
- $0.015-0.09 per vehicle insight
- $15-90 per 1000 vehicle insights

## Fallback Behavior

If no AI API keys are configured or if API calls fail:
- The system automatically falls back to enhanced mock insights
- Mock insights are still intelligent and data-driven
- No functionality is lost, but insights may be less nuanced
- All API endpoints continue to work normally

## Model Selection

Default models used:
- **OpenAI**: GPT-4 (most capable, higher cost)
- **Azure OpenAI**: GPT-4 (enterprise features)
- **Anthropic**: Claude-3-Sonnet (good balance of capability and cost)

You can modify model selection in `src/services/enhanced_insights.py` if needed.

