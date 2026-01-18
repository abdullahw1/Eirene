# Dashboard Usage Guide

## Starting the Dashboard

The Flask server is now running! You can access the dashboard at:

**http://localhost:5001**

## How to Use

### 1. Start the Dashboard Server

The server is already running in the background. If you need to restart it:

```bash
cd Eirene
bash start_dashboard.sh
```

### 2. Open the Dashboard

Open your web browser and navigate to:
- **http://localhost:5001**

### 3. Using the Monitor Agent Flow

1. **Click on "Monitor Agent"** card
2. **Click "Start Monitoring"** button
3. **Choose your data mode:**
   - **OFF (Curated Data)**: Instant results, perfect for demos ✅ RECOMMENDED
   - **ON (Live Data)**: Uses OpenAI to generate realistic data (~5-10 seconds)

4. **View Trending Topics**: You'll see 6 trending mental health topics with:
   - Severity indicators
   - Mention counts
   - Platform distribution

5. **Click any topic** to generate a therapeutic intervention video

### 4. Data Modes

#### Curated Data (Default - Recommended for Demos)
- ✅ Instant results
- ✅ Always works
- ✅ Perfect for presentations
- Toggle is OFF by default

#### Live Data (OpenAI)
- Uses OpenAI GPT-4 to generate realistic trending data
- Takes 5-10 seconds
- Requires OPENAI_API_KEY in .env file
- Toggle ON to enable

## Features

### Monitor Agent
- Real-time mental health signal detection
- Trending topics across Reddit, Twitter, TikTok, Instagram
- Platform distribution analytics

### Strategy Agent
- Maps signals to CBT/DBT therapeutic frameworks
- Clinical analysis and rationale

### Generation Agent
- Creates "Mindful Moment" videos
- Instant playback mode for demos

## Troubleshooting

### "Failed to fetch" Error
- **Solution**: Make sure the Flask server is running
- Run: `bash start_dashboard.sh` in the Eirene directory

### Server Not Starting
- Check if port 5001 is already in use
- Make sure virtual environment is activated
- Check that all dependencies are installed: `pip install -r requirements.txt`

### Live Data Not Working
- Make sure OPENAI_API_KEY is set in your .env file
- Check that openai package is installed: `pip install openai`

## Current Status

✅ Server is running on http://localhost:5001
✅ Curated data mode working perfectly
✅ Live data mode (OpenAI) working
✅ All endpoints functional

## API Endpoints

- `GET /` - Dashboard homepage
- `GET /api/agents` - List of available agents
- `POST /api/monitor/trending` - Get trending mental health topics
- `POST /api/topic/reasons` - Get specific reasons for a topic
- `POST /api/instant-playback` - Get pre-generated video
- `POST /api/run/pipeline` - Run full agent pipeline

## Notes

- The dashboard uses curated data by default for instant, reliable demos
- Live mode uses OpenAI (not TinyFish) to generate realistic data
- For demos, we recommend keeping the toggle OFF for instant results
- The server logs all requests to the console for debugging
