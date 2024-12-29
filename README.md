# TRMNL Chuck Norris Plugin

A TRMNL plugin that displays random Chuck Norris facts on your e-ink display.

## Features

- Fetches random Chuck Norris facts from api.chucknorris.io
- Optimized black and white display for e-ink screens
- Automatic text sizing and wrapping
- Dithered Chuck Norris image header
- Fact ID and timestamp footer
- Built-in caching system (1-hour default)
- Error handling with visual feedback

## Prerequisites

- Python 3.12+
- TRMNL device and API key
- Docker (optional)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/OptimumMeans/TRMNL-Chuck-Norris.git
cd TRMNL-Chuck-Norris
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create .env file:
```bash
cp .env.template .env
```

5. Update .env with your configuration:
```env
TRMNL_API_KEY=your_api_key_here
TRMNL_PLUGIN_UUID=your_plugin_uuid_here
```

## Development

### Running Locally

```bash
python -m src.app
```

The development server will start at:
- Home page: http://localhost:8080/
- Webhook endpoint: http://localhost:8080/webhook

### Display Configuration

The plugin is configured for TRMNL's 800x480 e-ink display and includes:

- Header with dithered Chuck Norris image
- Dynamically sized fact text
- Footer with fact ID and timestamp
- Automatic refresh every hour (configurable)

### Cache Configuration

- Facts are cached for 1 hour by default
- Cache timeout matches the display refresh interval
- Configure via `CACHE_TIMEOUT` and `REFRESH_INTERVAL` in .env

## Deployment

Deploy using render.yaml configuration:

```bash
render deploy
```

The render.yaml file includes:
- Python 3.12.0 runtime
- Gunicorn web server
- Environment variable configuration
- Build and start commands

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -am 'Add: new feature'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Create a Pull Request

## API Attribution

This plugin uses the [Chuck Norris API](https://api.chucknorris.io/), a free JSON API for hand curated Chuck Norris facts.

## License

MIT