# Swing Trading Analyzer - Next.js Frontend

A minimalist Next.js web application that displays stock market predictions for swing trading with entry points, exit points, and stop loss recommendations.

## Features

- Minimalist Design - Clean, distraction-free interface
- Real-time Data - Fetches predictions from Flask backend
- Configurable Results - Choose 5-30 stocks to display
- Probability Filtering - Filter by minimum probability
- Responsive Layout - Works on all devices
- Dark Mode Support - Automatic theme detection

## Prerequisites

- Node.js 18+
- Flask backend running on port 5000

## Installation

```bash
cd frontend

# Fix npm permissions if needed
sudo chown -R $(whoami) ~/.npm

# Install dependencies
npm install --legacy-peer-deps
```

## Configuration

Create `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:5000
```

## Running

```bash
# Development
npm run dev

# Production
npm run build
npm start
```

Open [http://localhost:3000](http://localhost:3000)

## Usage

1. **Start Flask Backend**: `cd .. && python app.py`
2. **Start Frontend**: `npm run dev`
3. Select number of stocks and minimum probability
4. Click Refresh to update data

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Main page
│   └── globals.css         # Styles
├── components/
│   ├── StockCard.tsx       # Stock display
│   └── LoadingSkeleton.tsx # Loading UI
├── lib/
│   └── api.ts              # API integration
└── .env.local              # Environment vars
```

## Troubleshooting

**Cannot connect to backend**:
- Ensure Flask is running: `python app.py`
- Check `.env.local` has correct URL
- Verify port 5000 is not blocked

**npm install fails**:
- Run: `npm cache clean --force`
- Use: `npm install --legacy-peer-deps`

## Deployment

Deploy to Vercel:
1. Push to GitHub
2. Connect to Vercel
3. Set `NEXT_PUBLIC_API_URL` environment variable
4. Deploy

## License

Educational purposes only. Not financial advice.

---

**Last Updated**: December 15, 2024
