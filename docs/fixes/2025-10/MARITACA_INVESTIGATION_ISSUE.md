# Maritaca AI Investigation Issue - Diagnosis Report

## Issue Summary
Investigations are getting stuck at 30% progress (anomaly_detection phase) when using Maritaca AI as the LLM provider.

## Current Status
- **LLM Provider**: Maritaca AI ✅ (configured correctly)
- **API Key**: Configured ✅ (ending in e836)
- **Model**: sabiazinho-3 ✅
- **Provider Initialization**: Success ✅
- **Investigation Progress**: Stuck at 30% ❌

## Test Results

### Configuration Test (PASSED)
```json
{
  "llm_provider": "maritaca",
  "maritaca_api_key": "***e836",
  "model": "sabiazinho-3",
  "initialization": "success"
}
```

### Investigation Test (FAILED)
- Investigation ID: 17ec5bfb-4f77-4a0e-ab88-2b37c592053f
- Status: Running for 2+ minutes
- Progress: 30% (anomaly_detection phase)
- Records Processed: 0
- Anomalies Detected: 0

## Root Cause Analysis

The investigation is stuck at the anomaly detection phase, which is the first phase that makes LLM calls. The issue appears to be:

1. **Timeout Configuration**: The timeout for Maritaca AI calls is set to 30 seconds, but the actual call might be taking longer or failing silently
2. **Model Mismatch**: The system is configured with `sabiazinho-3` but internally uses `mixtral-8x7b-32768` (as seen in debug endpoint)
3. **Error Handling**: Errors in the LLM call might not be properly propagated back to the investigation status

## Possible Solutions

### 1. Immediate Fix - Test with Different Model
The debug endpoint shows `llm_model_name: "mixtral-8x7b-32768"` while Maritaca uses `sabiazinho-3`. This mismatch might be causing issues.

**Action**: Update Railway environment variables:
```bash
LLM_MODEL_NAME=sabiazinho-3
```

### 2. Test API Key Validity
The Maritaca API key might be invalid or have insufficient permissions.

**Action**: Create a simple test script to validate the API key:
```python
import httpx
import json

headers = {
    "Authorization": "Bearer YOUR_MARITACA_API_KEY",
    "Content-Type": "application/json"
}

data = {
    "model": "sabiazinho-3",
    "messages": [{"role": "user", "content": "Olá"}],
    "max_tokens": 50
}

response = httpx.post(
    "https://chat.maritaca.ai/api/chat/completions",
    headers=headers,
    json=data,
    timeout=30
)
print(response.status_code)
print(response.json())
```

### 3. Increase Timeout
The current 30-second timeout might be insufficient for Maritaca AI.

**Files to modify**:
- `src/llm/providers.py`: Increase timeout from 30 to 60 seconds
- `src/services/investigation_service.py`: Increase investigation timeout

### 4. Add Better Error Logging
The current system doesn't log LLM errors properly during investigations.

**Files to modify**:
- `src/agents/zumbi.py`: Add try-catch around LLM calls with detailed logging
- `src/services/investigation_service.py`: Add error details to investigation metadata

## Verification Steps

1. **Check Railway Logs**:
   - Look for timeout errors
   - Look for 401/403 authentication errors
   - Look for "maritaca" related errors

2. **Test Direct API Call**:
   ```bash
   curl -X POST https://chat.maritaca.ai/api/chat/completions \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "model": "sabiazinho-3",
       "messages": [{"role": "user", "content": "Test"}],
       "max_tokens": 50
     }'
   ```

3. **Monitor Investigation**:
   - Create a simple investigation
   - Monitor every 5 seconds
   - Check when exactly it fails

## Recommended Next Steps

1. **Verify API Key**: Test the Maritaca API key directly with curl
2. **Check Model Name**: Ensure LLM_MODEL_NAME=sabiazinho-3 in Railway
3. **Review Logs**: Check Railway logs for specific error messages
4. **Test with Groq**: Temporarily switch to Groq to confirm the rest of the system works
5. **Contact Maritaca**: If API key is valid, contact Maritaca support for rate limits or issues

## Alternative Solution

If Maritaca continues to fail, consider using **Groq** as the primary provider:
- Groq is faster (typically < 2 second response times)
- Better error messages
- More stable API
- Still supports Portuguese reasonably well

To switch to Groq:
```bash
LLM_PROVIDER=groq
LLM_MODEL_NAME=mixtral-8x7b-32768
```

## Current Investigation Status

As of 2025-10-20 14:05 UTC:
- Investigation 17ec5bfb-4f77-4a0e-ab88-2b37c592053f is still running
- Stuck at 30% progress for 3+ minutes
- No errors reported in status endpoint
- Likely experiencing a silent timeout in LLM call
