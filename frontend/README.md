# Document Intelligence - Frontend

Streamlit-based frontend for the LangExtract POC.

## Features

- 📤 Easy file upload (PDF, DOCX, TXT)
- 📊 Real-time analysis with progress indicators
- 📄 Embedded PDF report viewer
- 🔍 Interactive entity explorer
- 💾 Download options (PDF & JSONL)
- 📱 Responsive design
- 🎨 Professional UI

## Quick Start

### Run Frontend Only

```bash
# Windows
streamlit run app.py
```

## Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run Streamlit
streamlit run app.py
```

## Usage

1. **Ensure backend is running** on http://localhost:8000
2. **Open frontend** at http://localhost:8501
3. **Upload a document** (PDF, DOCX, or TXT)
4. **Click "Analyze Document"**
5. **View results** in the PDF viewer or entity explorer
6. **Download** PDF report or JSONL data



## Features Explained

### PDF Report Viewer
- Embedded PDF display
- Full report with executive summary
- Key insights section
- Detailed entities

### Entity Explorer
- Grouped by category
- Expandable sections
- Mention counts displayed
- Attributes shown

### Downloads
- PDF report download
- JSONL data export
- Job ID reference

## Configuration

Edit `frontend/.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"

[server]
port = 8501
```

## Troubleshooting

### Cannot Connect to API
- Ensure backend is running: `uvicorn app.main:app --reload`
- Check backend URL: http://localhost:8000/health

### PDF Not Displaying
- Check browser PDF support
- Try downloading PDF instead
- Verify job_id is valid

### Slow Performance
- Large files take longer to process
- Wait for analysis to complete
- Check backend console for errors

## Requirements

- Python 3.9+
- Streamlit 1.39.0+
- Requests 2.32.3+
- Running backend API

## Tips

1. **Upload quality documents** for best results
2. **Check metrics** to verify analysis quality
3. **Use entity explorer** for quick insights
4. **Download PDF** for sharing
5. **Enable auto-download** for convenience

## Keyboard Shortcuts

- `Ctrl+R` - Refresh page
- `Ctrl+S` - Save (download)
- `Esc` - Close dialogs

## Browser Support

- Chrome (recommended)
- Firefox
- Edge
- Safari

## Development

To modify the frontend:

1. Edit `app.py`
2. Save changes
3. Streamlit auto-reloads

## API Integration

Frontend connects to:
- `POST /api/v1/analyze` - Upload & analyze
- `GET /api/v1/report/{job_id}` - Get PDF
- `GET /api/v1/data/{job_id}` - Get JSONL
- `GET /health` - Health check

## Customization

### Change Theme
Edit `.streamlit/config.toml`

### Modify Layout
Edit `app.py` - adjust columns, tabs, sections

### Add Features
- New tabs
- Additional metrics
- Custom visualizations

## Notes

- Frontend requires backend to be running
- PDF viewer works best in Chrome
- Large files may take 10-15 seconds to analyze
- Session state persists during page interactions