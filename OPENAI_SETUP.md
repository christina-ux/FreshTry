# Setting Up OpenAI API Integration

To set up the OpenAI API integration for PolicyEdgeAI, follow these steps:

## 1. Get an OpenAI API Key

1. Go to [OpenAI's platform](https://platform.openai.com/signup)
2. Create an account or sign in
3. Navigate to the [API keys section](https://platform.openai.com/account/api-keys)
4. Click "Create new secret key"
5. Copy the generated API key (it will only be shown once)

## 2. Add the API Key to Your Environment

### Option A: Update the .env File

Edit the `.env` file in the project root and update the OpenAI API key:

```
OPENAI_API_KEY=sk-your-actual-api-key-goes-here
```

Replace `sk-your-actual-api-key-goes-here` with the API key you copied from OpenAI.

### Option B: Set as Environment Variable

You can also set the API key as an environment variable:

```bash
# On macOS/Linux
export OPENAI_API_KEY=sk-your-actual-api-key-goes-here

# On Windows (Command Prompt)
set OPENAI_API_KEY=sk-your-actual-api-key-goes-here

# On Windows (PowerShell)
$env:OPENAI_API_KEY="sk-your-actual-api-key-goes-here"
```

## 3. Test the Integration

Run the test script to verify that the API connection works:

```bash
python test_openai.py
```

If successful, you'll see a message indicating that the API key was found and that the API call succeeded.

## 4. API Usage Notes

- **Costs**: OpenAI charges based on the number of tokens processed. Monitor your usage on the [OpenAI dashboard](https://platform.openai.com/usage).
- **Rate Limits**: The API has rate limits. If you hit them, your requests will be throttled.
- **Model Versions**: PolicyEdgeAI is configured to use GPT-4 Turbo. You can change this in the code if needed.

## 5. Next Steps

After confirming the API works, you can proceed with:

1. Building and pushing Docker images (see `SIMPLIFIED_DEPLOYMENT.md`)
2. Deploying the application (see deployment options)
3. Integrating OpenAI features into the compliance workflow