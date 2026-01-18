# 🌿 Project Eirene - Web Dashboard

## Quick Start

The web dashboard is now running and ready to test!

### Access the Dashboard

Open your browser and go to:
```
http://localhost:5001
```

## Features

### 🎯 Interactive Agent Testing

The dashboard provides a beautiful UI to test the Monitor and Strategy agents:

1. **Agent Cards** - Click on any agent card to see its status
   - 🔍 **Monitor Agent** - Ready to test
   - 🧠 **Strategy Agent** - Ready to test
   - 🎬 **Generation Agent** - Coming soon
   - ✅ **Audit Agent** - Coming soon
   - 💾 **Memory Agent** - Coming soon

2. **Test Section** - Run agents with custom or sample data
   - Load pre-configured test samples with one click
   - Enter custom URLs and content
   - Run individual agents or the complete pipeline

3. **Results Display** - See detailed results in real-time
   - Signal detection results (type, severity, community)
   - Therapeutic framework mapping (CBT/DBT)
   - Intervention specifications
   - Complete trace logs for debugging

### 🧪 Testing Options

#### Option 1: Use Sample Data
Click any of the sample buttons:
- **Anxiety - Reddit**: Test anxiety signal detection
- **Burnout - Work Forum**: Test burnout signal detection
- **Isolation - Support Group**: Test isolation signal detection
- **Depression - Mental Health Forum**: Test depression signal detection

#### Option 2: Custom Input
1. Enter a custom URL in the "Source URL" field
2. Enter custom content in the "Content" textarea
3. Click one of the run buttons

### 🚀 Run Buttons

- **🔍 Run Monitor Agent**: Test stress signal detection only
- **🧠 Run Strategy Agent**: Test therapeutic framework mapping only
- **🚀 Run Complete Pipeline**: Test Monitor → Strategy pipeline end-to-end

### 📊 Results

After running an agent, you'll see:

1. **Cycle Information**
   - Unique cycle ID for tracing
   - Number of trace log entries

2. **Monitor Agent Output** (if run)
   - Signal type (anxiety, burnout, isolation, etc.)
   - Severity score (0.0 to 1.0)
   - Community context
   - Source URL

3. **Strategy Agent Output** (if run)
   - Therapeutic framework (CBT or DBT)
   - Recommended techniques
   - Clinical rationale
   - Target emotion
   - Content theme
   - Visual and text guidelines
   - Therapeutic intent

4. **Trace Logs**
   - Complete execution trace
   - Timestamps for each action
   - Agent identifiers
   - Action status

## API Configuration

Your Yutori API key is already configured in the `.env` file:
```
YUTORI_API_KEY=yt_wdvZPjMPHcxhgtMv8K6xaEmoK7svej65w3VdUERJ2ls
```

Other API keys are set to demo values for testing purposes.

## Stopping the Dashboard

To stop the dashboard server:
1. Go to the terminal where it's running
2. Press `Ctrl+C`

Or if running in the background, find and kill the process:
```bash
lsof -ti:5001 | xargs kill
```

## Troubleshooting

### Port Already in Use
If port 5001 is already in use, edit `dashboard.py` and change the port:
```python
app.run(debug=True, host='0.0.0.0', port=5002)  # Change to any available port
```

### Module Not Found Errors
Make sure you're using the virtual environment:
```bash
source .venv/bin/activate  # On macOS/Linux
.venv\Scripts\activate     # On Windows
```

### API Errors
Check that your `.env` file has the correct API keys configured.

## Next Steps

Once you've tested the Monitor and Strategy agents:
1. The Generation Agent will create "Mindful Moment" videos
2. The Audit Agent will validate content quality
3. The Memory Agent will enable self-improvement

Stay tuned for these features!

## Technical Details

- **Framework**: Flask + vanilla JavaScript
- **Styling**: Custom CSS with gradient backgrounds
- **API**: RESTful JSON endpoints
- **Logging**: Complete trace logging to `traces/` directory
- **Real-time**: Async JavaScript for smooth UX

## Support

For issues or questions, check the main README.md or open an issue on GitHub.

---

**Enjoy testing Project Eirene! 🌿**
